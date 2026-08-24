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

```bash
pip install ms-fabric-cli
./deploy-with-fab.sh login
```

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
