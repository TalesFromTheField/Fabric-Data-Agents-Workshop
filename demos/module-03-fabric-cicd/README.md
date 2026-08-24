# Module 03 Demo: Deploying a Fabric Data Agent with `fabric-cicd`

A working, end-to-end demonstration of code-first CI/CD for Fabric data agents using Microsoft's [`fabric-cicd`](https://microsoft.github.io/fabric-cicd/) Python library.

Section 3.6 of Module 03 shows that everything you tuned in this module — agent instructions, example queries, data source instructions, table selections — is **configuration stored in files**. This demo takes the next step and proves those files are deployable: it moves a data agent out of a development workspace into a separate production workspace, re-points it at production data, and verifies the result.

**Runtime:** about 15 minutes presented, under 3 minutes of actual script execution.

Measured against a real workspace (8 items - a data agent, lakehouse, warehouse, semantic model, and four notebooks): `bootstrap` ~10s, `export` ~30s, `scan` <1s, `verify` ~20s. `deploy` is **1m19s** creating items from scratch and **31s** re-deploying into a workspace that already has them - which is another reason to pre-run the demo and leave the workspace in place.

---

## What this demo proves

| Beat | What the audience sees |
| --- | --- |
| Configuration is code | The real on-disk layout of a deployed data agent — `stage_config.json`, `datasource.json`, `fewshots.json` |
| Deployment is boring | Four lines of Python move an agent between workspaces |
| The silent failure | A data agent deployed as-is **keeps querying the dev lakehouse** and still returns answers |
| Parameterization is the fix | `parameter.yml` re-points every environment-specific reference |
| Re-runs are safe | Deploying twice updates; it does not duplicate |
| Structure ships, data does not | The prod lakehouse arrives empty |

The silent failure is the point of the demo. An agent pointed at the wrong data source does not throw an error — it answers confidently from the wrong environment. That is why parameterization is not optional.

---

## Prerequisites

- **Python 3.10 or newer.** `fabric-cicd` 1.3.0 advertises Python 3.9 support but does not import on it. macOS ships 3.9 as the system Python, so create a virtual environment with a newer interpreter.
- **Azure CLI**, logged in: `az login`
- **A Fabric workspace on a capacity** containing the lakehouse and data agent you built in Modules 02 and 03.
- **Permission to create a workspace** in your tenant. The demo creates a second workspace and deletes it at the end.

