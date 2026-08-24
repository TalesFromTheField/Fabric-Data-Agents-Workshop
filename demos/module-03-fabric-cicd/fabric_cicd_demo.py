#!/usr/bin/env python3
"""Module 03 CI/CD demo - deploy a Fabric data agent with fabric-cicd.

This script walks a workshop audience through a complete, working code-first
deployment of a Fabric data agent from a development workspace into a separate
production workspace, using the Microsoft `fabric-cicd` library.

It runs as a sequence of small, independently runnable stages so a presenter can
stop and talk between each one:

    bootstrap  Find the dev workspace and create/reuse a "<name> [prod]" workspace.
    export     Pull item definitions out of dev onto disk (what Git integration
               would give you), producing a valid fabric-cicd repository folder.
    scan       Find every cross-environment GUID reference in those files and
               generate a parameter.yml that re-points them. This is the dry run.
    deploy     Hand the folder to fabric-cicd and publish it into prod.
    verify     Re-export the deployed agent from prod and prove the references
               now point at prod items, not dev items.
    destroy    Delete the prod workspace so the demo leaves nothing behind.

    all        bootstrap -> export -> scan -> deploy -> verify.

Why the export stage exists: fabric-cicd deploys from a folder of item
definitions that normally arrives via Fabric Git integration. Wiring a workshop
room up to Azure DevOps or GitHub is a lot of setup for one demo, so this script
calls the Fabric item definition API to produce the same folder locally. The
files, the folder names, and the deployment behaviour are identical - only the
delivery mechanism differs.

Docs: https://microsoft.github.io/fabric-cicd/latest/
"""

from __future__ import annotations

import argparse
import base64
import contextlib
import json
import os
import re
import sys
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, List, NoReturn, Optional, Sequence, Set, Tuple

try:
    import requests
except ImportError:  # pragma: no cover - guidance for a fresh clone
    sys.exit("Missing dependency 'requests'. Run: pip install -r requirements.txt")


# --------------------------------------------------------------------------------------
# Constants
# --------------------------------------------------------------------------------------

FABRIC_API = "https://api.fabric.microsoft.com/v1"
FABRIC_SCOPE = "https://api.fabric.microsoft.com/.default"

# Item types the demo deploys. DataAgent is the star; the others are the data
# sources and assets it depends on. fabric-cicd publishes these in dependency
# order (Lakehouse before DataAgent) regardless of the order listed here.
DEFAULT_ITEM_TYPES = ["Lakehouse", "Warehouse", "Notebook", "SemanticModel", "DataAgent"]

# Fabric creates these items as an empty "shell" - they have no downloadable
# definition, so we synthesize a .platform file for them instead of calling
# getDefinition. This mirrors fabric_cicd.constants.SHELL_ONLY_PUBLISH.
SHELL_ONLY_TYPES = {"Lakehouse", "Warehouse", "SQLDatabase", "MLExperiment"}

PLATFORM_SCHEMA = (
    "https://developer.microsoft.com/json-schemas/fabric/gitIntegration/"
    "platformProperties/2.0.0/schema.json"
)

GUID_RE = re.compile(r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}")
NULL_GUID = "00000000-0000-0000-0000-000000000000"

STATE_FILE = ".demo-state.json"
WORKSPACE_DIR = "workspace"
PARAMETER_FILE = "parameter.yml"

# Cap on commented-out stubs written for unrecognized GUIDs. A single semantic
# model can contribute hundreds; listing them all helps nobody.
UNKNOWN_STUB_LIMIT = 20

# Stable namespace so a given item name+type always gets the same logicalId across
# re-runs of the demo. Keeps .platform files deterministic and diff-friendly.
LOGICAL_ID_NAMESPACE = uuid.UUID("6f1d6b18-9a2f-5f4e-93c0-3f0a3b1f77aa")


# --------------------------------------------------------------------------------------
# Console helpers
# --------------------------------------------------------------------------------------

_NO_COLOR = bool(os.environ.get("NO_COLOR")) or not sys.stdout.isatty()


def _c(code: str, text: str) -> str:
    return text if _NO_COLOR else f"\033[{code}m{text}\033[0m"


def stage(title: str) -> None:
    line = "=" * 74
    print(f"\n{_c('36', line)}\n{_c('1;36', title)}\n{_c('36', line)}")


def info(msg: str) -> None:
    print(f"  {msg}")


def ok(msg: str) -> None:
    print(f"  {_c('32', 'OK')}  {msg}")


def warn(msg: str) -> None:
    print(f"  {_c('33', 'WARN')}  {msg}")


def die(msg: str) -> NoReturn:
    print(f"\n  {_c('31', 'ERROR')}  {msg}\n", file=sys.stderr)
    raise SystemExit(1)


# --------------------------------------------------------------------------------------
# Authentication
# --------------------------------------------------------------------------------------


