![](../graphics/microsoftlogo.png)

# Workshop: Microsoft Fabric Data Agents and Beyond

#### <i>A workshop from the Tales from the Field team</i>

<p style="border-bottom: 1px solid lightgrey;"></p>

<img style="float: left; margin: 0px 15px 15px 0px;" src="../graphics/textbubble.png"> <h2>RTI, Operations Agents, & Data Agents</h2>

Real-time data changes how agents operate. In this module you'll explore Microsoft Fabric's Real-Time Intelligence (RTI) stack end to end — discover and ingest streaming data through the **Real-Time hub** and **Eventstreams**, store and query it in the **Eventhouse** with the Kusto Query Language (KQL) — and then cross into agentic scenarios. You'll wire a **Fabric Data Agent** directly over a live KQL database so it answers natural-language questions about events as they happen, and you'll build a **Fabric Activator** rule that acts as an "operations agent," autonomously monitoring the stream and triggering automated actions. By the end you'll see RTI's *detect → analyze → act* loop, combined with Data Agents, replace brittle scheduled jobs with event-driven, conversational, and agentic intelligence.

> **A note on terminology:** "operations agent" is an editorial framing we use in this workshop. The built-in Fabric construct that autonomously monitors data and takes action is **Activator**. Everywhere this module says "operations agent," map it to Activator.

In each section you'll get more references, which you should follow up on to learn more. Also watch for links within the text - click on each one to explore that topic.

