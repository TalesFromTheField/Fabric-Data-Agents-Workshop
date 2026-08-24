# Module 03 Demo: Deploying a Fabric Data Agent with `fabric-cicd`

A working, end-to-end demonstration of code-first CI/CD for Fabric data agents using Microsoft's [`fabric-cicd`](https://microsoft.github.io/fabric-cicd/) Python library.

Section 3.6 of Module 03 shows that everything you tuned in this module — agent instructions, example queries, data source instructions, table selections — is **configuration stored in files**. This demo takes the next step and deploys those files into a workspace, re-pointing the agent at that workspace's data on the way in.

**Runtime:** about 10 minutes presented, well under a minute of script execution.

---

## What this demo proves

| Beat | What the audience sees |
| --- | --- |
| Configuration is code | The real on-disk layout of a data agent — `stage_config.json`, `datasource.json`, `fewshots.json` |
| Deployment is a library call | One function, driven by a config file |
| The silent failure | A data agent deployed as-is **keeps querying the dev lakehouse** and still answers |
| Parameterization is the fix | `parameter.yml` re-points every environment-specific reference |
| Re-runs are safe | Deploying twice updates in place; it does not duplicate |
| Structure ships, data does not | The lakehouse and warehouse arrive empty |

The silent failure is the point. An agent pointed at the wrong data source does not throw — it answers confidently from the wrong environment. That is why parameterization is not optional.

---

## What the library does and does not do

Worth stating plainly, because it shapes everything here:

> **`fabric-cicd` makes a target workspace match a directory of item definitions. That is its entire job.**

It does **not** create workspaces, delete them, export items, or copy data. Those are real needs, they're just not this library's. The Fabric CLI covers them — see [`fabric-cli/`](fabric-cli/) for the same deployment driven that way, plus workspace create, list, export, and delete.

That's why this demo asks you to create the target workspace yourself. Auto-creating it would mean hand-rolling REST calls, which would bury the thing the demo is meant to teach.

---

## Prerequisites

- **Python 3.10 or newer.** `fabric-cicd` 1.3.0 advertises 3.9 support but does not import on it. macOS ships 3.9 as the system Python, so use a newer interpreter.
- **Azure CLI**, logged in: `az login`
- **A Fabric workspace on a capacity** to deploy into. Create it in the Fabric portal, or with `fabric-cli/deploy-with-fab.sh create`.

You do **not** need a Git-connected workspace, and you do not need to have finished Modules 02 and 03 — the sample agent in `sample-workspace/` stands in.

---

## Setup

```bash
cd demos/module-03-fabric-cicd

python3.12 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

az login
```

Then point `config.yml` at your workspace:

```yaml
core:
    workspace:
        TEST: "Your Workspace [test]"
        PROD: "Your Workspace [prod]"
```

---

## Running the demo

```bash
python deploy.py inspect --environment PROD    # local only, no API calls
python deploy.py deploy  --environment PROD
```

---

## Walkthrough, with talk track

### 1. `inspect` — what is on disk, and what will change

```bash
python deploy.py inspect --environment PROD
```

Reads `config.yml`, walks the repository directory, and prints every item it finds plus the replacement rules that will apply. **No API calls.**

> **Say this:** "Three items: a warehouse, a lakehouse, and the data agent that queries both. The agent's folder is Module 03 section 3.6 in file form — `stage_config.json` holds the agent instructions from 3.1, `fewshots.json` holds the example queries from 3.2, `datasource.json` holds the data source instructions from 3.3 and the table selections from 3.4. Everything you tuned this module is now a file you can review in a pull request."

Then the replacement table:

```
    FIND (dev value)                       REWRITES TO                            SCOPE
    22222222-2222-2222-2222-222222222222   $items.Warehouse.ContosoSales.$id      DataAgent
    33333333-3333-3333-3333-333333333333   $items.Lakehouse.MarketResearch.$id    DataAgent
    11111111-1111-1111-1111-111111111111   $workspace.$id                         DataAgent
```

> **Say this:** "Here's the whole problem. The agent has its development data source GUIDs baked in. Deploy it untouched and it lands in production still reading dev data. It doesn't fail. It answers — and the answers look fine."

