# The same deployment, via the Fabric CLI

`../deploy.py` uses the **fabric-cicd Python library** directly. This folder does the same deployment with the **Fabric CLI** (`fab`), for teams who would rather run a command than maintain a Python file.

They aren't really competing options: **`fab deploy` runs fabric-cicd internally**, and reads the same `config.yml` and `parameter.yml`.

## Why this exists

The Python library has a deliberately narrow job: make a target workspace match a directory of item definitions. It does **not** create workspaces, delete them, or export items back out.

The CLI covers that surrounding ground, which makes it a useful companion:

| Task | fabric-cicd (Python) | Fabric CLI |
| --- | --- | --- |
| Deploy items to a workspace | `deploy_with_config()` | `fab deploy` (runs fabric-cicd) |
| Create a workspace | not supported | `fab create <name>.Workspace` |
| Delete a workspace | not supported | `fab rm <name>.Workspace` |
| List workspace contents | not supported | `fab ls <name>.Workspace` |
| Export item definitions | not supported | `fab export <ws>/<item> -o <dir>` |

## Setup

`ms-fabric-cli` requires **Python 3.10, 3.11, 3.12, or 3.13**. Install it into the demo's virtual environment rather than globally:

```bash
cd demos/module-03-fabric-cicd
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install ms-fabric-cli

fab --version                      # expect 1.7.0 or newer
fab auth login
```

Three things go wrong if you install it any other way:

- **Python 3.14 silently installs the wrong version.** `ms-fabric-cli` 1.7.0 caps at `<3.14`, so pip does not error — it falls back to `0.1.10`, which predates `fab deploy`. Always check `fab --version` after installing. If Homebrew's `python3` is 3.14, create the venv with an explicit interpreter: `python3.12 -m venv .venv`.
- **Homebrew Python refuses global installs** with an `externally-managed-environment` error (PEP 668). Use a virtual environment; do not reach for `--break-system-packages`.
- **The package name is `ms-fabric-cli`, not `fabric-cli`.** `fabric-cli` on PyPI is an unrelated research project and provides no `fab` command.

`fab` keeps its own credential store, separate from `az login`, so `fab auth login` is required even if the Azure CLI is already authenticated.

## Running it

```bash
# Create the target workspace (the step fabric-cicd cannot do)
./deploy-with-fab.sh create "Fabric Agents Workshop [prod]" "My Capacity"

# Deploy - this is fabric-cicd under the hood
./deploy-with-fab.sh deploy PROD

# See what landed
./deploy-with-fab.sh list "Fabric Agents Workshop [prod]"

# Clean up
./deploy-with-fab.sh destroy "Fabric Agents Workshop [prod]"
```

Or call `fab` directly — the script is only a thin wrapper:

```bash
fab deploy --config ../config.yml --target_env PROD
```

## A note on `fab export`

`fab export` pulls item definitions out of a workspace. It's the reverse of deployment, with one important caveat: **exported items do not carry logical IDs**, so fabric-cicd cannot resolve references between them automatically. Cross-item references have to be handled in `parameter.yml`.

Items committed by **Fabric Git integration** do carry logical IDs, which is why Git integration is the recommended source for a real pipeline, and export is better treated as a migration or inspection tool.

## Further reading

- [Fabric CLI documentation](https://microsoft.github.io/fabric-cli/)
- [`fab deploy` reference](https://microsoft.github.io/fabric-cli/commands/fs/deploy/)
- [fabric-cicd configuration deployment](https://microsoft.github.io/fabric-cicd/latest/how_to/config_deployment/)