def build_credential(auth: str):
    """Return a TokenCredential.

    fabric-cicd requires an explicit credential - the old DefaultAzureCredential
    fallback and implicit notebook auth were removed for security reasons. Any
    object implementing azure.core.credentials.TokenCredential works.
    """
    try:
        from azure.identity import AzureCliCredential, ClientSecretCredential
    except ImportError:  # pragma: no cover
        die("Missing dependency 'azure-identity'. Run: pip install -r requirements.txt")

    if auth == "spn":
        tenant = os.environ.get("AZURE_TENANT_ID")
        client = os.environ.get("AZURE_CLIENT_ID")
        secret = os.environ.get("AZURE_CLIENT_SECRET")
        missing = [
            name
            for name, value in (
                ("AZURE_TENANT_ID", tenant),
                ("AZURE_CLIENT_ID", client),
                ("AZURE_CLIENT_SECRET", secret),
            )
            if not value
        ]
        if missing:
            die(f"--auth spn requires environment variables: {', '.join(missing)}")
        return ClientSecretCredential(tenant_id=tenant, client_id=client, client_secret=secret)

    # Default: whatever identity `az login` established (user, SPN, or managed identity).
    return AzureCliCredential()


# --------------------------------------------------------------------------------------
# Minimal Fabric REST client
# --------------------------------------------------------------------------------------


class FabricRestClient:
    """A deliberately small Fabric REST client.

    fabric-cicd talks to Fabric for us during `deploy`. This client covers only
    the handful of calls fabric-cicd does *not* do: creating a workspace,
    listing items, downloading definitions, and deleting a workspace.
    """

    def __init__(self, credential, timeout: int = 120) -> None:
        self._credential = credential
        self._timeout = timeout
        self._token: Optional[str] = None
        self._token_expiry: float = 0.0
        self._session = requests.Session()

    def _headers(self) -> Dict[str, str]:
        # Refresh a minute before expiry so long deployments don't fail mid-flight.
        if not self._token or time.time() > self._token_expiry - 60:
            token = self._credential.get_token(FABRIC_SCOPE)
            self._token = token.token
            self._token_expiry = float(token.expires_on)
        return {"Authorization": f"Bearer {self._token}", "Content-Type": "application/json"}

    def request(
        self,
        method: str,
        path: str,
        body: Optional[dict] = None,
        *,
        max_attempts: int = 5,
    ) -> Any:
        """Issue a request, transparently handling throttling and long-running ops."""
        url = path if path.startswith("http") else f"{FABRIC_API}{path}"

        for attempt in range(1, max_attempts + 1):
            response = self._session.request(
                method, url, headers=self._headers(), json=body, timeout=self._timeout
            )

            # 429/503: Fabric is throttling. Honour Retry-After and try again.
            if response.status_code in (429, 503):
                delay = int(response.headers.get("Retry-After", 2 ** attempt))
                warn(f"Throttled ({response.status_code}); retrying in {delay}s")
                time.sleep(delay)
                continue

            # 202: long-running operation. Poll to completion, then read the result.
            if response.status_code == 202:
                return self._await_operation(response)

            if not response.ok:
                raise FabricApiError(method, url, response)

            if not response.content:
                return None
            try:
                return response.json()
            except ValueError:
                return None

        die(f"Gave up after {max_attempts} attempts: {method} {url}")

    def _await_operation(self, response: requests.Response, max_wait: int = 600) -> Any:
        """Poll a Fabric long-running operation until it succeeds or fails."""
        location = response.headers.get("Location")
        if not location:
            # Accepted but nothing to poll - treat the body, if any, as the result.
            return response.json() if response.content else None

        # Never sleep for 0 seconds; a bad header would spin this loop.
        retry_after = max(1, int(response.headers.get("Retry-After", 3) or 3))

        waited = 0
        while waited < max_wait:
            time.sleep(retry_after)
            waited += retry_after

            poll = self._session.get(location, headers=self._headers(), timeout=self._timeout)
            if not poll.ok:
                raise FabricApiError("GET", location, poll)

            payload = poll.json() if poll.content else {}
            status = str(payload.get("status", "")).lower()

            if status in ("succeeded", "completed"):
                # The operation result lives on a sibling /result endpoint.
                result = self._session.get(
                    f"{location.rstrip('/')}/result", headers=self._headers(), timeout=self._timeout
                )
                if result.ok and result.content:
                    return result.json()
                return payload

            if status in ("failed", "cancelled"):
                error = payload.get("error") or payload
                raise RuntimeError(f"Fabric operation {status}: {json.dumps(error)[:500]}")

            if not status and payload:
                # Some endpoints return the finished payload directly instead of
                # a status envelope.
                return payload

        die(f"Long-running operation did not finish within {max_wait}s")

    # -- Convenience wrappers ----------------------------------------------------------

    def list_workspaces(self) -> List[dict]:
        return self.request("GET", "/workspaces").get("value", [])

    def get_workspace(self, workspace_id: str) -> dict:
        return self.request("GET", f"/workspaces/{workspace_id}")

    def create_workspace(self, display_name: str, capacity_id: Optional[str]) -> dict:
        body: Dict[str, Any] = {
            "displayName": display_name,
            "description": "Created by the Module 03 fabric-cicd workshop demo.",
        }
        if capacity_id:
            body["capacityId"] = capacity_id
        return self.request("POST", "/workspaces", body)

    def delete_workspace(self, workspace_id: str) -> None:
        self.request("DELETE", f"/workspaces/{workspace_id}")

    def list_items(self, workspace_id: str) -> List[dict]:
        return self.request("GET", f"/workspaces/{workspace_id}/items").get("value", [])

    def get_item_definition(self, workspace_id: str, item_id: str, fmt: Optional[str] = None) -> dict:
        path = f"/workspaces/{workspace_id}/items/{item_id}/getDefinition"
        if fmt:
            path += f"?format={fmt}"
        return self.request("POST", path) or {}


