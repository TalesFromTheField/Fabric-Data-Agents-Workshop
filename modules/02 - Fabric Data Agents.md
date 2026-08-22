![](../graphics/microsoftlogo.png)

# Workshop: Microsoft Fabric Data Agents and Beyond

#### <i>A workshop from the Tales from the Field team</i>

<p style="border-bottom: 1px solid lightgrey;"></p>

<h2 id="02"><img style="float: left; margin: 0px 15px 15px 0px;" src="../graphics/textbubble.png">02 - Fabric Data Agents</h2>

A Fabric data agent is a generally available feature of Microsoft Fabric that lets you build your own conversational Q&A system over the data your organization already stores in OneLake. Your colleagues ask questions in plain English, and the agent generates and runs the query for them - no SQL, DAX, or KQL required from the person asking.

In this module you'll learn what a data agent actually is under the hood: how it routes a plain-English question to the right query engine, and how it enforces your existing security while it does so. You'll then build one end to end - create the item, attach a data source, select the tables the agent is allowed to see, test it, and publish it - leaving you with a working, published agent that is ready for the consumption patterns covered in Module 03.

In each section you'll get more references, which you should follow up on to learn more. Also watch for links within the text - click on each one to explore that topic.

(<a href="00%20-%20Pre-Requisites.md">Make sure you check out the <b>Pre-Requisites</b> page before you start</a>. You'll need all of the items loaded there before you can proceed with the workshop.)

You'll cover these topics in this module:

<dl>

  <dt><a href="#2.1">2.1 - What Is a Fabric Data Agent?</a></dt>
  <dt><a href="#2.2">2.2 - Prerequisites and Tenant Configuration</a></dt>
  <dt><a href="#2.3">2.3 - Creating an Agent and Adding Data Sources</a></dt>
  <dt><a href="#2.4">2.4 - Publishing Your Agent (Go Live)</a></dt>

</dl>

<p style="border-bottom: 1px solid lightgrey;"></p>

<h2 id="2.1"><img style="float: left; margin: 0px 15px 15px 0px;" src="../graphics/pencil2.png">2.1 What Is a Fabric Data Agent?</h2>

A Fabric data agent is a Fabric item - just like a lakehouse, a notebook, or a report - that you create, configure, test, and publish. Once published, people in your organization ask it questions in plain English and get back structured, human-readable answers drawn from governed data in OneLake.

The mental model to hold onto is the Power BI report lifecycle: you *build* the artifact first, refine it until it behaves the way you want, and then you *publish* it so colleagues can consume it. A data agent works exactly the same way, and that build-then-publish arc is what this module walks you through.

One important thing you do **not** have to do: you don't create or supply an Azure OpenAI key or an access token. Fabric uses a Microsoft-managed Azure OpenAI Assistant and handles authentication for you.

### How a question becomes an answer

When a user asks a question, the agent runs it through a pipeline rather than handing the question straight to a language model. Understanding these stages is what lets you troubleshoot an agent later, so it's worth learning them by name:

1. **Question parsing and validation** - The question is checked against security protocols, Responsible AI policies, and the user's own permissions. The agent maintains strictly read-only connections to every data source.
2. **Enforcement** - The agent runs using the *requesting user's* credentials to enforce least-privilege access, evaluates the request against tenant and workspace policy, and applies guardrails that keep tool calls inside the data sources you configured.
3. **Data source identification** - Using that same user's credentials, the agent reads the schema it is allowed to see, then evaluates the question against every data source attached to the agent to decide which one should answer it.
4. **Tool invocation and query generation** - The agent rephrases the question for clarity and calls the matching engine to write a query.
5. **Query validation** - The generated query is validated for correct form and compliance before anything runs.
6. **Query execution and response** - The query executes against the chosen source, and the results are formatted into a readable response - a table, a summary, or a set of key insights.

The takeaway from that pipeline: **the agent never elevates anybody's access.** It runs as the person asking, which is why two different users can ask the same agent the same question and legitimately get different answers.

### Data sources and the engine behind each one

Step 4 above is the part that surprises people. A data agent doesn't have one query language - it picks the right translation engine for whichever source it selected.

<table style="tr:nth-child(even) {background-color: #f2f2f2;}; text-align: left; display: table; border-collapse: collapse; border-spacing: 2px; border-color: gray;">

  <tr><th style="background-color: #1b20a1; color: white;">Data source</th> <th style="background-color: #1b20a1; color: white;">How the agent queries it</th> <th style="background-color: #1b20a1; color: white;">When to reach for it</th></tr>

  <tr><td><b>Lakehouse</b></td><td>Natural language to SQL (NL2SQL)</td><td>Raw and curated table exploration over Delta tables in OneLake.</td></tr>
  <tr><td><b>Warehouse</b></td><td>Natural language to SQL (NL2SQL)</td><td>Modeled, SQL-first analytics where the schema is already shaped for reporting.</td></tr>
  <tr><td><b>Power BI semantic model</b></td><td>Natural language to DAX (NL2DAX)</td><td>Questions that must respect certified business measures and KPIs rather than recomputing them from raw tables.</td></tr>
  <tr><td><b>KQL database (including Eventhouse)</b></td><td>Natural language to KQL (NL2KQL)</td><td>Log analysis, event data, and time-series questions. NL2KQL can use KQL user-defined functions when they exist, and runs against both live and historical Eventhouse data.</td></tr>
  <tr><td><b>Mirrored database</b></td><td>Selected like any other tabular source</td><td>Operational data replicated into OneLake that you want to query in place. Listed in the documented prerequisites as a supported source; you need read access to it.</td></tr>
  <tr><td><b>Ontology</b></td><td>Selected like any other source</td><td>Questions expressed in shared business concepts rather than physical table names. Ontologies were introduced in Module 01 and are covered in depth in Modules 04 and 05.</td></tr>
  <tr><td><b>Microsoft Graph</b></td><td>Microsoft Graph queries</td><td>Organizational data - people, groups, and related context accessible through Microsoft Graph.</td></tr>

</table>

<br>

Because the agent chooses the source itself, you can mix source types in a single agent. A single agent might route financial-metric questions to a semantic model, raw exploration to a lakehouse, and log analysis to a KQL database - all from the same chat box.

> **Note:** Azure AI Search is not currently listed in the Fabric documentation as a supported data agent data source. Stick to the sources in the table above when you plan an agent.

### How a data agent differs from a Copilot

Both use generative AI over your data, and the two get conflated constantly. The documented differences are worth memorizing:

- **Configuration flexibility** - You can heavily configure a data agent with your own instructions and examples so it behaves the way your organization needs. Fabric copilots come preconfigured and don't offer that level of customization.
- **Scope and use case** - A Fabric copilot helps *you* do work inside Fabric, such as generating notebook code or warehouse queries. A data agent is a standalone, configurable artifact that queries data across OneLake and semantic models, and it can be surfaced outside Fabric - through Microsoft 365 Copilot, Microsoft Copilot Studio, Azure AI Foundry, or Microsoft Teams.

If you remember one sentence: a copilot helps the *builder*, a data agent serves the *consumer*.

### Governance and intent layers

When several parties all try to influence agent behavior, Fabric resolves the conflict using a fixed precedence order. From highest to lowest:

1. **Organizational intent** - Tenant-wide policies and compliance requirements set by administrators. Highest precedence, and no other layer can override it.
2. **Role-based intent** - Workspace governance settings and permission boundaries for specific roles or groups.
3. **Developer intent** - The custom instructions, example queries, and data source configuration *you* provide when you build the agent.
4. **User intent** - The questions and prompts end users submit during a conversation.

Higher layers always win. This is the reason a developer instruction can never talk the agent into bypassing read-only behavior or reaching a source outside its configured scope - the agent refuses or redirects the request instead.

### Know these limitations before you design an agent

The documented limitations shape what you should and shouldn't promise your stakeholders:

- The agent generates **read** queries only. It never creates, updates, or deletes data.
- **Unstructured data isn't supported** - no .pdf, .docx, or .txt files.
- For lakehouses, the agent answers from the **tables you select**. It doesn't read standalone files such as CSV or JSON unless they're ingested or exposed as tables.
- **English only** today. Provide questions, instructions, and example queries in English.
- You **can't change the LLM** the agent uses.
- Conversation history **might not always persist** across service updates or model upgrades.
- The agent **can't query across capacity regions**. If the data source's workspace capacity is in a different region than the agent's workspace capacity, the query fails.
- Responses are **capped at 25 rows and 25 columns**. Data agents are built for conversational insight, not for returning complete datasets - and because earlier turns influence later ones, start a new chat when a capped result has skewed the conversation.
- Purview DLP and access restriction policies can **truncate or block** responses, and assets marked sensitive may be unreachable, producing incomplete answers.
- Agent interactions **may be logged and discoverable** through Microsoft Purview Audit and eDiscovery.

Some question types are simply out of scope. "What were the top selling products last quarter?" translates cleanly to a query. "Why is our factory productivity lower in Q2?" or "What is the root cause of our sales spike?" do not - they need causal inference and correlation analysis that the data agent doesn't perform.

<br>

<p><img style="float: left; margin: 0px 15px 15px 0px;" src="../graphics/point1.png"><b>Activity: Map the Anatomy</b></p>

A discussion exercise - no Fabric tenant required. Working in pairs or as a group, reason through how the agent would handle a set of questions before you ever build one.

<p><img style="margin: 0px 15px 15px 0px;" src="../graphics/checkmark.png"><b>Steps</b></p>

- For each question below, decide **which data source** you would expect the agent to select and **which engine** it would use (NL2SQL, NL2DAX, NL2KQL, or Microsoft Graph):
  - "What was certified net revenue by region last quarter?"
  - "Which raw sales rows have a null postal code?"
  - "Show me the error spike in the ingestion pipeline over the last six hours."
  - "Which customers are connected to a delayed shipment?"
- Name the six pipeline stages a question passes through, in order, and state which stage stops a user from seeing data they aren't permitted to see.
- Identify which of these requests the agent should **refuse or redirect**, and which governance layer forces that outcome:
  - A user asks the agent to delete last year's test records.
  - A builder writes an instruction telling the agent to ignore workspace permissions.
- Pick two of the documented limitations above and describe how each one would change what you promise a business stakeholder.

<p style="border-bottom: 1px solid lightgrey;"></p>

<h2 id="2.2"><img style="float: left; margin: 0px 15px 15px 0px;" src="../graphics/pencil2.png">2.2 Prerequisites and Tenant Configuration</h2>

Data agents are one of the Fabric features most likely to fail for *environmental* reasons rather than authoring mistakes. Working through this section before you build will save you from debugging an agent that was never going to run.

### Capacity and data requirements

- A paid **F2 or higher Fabric capacity**, or a **Power BI Premium per capacity (P1 or higher)** capacity with Microsoft Fabric enabled.
- At least one supported data source **containing data**: a warehouse, a lakehouse, a Power BI semantic model, a KQL database, a mirrored database, or an ontology.
- **Read access** to that data source.

Two capacity details catch people out. First, the agent and its data sources must live on capacity in the **same region** - a lakehouse on North Europe capacity will fail for an agent on France Central capacity. Second, remember the permission exception for semantic models: interacting with a Power BI semantic model through a data agent requires only **Read** permission on the model. Workspace access such as Member or Contributor, and Build permission, aren't required. Write permission is needed only to modify the model itself or to use capabilities such as Prep for AI.

### Tenant settings

Data agents depend on the Copilot and Azure OpenAI tenant switches. A Fabric administrator enables these in the **Admin portal**.

<table style="tr:nth-child(even) {background-color: #f2f2f2;}; text-align: left; display: table; border-collapse: collapse; border-spacing: 2px; border-color: gray;">

  <tr><th style="background-color: #1b20a1; color: white;">Setting</th> <th style="background-color: #1b20a1; color: white;">Where</th> <th style="background-color: #1b20a1; color: white;">Why it matters</th></tr>

  <tr><td><b>Users can use Copilot and other features powered by Azure OpenAI</b></td><td>Tenant settings &gt; Copilot and Azure AI</td><td>The master switch. Without it, nobody in the tenant can use a Fabric data agent.</td></tr>
  <tr><td><b>Capacities can be designated as Fabric Copilot capacities</b></td><td>Tenant settings &gt; Copilot and Azure AI</td><td>Lets capacity administrators designate which capacities carry Copilot workloads.</td></tr>
  <tr><td><b>Data sent to Azure OpenAI can be processed outside your capacity's geographic region, compliance boundary, or national cloud instance</b></td><td>Tenant settings &gt; Copilot and Azure AI</td><td>Required when your capacity region sits outside the EU data boundary and the US.</td></tr>
  <tr><td><b>Data sent to Azure OpenAI can be stored outside your capacity's geographic region, compliance boundary, or national cloud instance</b></td><td>Tenant settings &gt; Copilot and Azure AI</td><td>Required for Copilot in Notebooks and for data agents when your capacity region sits outside the EU data boundary and the US.</td></tr>
  <tr><td><b>Standalone Copilot experience</b></td><td>Tenant settings &gt; Copilot</td><td>If this isn't enabled you won't be able to use the data agent inside Copilot scenarios, even when every other Copilot switch is on.</td></tr>

</table>

<br>

The two cross-geo settings are the ones that confuse people most. They exist because Fabric uses a **Microsoft-managed** Azure OpenAI service, and inference may need to happen outside your capacity's home geography. If your organization can't allow that, the setting stays off - and the agent won't run in an affected region. That's a conversation to have with your compliance team, not a switch to flip quietly.

> **Important:** Tenant settings can take **up to one hour** to take effect after you enable them. Enable them well before class or a demo - not five minutes beforehand.

### A governance caution before you go further

You can configure data agents to be consumed from services outside Fabric, such as Microsoft Foundry, Microsoft Copilot Studio, Microsoft 365 Copilot, or as an MCP server. When you connect to these non-Fabric services, responses returned by the agent **may be sent outside of Fabric's compliance boundary or geographic region**, and are then processed and stored according to that service's own terms and data handling policies.

Also worth confirming up front: if your tenant or workspace is governed by Microsoft Purview policies, the agent must operate within them. Purview DLP policies in Fabric Data Warehouse are generally available, and access restriction policies for Fabric KQL Database, Fabric SQL Database, and Fabric Data Warehouse are in preview. Either can limit what your agent returns.

<br>

<p><img style="float: left; margin: 0px 15px 15px 0px;" src="../graphics/point1.png"><b>Activity: Preflight Check</b></p>

Confirm your environment can actually run a data agent before you build one. You'll need Fabric administrator rights to view or change tenant settings - if you don't have them, work through this with your administrator and record what you find.

<p><img style="margin: 0px 15px 15px 0px;" src="../graphics/checkmark.png"><b>Steps</b></p>

- Confirm your workspace is backed by an **F2 or higher** capacity, or a **P1 or higher** capacity with Fabric enabled. Write down the capacity name and its **region**.
- Open the **Admin portal** and review the Copilot and Azure AI tenant settings listed in the table above. Record the current state of each one.
- Determine whether your capacity region requires the two **cross-geo** settings, and note who in your organization would need to approve them.
- Confirm the **Standalone Copilot experience** setting under Tenant settings &gt; Copilot.
- Identify the data source you'll use in section 2.3, and confirm it is on capacity in the **same region** as the workspace where you'll create the agent.
- Verify you have at least **Read** access to that data source.
- If you changed any tenant setting, note the time - allow up to an hour before testing.

<p style="border-bottom: 1px solid lightgrey;"></p>

<h2 id="2.3"><img style="float: left; margin: 0px 15px 15px 0px;" src="../graphics/pencil2.png">2.3 Creating an Agent and Adding Data Sources</h2>

With prerequisites confirmed, creating the agent itself is quick. The decisions that determine whether it gives good answers are made in this section - specifically, *which* sources you attach and *which tables* you expose.

### Create the item

Navigate to your workspace and select the **+ New Item** button.

<p><img style="box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.19);" src="https://learn.microsoft.com/en-us/fabric/data-science/media/data-agent-scenario/create-data-agent.png" height="400"></p>

In the **All items** tab, search for **Fabric data agent**. Once you select it, you're prompted to provide a name for the agent.

<p><img style="box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.19);" src="https://learn.microsoft.com/en-us/fabric/data-science/media/data-agent-scenario/name-data-agent.png" height="400"></p>

Name it for the **business domain it serves**, not for the technology - `Sales Analytics` rather than `Lakehouse Agent`. That name is what your colleagues will see, and after Module 03 it's also what routes questions to this agent from other surfaces.

### Add your data sources

Select the source you want and choose **Add**.

<p><img style="box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.19);" src="https://learn.microsoft.com/en-us/fabric/data-science/media/data-agent-scenario/select-and-add-lakehouse.png" height="400"></p>

A data agent supports **up to five data sources in any combination**. That could be five Power BI semantic models, or a mix such as two semantic models, one lakehouse, and one KQL database. Add them one at a time; once added, the source appears in the **Explorer** pane on the left side of the data agent page. Use **+ Data source** in that pane to add subsequent sources. Hovering over a source and opening its three-dot menu gives you **Remove** and **Refresh** - use **Refresh** after the underlying schema changes so the agent sees new tables and columns.

The five-source ceiling is a design constraint, not a suggestion. If a domain genuinely needs more, that's a signal to build a *second* agent scoped to a different business domain rather than to overload one.

### Select the tables the agent can see

Select a source in the Explorer pane to view its available tables, then use the checkboxes to choose the tables you want to make available to the AI.

<p><img style="box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.19);" src="https://learn.microsoft.com/en-us/fabric/data-science/media/data-agent-scenario/get-started.png" height="400"></p>

This is the highest-leverage decision in the whole module. Selecting only relevant tables focuses the agent on the data that matters and helps it return accurate results. Every extra table you check is one more candidate the model has to reason about - and one more chance for it to join the wrong thing. **Select deliberately, not exhaustively.**

A few source-specific notes:

- **Lakehouse** - Select lakehouse *tables*, not individual files. If your data starts life as CSV or JSON files, ingest it into tables or otherwise expose it through tables first.
- **OneLake shortcuts** - The OneLake catalog can include tables exposed through shortcuts, and the agent can query those shortcut-backed tables directly, without copying data into the workspace. Data shared from another tenant through OneLake external data sharing is queryable through the shortcut created when the share was accepted.
- **KQL databases backed by Eventhouse** - Select only the tables most relevant to typical questions, and encourage users to include time filters when querying high-volume time-series or event data so responses stay fast.

### Test as you go

The agent has a chat experience built into the authoring page - use it. Ask a question you already know the answer to, so you can tell the difference between a wrong answer and a surprising one. The **Clear chat** button resets the conversation, which matters more than it sounds: earlier turns influence later answers, and the 25-row response cap means a follow-up question can inherit an already-truncated context. When results start looking odd, clear the chat and start clean.

<br>

<p><img style="float: left; margin: 0px 15px 15px 0px;" src="../graphics/point1.png"><b>Activity: Build Your First Agent</b></p>

Create a working data agent over the AdventureWorks sample data. If your instructor has pre-loaded the lakehouse, skip the first step.

<p><img style="margin: 0px 15px 15px 0px;" src="../graphics/checkmark.png"><b>Steps</b></p>

- Create a lakehouse named `AdventureWorksLH` and populate it by following the **Create a lakehouse with AdventureWorksLH** section of the <a href="https://learn.microsoft.com/en-us/fabric/data-science/data-agent-end-to-end-tutorial">Fabric data agent scenario</a> tutorial, which provides the notebook code that loads the sample tables.
- When the load finishes, **stop the notebook session** (Notebook toolbar &gt; Stop session). A notebook left running continues to consume Fabric capacity.
- In the same workspace, select **+ New Item**, search the **All items** tab for **Fabric data agent**, and give your agent a business-oriented name.
- Add the `AdventureWorksLH` lakehouse as a data source and select **Add**.
- In the **Explorer** pane, select the lakehouse and check these tables: `dimcustomer`, `dimdate`, `dimgeography`, `dimproduct`, `dimproductcategory`, `dimpromotion`, `dimreseller`, `dimsalesterritory`, `factinternetsales`, `factresellersales`.
- Smoke-test the agent with one question you can verify, such as *"How many customers are there by country?"*, and confirm you get a sensible answer.
- Note which tables the agent used to answer. Then ask yourself: if you had checked **every** table in the lakehouse, would that answer have been easier or harder for the agent to get right?

<p><img style="float: left; margin: 0px 15px 15px 0px;" src="../graphics/point1.png"><b>Self-Guided Activity: Add a Second Source</b></p>

After the workshop, extend the agent to a mixed-source design so you can watch the routing behavior described in section 2.1.

<p><img style="margin: 0px 15px 15px 0px;" src="../graphics/checkmark.png"><b>Steps</b></p>

- Using **+ Data source** in the Explorer pane, add a second source of a *different type* - a Power BI semantic model or a KQL database.
- Ask a question that clearly belongs to each source, and observe which one the agent selects.
- Confirm for yourself that adding a semantic model required only **Read** permission on the model.
- Change a table in one of the underlying sources, then use **Refresh** on that data source and confirm the agent picks up the change.

<p style="border-bottom: 1px solid lightgrey;"></p>

<h2 id="2.4"><img style="float: left; margin: 0px 15px 15px 0px;" src="../graphics/pencil2.png">2.4 Publishing Your Agent (Go Live)</h2>

Everything so far has happened in the **draft** version of your agent - a private workspace only you and other builders see. Publishing is what turns that draft into something colleagues can actually use.

### Draft and published versions

When you publish, Fabric takes a **snapshot** of the current configuration. From that point on your agent has two versions:

- The **published version** - a read-only, shareable snapshot. This is what consumers query.
- The **draft version** - still fully editable, and isolated from the published one.

That separation is the whole point. You can keep refining the draft - adding sources, changing table selections, testing new questions - without any of it reaching your users until you publish again. You can also switch between draft and published to compare how each one answers the same question, which is the fastest way to sanity-check a change before you ship it.

### Publish

Once you've validated the agent's performance, select **Publish**.

<p><img style="box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.19);" src="https://learn.microsoft.com/en-us/fabric/data-science/media/data-agent-scenario/ai-select-publish.png" height="400"></p>

The **Publish data agent** box opens and prompts you for a description of the agent.

<p><img style="box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.19);" src="https://learn.microsoft.com/en-us/fabric/data-science/media/data-agent-scenario/publish-data-agent.png" height="400"></p>

Treat that description as a real deliverable rather than a formality. It tells consumers what this agent is for, and in later modules it becomes the routing hint that other surfaces use to decide whether *this* agent should field a given question. A vague description produces an agent nobody trusts and nothing can route to.

There's a neat trick for writing it: **ask the agent to describe what it does**, then refine and summarize its answer into the description. It has the schema and your configuration in front of it, so it tends to produce a better first draft than you would from memory.

Select **Publish** in the box to complete publishing. The published URL for the agent then appears.

<p><img style="box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.19);" src="https://learn.microsoft.com/en-us/fabric/data-science/media/data-agent-scenario/fabric-notebook-data-agent-published-url-value.png" height="400"></p>

Capture that URL - it's the handle that programmatic and external consumers use, and you'll want it in Module 03.

If you later need to change only the description without republishing configuration, go to **Settings &gt; Publishing** and update it there.

### What consumers need

One pointer before you hand off, because it's the single most common surprise after a first publish: publishing does **not** grant anybody access to your data. The agent runs as the person asking, so each consumer still needs their own read access to the underlying sources, and Row-Level Security and Column-Level Security continue to apply. Sharing, the permission model, and every consumption surface are covered in **Module 03**.

<br>

<p><img style="float: left; margin: 0px 15px 15px 0px;" src="../graphics/point1.png"><b>Activity: Publish and Hand Off</b></p>

Take the agent you built in section 2.3 live, and leave yourself ready for Module 03.

<p><img style="margin: 0px 15px 15px 0px;" src="../graphics/checkmark.png"><b>Steps</b></p>

- Ask your agent to describe what it does, and keep the response as raw material.
- Select **Publish**, then write a consumer-facing description in the **Publish data agent** box. Aim for two or three sentences that state the business domain it covers, the kinds of questions it answers well, and anything it deliberately doesn't cover.
- Complete publishing and **copy the published URL** somewhere you can find it again in Module 03.
- Make a small change in the **draft** version - for example, add or remove one table - and confirm the published version is unaffected.
- Switch between the draft and published versions and ask both the same question. Note any difference in the answers.
- Open **Settings &gt; Publishing** and confirm you can update the description without republishing.

<p style="border-bottom: 1px solid lightgrey;"></p>

<p><img style="margin: 0px 15px 15px 0px;" src="../graphics/owl.png"><b>For Further Study</b></p>
<ul>
  <li><a href="https://learn.microsoft.com/en-us/fabric/data-science/concept-data-agent">Fabric data agent concepts</a></li>
  <li><a href="https://learn.microsoft.com/en-us/fabric/data-science/how-to-create-data-agent">Create a Fabric data agent</a></li>
  <li><a href="https://learn.microsoft.com/en-us/fabric/data-science/data-agent-configurations">Fabric data agent configurations</a></li>
  <li><a href="https://learn.microsoft.com/en-us/fabric/data-science/data-agent-tenant-settings">Fabric data agent tenant settings</a></li>
  <li><a href="https://learn.microsoft.com/en-us/fabric/data-science/data-agent-end-to-end-tutorial">Fabric data agent scenario - end-to-end tutorial</a></li>
  <li><a href="https://learn.microsoft.com/en-us/fabric/data-science/data-agent-sharing">Fabric data agent sharing and permission management</a></li>
  <li><a href="https://learn.microsoft.com/en-us/fabric/governance/microsoft-purview-fabric">Use Microsoft Purview to govern Microsoft Fabric</a></li>
  <li><a href="https://learn.microsoft.com/en-us/fabric/get-started/copilot-fabric-overview">Overview of Copilot in Fabric</a></li>
  <li><a href="https://learn.microsoft.com/en-us/fabric/get-started/whats-new">As always, this is a fast-changing technology, so check this reference for the latest improvements</a></li>
</ul>

<p style="border-bottom: 1px solid lightgrey;"></p>

Congratulations! You have completed this Module. You can now explain what a Fabric data agent is and how it turns a plain-English question into a governed query, you've confirmed the capacity and tenant configuration it depends on, and you've created, scoped, tested, and published a working agent.

If you understand the concepts here and have completed all of the Activities, you can [proceed to the next Module](03%20-%20Fabric%20Data%20Agents%20-%20In%20Use.md), where you'll share that published agent and put it to work across Fabric and beyond.
