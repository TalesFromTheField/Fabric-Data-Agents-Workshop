#!/usr/bin/env python3
"""Deploy a Fabric data agent with the fabric-cicd Python library.

This is the Module 03 CI/CD demo. It uses nothing but `fabric-cicd` and
`azure-identity` - no hand-rolled REST calls, no Fabric CLI. (A Fabric CLI
version of the same deployment lives in ./fabric-cli/ if you want to compare.)

The library has exactly one job: take a directory of Fabric item definitions
and make a target workspace match it. It does not create workspaces, it does
not export items, and it does not copy data. Everything here stays inside that
job.

Commands:

    inspect   Show what is in the repository directory and what parameter.yml
              will rewrite. Pure local file reading - touches no API.

    deploy    Deploy into the target workspace and report what landed.

Two deployment styles are shown, because the library offers both:

    --mode config     deploy_with_config() reads config.yml. This is the
                      recommended path and what `fab deploy` runs internally.

    --mode explicit   FabricWorkspace(...) + publish_all_items(). The
                      imperative form, useful when settings are computed at
                      runtime rather than committed to a file.

Before running, create your target workspace in Fabric and put its name in
config.yml. Creating workspaces is deliberately out of scope - see the README.

Docs: https://microsoft.github.io/fabric-cicd/latest/
"""

from __future__ import annotations

import argparse
import contextlib
import json
import sys
from pathlib import Path
from typing import Any, List, Optional, Tuple

import yaml

DEMO_DIR = Path(__file__).resolve().parent
DEFAULT_CONFIG = DEMO_DIR / "config.yml"


# --------------------------------------------------------------------------------------
# Console helpers
# --------------------------------------------------------------------------------------


def stage(title: str) -> None:
    bar = "=" * 74
    print(f"\n{bar}\n{title}\n{bar}")


def info(msg: str) -> None:
    print(f"  {msg}")


def ok(msg: str) -> None:
    print(f"  OK    {msg}")


def warn(msg: str) -> None:
    print(f"  WARN  {msg}")


def die(msg: str) -> "None":
    print(f"\n  ERROR {msg}\n", file=sys.stderr)
    raise SystemExit(1)


# --------------------------------------------------------------------------------------
# Local inspection - no API calls
# --------------------------------------------------------------------------------------


def load_config(config_path: Path) -> dict:
    if not config_path.is_file():
        die(f"Config file not found: {config_path}")
    return yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}


def resolve_setting(value: Any, environment: str) -> Any:
    """config.yml values are either a plain value or a per-environment mapping."""
    if isinstance(value, dict) and environment in value:
        return value[environment]
    if isinstance(value, dict) and any(k.isupper() for k in value):
        return None  # an environment mapping that has no entry for this environment
    return value


def repository_directory(config: dict, environment: str, config_path: Path) -> Path:
    raw = resolve_setting(config.get("core", {}).get("repository_directory"), environment)
    if not raw:
        die("core.repository_directory is missing from the config file.")
    path = Path(raw)
    # Relative paths in config.yml resolve against the config file's location.
    return path if path.is_absolute() else (config_path.parent / path).resolve()


def discover_items(repo_dir: Path) -> List[Tuple[str, str, Path]]:
    """Find every Fabric item in the directory by locating .platform files.

    This is the same marker fabric-cicd uses to identify items on disk.
    """
    items: List[Tuple[str, str, Path]] = []
    for platform in sorted(repo_dir.rglob(".platform")):
        try:
            meta = json.loads(platform.read_text(encoding="utf-8")).get("metadata", {})
        except (json.JSONDecodeError, OSError):
            warn(f"Could not read {platform}")
            continue
        items.append((meta.get("type", "?"), meta.get("displayName", "?"), platform.parent))
    return items