class FabricApiError(RuntimeError):
    """Raised when the Fabric API returns an error, with a readable message."""

    def __init__(self, method: str, url: str, response: requests.Response) -> None:
        detail = (response.text or "").strip()
        if len(detail) > 600:
            detail = detail[:600] + " ..."
        super().__init__(f"{method} {url} -> HTTP {response.status_code}\n  {detail}")
        self.status_code = response.status_code


# --------------------------------------------------------------------------------------
# Demo state (carried between stages)
# --------------------------------------------------------------------------------------


@dataclass
class DemoState:
    path: Path
    dev_workspace_id: Optional[str] = None
    dev_workspace_name: Optional[str] = None
    prod_workspace_id: Optional[str] = None
    prod_workspace_name: Optional[str] = None
    capacity_id: Optional[str] = None
    exported_items: List[dict] = field(default_factory=list)

    @classmethod
    def load(cls, path: Path) -> "DemoState":
        if path.exists():
            data = json.loads(path.read_text(encoding="utf-8"))
            return cls(
                path=path,
                dev_workspace_id=data.get("dev_workspace_id"),
                dev_workspace_name=data.get("dev_workspace_name"),
                prod_workspace_id=data.get("prod_workspace_id"),
                prod_workspace_name=data.get("prod_workspace_name"),
                capacity_id=data.get("capacity_id"),
                exported_items=data.get("exported_items", []),
            )
        return cls(path=path)

    def save(self) -> None:
        payload = {
            "dev_workspace_id": self.dev_workspace_id,
            "dev_workspace_name": self.dev_workspace_name,
            "prod_workspace_id": self.prod_workspace_id,
            "prod_workspace_name": self.prod_workspace_name,
            "capacity_id": self.capacity_id,
            "exported_items": self.exported_items,
        }
        self.path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


# --------------------------------------------------------------------------------------
# Stage 1: bootstrap
# --------------------------------------------------------------------------------------


def resolve_workspace(client: FabricRestClient, ref: str) -> dict:
    """Resolve a workspace by GUID or by display name."""
    if GUID_RE.fullmatch(ref):
        try:
            return client.get_workspace(ref)
        except FabricApiError as exc:
            die(f"No workspace with ID '{ref}'.\n  {exc}")

    matches = [w for w in client.list_workspaces() if w.get("displayName") == ref]
    if not matches:
        available = sorted(w.get("displayName", "?") for w in client.list_workspaces())
        die(
            f"No workspace named '{ref}'. Workspaces you can see:\n    "
            + "\n    ".join(available[:25])
        )
    if len(matches) > 1:
        die(f"Multiple workspaces named '{ref}'. Pass the workspace ID instead.")
    return client.get_workspace(matches[0]["id"])


def cmd_bootstrap(args: argparse.Namespace, client: FabricRestClient, state: DemoState) -> None:
    stage("STAGE 1/6  bootstrap - resolve dev workspace, create the prod workspace")

    dev = resolve_workspace(client, args.dev_workspace)
    state.dev_workspace_id = dev["id"]
    state.dev_workspace_name = dev.get("displayName")
    state.capacity_id = dev.get("capacityId")
    ok(f"Dev workspace : {state.dev_workspace_name}  ({state.dev_workspace_id})")

    if not state.capacity_id:
        warn(
            "Dev workspace reports no capacity. The prod workspace will be created "
            "without one, and Fabric items will fail to deploy into it."
        )
    else:
        info(f"Capacity      : {state.capacity_id}")

    prod_name = args.prod_workspace or f"{state.dev_workspace_name} [prod]"

    existing = [w for w in client.list_workspaces() if w.get("displayName") == prod_name]
    if existing:
        prod = client.get_workspace(existing[0]["id"])
        ok(f"Prod workspace: {prod_name}  ({prod['id']})  [reusing existing]")
    else:
        info(f"Creating workspace '{prod_name}' ...")
        created = client.create_workspace(prod_name, state.capacity_id)
        prod = client.get_workspace(created["id"])
        ok(f"Prod workspace: {prod_name}  ({prod['id']})  [created]")

    if not prod.get("capacityId"):
        warn("Prod workspace has no capacity assigned - deployment will likely fail.")

    state.prod_workspace_id = prod["id"]
    state.prod_workspace_name = prod_name
    state.save()

    print()
    info("Talk track: nothing here is fabric-cicd yet. This is plain Fabric REST,")
    info("standing in for whatever provisions your environments today.")


# --------------------------------------------------------------------------------------
# Stage 2: export
# --------------------------------------------------------------------------------------


def logical_id_for(item_name: str, item_type: str) -> str:
    return str(uuid.uuid5(LOGICAL_ID_NAMESPACE, f"{item_type}:{item_name}"))


