#!/usr/bin/env python3
"""Production-shaped fabric-cicd deployment for a CI/CD pipeline.

`fabric_cicd_demo.py` is classroom scaffolding: it creates workspaces and
exports items so a demo can run in one workspace. This file is the opposite -
it is the ~40 lines you would actually put in a pipeline once Fabric Git
integration is committing your workspace to a repository.

Everything is driven by environment variables so the same script works in
GitHub Actions, Azure DevOps, or on a laptop:

    FABRIC_WORKSPACE_ID         Target workspace GUID          (required*)
    FABRIC_WORKSPACE_NAME       Target workspace display name  (*or this)
    FABRIC_ENVIRONMENT          parameter.yml environment key  (default: PROD)
    FABRIC_REPOSITORY_DIRECTORY Folder holding the items       (default: ./workspace)
    FABRIC_ITEM_TYPES           Comma-separated item types     (default: all in scope)
    FABRIC_UNPUBLISH_ORPHANS    "true" to delete items missing from the repo
    FABRIC_DEBUG                "true" for verbose fabric-cicd logging

Authentication uses the ambient Azure CLI login (azure/login in GitHub Actions,
AzureCLI@2 in Azure DevOps). Set AZURE_TENANT_ID / AZURE_CLIENT_ID /
AZURE_CLIENT_SECRET to use an explicit service principal instead.

Note: service principals are supported by Fabric data agents *only* for ALM
scenarios such as this one. They cannot be used to query an agent.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from azure.identity import AzureCliCredential, ClientSecretCredential

from fabric_cicd import (
    FabricWorkspace,
    change_log_level,
    publish_all_items,
    unpublish_all_orphan_items,
)


def env_flag(name: str) -> bool:
    return os.getenv(name, "").strip().lower() in {"1", "true", "yes"}


def main() -> int:
    # Unbuffered output so pipeline logs stream in real time.
    sys.stdout.reconfigure(line_buffering=True, write_through=True)

    if env_flag("FABRIC_DEBUG") or env_flag("SYSTEM_DEBUG") or env_flag("RUNNER_DEBUG"):
        change_log_level("DEBUG")

    workspace_id = os.getenv("FABRIC_WORKSPACE_ID")
    workspace_name = os.getenv("FABRIC_WORKSPACE_NAME")
    if not workspace_id and not workspace_name:
        sys.exit("Set FABRIC_WORKSPACE_ID or FABRIC_WORKSPACE_NAME.")

    repository_directory = Path(
        os.getenv("FABRIC_REPOSITORY_DIRECTORY", Path(__file__).resolve().parent / "workspace")
    ).resolve()
    if not repository_directory.is_dir():
        sys.exit(f"Repository directory not found: {repository_directory}")

    item_types_raw = os.getenv("FABRIC_ITEM_TYPES", "")
    item_type_in_scope = [t.strip() for t in item_types_raw.split(",") if t.strip()] or None

    # Prefer an explicit service principal when one is configured; otherwise use
    # whatever identity the pipeline's Azure login step established.
    if os.getenv("AZURE_CLIENT_SECRET"):
        credential = ClientSecretCredential(
            tenant_id=os.environ["AZURE_TENANT_ID"],
            client_id=os.environ["AZURE_CLIENT_ID"],
            client_secret=os.environ["AZURE_CLIENT_SECRET"],
        )
    else:
        credential = AzureCliCredential()

    target_workspace = FabricWorkspace(
        workspace_id=workspace_id,
        workspace_name=workspace_name,
        environment=os.getenv("FABRIC_ENVIRONMENT", "PROD"),
        repository_directory=str(repository_directory),
        item_type_in_scope=item_type_in_scope,
        token_credential=credential,
    )

    publish_all_items(target_workspace)

    if env_flag("FABRIC_UNPUBLISH_ORPHANS"):
        # The repository is the source of truth: remove anything it no longer defines.
        unpublish_all_orphan_items(target_workspace)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