(<a href="\00 - Pre-Requisites.md" target="_blank">Make sure you check out the <b>Pre-Requisites</b> page before you start</a>. You'll need all of the items loaded there before you can proceed with the workshop.)

You'll cover these topics in this module:
<dl>

  <dt><a href="#6.1" target="_blank">6.1 - RTI Architecture: Real-Time hub, Eventstreams & Eventhouse</a></dt>
  <dt><a href="#6.2" target="_blank">6.2 - Analyzing Streams: KQL Querysets & Real-Time Dashboards</a></dt>
  <dt><a href="#6.3" target="_blank">6.3 - Conversational Analytics: a Data Agent over live Eventhouse data</a></dt>
  <dt><a href="#6.4" target="_blank">6.4 - Operations Agents: Activator rules for automated action</a></dt>

</dl>

<p style="border-bottom: 1px solid lightgrey;"></p>

<h2 id="6.1"><img style="float: left; margin: 0px 15px 15px 0px;" src="../graphics/pencil2.png">6.1 RTI Architecture: Real-Time hub, Eventstreams & Eventhouse</h2>

[Real-Time Intelligence](https://learn.microsoft.com/en-us/fabric/real-time-intelligence/overview) is the Microsoft Fabric workload for data *in motion*. Where the lakehouse and warehouse you've used in earlier modules are optimized for data at rest, RTI is optimized for streaming and time-series data — telemetry, logs, IoT signals, application events, and business events — that arrive continuously and lose value if they sit in a queue waiting for the next scheduled batch. RTI gives you an end-to-end path to **discover, ingest, store, query, visualize, and act on** that data with second-level latency.

Before you build anything, it helps to hold a clear mental model of the three core building blocks and how event data flows through them.

<p><img style="height: 400; box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.19);" src="https://learn.microsoft.com/en-us/fabric/real-time-intelligence/media/overview/overview-schematic.png"></p>

<h3>Real-Time hub — the catalog of streams</h3>

The [Real-Time hub](https://learn.microsoft.com/en-us/fabric/real-time-hub/real-time-hub-overview) is the single, tenant-wide place where every stream in your organization is discoverable. It is to streaming data what the OneLake catalog is to data at rest: a centralized catalog that lets you find, add, explore, and share streams across domains. From the hub you can browse data that's already flowing (Fabric events, Azure events, and streams other teams have published), connect brand-new sources, and preview events before you commit to a pipeline. Making streams broadly discoverable is what unlocks organization-wide real-time intelligence rather than a collection of disconnected, one-off pipelines.

<h3>Eventstreams — ingest, transform, and route (no-code)</h3>

An [Eventstream](https://learn.microsoft.com/en-us/fabric/real-time-intelligence/event-streams/overview) is the pipeline that captures, transforms, and routes real-time events to their destinations — all in a no-code, drag-and-drop canvas. You add one or more **sources** (for example, built-in sample data, Azure Event Hubs, Azure IoT Hub, or a Custom App endpoint you push to), optionally drop in an **event processor** to filter, aggregate, or reshape events on the way through, and connect one or more **destinations** such as an Eventhouse (KQL database), a lakehouse, or a Custom App. Because the end-to-end flow is drawn as a diagram, an Eventstream doubles as living documentation of exactly how your event data moves and changes. Fabric manages the underlying scalable infrastructure for you.

<h3>Eventhouse — the time-indexed store (KQL database)</h3>

An [Eventhouse](https://learn.microsoft.com/en-us/fabric/real-time-intelligence/eventhouse) is the storage and analytics engine at the end of the pipeline, purpose-built for streaming and time-series data. It's powered by the **Kusto engine**, the same core engine as Azure Data Explorer, and it automatically indexes and partitions incoming data by ingestion time so you can query petabytes with millisecond-to-second response. An Eventhouse is a *workspace of databases*: it can host multiple **KQL databases** that share capacity, monitoring, and management. A useful analogy from the on-premises world — the **Eventhouse** is like a SQL Server instance, and each **KQL database** inside it is like a database on that server. To optimize cost, an Eventhouse can suspend itself when idle and reactivate on demand (with a few seconds of latency), or you can set a **Minimum consumption** level to keep it always warm for time-sensitive workloads.

Put together, the flow is simple to hold in your head: **Real-Time hub** (discover the stream) → **Eventstream** (ingest, transform, route) → **Eventhouse / KQL database** (store and query). Everything else in this module builds on top of that spine.

<br>

<p><img style="float: left; margin: 0px 15px 15px 0px;" src="../graphics/point1.png"><b>Activity: Your First Streaming Pipeline</b></p>

<p><img style="margin: 0px 15px 15px 0px;" src="../graphics/checkmark.png"><b>Description</b></p>

In this activity you'll stand up the RTI spine end to end using Microsoft's official Real-Time Intelligence tutorial. You'll set up an Eventhouse, then use the Real-Time hub to bring a built-in sample stream (bicycle data) into an Eventstream and land it in your KQL database — proving that live rows are flowing before you do anything else with them. This is the reusable Microsoft Learn tutorial, so the steps stay current with the product.

<p><img style="margin: 0px 15px 15px 0px;" src="../graphics/checkmark.png"><b>Steps</b></p>

- [ ] Open the [Real-Time Intelligence tutorial - Introduction](https://learn.microsoft.com/en-us/fabric/real-time-intelligence/tutorial-introduction) and review the scenario and prerequisites.
- [ ] Complete [Part 1 - Set up resources](https://learn.microsoft.com/en-us/fabric/real-time-intelligence/tutorial-1-resources) to create your Eventhouse and KQL database.
- [ ] Complete [Part 2 - Get real-time events](https://learn.microsoft.com/en-us/fabric/real-time-intelligence/tutorial-2-get-real-time-events) to connect the sample source through the Real-Time hub into an Eventstream and route it to your Eventhouse.
- [ ] In a KQL queryset, confirm live data is landing by running a quick check against your table: `<YourTableName> | take 10` — then re-run it and watch the row values change as new events arrive.
- [ ] Keep these resources — you'll build directly on this Eventhouse in sections 6.2, 6.3, and 6.4.

<p style="border-bottom: 1px solid lightgrey;"></p>

<h2 id="6.2"><img style="float: left; margin: 0px 15px 15px 0px;" src="../graphics/pencil2.png">6.2 Analyzing Streams: KQL Querysets & Real-Time Dashboards</h2>

Once events are landing in your Eventhouse, you need a way to ask questions of them. Real-Time Intelligence uses the [Kusto Query Language (KQL)](https://learn.microsoft.com/en-us/azure/data-explorer/kusto/query/) — an open-source, read-only query language designed for exactly this kind of structured, semi-structured, and unstructured time-series data. KQL reads top to bottom as a pipeline of operators separated by the pipe (`|`) character, which makes time-series and log exploration remarkably concise. RTI also supports many T-SQL functions if you're coming from a SQL background.

<h3>KQL Querysets</h3>

A [KQL queryset](https://learn.microsoft.com/en-us/fabric/real-time-intelligence/create-query-set) is the item you use to run, view, and customize queries against a KQL database. Each tab in a queryset can point at a different KQL database, and you can save queries for later, share them with colleagues, and export results — including generating a Power BI report from a query. Because you can re-point a tab at a different database, the same query can be run against data in different states, which is handy for comparing environments.

<h4>Copilot and natural language to KQL (NL2KQL)</h4>

If KQL is new to your attendees, Fabric includes **Copilot for Real-Time Intelligence**, which translates plain-English questions into KQL (NL2KQL). A user can type "how many trips started at each station in the last hour?" and Copilot drafts the KQL for them to review, run, and refine. This lowers the barrier to entry dramatically and is a natural stepping stone to the fully conversational Data Agent you'll build in section 6.3.

<p><img src="https://learn.microsoft.com/en-us/azure/data-explorer/media/data-explorer-overview/workflow.png" height="400"></p>

<h3>Real-Time Dashboards</h3>

A [Real-Time Dashboard](https://learn.microsoft.com/en-us/fabric/real-time-intelligence/dashboard-real-time-create) is a collection of tiles, optionally organized into pages, where each tile is backed by a KQL query and rendered as a visual. You author a query in your queryset and export it directly to a dashboard tile, then adjust the visual formatting and — importantly — set an **auto-refresh** interval so the tiles continuously re-run their queries and reflect the latest events without anyone clicking refresh. Real-Time Dashboards are *distinct from Power BI dashboards*: they're built for high-volume, low-latency KQL data and offer improved query and visualization performance for streaming scenarios, whereas Power BI remains the right tool for governed, semantic-model-driven business reporting. Both have their place; this module focuses on the real-time variety.

<br>

<p><img style="float: left; margin: 0px 15px 15px 0px;" src="../graphics/point1.png"><b>Activity: From Bytes to Board</b></p>

<p><img style="margin: 0px 15px 15px 0px;" src="../graphics/checkmark.png"><b>Description</b></p>

Building on the Eventhouse from section 6.1, you'll query your streaming data with KQL — including at least one query drafted for you by Copilot — and then turn those queries into a live, auto-refreshing Real-Time Dashboard. You'll continue with the official Microsoft Learn tutorial so the experience stays current with the product.

<p><img style="margin: 0px 15px 15px 0px;" src="../graphics/checkmark.png"><b>Steps</b></p>

- [ ] Complete [Part 3 - Query streaming data using KQL](https://learn.microsoft.com/en-us/fabric/real-time-intelligence/tutorial-3-query-data). As you go, write **three** queries against your table:
    - [ ] one that filters events by time (for example, the last 15 minutes),
    - [ ] one that aggregates (for example, a count or average grouped by a category), and
    - [ ] one that you generate with **Copilot** by typing a plain-English question, then inspect the KQL it produced.
- [ ] Complete [Part 4 - Create a Real-Time Dashboard](https://learn.microsoft.com/en-us/fabric/real-time-intelligence/tutorial-4-create-dashboard), pinning your queries as tiles.
- [ ] Set the dashboard's **auto-refresh** interval (for example, 30 seconds) and watch the tiles update as new events land.
- [ ] Optional: explore [Part 5 - Create a Power BI report](https://learn.microsoft.com/en-us/fabric/real-time-intelligence/tutorial-5-power-bi-report) to contrast the Real-Time Dashboard with a Power BI report over the same data.

<p style="border-bottom: 1px solid lightgrey;"></p>

<h2 id="6.3"><img style="float: left; margin: 0px 15px 15px 0px;" src="../graphics/pencil2.png">6.3 Conversational Analytics: a Data Agent over live Eventhouse data</h2>

You already know from Modules 02–03 what a [Fabric Data Agent](https://learn.microsoft.com/en-us/fabric/data-science/concept-data-agent) is: a generally available feature that lets you build conversational, natural-language Q&A systems over governed data in OneLake using generative AI. What's new here is pointing that same capability at **live, streaming data**. A Data Agent connects to your data through lakehouses, warehouses, Power BI semantic models, **KQL databases**, ontologies, and Microsoft Graph — up to five sources in any combination — and answers plain-English questions so that people without KQL, SQL, or DAX skills can still get precise, context-rich answers.

<h3>NL2KQL over Eventhouse — querying events in place</h3>

When you add a **KQL database** as a source, the Data Agent uses **natural language to KQL (NL2KQL)** to translate a question into a Kusto query. Critically, this works against **Eventhouse KQL databases for both live and historical event and time-series data** — standard KQL time filters and time-series patterns are supported, and the agent queries the Eventhouse **in place, with no data movement**. That makes the Data Agent the *on-demand, conversational* complement to the *automated, event-driven* Activator path you'll build in section 6.4: when a human wants to investigate the stream ("which stations ran dry in the last hour, and how does that compare to yesterday?"), they ask the Data Agent; when a condition should trigger action without a human in the loop, Activator handles it.

<h3>How it works, and how it stays governed</h3>

Under the hood the Data Agent uses large language models (via the Azure OpenAI Assistant API) to parse the question, identify the most relevant source among those you configured, generate and validate a query, execute it, and format the result into a human-readable answer. Every interaction is **read-only** and runs under the **requesting user's own credentials and permissions**, so an agent can never surface data the user isn't authorized to see. It respects Microsoft Purview governance — including Data Loss Prevention and access-restriction policies — and you can sharpen accuracy by adding **agent instructions** (for example, "route log-analysis questions to the KQL database") and **example question/query pairs**. For high-volume event tables, a good practice is to expose only the most relevant tables and encourage users to include time filters so responses stay fast.

<h3>Environment requirements — read this before you demo</h3>

A Data Agent has real capacity and tenant requirements, and it will fail quietly if they aren't met. You need a **paid F2 (or higher) Fabric capacity** — or a Power BI Premium P1+ capacity with Fabric enabled — **and** the **cross-geo processing and cross-geo storing for AI** tenant settings enabled. On a trial or F1 capacity the Data Agent experience will not work as expected, so confirm these settings before relying on it in front of an audience.

<br>

<p><img style="float: left; margin: 0px 15px 15px 0px;" src="../graphics/point1.png"><b>Activity: Ask Your Stream</b></p>

<p><img style="margin: 0px 15px 15px 0px;" src="../graphics/checkmark.png"><b>Description</b></p>

> ⚠️ **Flagged for the workshop maintainer — activity to be authored.** At the time this module was written, Microsoft Learn does **not** publish a reusable, hands-on tutorial that builds a Fabric Data Agent over a **live Eventhouse / KQL database** source. The published Data Agent end-to-end tutorial uses the **AdventureWorks** dataset in a *lakehouse* (data at rest), not a streaming KQL source, so it does not match this section's topic. In keeping with this workshop's rule — *reuse a Microsoft Learn activity, or flag it rather than inventing one* — no step-by-step activity is provided here yet. The conceptual content above is complete and can be taught as-is; the hands-on activity below is a placeholder for you to author (or to approve building from the reference docs listed).

<p><img style="margin: 0px 15px 15px 0px;" src="../graphics/checkmark.png"><b>Steps</b></p>

- [ ] **TODO (maintainer):** Author "Ask Your Stream" — build a Data Agent on the KQL database created in section 6.1, ask natural-language questions about the live events, and inspect the generated KQL. Reference material to build from:
    - [Create a Fabric data agent](https://learn.microsoft.com/en-us/fabric/data-science/how-to-create-data-agent) (how-to)
    - [Add and configure data sources in a Fabric data agent](https://learn.microsoft.com/en-us/fabric/data-science/data-agent-add-datasources) (confirms KQL database as a source)
    - [Fabric data agent concepts](https://learn.microsoft.com/en-us/fabric/data-science/concept-data-agent) (NL2KQL over Eventhouse, governance, prerequisites)
- [ ] Confirm the F2+ capacity and cross-geo AI tenant settings are in place before finalizing the activity, since the experience depends on them.

<p style="border-bottom: 1px solid lightgrey;"></p>

<h2 id="6.4"><img style="float: left; margin: 0px 15px 15px 0px;" src="../graphics/pencil2.png">6.4 Operations Agents: Activator rules for automated action</h2>

The conversational Data Agent answers questions when a human asks. But many real-time scenarios need something to watch the stream *continuously* and act *without* a human in the loop — this is the "operations agent" pattern, and in Fabric it's delivered by [Fabric Activator](https://learn.microsoft.com/en-us/fabric/real-time-intelligence/data-activator/activator-introduction). Activator is a **no-code event-detection engine** that transforms data streams into automated actions: it continuously monitors sources with low latency (subsecond for stateless rules on streaming data) and, when a threshold is crossed or a pattern appears, automatically triggers an action.

<h3>The core concepts</h3>

Activator organizes everything around four ideas:

<h4>Events</h4>

Activator treats every source as a stream of **events** — observations about the state of something, each with an object identifier, a timestamp, and the field values you're monitoring. Sources include Eventstreams (the common case), Fabric events, Azure events, business events, and even Power BI report data (a slow-moving eventstream that updates on the model's refresh schedule).

<h4>Objects</h4>

An **object** is the business entity you're monitoring — a freezer, a vehicle, a package, a bike station, an account. Activator groups incoming events by a column you choose as the object ID (for example, `bikepoint_id`), so a single rule automatically produces an independent evaluation for **each** object instance. The whole set of instances is the *population*.

<h4>Rules (stateless and stateful)</h4>

**Rules** define the condition to detect and the action to take. A **stateless** rule evaluates each event in isolation (`value < 50`). A **stateful** rule keeps memory across events per object so it can detect *changes over time* — conditions like `BECOMES`, `INCREASES`, `DECREASES`, `EXIT RANGE`, or the absence of expected data (a heartbeat). Crucially, stateful rules fire only on **entry into a new state**, not on every event that remains in that state — this state-transition behavior is what prevents alert spam when a value simply stays over a threshold.

<h4>Actions</h4>

When a rule activates, Activator can send a **Teams message** or **email**, launch a **Power Automate** flow, or trigger Fabric items directly — a **pipeline**, **notebook**, **Spark job**, **dataflow**, **User Data Function**, or **copy job** — turning detection into automated remediation or downstream processing. See [Trigger Fabric items from Activator](https://learn.microsoft.com/en-us/fabric/real-time-intelligence/data-activator/activator-trigger-fabric-items) for the full set of targets.

<h3>Designing rules that don't cry wolf</h3>

Before you activate a rule, Activator can show a **preview and impact estimate** — how often the rule *would have* fired against historical data — so you can tune thresholds and avoid over-firing. Combined with state-transition semantics and an appropriate **lookback period** (enough history to compute averages even when data arrives late), this lets you build alerting that's timely without being noisy. You only pay while rules are actively running, which keeps intermittent detection scenarios cost-efficient.

<br>

<p><img style="float: left; margin: 0px 15px 15px 0px;" src="../graphics/point1.png"><b>Activity: Detect a Condition, Trigger an Action</b></p>

<p><img style="margin: 0px 15px 15px 0px;" src="../graphics/checkmark.png"><b>Description</b></p>

You'll turn the Real-Time Dashboard from section 6.2 into an operations agent by attaching an Activator rule to a tile. When the underlying data crosses a threshold you define, Activator will automatically send you a Teams or email alert — the same mechanism you'd use in production to trigger remediation. This uses Microsoft's official Activator walkthrough so the steps stay current.

<p><img style="margin: 0px 15px 15px 0px;" src="../graphics/checkmark.png"><b>Steps</b></p>

- [ ] Follow [Create Activator alerts for a Real-Time Dashboard](https://learn.microsoft.com/en-us/fabric/real-time-intelligence/data-activator/activator-get-data-real-time-dashboard) to add an alert from a dashboard tile.
- [ ] In the **Set alert** pane, define the **condition** (for example, a value going above a threshold on your chosen object ID) and choose an **action** — start with a **Teams message** or **email** to yourself.
- [ ] Open the rule in Activator, review it against [Create Activator rules](https://learn.microsoft.com/en-us/fabric/real-time-intelligence/data-activator/activator-create-activators), and use the **Test action** / preview to confirm it fires (and to see how often it *would* fire) before activating.
- [ ] Discuss: how does the **state-transition** behavior (firing only on entry into a new state) prevent alert spam compared with a rule that fires on every event over the threshold?
- [ ] Stretch goal: change the action from a notification to triggering a **Fabric pipeline or notebook** using [Trigger Fabric items from Activator](https://learn.microsoft.com/en-us/fabric/real-time-intelligence/data-activator/activator-trigger-fabric-items), turning the alert into automated remediation.

<p style="border-bottom: 1px solid lightgrey;"></p>

<h3>Wrapping up: two agentic patterns over the same stream</h3>

In this module you built the RTI spine and then placed *two* different kinds of agent on top of it. It's worth contrasting them side by side, because choosing the right one is a design decision you'll make again and again:

| Pattern | Component | Trigger | Best for |
| --- | --- | --- | --- |
| **Automated operations agent** | Fabric **Activator** | Continuous, event-driven | Threshold alerts, automated remediation, kicking off pipelines/notebooks |
| **Conversational data agent** | Fabric **Data Agent** (NL2KQL) | On-demand, human question | Ad-hoc investigation, democratized querying of live and historical events |

Together they turn a raw stream into a system that both **acts on its own** when conditions demand it and **answers questions** when people ask — the essence of RTI's *detect → analyze → act* loop.

<p><img style="margin: 0px 15px 15px 0px;" src="../graphics/owl.png"><b>For Further Study</b></p>
<ul>
    <li><a href="https://learn.microsoft.com/en-us/fabric/real-time-intelligence/overview" target="_blank">What is Real-Time Intelligence in Microsoft Fabric?</a> (notes RTI's integration with Data Agents)</li>
    <li><a href="https://learn.microsoft.com/en-us/fabric/real-time-hub/real-time-hub-overview" target="_blank">Introduction to the Real-Time hub</a></li>
    <li><a href="https://learn.microsoft.com/en-us/fabric/real-time-intelligence/event-streams/overview" target="_blank">Fabric Eventstreams overview</a></li>
    <li><a href="https://learn.microsoft.com/en-us/fabric/real-time-intelligence/eventhouse" target="_blank">Eventhouse overview</a></li>
    <li><a href="https://learn.microsoft.com/en-us/azure/data-explorer/kusto/query/" target="_blank">Kusto Query Language (KQL) reference</a></li>
    <li><a href="https://learn.microsoft.com/en-us/fabric/data-science/concept-data-agent" target="_blank">What is a Fabric Data Agent?</a> (confirms KQL/Eventhouse as a supported source)</li>
    <li><a href="https://learn.microsoft.com/en-us/fabric/real-time-intelligence/data-activator/activator-introduction" target="_blank">What is Fabric Activator?</a></li>
    <li><a href="https://learn.microsoft.com/en-us/fabric/real-time-intelligence/anomaly-detection" target="_blank">Anomaly detection in Real-Time Intelligence</a> ⚠️ <i>Preview — requires admin enablement; treat as further study, not a graded activity.</i></li>
</ul>

<p style="border-bottom: 1px solid lightgrey;"></p>

Congratulations! You have completed this module on **RTI, Operations Agents, & Data Agents**. You now understand Fabric's Real-Time Intelligence stack end to end, and you've placed both a conversational **Data Agent** and an automated **Activator** operations agent over a live stream. When you're ready, <a href="\07 - Extending Data Agents Beyond Microsoft Fabric.md" target="_blank">proceed to the next module</a>.
