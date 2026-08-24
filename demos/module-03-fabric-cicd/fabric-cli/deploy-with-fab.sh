#!/usr/bin/env bash
# =============================================================================
# The same deployment, driven by the Fabric CLI instead of Python.
#
# `fab deploy` runs the fabric-cicd library internally and reads the SAME
# config.yml and parameter.yml as ../deploy.py. If you prefer a command line to
# a Python file, this is the equivalent path - and it also covers the things
# fabric-cicd deliberately does not do, such as creating and deleting
# workspaces.
#
# Install:  pip install ms-fabric-cli
# Docs:     https://microsoft.github.io/fabric-cli/
#
# Usage:
#   ./deploy-with-fab.sh login
#   ./deploy-with-fab.sh create   "Fabric Agents Workshop [prod]" <capacity-name>
#   ./deploy-with-fab.sh deploy   PROD
#   ./deploy-with-fab.sh list     "Fabric Agents Workshop [prod]"
#   ./deploy-with-fab.sh export   "Fabric Agents Workshop [prod]" ./exported
#   ./deploy-with-fab.sh destroy  "Fabric Agents Workshop [prod]"
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG="${SCRIPT_DIR}/../config.yml"

command -v fab >/dev/null 2>&1 || {
    echo "ERROR: 'fab' not found. Install it with: pip install ms-fabric-cli" >&2
    exit 1
}

usage() { sed -n '2,21p' "$0" | sed 's/^# \{0,1\}//'; exit 1; }

case "${1:-}" in

login)
    # Interactive by default. For CI use a service principal:
    #   fab auth login -u <client-id> -p <secret> -t <tenant-id>
    fab auth login
    ;;

create)
    # fabric-cicd cannot create workspaces - this is why the CLI is useful.
    WORKSPACE="${2:?workspace name required}"
    CAPACITY="${3:-}"
    if [[ -n "${CAPACITY}" ]]; then
        fab create "${WORKSPACE}.Workspace" -P capacityName="${CAPACITY}"
    else
        fab create "${WORKSPACE}.Workspace"
    fi
    ;;

deploy)
    # This is the fabric-cicd library, invoked through the CLI. Same config.yml,
    # same parameter.yml, same publish and unpublish behaviour as ../deploy.py.
    ENVIRONMENT="${2:-PROD}"
    fab deploy --config "${CONFIG}" --target_env "${ENVIRONMENT}" --force
    ;;

list)
    WORKSPACE="${2:?workspace name required}"
    fab ls "${WORKSPACE}.Workspace"
    ;;

export)
    # Pulls item definitions back out - the reverse direction, which the
    # fabric-cicd library does not offer at all.
    #
    # Note: exported items do not carry logical IDs, so cross-item references
    # must be resolved with parameter.yml rather than automatically.
    WORKSPACE="${2:?workspace name required}"
    OUTPUT="${3:-./exported}"
    mkdir -p "${OUTPUT}"
    fab export "${WORKSPACE}.Workspace" -o "${OUTPUT}" -a --force
    ;;

destroy)
    WORKSPACE="${2:?workspace name required}"
    read -r -p "Delete workspace '${WORKSPACE}' and everything in it? [y/N] " reply
    [[ "${reply}" == "y" ]] || { echo "Cancelled."; exit 0; }
    fab rm "${WORKSPACE}.Workspace" --force
    ;;

*)
    usage
    ;;
esac