def write_platform_file(folder: Path, item_name: str, item_type: str, description: str) -> None:
    """Write the .platform file fabric-cicd uses to identify an item on disk."""
    payload = {
        "$schema": PLATFORM_SCHEMA,
        "metadata": {"type": item_type, "displayName": item_name, "description": description or ""},
        "config": {"version": "2.0", "logicalId": logical_id_for(item_name, item_type)},
    }
    (folder / ".platform").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def export_item(
    client: FabricRestClient, workspace_id: str, item: dict, target_root: Path
) -> Tuple[Path, int]:
    """Write one item's definition to disk as <Name>.<Type>/... and return the folder."""
    item_name = item["displayName"]
    item_type = item["type"]
    folder = target_root / f"{item_name}.{item_type}"
    folder.mkdir(parents=True, exist_ok=True)

    if item_type in SHELL_ONLY_TYPES:
        # No definition to download - Fabric creates these as empty shells.
        write_platform_file(folder, item_name, item_type, item.get("description", ""))
        return folder, 1

    # Notebooks are requested in .ipynb form; fabric-cicd publishes them the same way.
    fmt = "ipynb" if item_type == "Notebook" else None
    definition = client.get_item_definition(workspace_id, item["id"], fmt)
    parts = definition.get("definition", {}).get("parts", [])
    if not parts:
        warn(f"'{item_name}' ({item_type}) returned no definition parts; writing shell only.")
        write_platform_file(folder, item_name, item_type, item.get("description", ""))
        return folder, 1

    written = 0
    for part in parts:
        rel = part.get("path")
        payload = part.get("payload")
        if not rel or payload is None:
            continue
        destination = folder / rel
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(base64.b64decode(payload))
        written += 1

    # The export API stamps a placeholder logicalId. Replace it with a deterministic
    # one so every item on disk has a unique, stable identity across re-runs.
    normalize_platform_file(folder, item_name, item_type, item.get("description", ""))
    return folder, written


