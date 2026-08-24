![](../graphics/microsoftlogo.png)

# Workshop: Microsoft Fabric Data Agents and Beyond

#### <i>A workshop from the Tales from the Field team</i>

<p style="border-bottom: 1px solid lightgrey;"></p>

<img style="float: left; margin: 0px 15px 15px 0px;" src="../graphics/textbubble.png"> <h2>RTI, Operations Agents, & Data Agents</h2>

Real-time data changes how agents operate. Every module before this one has worked with data *at rest* — tables in a lakehouse or warehouse that you load on a schedule and query after the fact. This module is about data *in motion*: telemetry, logs, IoT signals, application events, and business events that arrive continuously and lose most of their value if they sit in a queue waiting for the next nightly batch. Microsoft Fabric's **Real-Time Intelligence (RTI)** workload is built end to end for exactly this kind of data, and it is the foundation that makes real-time agentic scenarios possible.

You'll walk RTI's core loop — **discover → ingest → store → query → visualize → act** — and then place two very different kinds of agent on top of it:

* a **Fabric Data Agent** wired directly over a live KQL database, so people can ask natural-language questions about events *as they happen*; and
* a **Fabric Activator** rule that behaves as an **operations agent** — autonomously watching the stream and firing an action the instant a condition is met, with no human in the loop.

By the end you'll understand how RTI's *detect → analyze → act* pattern, combined with Data Agents, replaces brittle scheduled jobs with event-driven, conversational, and agentic intelligence — and, just as importantly, when to reach for each tool.

> **A note on terminology:** "operations agent" is an editorial framing we use in this workshop. The built-in Fabric construct that autonomously monitors data and takes action is **Activator**. Everywhere this module says "operations agent," map it to Activator.

The four sections build on each other deliberately — the resources you create in 6.1 are the same ones you query in 6.2, converse with in 6.3, and automate in 6.4 — so it's best to work through them in order. In each section you'll get more references, which you should follow up on to learn more. Also watch for links within the text — click on each one to explore that topic.

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