def cmd_inspect(args: argparse.Namespace) -> None:
    stage("INSPECT - what is in the repository, and what will be rewritten")

    config = load_config(args.config)
    core = config.get("core", {})
    repo_dir = repository_directory(config, args.environment, args.config)

    workspace = resolve_setting(core.get("workspace"), args.environment)
    workspace_id = resolve_setting(core.get("workspace_id"), args.environment)
    in_scope = resolve_setting(core.get("item_types_in_scope"), args.environment)

    info(f"Config file      : {args.config}")
    info(f"Environment      : {args.environment}")
    info(f"Target workspace : {workspace_id or workspace or '(not set for this environment)'}")
    info(f"Repository       : {repo_dir}")
    info(f"Item types       : {', '.join(in_scope) if in_scope else 'all supported types'}")

    if not repo_dir.is_dir():
        die(f"Repository directory does not exist: {repo_dir}")

    items = discover_items(repo_dir)
    if not items:
        die(f"No Fabric items found in {repo_dir} (looked for .platform files).")

    print()
    info(f"{len(items)} item(s) found:")
    for item_type, name, path in items:
        file_count = sum(1 for p in path.rglob("*") if p.is_file())
        scope_note = ""
        if in_scope and item_type not in in_scope:
            scope_note = "  [OUT OF SCOPE - will not deploy]"
        ok(f"{item_type:<12} {name:<24} {file_count:>2} file(s){scope_note}")

    # Show the agent's on-disk shape - this is Module 03 section 3.6 in file form.
    agents = [(t, n, p) for t, n, p in items if t == "DataAgent"]
    for _, name, path in agents:
        print()
        info(f"'{name}' file layout:")
        for f in sorted(p for p in path.rglob("*") if p.is_file()):
            print(f"      {f.relative_to(path).as_posix()}")

    # Show what parameter.yml will do.
    param_raw = resolve_setting(core.get("parameter"), args.environment)
    if not param_raw:
        print()
        warn("No parameter file configured - nothing will be re-pointed.")
        warn("A data agent deployed this way keeps its development data sources.")
        return

    param_path = Path(param_raw)
    if not param_path.is_absolute():
        param_path = (args.config.parent / param_path).resolve()
    if not param_path.is_file():
        die(f"Parameter file not found: {param_path}")

    parameters = yaml.safe_load(param_path.read_text(encoding="utf-8")) or {}
    replacements = parameters.get("find_replace") or []

    print()
    info(f"parameter.yml -> {len(replacements)} replacement rule(s) for {args.environment}:")
    print()
    print(f"    {'FIND (dev value)':<40} {'REWRITES TO':<38} SCOPE")
    print(f"    {'-' * 40} {'-' * 38} {'-' * 12}")
    for rule in replacements:
        find = str(rule.get("find_value", "?"))
        target = (rule.get("replace_value") or {}).get(args.environment)
        scope = rule.get("item_type", "all items")
        if isinstance(scope, list):
            scope = ", ".join(scope)
        if target is None:
            print(f"    {find:<40} {'(no value for this environment)':<38} {scope}")
        else:
            print(f"    {find:<40} {str(target):<38} {scope}")

    missing = [
        r for r in replacements if (r.get("replace_value") or {}).get(args.environment) is None
    ]
    if missing:
        print()
        warn(
            f"{len(missing)} rule(s) have no value for '{args.environment}'. Those are skipped "
            "silently at deploy time - the deployment still succeeds, with dev values in place."
        )

    print()
    info("Nothing has been deployed. fabric-cicd has no dry-run mode, so this")
    info("local read is the closest thing to a plan step.")


# --------------------------------------------------------------------------------------
# Deploy
# --------------------------------------------------------------------------------------


def build_credential(auth: str):
    """Return a TokenCredential. fabric-cicd requires one explicitly."""
    from azure.identity import AzureCliCredential, ClientSecretCredential

    if auth == "spn":
        import os

        missing = [
            v
            for v in ("AZURE_TENANT_ID", "AZURE_CLIENT_ID", "AZURE_CLIENT_SECRET")
            if not os.environ.get(v)
        ]
        if missing:
            die(f"--auth spn needs environment variables: {', '.join(missing)}")
        return ClientSecretCredential(
            tenant_id=os.environ["AZURE_TENANT_ID"],
            client_id=os.environ["AZURE_CLIENT_ID"],
            client_secret=os.environ["AZURE_CLIENT_SECRET"],
        )
    return AzureCliCredential()


def report_responses(responses: Optional[dict]) -> None:
    """Print what landed, using the API responses the library already collected.

    Requires the `enable_response_collection` feature flag, which config.yml
    turns on. No extra API calls are made here - these IDs come straight off
    the DeploymentResult.

    Shape is {item_type: {item_name: {"body": {...}, "status_code": int}}}.
    """
    if not responses:
        warn("No responses collected - add 'enable_response_collection' to config.yml features.")
        return

    published = responses.get("publish") or {}
    if not published:
        return

    rows: List[Tuple[str, str, str]] = []
    for item_type, by_name in published.items():
        if not isinstance(by_name, dict):
            continue
        for item_name, response in by_name.items():
            body = response.get("body") if isinstance(response, dict) else None
            item_id = body.get("id", "") if isinstance(body, dict) else ""
            rows.append((str(item_type), str(item_name), str(item_id)))

    if rows:
        print()
        info("Items published (IDs come from the deployment result, not a follow-up call):")
        for item_type, name, item_id in sorted(rows):
            ok(f"{item_type:<12} {name:<24} {item_id}")

        agent_rows = [r for r in rows if r[0] == "DataAgent"]
        source_rows = [r for r in rows if r[0] in ("Lakehouse", "Warehouse", "SemanticModel")]
        if agent_rows and source_rows:
            print()
            info("The agent's datasource.json now carries the IDs above, not the")
            info("development ones committed in the repository. That is parameter.yml")
            info("doing its job.")