`$items.<Type>.<Name>.$id` resolves at deploy time against the workspace being deployed into, so `parameter.yml` holds no target-specific GUIDs and keeps working as you add environments.

Note there is **no dry-run** in `fabric-cicd`. This local read is the closest thing to a plan step.

### 2. `deploy` — hand it to the library

```bash
python deploy.py deploy --environment PROD
```

The whole library surface for this demo:

```python
result = deploy_with_config(
    config_file_path="config.yml",
    token_credential=AzureCliCredential(),
    environment="PROD",
)
```

> **Say this:** "That's it. `config.yml` names the workspace, the folder, the item types, and the parameter file. The library publishes in dependency order — warehouse and lakehouse before the agent that references them — so you don't sequence anything yourself."

The demo then prints what landed, with IDs taken from `DeploymentResult.responses` rather than a follow-up API call (that's the `enable_response_collection` feature flag in `config.yml`):

```
  DataAgent    Sales Analysis Agent     5c82c38e-...
  Lakehouse    MarketResearch           d7491b37-...
  Warehouse    ContosoSales             69cca313-...
```

Run it a second time:

> **Say this:** "Same command, same result. `fabric-cicd` matches items by name and type, so a second run updates instead of duplicating. That matters — your pipeline runs on every merge, and full deployment every time is the design. It doesn't diff commits; it makes the workspace match the repo."

### 3. Show the result in Fabric

Open the agent in the target workspace and look at its data sources: they point at that workspace's warehouse and lakehouse, not the development ones.

> **Say this:** "Notice the lakehouse and warehouse are empty. `fabric-cicd` deploys item *structure*, not data. Loading data is a separate pipeline, and that's correct — you don't want your deployment tool copying rows between environments."

One more beat: the deployed agent is a **draft**. An agent must be published to be consumable from Copilot in Power BI, Copilot Studio, or Foundry — even sitting in production. Deployment and publishing are two different steps.

---

## The two library APIs

`deploy.py` can drive either, so you can show both:

```bash
python deploy.py deploy --environment PROD                    # deploy_with_config()
python deploy.py deploy --environment PROD --mode explicit    # FabricWorkspace + publish_all_items()
```

| | Config-driven | Explicit |
| --- | --- | --- |
| Call | `deploy_with_config()` | `FabricWorkspace(...)` + `publish_all_items()` |
| Settings live in | `config.yml`, committed | Python arguments |
| Multi-environment | Built in, via environment mappings | You write the branching |
| Returns | `DeploymentResult` | `None` |
| Used by | `fab deploy` internally | — |

Config-driven is the recommended path. Explicit is useful when settings are computed at runtime.

---

## Useful variations

Show the destructive half of "the repository is the source of truth" by setting `unpublish.skip: false` in `config.yml`, or:

```bash
python deploy.py deploy --environment PROD --mode explicit --unpublish-orphans
```

`unpublish_all_orphan_items` removes target items the repository no longer defines. It's off by default here for a reason. Lakehouses, warehouses, SQL databases, and eventhouses are protected even then, and need a feature flag such as `enable_lakehouse_unpublish` — the library guards data-bearing items by default.

See the exact API calls:

```bash
python deploy.py deploy --environment PROD --debug
```

Run as a service principal:

```bash
export AZURE_TENANT_ID=… AZURE_CLIENT_ID=… AZURE_CLIENT_SECRET=…
python deploy.py deploy --environment PROD --auth spn
```

---

## Where the sample workspace comes from

`sample-workspace/` is a hand-built Fabric workspace export: a warehouse, a lakehouse, and a data agent attached to both. It exists so the demo runs without requiring a Git-connected workspace or a finished Module 02.

In real use that folder comes from **Fabric Git integration** — connect a workspace to Azure DevOps or GitHub in workspace settings, Fabric commits the items, and your pipeline checks the repository out. The files, the folder names, and the deployment behaviour are identical; only the delivery differs.

To deploy your own agent instead, replace `sample-workspace/` with your Git-synced folder and update `parameter.yml` with your development GUIDs.

---

## Taking it to a pipeline

`pipelines/` has working starting points:

| File | Platform | Notes |
| --- | --- | --- |
| `pipelines/github-actions.yml` | GitHub Actions | OIDC login via `azure/login`, no stored secret |
| `pipelines/azure-pipelines.yml` | Azure DevOps | `AzureCLI@2` with a service connection, TEST → PROD with approvals |

Both call `deploy.py`. Setup needs an Entra app with Contributor or Admin on the target workspaces, the Fabric tenant setting **Service principals can use Fabric APIs** enabled, and a workspace per environment in `config.yml`.

> **Important:** Fabric data agents support service principals for **ALM only**. A service principal can deploy an agent; it cannot query one.

---

## Gotchas worth mentioning

Several of these came out of building this demo against a live tenant.

| Symptom | Cause |
| --- | --- |
| Agent answers from the wrong data | Data source GUID not parameterized — the failure this demo exists to show |
| Replacements silently did not happen | `--environment` doesn't match a key in `parameter.yml`. No match means no replacement, **and no error** |
| `ImportError` on `fabric_cicd` | Python 3.9. Use 3.10 or newer |
| Target lakehouse and warehouse are empty | Expected. Item structure deploys; data does not |
| Agent not usable in prod | It deployed as a draft. Publish it |
| `DisplayName is Invalid for ArtifactType` | **Lakehouse names cannot contain spaces.** Warehouse names can |
| Data agent fails with `Unknown error` | The API gives no detail. In practice it means a malformed definition — check `type` in each `datasource.json`, below |
| Deployment fails on a connection GUID | Connections are not source controlled. Create them in the target first, and give the deploying identity access |
| Deployment stalls resolving a SQL endpoint | When any `$items`/`$workspace` variable is used, the library eagerly resolves SQL endpoints for every lakehouse and warehouse in the target. It waits for provisioning on its own — about 10s on a fresh lakehouse |

The `type` field in `datasource.json` is not what you'd guess:

| Data source | Folder prefix | `type` | Element types |
| --- | --- | --- | --- |
| Lakehouse | `lakehouse-tables-` | `lakehouse_tables` | `lakehouse_tables.table`, `.column` |
| Warehouse | `data-warehouse-` | `data_warehouse` | `warehouse_tables.table`, `.column` |

A warehouse source is `data_warehouse` at the top level but `warehouse_tables.*` for its elements. Getting that wrong produces the opaque `Unknown error` above.

Also note that `data_type` on a column must be a SQL type name — `varchar`, `int`, `decimal`, `float`, `date`, `bit`, `char`, `bigint`, `smallint`. Values like `string` or `double` are rejected.

---

## Files in this folder

| File | Purpose |
| --- | --- |
| `deploy.py` | The demo — `inspect` and `deploy`, pure fabric-cicd |
| `config.yml` | Deployment configuration, consumed by both `deploy.py` and `fab deploy` |
| `sample-workspace/` | A deployable Fabric workspace: warehouse, lakehouse, data agent |
| `sample-workspace/parameter.yml` | The environment-specific replacements |
| `parameter.example.yml` | Annotated reference covering options the demo doesn't use |
| `fabric-cli/` | The same deployment via the Fabric CLI, plus workspace lifecycle |
| `pipelines/` | GitHub Actions and Azure DevOps samples |

---

## Further reading

- [fabric-cicd documentation](https://microsoft.github.io/fabric-cicd/latest/)
- [Configuration deployment](https://microsoft.github.io/fabric-cicd/latest/how_to/config_deployment/) — the `config.yml` reference
- [Parameterization](https://microsoft.github.io/fabric-cicd/latest/how_to/parameterization/) — `find_replace` and dynamic variables
- [Item type notes](https://microsoft.github.io/fabric-cicd/latest/reference/item_types/) — per-type limitations, including Data Agent
- [Source control, CI/CD, and ALM for Fabric data agents](https://learn.microsoft.com/en-us/fabric/data-science/data-agent-source-control)
- [Fabric CLI](https://microsoft.github.io/fabric-cli/)