def normalize_platform_file(folder: Path, item_name: str, item_type: str, description: str) -> None:
    platform = folder / ".platform"
    if not platform.exists():
        write_platform_file(folder, item_name, item_type, description)
        return

    try:
        data = json.loads(platform.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        write_platform_file(folder, item_name, item_type, description)
        return

    config = data.setdefault("config", {})
    if not config.get("logicalId") or config["logicalId"] == NULL_GUID:
        config["logicalId"] = logical_id_for(item_name, item_type)
    data.setdefault("metadata", {}).setdefault("displayName", item_name)
    data["metadata"].setdefault("type", item_type)
    platform.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def cmd_export(args: argparse.Namespace, client: FabricRestClient, state: DemoState) -> None:
    stage("STAGE 2/6  export - pull item definitions out of dev onto disk")

    if not state.dev_workspace_id:
        die("No dev workspace in state. Run the 'bootstrap' stage first.")

    target_root = args.demo_dir / WORKSPACE_DIR
    if target_root.exists() and not args.keep:
        import shutil

        shutil.rmtree(target_root)
    target_root.mkdir(parents=True, exist_ok=True)

    in_scope = set(args.item_types)
    all_items = client.list_items(state.dev_workspace_id)
    selected = [i for i in all_items if i["type"] in in_scope]

    skipped = [i for i in all_items if i["type"] not in in_scope]
    if skipped:
        types = sorted({i["type"] for i in skipped})
        info(f"Skipping out-of-scope item types: {', '.join(types)}")

    if not selected:
        die(
            "No in-scope items found in the dev workspace.\n"
            f"  Looking for: {', '.join(sorted(in_scope))}\n"
            "  Build the lakehouse and data agent from Modules 02/03 first."
        )

    agents = [i for i in selected if i["type"] == "DataAgent"]
    if not agents:
        warn("No DataAgent found in the dev workspace - the headline of this demo is missing.")

    exported: List[dict] = []
    for item in sorted(selected, key=lambda i: (i["type"], i["displayName"])):
        folder, count = export_item(client, state.dev_workspace_id, item, target_root)
        exported.append(
            {"id": item["id"], "name": item["displayName"], "type": item["type"], "folder": folder.name}
        )
        suffix = "shell only (no definition)" if item["type"] in SHELL_ONLY_TYPES else f"{count} file(s)"
        ok(f"{item['type']:<14} {item['displayName']:<32} -> {folder.name}  [{suffix}]")

    state.exported_items = exported
    state.save()

    print()
    info(f"Repository folder: {target_root}")
    info("This is exactly the folder layout Fabric Git integration produces, and")
    info("exactly what fabric-cicd expects as its `repository_directory`.")

    if agents:
        print()
        info("Data agent layout (Module 03 section 3.6 in file form):")
        agent_folder = target_root / f"{agents[0]['displayName']}.DataAgent"
        print_tree(agent_folder, prefix="    ", max_entries=args.tree_limit)


def print_tree(root: Path, prefix: str = "", max_entries: int = 40) -> None:
    """Print a compact directory tree so the audience can see the real structure."""
    if not root.exists():
        return
    paths = sorted(p for p in root.rglob("*") if p.is_file())
    print(f"{prefix}{root.name}/")
    for path in paths[:max_entries]:
        rel = path.relative_to(root).as_posix()
        print(f"{prefix}  {rel}")
    if len(paths) > max_entries:
        print(f"{prefix}  ... and {len(paths) - max_entries} more file(s)")


# --------------------------------------------------------------------------------------
# Stage 3: scan + generate parameter.yml
# --------------------------------------------------------------------------------------

# Files fabric-cicd never parameterizes, so there is no point reporting hits in them.
NON_PARAMETERIZED_FILES = {".platform"}


def discover_item_folders(root: Path) -> List[Tuple[Path, str]]:
    """Find every item folder under root, using .platform as the marker.

    This is how fabric-cicd itself identifies items, and it conveniently excludes
    anything that is not part of an item - including the parameter.yml we
    generate into the same directory.
    """
    folders: List[Tuple[Path, str]] = []
    for platform in sorted(root.rglob(".platform")):
        folder = platform.parent
        item_type = ""
        try:
            data = json.loads(platform.read_text(encoding="utf-8"))
            item_type = data.get("metadata", {}).get("type", "")
        except (json.JSONDecodeError, OSError):
            pass
        if not item_type and "." in folder.name:
            item_type = folder.name.rsplit(".", 1)[1]
        folders.append((folder, item_type))
    return folders


def iter_text_files(root: Path) -> Iterable[Tuple[Path, str]]:
    """Yield (file, owning item type) for every parameterizable file under root."""
    for folder, item_type in discover_item_folders(root):
        for path in sorted(folder.rglob("*")):
            if not path.is_file() or path.name in NON_PARAMETERIZED_FILES:
                continue
            try:
                path.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                continue
            yield path, item_type


def scan_for_references(
    workspace_root: Path, dev_workspace_id: str, exported_items: Sequence[dict]
) -> Dict[str, Dict[str, Any]]:
    """Find dev workspace/item GUIDs referenced inside the exported definitions.

    Returns a map of guid -> {"kind", "name", "type", "files": [...], "item_types": {...}}.
    """
    by_guid: Dict[str, dict] = {i["id"].lower(): i for i in exported_items}
    findings: Dict[str, Dict[str, Any]] = {}

    for path, owner_type in iter_text_files(workspace_root):
        content = path.read_text(encoding="utf-8")

        for match in set(GUID_RE.findall(content)):
            guid = match.lower()
            if guid == NULL_GUID:
                continue

            if guid == dev_workspace_id.lower():
                entry = findings.setdefault(
                    guid,
                    {"kind": "workspace", "name": "(dev workspace)", "type": "", "files": [], "item_types": set()},
                )
            elif guid in by_guid:
                item = by_guid[guid]
                entry = findings.setdefault(
                    guid,
                    {"kind": "item", "name": item["name"], "type": item["type"], "files": [], "item_types": set()},
                )
            else:
                # A GUID we can't attribute: a connection, a source outside the
                # workspace, or an internal identifier. Report it, don't guess.
                entry = findings.setdefault(
                    guid,
                    {"kind": "unknown", "name": "(unrecognized)", "type": "", "files": [], "item_types": set()},
                )

            entry["files"].append(path.relative_to(workspace_root).as_posix())
            if owner_type:
                entry["item_types"].add(owner_type)

    return findings


def render_parameter_yaml(
    findings: Dict[str, Dict[str, Any]], environment: str, include_unknown: bool
) -> Optional[str]:
    """Build a parameter.yml that re-points dev references at target-workspace items.

    Uses fabric-cicd dynamic replacement variables so the file stays portable:
      $workspace.$id                      -> the target workspace's ID
      $items.<Type>.<Name>.$id            -> the deployed item's ID in the target

    Returns None when there is nothing to parameterize. An empty parameter.yml is
    not valid to fabric-cicd, and a missing one simply means "no replacements".
    """
    lines: List[str] = [
        "# Generated by fabric_cicd_demo.py - safe to edit and commit.",
        "#",
        "# Every entry below is a value that is correct in DEV and wrong everywhere else.",
        "# fabric-cicd rewrites them in memory at deploy time; your source files are",
        "# never modified.",
        "#",
        "# $workspace.$id            -> ID of the workspace being deployed into",
        "# $items.<Type>.<Name>.$id  -> ID of that item *after* it lands in the target",
        "#",
        "# Docs: https://microsoft.github.io/fabric-cicd/latest/how_to/parameterization/",
        "",
    ]

    body: List[str] = []
    emitted = 0
    unknown_stubs: List[str] = []
    unknown_stub_count = 0

    for guid, entry in sorted(findings.items(), key=lambda kv: (kv[1]["kind"], kv[1]["name"])):
        if entry["kind"] == "unknown":
            if not include_unknown:
                continue
            # Emit these COMMENTED OUT on purpose. Most unrecognized GUIDs are
            # internal identifiers (TMDL lineageTag, and similar), not
            # cross-environment references. Replacing them would corrupt the
            # item. Uncomment only the ones you have confirmed are connections
            # or external references, and supply a real value.
            if unknown_stub_count < UNKNOWN_STUB_LIMIT:
                unknown_stubs.append(f"    #   seen in: {sorted(set(entry['files']))[0]}")
                unknown_stubs.append(f'    # - find_value: "{guid}"')
                unknown_stubs.append("    #   replace_value:")
                unknown_stubs.append(f'    #       {environment}: "REPLACE-ME"')
                unknown_stubs.append("")
                unknown_stub_count += 1
            continue

        if entry["kind"] == "workspace":
            replacement = "$workspace.$id"
            comment = "the dev workspace ID, wherever the agent recorded it"
        else:
            replacement = f"$items.{entry['type']}.{entry['name']}.$id"
            comment = f"dev {entry['type']} '{entry['name']}'"

        item_types = sorted(entry["item_types"])
        body.append(f"    # {comment}")
        for ref in sorted(set(entry["files"]))[:4]:
            body.append(f"    #   seen in: {ref}")
        body.append(f'    - find_value: "{guid}"')
        body.append("      replace_value:")
        body.append(f'          {environment}: "{replacement}"')
        if item_types:
            if len(item_types) == 1:
                body.append(f'      item_type: "{item_types[0]}"')
            else:
                rendered = ", ".join(f'"{t}"' for t in item_types)
                body.append(f"      item_type: [{rendered}]")
        body.append("")
        emitted += 1

    if emitted == 0:
        return None

    lines.append("find_replace:")
    lines.extend(body)

    if unknown_stubs:
        lines.append("    # ---------------------------------------------------------------")
        lines.append("    # Unrecognized GUIDs, deliberately COMMENTED OUT.")
        lines.append("    #")
        lines.append("    # Most are internal identifiers - TMDL lineageTag values in semantic")
        lines.append("    # models, and similar - and replacing them would corrupt the item.")
        lines.append("    # Uncomment only entries you have confirmed are connections or")
        lines.append("    # external references, and supply a real value.")
        lines.append("    # ---------------------------------------------------------------")
        lines.extend(unknown_stubs)

    return "\n".join(lines)


def cmd_scan(args: argparse.Namespace, client: FabricRestClient, state: DemoState) -> None:
    stage("STAGE 3/6  scan - find environment-specific references, write parameter.yml")

    workspace_root = args.demo_dir / WORKSPACE_DIR
    if not workspace_root.exists():
        die("No exported workspace folder. Run the 'export' stage first.")
    if not state.dev_workspace_id:
        die("No dev workspace in state. Run the 'bootstrap' stage first.")

    findings = scan_for_references(workspace_root, state.dev_workspace_id, state.exported_items)

    actionable = {g: e for g, e in findings.items() if e["kind"] in ("workspace", "item")}
    unknown = {g: e for g, e in findings.items() if e["kind"] == "unknown"}

    if not actionable:
        warn("No references to in-scope items were found. Nothing needs re-pointing.")
    else:
        info(f"{len(actionable)} reference(s) that MUST change between environments:")
        print()
        print(f"    {'KIND':<10} {'WHAT':<34} {'FOUND IN':<28} REWRITES TO")
        print(f"    {'-' * 10} {'-' * 34} {'-' * 28} {'-' * 30}")
        for guid, entry in sorted(actionable.items(), key=lambda kv: (kv[1]["kind"], kv[1]["name"])):
            if entry["kind"] == "workspace":
                target = "$workspace.$id"
                what = entry["name"]
            else:
                target = f"$items.{entry['type']}.{entry['name']}.$id"
                what = f"{entry['type']} / {entry['name']}"
            owners = ", ".join(sorted(entry["item_types"])) or "-"
            print(f"    {entry['kind']:<10} {what[:34]:<34} {owners[:28]:<28} {target}")
            info(f"       {guid}")

    if unknown:
        # Summarize rather than list. A semantic model alone can contribute
        # hundreds of internal GUIDs, which would bury the useful output.
        by_type: Dict[str, int] = {}
        for entry in unknown.values():
            for owner in entry["item_types"] or {"(unattributed)"}:
                by_type[owner] = by_type.get(owner, 0) + 1
        summary = ", ".join(f"{t} ({n})" for t, n in sorted(by_type.items(), key=lambda kv: -kv[1]))

        print()
        info(f"{len(unknown)} unrecognized GUID(s), by owning item type: {summary}")
        info("Most of these are internal identifiers - TMDL lineageTag values in")
        info("semantic models, and similar - not cross-environment references, so")
        info("they are left alone. Connections also land here: those are not source")
        info("controlled and must already exist in the target workspace.")
        if not args.include_unknown:
            info("Use --include-unknown to emit them as commented-out stubs.")

    parameter_path = workspace_root / PARAMETER_FILE
    content = render_parameter_yaml(findings, args.environment, args.include_unknown)

    if content is None:
        if parameter_path.exists():
            parameter_path.unlink()
        print()
        warn("Nothing to parameterize, so no parameter.yml was written.")
        warn("fabric-cicd treats a missing parameter file as 'no replacements'.")
        return

    parameter_path.write_text(content, encoding="utf-8")

    print()
    ok(f"Wrote {parameter_path}")
    print()
    print(_c("2", content.rstrip()))
    print()
    info("This is the dry run. Nothing has been deployed. Read the file, edit if needed,")
    info("then run the deploy stage.")


# --------------------------------------------------------------------------------------
# Stage 4: deploy (this is the fabric-cicd part)
# --------------------------------------------------------------------------------------


def cmd_deploy(args: argparse.Namespace, client: FabricRestClient, state: DemoState) -> None:
    stage("STAGE 4/6  deploy - hand the folder to fabric-cicd")

    if not state.prod_workspace_id:
        die("No prod workspace in state. Run the 'bootstrap' stage first.")

    workspace_root = args.demo_dir / WORKSPACE_DIR
    if not workspace_root.exists():
        die("No exported workspace folder. Run the 'export' stage first.")
    if not (workspace_root / PARAMETER_FILE).exists():
        warn("No parameter.yml found - deploying without any value replacement.")
        warn("Run the 'scan' stage first if you expected references to be re-pointed.")

    try:
        from fabric_cicd import FabricWorkspace, publish_all_items, unpublish_all_orphan_items
    except ImportError:
        die("Missing dependency 'fabric-cicd'. Run: pip install -r requirements.txt")

    if args.debug:
        from fabric_cicd import change_log_level

        change_log_level("DEBUG")

    info(f"Target workspace : {state.prod_workspace_name}  ({state.prod_workspace_id})")
    info(f"Repository       : {workspace_root}")
    info(f"Environment key  : {args.environment}")
    info(f"Item types       : {', '.join(args.item_types)}")
    print()

    # ---- The entire fabric-cicd surface area for this demo is these few lines. ----
    target_workspace = FabricWorkspace(
        workspace_id=state.prod_workspace_id,
        environment=args.environment,
        repository_directory=str(workspace_root),
        item_type_in_scope=list(args.item_types),
        token_credential=args.credential,
    )

    publish_all_items(target_workspace)

    if args.unpublish_orphans:
        # Deletes anything in the target that is no longer in the repository.
        # Off by default: it is the destructive half of "the repo is the truth".
        unpublish_all_orphan_items(target_workspace)
    # ------------------------------------------------------------------------------

    print()
    ok("Deployment complete.")
    info("Re-run this stage as often as you like - fabric-cicd matches items by")
    info("name and type, so a second run updates rather than duplicates.")


# --------------------------------------------------------------------------------------
# Stage 5: verify
# --------------------------------------------------------------------------------------


def cmd_verify(args: argparse.Namespace, client: FabricRestClient, state: DemoState) -> None:
    stage("STAGE 5/6  verify - prove the agent points at PROD, not DEV")

    if not state.prod_workspace_id or not state.dev_workspace_id:
        die("Missing workspace state. Run the 'bootstrap' stage first.")

    prod_items = client.list_items(state.prod_workspace_id)
    in_scope = set(args.item_types)
    deployed = [i for i in prod_items if i["type"] in in_scope]

    expected = {(i["name"], i["type"]) for i in state.exported_items}
    actual = {(i["displayName"], i["type"]) for i in deployed}

    info("Items now in the prod workspace:")
    for item in sorted(deployed, key=lambda i: (i["type"], i["displayName"])):
        ok(f"{item['type']:<14} {item['displayName']:<32} {item['id']}")

    missing = expected - actual
    if missing:
        print()
        for name, item_type in sorted(missing):
            warn(f"Expected but not found: {item_type} '{name}'")

    # Re-export the prod data agent and check which GUIDs it now carries.
    agents = [i for i in deployed if i["type"] == "DataAgent"]
    if not agents:
        warn("No DataAgent in the prod workspace - cannot verify re-pointing.")
        return

    verify_root = args.demo_dir / ".verify"
    if verify_root.exists():
        import shutil

        shutil.rmtree(verify_root)
    verify_root.mkdir(parents=True, exist_ok=True)

    dev_guids = {i["id"].lower() for i in state.exported_items}
    dev_guids.add(state.dev_workspace_id.lower())
    prod_guids = {i["id"].lower() for i in deployed}
    prod_guids.add(state.prod_workspace_id.lower())

    stale: Dict[str, Set[str]] = {}
    fresh: Dict[str, Set[str]] = {}

    for agent in agents:
        folder, _ = export_item(client, state.prod_workspace_id, agent, verify_root)
        for path, _owner_type in iter_text_files(folder):
            rel = path.relative_to(verify_root).as_posix()
            for guid in {g.lower() for g in GUID_RE.findall(path.read_text(encoding="utf-8"))}:
                if guid in dev_guids:
                    stale.setdefault(rel, set()).add(guid)
                elif guid in prod_guids:
                    fresh.setdefault(rel, set()).add(guid)

    print()
    if fresh:
        ok(f"Found PROD references in {len(fresh)} file(s) of the deployed agent:")
        for rel, guids in sorted(fresh.items()):
            for guid in sorted(guids):
                info(f"  {rel}  ->  {guid}")

    if stale:
        print()
        warn(f"Still-DEV references in {len(stale)} file(s) - parameterization missed these:")
        for rel, guids in sorted(stale.items()):
            for guid in sorted(guids):
                warn(f"  {rel}  ->  {guid}")
        warn("Add them to parameter.yml and re-run scan/deploy.")
    else:
        print()
        ok("No dev-workspace references remain in the deployed agent. Re-pointing worked.")

    print()
    info("Reminder: a Lakehouse deploys as an empty shell. The prod agent is wired")
    info("to the prod lakehouse, but that lakehouse has no data until you load it.")
    info("Open the agent in prod and confirm its data source shows the prod lakehouse.")


# --------------------------------------------------------------------------------------
# Stage 6: destroy
# --------------------------------------------------------------------------------------


def cmd_destroy(args: argparse.Namespace, client: FabricRestClient, state: DemoState) -> None:
    stage("STAGE 6/6  destroy - remove the prod workspace")

    if not state.prod_workspace_id:
        die("No prod workspace in state; nothing to delete.")

    name = state.prod_workspace_name or state.prod_workspace_id

    if not args.yes:
        answer = input(f"  Delete workspace '{name}' and everything in it? [y/N] ").strip().lower()
        if answer != "y":
            info("Cancelled - nothing deleted.")
            return

    client.delete_workspace(state.prod_workspace_id)
    ok(f"Deleted workspace '{name}'.")

    state.prod_workspace_id = None
    state.prod_workspace_name = None
    state.save()

    info("The dev workspace and the exported folder are untouched.")


# --------------------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------------------

STAGES = {
    "bootstrap": cmd_bootstrap,
    "export": cmd_export,
    "scan": cmd_scan,
    "deploy": cmd_deploy,
    "verify": cmd_verify,
    "destroy": cmd_destroy,
}

ALL_SEQUENCE = ["bootstrap", "export", "scan", "deploy", "verify"]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="fabric_cicd_demo.py",
        description="Deploy a Fabric data agent from dev to prod with fabric-cicd.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  # Run the whole demo end to end\n"
            "  python fabric_cicd_demo.py all --dev-workspace 'Fabric Agents Workshop'\n\n"
            "  # Or one stage at a time, pausing to talk between each\n"
            "  python fabric_cicd_demo.py bootstrap --dev-workspace 'Fabric Agents Workshop'\n"
            "  python fabric_cicd_demo.py export\n"
            "  python fabric_cicd_demo.py scan\n"
            "  python fabric_cicd_demo.py deploy\n"
            "  python fabric_cicd_demo.py verify\n"
            "  python fabric_cicd_demo.py destroy --yes\n"
        ),
    )
    parser.add_argument(
        "stage",
        choices=sorted(STAGES) + ["all"],
        help="Which stage to run ('all' runs bootstrap through verify).",
    )
    parser.add_argument(
        "--dev-workspace",
        help="Source workspace name or ID. Required for 'bootstrap' and 'all'.",
    )
    parser.add_argument(
        "--prod-workspace",
        help="Target workspace name. Defaults to '<dev name> [prod]'.",
    )
    parser.add_argument(
        "--environment",
        default="PROD",
        help="parameter.yml environment key to apply (default: PROD).",
    )
    parser.add_argument(
        "--item-types",
        nargs="+",
        default=DEFAULT_ITEM_TYPES,
        metavar="TYPE",
        help=f"Item types in scope (default: {' '.join(DEFAULT_ITEM_TYPES)}).",
    )
    parser.add_argument(
        "--auth",
        choices=["cli", "spn"],
        default="cli",
        help="cli = use 'az login' identity (default). spn = AZURE_* env vars.",
    )
    parser.add_argument(
        "--unpublish-orphans",
        action="store_true",
        help="Also delete target items that no longer exist in the repository.",
    )
    parser.add_argument(
        "--include-unknown",
        action="store_true",
        help="Include unattributable GUIDs in parameter.yml as REPLACE-ME entries.",
    )
    parser.add_argument("--keep", action="store_true", help="Do not wipe the export folder first.")
    parser.add_argument("--debug", action="store_true", help="Enable fabric-cicd DEBUG logging.")
    parser.add_argument("--yes", action="store_true", help="Skip the destroy confirmation prompt.")
    parser.add_argument(
        "--tree-limit", type=int, default=40, help="Max files to print in the tree view."
    )
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    args.demo_dir = Path(__file__).resolve().parent

    # fabric-cicd logs through the logging module while this script uses print().
    # Without line buffering the two streams interleave out of order whenever
    # stdout is piped, which makes the staged output confusing to follow.
    with contextlib.suppress(AttributeError, ValueError):
        sys.stdout.reconfigure(line_buffering=True, write_through=True)

    stages = ALL_SEQUENCE if args.stage == "all" else [args.stage]

    if "bootstrap" in stages and not args.dev_workspace:
        parser.error("--dev-workspace is required for the 'bootstrap' stage")

    credential = build_credential(args.auth)
    args.credential = credential
    client = FabricRestClient(credential)
    state = DemoState.load(args.demo_dir / STATE_FILE)

    try:
        for name in stages:
            STAGES[name](args, client, state)
    except FabricApiError as exc:
        die(str(exc))
    except KeyboardInterrupt:
        print("\n  Interrupted.", file=sys.stderr)
        return 130

    if args.stage == "all":
        stage("Demo complete")
        info("Run 'python fabric_cicd_demo.py destroy' to remove the prod workspace.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