def cmd_deploy(args: argparse.Namespace) -> None:
    stage(f"DEPLOY - fabric-cicd, {args.mode} mode, environment {args.environment}")

    from fabric_cicd import DeploymentStatus, change_log_level

    if args.debug:
        change_log_level("DEBUG")

    credential = build_credential(args.auth)

    if args.mode == "config":
        # ---- Configuration-driven: everything comes from config.yml ----------------
        from fabric_cicd import deploy_with_config

        info(f"deploy_with_config('{args.config.name}', environment='{args.environment}')")
        print()

        result = deploy_with_config(
            config_file_path=str(args.config),
            token_credential=credential,
            environment=args.environment,
        )

        print()
        if result.status == DeploymentStatus.COMPLETED:
            ok(f"{result.message}")
        else:
            die(f"Deployment failed: {result.message}")
        report_responses(result.responses)

    else:
        # ---- Explicit: build the workspace object and publish yourself --------------
        from fabric_cicd import FabricWorkspace, publish_all_items, unpublish_all_orphan_items

        config = load_config(args.config)
        core = config.get("core", {})
        repo_dir = repository_directory(config, args.environment, args.config)
        workspace = resolve_setting(core.get("workspace"), args.environment)
        workspace_id = resolve_setting(core.get("workspace_id"), args.environment)
        in_scope = resolve_setting(core.get("item_types_in_scope"), args.environment)

        if not workspace and not workspace_id:
            die(f"No workspace configured for environment '{args.environment}' in {args.config}")

        info("FabricWorkspace(...) + publish_all_items(...)")
        print()

        target_workspace = FabricWorkspace(
            workspace_id=workspace_id,
            workspace_name=workspace,
            environment=args.environment,
            repository_directory=str(repo_dir),
            item_type_in_scope=in_scope,
            token_credential=credential,
        )

        publish_all_items(target_workspace)

        if args.unpublish_orphans:
            unpublish_all_orphan_items(target_workspace)

        print()
        ok("Deployment complete.")

    print()
    info("Re-run this as often as you like. fabric-cicd matches items by name and")
    info("type, so a second run updates in place rather than creating duplicates.")
    print()
    info("Open the data agent in the target workspace and check its data sources:")
    info("they point at that workspace's items, not the development ones.")
    info("The lakehouse and warehouse deploy as empty shells - structure ships, data does not.")


# --------------------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------------------


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        prog="deploy.py",
        description="Deploy a Fabric data agent with the fabric-cicd Python library.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python deploy.py inspect --environment PROD\n"
            "  python deploy.py deploy  --environment PROD\n"
            "  python deploy.py deploy  --environment PROD --mode explicit\n"
        ),
    )
    parser.add_argument("command", choices=["inspect", "deploy"])
    parser.add_argument(
        "--environment",
        default="PROD",
        help="Environment key from config.yml and parameter.yml (default: PROD).",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG,
        help="Path to config.yml (default: alongside this script).",
    )
    parser.add_argument(
        "--mode",
        choices=["config", "explicit"],
        default="config",
        help="Which library API to use (default: config).",
    )
    parser.add_argument("--auth", choices=["cli", "spn"], default="cli", help="Credential source.")
    parser.add_argument(
        "--unpublish-orphans",
        action="store_true",
        help="Explicit mode only: also delete target items missing from the repository.",
    )
    parser.add_argument("--debug", action="store_true", help="Enable fabric-cicd DEBUG logging.")

    args = parser.parse_args(argv)
    args.config = args.config.resolve()

    # fabric-cicd logs via the logging module while this script uses print();
    # line buffering keeps the two in order when stdout is piped.
    with contextlib.suppress(AttributeError, ValueError):
        sys.stdout.reconfigure(line_buffering=True, write_through=True)

    if args.command == "inspect":
        cmd_inspect(args)
    else:
        cmd_deploy(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