[Real-Time Intelligence](https://learn.microsoft.com/en-us/fabric/real-time-intelligence/overview) is a fully managed, end-to-end SaaS experience in Microsoft Fabric for analyzing data in motion. It empowers everyone in your organization to extract insights and visualize streaming data, whether you're dealing with gigabytes or petabytes. All of your organization's data in motion converges in the **Real-Time hub**, connects through **no-code connectors**, and becomes available for immediate visual insights, geospatial analysis, and trigger-based reactions — all as part of an organization-wide catalog. Critically, even though it's called "real-time," your data doesn't have to arrive at high rates and volumes: RTI simply gives you solutions that react to events *as they happen* rather than solutions that run on a schedule.

It's worth situating RTI against a service you may already know. The engine underneath RTI is **Kusto** — the very same core engine as **Azure Data Explorer (ADX)**. The difference is the operating model: ADX is a **PaaS** service in Azure that you provision and manage, while RTI delivers that same engine as a **SaaS** experience fully integrated with the rest of Fabric — OneLake, Power BI, notebooks, pipelines, and the Data Agents you'll build later in this module. Same query power; far less to manage.

<p><img style="height: 400px; box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.19);" src="https://learn.microsoft.com/en-us/fabric/real-time-intelligence/media/overview/overview-schematic.png"></p>

<h3>Is Real-Time Intelligence the right tool?</h3>

RTI is the right choice whenever your questions have a *time* dimension and freshness matters. Reach for it when any of these describe your workload:

* You need **high freshness** — the gap between an event occurring and being queryable should be seconds, not hours.
* You want to **transform streaming data** on the way in, or route it to different places based on its content.
* A downstream service needs **low query latency** (results in seconds) over large volumes.
* Your data comes in **mixed shapes** — structured, semi-structured (JSON, arrays), or unstructured free text.
* Your data has a **time component** that benefits from a time-series-optimized store, and you want ad-hoc queries on any field without pre-optimizing.

Those characteristics show up across a wide range of industries and scenarios — **automotive, manufacturing, IoT, smart cities and buildings, transportation and logistics, finance and fraud detection, and business operations management**, to name a few. Increasingly, RTI also underpins **AI and agentic scenarios** such as real-time content-safety monitoring and telemetry for generative apps, where safety signals and conversation events are streamed and analyzed for immediate action.

Before you build anything, it helps to hold a clear mental model of the three core building blocks and how event data flows through them: you **discover** a stream in the Real-Time hub, **ingest and shape** it with an Eventstream, and **store and query** it in an Eventhouse.

<h3>Real-Time hub — the catalog of streams</h3>

The [Real-Time hub](https://learn.microsoft.com/en-us/fabric/real-time-hub/real-time-hub-overview) is the single, tenant-wide place where every stream in your organization is discoverable. It is to streaming data what the OneLake catalog is to data at rest: a centralized catalog that lets you find, add, explore, and share streams across domains, so that streaming data becomes *accessible to everyone* rather than trapped in disconnected, one-off pipelines. The hub organizes data in motion into a few categories:

* **Data streams** — every stream actively running in Fabric that you have access to.
* **Microsoft sources** — streaming sources you can discover and quickly configure for ingestion, including **Change Data Capture (CDC)** sources that track and stream row-level changes from databases in real time: Azure Event Hubs, Azure IoT Hub, Azure SQL DB CDC, Azure Cosmos DB CDC, and PostgreSQL CDC.
* **Fabric events** — event-driven notifications for **Fabric workspace item events**, **OneLake events**, **Fabric job events**, and **Azure Blob Storage events**. These can trigger downstream actions or workflows — invoking a pipeline, sending a notification, or (as you'll see in 6.4) firing an Activator rule — enabling fully event-driven orchestration with no schedules.

<h3>Eventstreams — ingest, transform, and route (no-code)</h3>

An [Eventstream](https://learn.microsoft.com/en-us/fabric/real-time-intelligence/event-streams/overview) is the pipeline that captures, transforms, and routes real-time events to their destinations — all on a no-code, drag-and-drop canvas. Because the whole flow is drawn as a diagram, an Eventstream doubles as living documentation of exactly how your event data moves and changes, and Fabric manages the scalable infrastructure underneath it for you.

**Sources** go well beyond Fabric's built-in sample data. Eventstreams ship with connectors for **Azure Event Hubs**, **Azure IoT Hub**, **Apache Kafka**, database **CDC** feeds, **Amazon Kinesis**, **Google Cloud Pub/Sub**, **MQTT**, a **Real-Time Weather** connector, and a **Custom App** endpoint you can push your own application telemetry to.

Between source and destination you can drop in an **event processor** — a set of no-code transformations that reshape events on the way through:

| Transformation | What it does |
| --- | --- |
| **Filter** | Keep only events that match a condition on a field. |
| **Manage fields** | Add, remove, rename, or change the data type of fields. |
| **Aggregate** | Calculate a running sum / min / max / average as each event arrives. |
| **Group by** | Aggregate across all events within a defined time window. |
| **Union** | Merge two or more streams that share fields into one. |
| **Expand** | Emit a new row for each value in an array. |
| **Join** | Combine two streams on a matching condition. |

You can also route events to different destinations based on their content, and publish a **derived stream** — a new, transformed stream that other people can pick up from the Real-Time hub. **Destinations** include an **Eventhouse (KQL database)**, a **Lakehouse**, a **Custom App**, a derived stream, or **Activator** for immediate alerting.

<h3>Eventhouse — the time-indexed store (KQL database)</h3>

An [Eventhouse](https://learn.microsoft.com/en-us/fabric/real-time-intelligence/eventhouse) is the storage and analytics engine at the end of the pipeline, purpose-built for streaming and time-series data. Incoming data is **automatically organized by the time it arrived**, so you can run fast, detailed queries even over enormous volumes, and the data stored in an Eventhouse can be made available in **OneLake** as one logical copy for other Fabric experiences — notebooks, Power BI, and Data Agents — to consume without moving it. An Eventhouse even includes native **anomaly detection** that runs *in place* against live time-series data, complementing the dashboards and KQL analytics you'll build in 6.2.

<h4>The Kusto engine and the KQL database</h4>

An Eventhouse is a *workspace of databases*: it can host multiple **KQL databases** that share capacity, monitoring, and management. A useful analogy from the on-premises world — the **Eventhouse** is like a SQL Server *instance*, and each **KQL database** inside it is like a *database* on that server. The Kusto engine uses a familiar **relational model**: data lives in **tables** with strongly-typed schemas, tables live in databases, and a single engine can manage many databases. Each database carries its own permissions under Role-Based Access Control (RBAC). That combination — relational structure, strong typing, and enterprise-grade security — makes the engine ideal for log analytics, time-series analytics, IoT, and general-purpose exploratory analytics.

<h4>Velocity, Variety, and Volume</h4>

What sets the engine apart is its handling of the "three Vs" of streaming data. **Velocity:** it ingests millions of events per second at low latency and returns query results in milliseconds to seconds. **Variety:** it happily stores structured, semi-structured (JSON and nested arrays), and unstructured free text side by side. **Volume:** you can ingest terabytes in minutes and query petabytes, because data is automatically indexed and partitioned by ingestion time. To keep costs sensible, an Eventhouse can **suspend** itself when idle and reactivate on demand (with a few seconds of latency); if you can't tolerate that latency, a **Minimum consumption** setting keeps it always warm at a compute level you choose.

Put together, the flow is simple to hold in your head: **Real-Time hub** (discover the stream) → **Eventstream** (ingest, transform, route) → **Eventhouse / KQL database** (store and query). Everything else in this module — querying, dashboards, Data Agents, and Activator — builds on top of that spine. Let's stand it up now, and then in 6.2 we'll start asking questions of the data flowing through it.

<br>

<p><img style="float: left; margin: 0px 15px 15px 0px;" src="../graphics/point1.png"><b>Activity: Your First Streaming Pipeline</b></p>

<p><img style="margin: 0px 15px 15px 0px;" src="../graphics/checkmark.png"><b>Description</b></p>

In this activity you'll stand up the RTI spine end to end using Microsoft's official Real-Time Intelligence tutorial. You'll create an Eventhouse, then use the Real-Time hub to bring a built-in sample stream into an Eventstream and land it in your KQL database — proving that live rows are flowing before you do anything else with them. This is the reusable Microsoft Learn tutorial, so the steps stay current with the product, and the resources you create here are reused in every following section.

<p><img style="margin: 0px 15px 15px 0px;" src="../graphics/checkmark.png"><b>Steps</b></p>

- [ ] Open the [Real-Time Intelligence tutorial - Introduction](https://learn.microsoft.com/en-us/fabric/real-time-intelligence/tutorial-introduction) and review the scenario and prerequisites.
- [ ] Complete [Part 1 - Set up resources](https://learn.microsoft.com/en-us/fabric/real-time-intelligence/tutorial-1-resources) to create your Eventhouse and KQL database.
- [ ] Complete [Part 2 - Get real-time events](https://learn.microsoft.com/en-us/fabric/real-time-intelligence/tutorial-2-get-real-time-events) to connect the sample source through the Real-Time hub into an Eventstream and route it to your Eventhouse.
- [ ] In a KQL queryset, confirm live data is landing by running a quick check against your table: `<YourTableName> | take 10` — then re-run it and watch the row values change as new events arrive.
- [ ] Keep these resources — you'll build directly on this Eventhouse in sections 6.2, 6.3, and 6.4.

<p style="border-bottom: 1px solid lightgrey;"></p>

<h2 id="6.2"><img style="float: left; margin: 0px 15px 15px 0px;" src="../graphics/pencil2.png">6.2 Analyzing Streams: KQL Querysets & Real-Time Dashboards</h2>

Your pipeline from 6.1 is now landing live rows in the Eventhouse. Storing events is only useful if you can *ask questions* of them — first interactively, to explore and validate, and then continuously, on a dashboard that never stops refreshing. This section covers both, and introduces the language that powers everything: KQL.

<h3>The Kusto Query Language (KQL)</h3>

Real-Time Intelligence queries data with the [Kusto Query Language (KQL)](https://learn.microsoft.com/en-us/azure/data-explorer/kusto/query/) — an open-source language, originally invented by the Kusto engine team, and designed specifically for structured, semi-structured, and unstructured time-series data. KQL is **read-only** (it queries data, it doesn't change it), and it reads top-to-bottom as a **pipeline of operators** joined by the pipe (`|`) character. Each operator takes the table produced by the previous step and passes its result to the next, which makes log and time-series exploration remarkably concise. If you come from a SQL background, RTI also supports many **T-SQL** functions, and you can mix them into the KQL queryset.

A first query against your streaming table might look like this — filter to a time window, aggregate, and sort:

```kusto
BikepointStatus
| where Timestamp > ago(15m)          // only the last 15 minutes of events
| summarize AvailableBikes = avg(No_Bikes) by Neighbourhood
| order by AvailableBikes asc          // scarcest neighbourhoods first
```

Read it aloud and it almost narrates itself: *take the table, keep the last 15 minutes, average the available bikes per neighbourhood, and sort ascending.* That readability — plus operators for windowing, time-series, and even inline visualization with `render` — is why KQL is the lingua franca of everything in this module. (Adjust the table and column names to match the table you created in 6.1.)

<h3>KQL Querysets</h3>

A [KQL queryset](https://learn.microsoft.com/en-us/fabric/real-time-intelligence/create-query-set) is the item you use to run, view, and customize queries against a KQL database. It's your interactive workbench. Each **tab** in a queryset can point at a *different* KQL database, so you can save queries for later, share them with colleagues, export results, and even **generate a Power BI report** straight from a query. Because you can re-point a tab at another database, the same query can be run against data in different states — handy for comparing environments or before/after windows.

<h4>Copilot and natural language to KQL (NL2KQL)</h4>

If KQL is new to your attendees, Fabric includes **Copilot for Real-Time Intelligence**, which translates plain-English questions into KQL — a capability called **NL2KQL**. A user can type *"how many trips started at each station in the last hour?"* and Copilot drafts the KQL for them to review, run, and refine. This lowers the barrier to entry dramatically, and it's a natural stepping stone to the *fully* conversational Data Agent you'll build in section 6.3 — the difference being that Copilot helps you *author a query*, while a Data Agent answers the *question* directly and can reason across several sources at once.

<p><img style="height: 400px;" src="https://learn.microsoft.com/en-us/azure/data-explorer/media/data-explorer-overview/workflow.png"></p>

<h3>Real-Time Dashboards</h3>

Interactive queries are perfect for exploration, but nobody wants to re-run a query by hand every thirty seconds. A [Real-Time Dashboard](https://learn.microsoft.com/en-us/fabric/real-time-intelligence/dashboard-real-time-create) is a collection of **tiles**, optionally organized into **pages**, where each tile is backed by a KQL query and rendered as a visual. You author a query in your queryset and **export it directly to a tile**, or build the tile in place. When editing a dashboard, the **Home** tab lets you add visuals, markdown boxes, alerts, data sources, and parameters, while the **Manage** tab is where you configure **parameters**, **base queries**, the **refresh setting**, and data sources. Two features make these dashboards feel genuinely "real-time":

* **Live (auto-)refresh** — set an interval (say, 30 seconds) and every tile silently re-runs its query, so the board always reflects the latest events with no one clicking refresh.
* **Copilot tile authoring (preview)** — describe the visual you want in natural language and Copilot generates the tile's KQL and chart, so non-experts can build visuals independently. You can switch between Copilot and hand-written KQL at any time.

Real-Time Dashboards are **distinct from Power BI dashboards**. They're tuned for high-volume, low-latency KQL data and offer better query and visualization performance for streaming scenarios, whereas Power BI remains the right tool for governed, semantic-model-driven business reporting. Both have their place — and, as you'll see in 6.4, *both* can have Activator alerts built on top of them. For now, note the limitation this exposes: a dashboard shows the data, but a human still has to *look* at it. That leads to the two questions the rest of the module answers — *what if anyone could just ask the data in plain language?* (6.3) and *what if the system watched the data for us and acted on its own?* (6.4).

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

In 6.2 you saw two ways to get answers from a stream: write KQL yourself, or have Copilot draft it for you. Both still assume the person at the keyboard is building a query and reading a result. This section removes that assumption. A **Fabric Data Agent** lets *anyone* — with no KQL, SQL, or DAX — hold a conversation with the data and get precise, context-rich answers.

You already know from Modules 02–03 what a [Fabric Data Agent](https://learn.microsoft.com/en-us/fabric/data-science/concept-data-agent) is: a generally available Fabric feature that builds conversational, natural-language Q&A systems over governed data in OneLake using generative AI. What's new *here* is pointing that same capability at **live, streaming data** in your Eventhouse.

<h3>What a Data Agent connects to</h3>

A single Data Agent can span **up to five data sources, in any combination** — lakehouses, warehouses, Power BI semantic models, **KQL databases**, ontologies, and Microsoft Graph. You might configure five semantic models, or a mix of two semantic models, a lakehouse, and a KQL database. **Eventhouse KQL databases are supported as a source**, which is what makes conversational analytics over a live stream possible. Configuring an agent feels a lot like building a Power BI report: you design and refine it until it meets your needs, then publish and share it so colleagues can interact with the data.

<h3>NL2KQL over Eventhouse — querying events in place</h3>

When you add a **KQL database** as a source, the Data Agent uses **natural language to KQL (NL2KQL)** to translate a question into a Kusto query. Crucially, this works against Eventhouse KQL databases for **both live and historical** event and time-series data — standard KQL time filters and time-series patterns are supported — and the agent queries the Eventhouse **in place, with no data movement**. That makes the Data Agent the *on-demand, conversational* complement to the *automated, event-driven* Activator path you'll build in 6.4: when a human wants to investigate the stream — *"which stations ran dry in the last hour, and how does that compare to yesterday?"* — they ask the Data Agent; when a condition should trigger action without anyone asking, Activator handles it.

<h3>How it works, and how it stays governed</h3>

Under the hood the Data Agent uses large language models (via the **Azure OpenAI Assistant API**) to parse the question, identify the most relevant source among those you configured, generate and validate a query, execute it, and format the result into a human-readable answer. Two properties make this safe for enterprise use. First, every interaction is **read-only**. Second, each query runs under the **requesting user's own credentials and permissions**, so an agent can never surface data the user isn't authorized to see. It respects Microsoft **Purview** governance — including Data Loss Prevention and access-restriction policies — so conversational access doesn't become a governance backdoor.

<h3>Making it accurate — instructions and examples</h3>

Out of the box an agent is capable; with a little context it becomes genuinely reliable. You improve accuracy in three ways:

* **Choose the relevant tables.** After adding a source, pick the specific tables the agent should use. For a high-volume Eventhouse, expose only the tables that matter for typical questions.
* **Add data-agent instructions.** Give the agent routing rules and organizational definitions — for example, send **financial-metric** questions to a semantic model, **raw-data exploration** to the lakehouse, and **log-analysis** questions to the KQL database.
* **Provide example question/query pairs.** A few worked examples teach the agent your schema and phrasing, sharpening the KQL it generates.

A practical tip for streaming sources: encourage users to include **time filters** in their questions ("in the last hour," "since 9am"), which keeps queries against large event tables fast and inexpensive.

<h3>Choosing the right tool</h3>

By now you've seen four ways to get value from the same stream, and part of designing a good solution is picking the right one:

* **KQL queryset** — you write precise queries; best for power users and deep, exploratory analysis.
* **Copilot NL2KQL** — Copilot drafts a query *for you to run*; best when you want a query but aren't fluent in KQL.
* **Data Agent** — you have a *conversation* and get an answer; best for democratized, ad-hoc questions across one or more sources, live or historical.
* **Activator** (next section) — no one asks at all; the system watches and acts. Best for continuous monitoring and automated response.

<h3>Environment requirements — read this before you demo</h3>

A Data Agent has real capacity and tenant requirements, and it will fail *quietly* if they aren't met. You need a **paid F2 (or higher) Fabric capacity** — or a Power BI Premium P1+ capacity with Fabric enabled — **and** the **cross-geo processing and cross-geo storing for AI** tenant settings enabled. On a trial or F1 capacity the Data Agent experience will not work as expected, so confirm these settings before relying on it in front of an audience.

<br>

<p><img style="float: left; margin: 0px 15px 15px 0px;" src="../graphics/point1.png"><b>Activity: Ask Your Stream</b></p>

<p><img style="margin: 0px 15px 15px 0px;" src="../graphics/checkmark.png"><b>Description</b></p>

> ⚠️ **Flagged for the workshop maintainer — activity to be authored.** At the time this module was written, Microsoft Learn does **not** publish a reusable, hands-on tutorial that builds a Fabric Data Agent over a **live Eventhouse / KQL database** source. The published Data Agent end-to-end tutorial uses the **AdventureWorks** dataset in a *lakehouse* (data at rest), not a streaming KQL source, so it does not match this section's topic. In keeping with this workshop's rule — *reuse a Microsoft Learn activity, or flag it rather than inventing one* — no step-by-step activity is provided here yet. The conceptual content above is complete and can be taught as-is; the hands-on activity below is a placeholder for you to author (or to approve building from the reference docs listed).

<p><img style="margin: 0px 15px 15px 0px;" src="../graphics/checkmark.png"><b>Steps</b></p>

- [ ] Author "Ask Your Stream" — build a Data Agent on the KQL database created in section 6.1, ask natural-language questions about the live events, and inspect the generated KQL. Reference material to build from:
    - [Create a Fabric data agent](https://learn.microsoft.com/en-us/fabric/data-science/how-to-create-data-agent) (how-to)
    - [Add and configure data sources in a Fabric data agent](https://learn.microsoft.com/en-us/fabric/data-science/data-agent-add-datasources) (confirms KQL database as a source)
    - [Fabric data agent concepts](https://learn.microsoft.com/en-us/fabric/data-science/concept-data-agent) (NL2KQL over Eventhouse, governance, prerequisites)
- [ ] Confirm the F2+ capacity and cross-geo AI tenant settings are in place before finalizing the activity, since the experience depends on them.

<p style="border-bottom: 1px solid lightgrey;"></p>

<h2 id="6.4"><img style="float: left; margin: 0px 15px 15px 0px;" src="../graphics/pencil2.png">6.4 Operations Agents: Activator rules for automated action</h2>

The Data Agent in 6.3 answers when a human asks. But the most valuable real-time scenarios often need something to watch the stream *continuously* and act *without* anyone in the loop — the freezer that's warming up at 2 a.m., the payment pattern that looks like fraud, the fleet vehicle that's gone off-route. This is the **operations agent** pattern, and in Fabric it's delivered by [Fabric Activator](https://learn.microsoft.com/en-us/fabric/real-time-intelligence/data-activator/activator-introduction).

Activator is a **no-code event-detection engine** that turns data streams into automated actions. It continuously monitors sources with low latency and, when a threshold is crossed or a pattern appears, automatically triggers an action. The promise is that business users can build a **"digital nervous system"** for their data: they describe a business condition in a no-code experience and wire it to an action — no custom monitoring service, and far less reliance on internal IT or developer teams. That self-service model is what lets alerting scale across an organization.

<h3>The core concepts</h3>

Activator organizes everything around a small set of ideas. Understanding them is most of the battle.

<h4>Events</h4>

Activator treats every source as a stream of **events** — observations about the state of something, each with an object identifier, a timestamp, and the field values you're monitoring. Sources include Eventstreams (the common case), Fabric events, Azure events, business events, and even **Power BI report data** (a slow-moving eventstream that updates on the semantic model's refresh schedule).

<h4>Objects</h4>

An **object** is the business entity you're monitoring — a freezer, a vehicle, a package, a bike station, an advertising campaign, an account. Activator groups incoming events by a column you choose as the **object ID** (for example, `bikepoint_id`), so a single rule automatically produces an *independent* evaluation for **each** object instance. The whole set of instances is called the **population**. This is the feature that lets one rule scale to thousands of freezers or stations without you defining a rule per device.

<h4>Rules (stateless and stateful)</h4>

**Rules** define the condition to detect and the action to take. A **stateless** rule evaluates each event in isolation (`temperature > 40`). A **stateful** rule keeps memory across events per object, so it can detect *changes over time* — conditions like `BECOMES`, `INCREASES`, `DECREASES`, `EXIT RANGE`, or the *absence* of expected data (a missed heartbeat). Crucially, stateful rules fire only on **entry into a new state**, not on every event that stays in that state. That state-transition behavior is what prevents alert spam when a value simply sits above a threshold for an hour.

<h4>Properties</h4>

**Properties** are reusable pieces of logic you define once on an object and use across many rules. You might define a property on a *Freezer* object that smooths temperature over a one-hour window, then reference that smoothed value in several different triggers. Properties keep your rules consistent and dry.

<h4>Actions</h4>

When a rule activates, Activator can send a **Teams message** or **email**, launch a **Power Automate** flow, or trigger Fabric items directly — a **pipeline**, **notebook**, **Spark job**, **dataflow**, **User Data Function**, or **copy job** — turning detection into automated remediation or downstream processing. See [Trigger Fabric items from Activator](https://learn.microsoft.com/en-us/fabric/real-time-intelligence/data-activator/activator-trigger-fabric-items) for the full set of targets.

<h3>What can trigger a rule</h3>

The condition itself can be as simple or as rich as you need: a **static threshold** (value over a limit), a **pattern over time** (the same event happening repeatedly within a window), or the **result of a KQL query**, which lets you express arbitrarily complex logic. Activator also integrates with the **Power BI service**, so it can notify users when a specified condition appears in a published report — for instance, when a new row shows up in a table visual.

<h3>Designing rules that don't cry wolf</h3>

Before you activate a rule, Activator can show a **preview and impact estimate** — how often the rule *would have* fired against historical data — so you can tune thresholds before anyone gets paged. Combine that with state-transition semantics and an appropriate **lookback period** (enough history to compute averages even when data arrives a little late), and you get alerting that's timely without being noisy. And because you only pay while rules are actively running, intermittent detection scenarios stay cost-efficient.

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

In this module you built the RTI spine — hub, Eventstream, Eventhouse — learned to query and visualize it with KQL and Real-Time Dashboards, and then placed *two* different kinds of agent on top of it. It's worth contrasting them side by side, because choosing the right one is a design decision you'll make again and again:

| Pattern | Component | Trigger | Best for |
| --- | --- | --- | --- |
| **Automated operations agent** | Fabric **Activator** | Continuous, event-driven | Threshold alerts, automated remediation, kicking off pipelines/notebooks |
| **Conversational data agent** | Fabric **Data Agent** (NL2KQL) | On-demand, human question | Ad-hoc investigation, democratized querying of live and historical events |

They're complementary, not competing. Together they turn a raw stream into a system that both **acts on its own** when conditions demand it and **answers questions** when people ask — the essence of RTI's *detect → analyze → act* loop, and the foundation the next module builds on when it extends Data Agents beyond Fabric.

<p><img style="margin: 0px 15px 15px 0px;" src="../graphics/owl.png"><b>For Further Study</b></p>
<ul>
    <li><a href="https://learn.microsoft.com/en-us/fabric/real-time-intelligence/overview" target="_blank">What is Real-Time Intelligence in Microsoft Fabric?</a> (notes RTI's integration with Data Agents)</li>
    <li><a href="https://learn.microsoft.com/en-us/fabric/real-time-hub/real-time-hub-overview" target="_blank">Introduction to the Real-Time hub</a></li>
    <li><a href="https://learn.microsoft.com/en-us/fabric/real-time-intelligence/event-streams/overview" target="_blank">Fabric Eventstreams overview</a> (sources, transformations, and destinations)</li>
    <li><a href="https://learn.microsoft.com/en-us/fabric/real-time-intelligence/eventhouse" target="_blank">Eventhouse overview</a></li>
    <li><a href="https://learn.microsoft.com/en-us/azure/data-explorer/kusto/query/" target="_blank">Kusto Query Language (KQL) reference</a></li>
    <li><a href="https://learn.microsoft.com/en-us/fabric/real-time-intelligence/dashboard-real-time-create" target="_blank">Create a Real-Time Dashboard</a></li>
    <li><a href="https://learn.microsoft.com/en-us/fabric/data-science/concept-data-agent" target="_blank">What is a Fabric Data Agent?</a> (confirms KQL/Eventhouse as a supported source)</li>
    <li><a href="https://learn.microsoft.com/en-us/fabric/real-time-intelligence/data-activator/activator-introduction" target="_blank">What is Fabric Activator?</a></li>
    <li><a href="https://learn.microsoft.com/en-us/fabric/real-time-intelligence/data-activator/activator-trigger-fabric-items" target="_blank">Trigger Fabric items from Activator</a></li>
    <li><a href="https://learn.microsoft.com/en-us/fabric/real-time-intelligence/anomaly-detection" target="_blank">Native anomaly detection in Real-Time Intelligence</a></li>
    <li><a href="https://learn.microsoft.com/en-us/fabric/real-time-intelligence/realtime-intelligence-compare" target="_blank">Comparing Real-Time Intelligence with comparable Azure solutions</a></li>
</ul>

<p style="border-bottom: 1px solid lightgrey;"></p>

Congratulations! You have completed this module on **RTI, Operations Agents, & Data Agents**. You now understand Fabric's Real-Time Intelligence stack end to end — the hub, Eventstream, and Eventhouse spine; querying and visualizing with KQL and Real-Time Dashboards — and you've placed both a conversational **Data Agent** and an automated **Activator** operations agent over a live stream. When you're ready, <a href="\07 - Extending Data Agents Beyond Microsoft Fabric.md" target="_blank">proceed to the next module</a>.