You do **not** need a GitHub or Azure DevOps repository connected to Fabric. See [How this differs from real Git integration](#how-this-differs-from-real-git-integration) for why.

---

## Setup

```bash
cd demos/module-03-fabric-cicd

python3.12 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

az login
```

Confirm the library and your identity are both working:

```bash
python -c "import fabric_cicd; print('fabric-cicd ready')"
az account show --query user.name -o tsv
```

---

## Running the demo

Run it one stage at a time so you can talk between each. Every stage is independently re-runnable.

```bash
python fabric_cicd_demo.py bootstrap --dev-workspace "Your Workshop Workspace"
python fabric_cicd_demo.py export
python fabric_cicd_demo.py scan
python fabric_cicd_demo.py deploy
python fabric_cicd_demo.py verify
python fabric_cicd_demo.py destroy
```

Or run the whole thing unattended:

```bash
python fabric_cicd_demo.py all --dev-workspace "Your Workshop Workspace"
```

State carries between stages in `.demo-state.json`, so you can stop, answer questions, and pick up later — even in a new terminal.

---

## Stage by stage, with talk track

### 1. `bootstrap` — create the target environment

```bash
python fabric_cicd_demo.py bootstrap --dev-workspace "Your Workshop Workspace"
```

Resolves your existing workspace, reads its capacity, and creates `Your Workshop Workspace [prod]` on that same capacity. If the workspace already exists it is reused, so re-running is safe.

> **Say this:** "Nothing here is `fabric-cicd` yet — this is plain Fabric REST, standing in for whatever provisions environments in your organization. Most of you already have dev, test, and prod workspaces and would skip this entirely."

### 2. `export` — get the item definitions onto disk

```bash
python fabric_cicd_demo.py export
```

Downloads each in-scope item's definition from the dev workspace and writes it out as `workspace/<Name>.<Type>/…`, then prints the data agent's file tree.

> **Say this:** "This is the folder Module 03 section 3.6 described, and it's what Fabric Git integration commits for you. `stage_config.json` holds your agent instructions from 3.1. `fewshots.json` holds your example queries from 3.2. `datasource.json` holds your data source instructions from 3.3 and your table selections from 3.4. Every lever you spent this module tuning is now a file you can review in a pull request."

Point at the lakehouse folder too: it contains only a `.platform` file. Fabric creates a lakehouse as an empty shell with no downloadable definition — a detail that matters two stages from now.

### 3. `scan` — find what breaks across environments

```bash
python fabric_cicd_demo.py scan
```

This is the dry run. Nothing deploys. The script reads every exported file, finds each GUID that refers to the dev workspace or a dev item, reports where it appears, and writes `workspace/parameter.yml`.

You will see something like:

```
    KIND       WHAT                               FOUND IN         REWRITES TO
    item       Lakehouse / Cold Chain LH          DataAgent        $items.Lakehouse.Cold Chain LH.$id
    workspace  (dev workspace)                    DataAgent        $workspace.$id
```

> **Say this:** "Here is the whole problem in one table. The agent has your dev lakehouse's GUID baked into it. Deploy it as-is and the agent lands in production and keeps answering questions from dev data. It doesn't fail. It doesn't warn you. It just quietly answers from the wrong environment — and the answers look fine."

Open the generated `parameter.yml` and read one entry aloud:

```yaml
find_replace:
    - find_value: "8f3c…"                                    # the dev lakehouse GUID
      replace_value:
          PROD: "$items.Lakehouse.Cold Chain LH.$id"          # whatever it is in the target
      item_type: "DataAgent"
```

> **Say this:** "`$items.Lakehouse.<name>.$id` is resolved by `fabric-cicd` at deploy time, against the workspace it is deploying into. That means this file has no environment-specific GUIDs on the right-hand side — it works for test, prod, and every workspace you add later."

If the scan reports **unrecognized** GUIDs, that is usually a connection. Say so: connections are not source controlled, must already exist in the target, and the deploying identity needs access to them.

### 4. `deploy` — hand it to `fabric-cicd`

```bash
python fabric_cicd_demo.py deploy
```

Open `fabric_cicd_demo.py` and show the block marked `The entire fabric-cicd surface area for this demo`:

```python
target_workspace = FabricWorkspace(
    workspace_id=state.prod_workspace_id,
    environment=args.environment,             # matches a key in parameter.yml
    repository_directory=str(workspace_root),
    item_type_in_scope=list(args.item_types),
    token_credential=args.credential,
)

publish_all_items(target_workspace)
```

> **Say this:** "That's the library. Everything else in this script is scaffolding to make the demo runnable in one workspace. `fabric-cicd` publishes in dependency order — the lakehouse is created before the agent that references it — so you don't sequence anything yourself."

Then run it again:

```bash
python fabric_cicd_demo.py deploy
```

> **Say this:** "Same command, same result. `fabric-cicd` matches items by name and type, so a second run updates instead of duplicating. This matters: your pipeline runs on every merge, and full deployment every time is the design — it doesn't diff commits, it makes the workspace match the repo."

### 5. `verify` — prove it worked

```bash
python fabric_cicd_demo.py verify
```

Lists what landed in prod, then re-exports the deployed agent and checks which GUIDs it now carries. You want:

```
  OK  No dev-workspace references remain in the deployed agent. Re-pointing worked.
```

Now open the prod workspace in the browser, open the data agent, and show its data source pointing at the **prod** lakehouse.

> **Say this:** "The agent is in production, wired to production data, with the instructions and example queries you wrote — and none of it was clicked into a UI."

Then set expectations honestly:

> **Say this:** "Notice the prod lakehouse is empty. `fabric-cicd` deploys item *structure*, not data. Loading production data is a separate pipeline, and that's correct — you don't want your deployment tool copying rows between environments."

One more beat worth landing: the deployed agent is a **draft**. An agent must be published to be consumable through Copilot in Power BI, Copilot Studio, or Foundry — even sitting in production. Deployment and publishing are two different steps.

### 6. `destroy` — clean up

```bash
python fabric_cicd_demo.py destroy
```

Prompts before deleting the prod workspace. Add `--yes` to skip the prompt. Your dev workspace and the exported folder are untouched.

---

## Useful variations

Show the destructive half of "the repository is the source of truth":

```bash
# Delete a folder from workspace/, then:
python fabric_cicd_demo.py deploy --unpublish-orphans
```

`unpublish_all_orphan_items` removes target items the repository no longer defines. It is off by default here for a reason. Note that lakehouses, warehouses, SQL databases, and eventhouses are **not** deleted unless you also opt in with a feature flag such as `enable_lakehouse_unpublish` — the library protects data-bearing items by default.

Deploy a subset:

```bash
python fabric_cicd_demo.py deploy --item-types DataAgent
```

Target a different environment key:

```bash
python fabric_cicd_demo.py scan --environment TEST
python fabric_cicd_demo.py deploy --environment TEST
```

See exactly which API calls are made:

```bash
python fabric_cicd_demo.py deploy --debug
```

Run as a service principal instead of your own identity:

```bash
export AZURE_TENANT_ID=… AZURE_CLIENT_ID=… AZURE_CLIENT_SECRET=…
python fabric_cicd_demo.py deploy --auth spn
```

---

## How this differs from real Git integration

`fabric-cicd` deploys from a folder of item definitions that normally arrives via **Fabric Git integration**: you connect a workspace to Azure DevOps or GitHub in workspace settings, Fabric commits the items, and your pipeline checks that repository out.

Wiring a workshop room up to a Git provider is a lot of setup for one demo, so the `export` stage calls the Fabric item definition API to produce the same folder locally. **The files, the folder names, and the deployment behaviour are identical** — only the delivery mechanism differs.

Two consequences worth naming out loud:

- In real use you would **not** run `export`. Git integration produces the folder, and code review happens on the resulting pull request.
- In real use `parameter.yml` is **hand-written once and committed**, not regenerated. The `scan` stage exists to show you what to put in it.

`ci_deploy.py` in this folder is the production-shaped version: about 40 lines, environment-variable driven, no export and no workspace creation. That is what a pipeline actually runs.

---

## Taking it to a pipeline

`pipelines/` contains working starting points for both platforms:

| File | Platform | Notes |
| --- | --- | --- |
| `pipelines/github-actions.yml` | GitHub Actions | OIDC login via `azure/login`, no stored secret |
| `pipelines/azure-pipelines.yml` | Azure DevOps | `AzureCLI@2` with an ARM service connection, PPE → PROD stages with approvals |

Both call `ci_deploy.py`. Point them at the folder Fabric Git integration commits, set the workspace ID per environment, and match `FABRIC_ENVIRONMENT` to a key in your `parameter.yml`.

Setup either one needs:

1. An Entra app registration with Contributor or Admin on the target workspaces.
2. The Fabric tenant setting **Service principals can use Fabric APIs** enabled.
3. A workspace ID stored per environment.

> **Important:** Service principals are supported by Fabric data agents **only** for ALM scenarios — Git integration and deployment pipelines. A service principal can deploy an agent; it cannot query one.

If you would rather not write Python at all, the [Fabric CLI](https://microsoft.github.io/fabric-cli/) `fab deploy` command runs `fabric-cicd` under the hood using a shared `config.yml`.

---

## Gotchas worth mentioning

| Symptom | Cause |
| --- | --- |
| Agent answers from the wrong data | Data source GUID not parameterized — the failure this demo exists to show |
| `ImportError` on `fabric_cicd` | Python 3.9. Use 3.10 or newer |
| Prod lakehouse has no tables | Expected. Item structure deploys; data does not |
| Agent not usable in prod | It deployed as a draft. Publish it |
| Deployment fails on a connection GUID | Connections are not source controlled. Create them in the target first, and give the deploying identity access |
| Deployment fails resolving a SQL endpoint | When any `$items`/`$workspace` variable is used, `fabric-cicd` eagerly resolves SQL endpoints for **every** lakehouse and warehouse in the target. The library waits for provisioning on its own (observed: ~10s on a fresh lakehouse), but a slow tenant can still time out — re-run if so |
| Replacements silently did not happen | `--environment` does not match a key in `parameter.yml`. No match means no replacement, and no error |
| Nothing found to export | The item types are out of scope. Pass `--item-types` |

That second-to-last one is worth dwelling on: a mismatched environment key fails **open**, not closed. It deploys successfully with dev values still in place.

---

## Files in this folder

| File | Purpose |
| --- | --- |
| `fabric_cicd_demo.py` | The staged classroom demo |
| `ci_deploy.py` | Production-shaped deployment script for pipelines |
| `parameter.example.yml` | Annotated reference showing `find_replace`, regex, `key_value_replace`, and `spark_pool` |
| `requirements.txt` | Pinned dependencies |
| `pipelines/` | GitHub Actions and Azure DevOps samples |
| `workspace/` | Generated by `export`. Git-ignored |
| `.demo-state.json` | Generated state carried between stages. Git-ignored |

---

## Further reading

- [fabric-cicd documentation](https://microsoft.github.io/fabric-cicd/latest/)
- [Parameterization reference](https://microsoft.github.io/fabric-cicd/latest/how_to/parameterization/) — the `find_replace` and dynamic variable rules
- [Item type notes](https://microsoft.github.io/fabric-cicd/latest/reference/item_types/) — per-type limitations, including Data Agent
- [Source control, CI/CD, and ALM for Fabric data agents](https://learn.microsoft.com/en-us/fabric/data-science/data-agent-source-control)
- [What is Microsoft Fabric Git integration?](https://learn.microsoft.com/en-us/fabric/cicd/git-integration/intro-to-git-integration)
- [Fabric CLI](https://microsoft.github.io/fabric-cli/)
