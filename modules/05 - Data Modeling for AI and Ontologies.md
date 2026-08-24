![](../graphics/microsoftlogo.png)

# Workshop: Microsoft Fabric Data Agents and Beyond

#### <i>A workshop from the Tales from the Field team</i>

<p style="border-bottom: 1px solid lightgrey;"></p>

<img style="float: left; margin: 0px 15px 15px 0px;" src="../graphics/textbubble.png"> <h2>05 - Data Modeling for AI &amp; Ontologies</h2>

In this module you'll cover how to shape and describe data so agents and ontologies can reason over it reliably. The goal is not to make the model fancy. The goal is to make the business meaning obvious: entity types, properties, relationships, synonyms, approved calculations, and the bindings that connect business concepts to the physical tables underneath them.

In each section you'll get more references, which you should follow up on to learn more. Also watch for links within the text - click on each one to explore that topic.

(<a href="https://github.com/TalesFromTheField/Fabric-Data-Agents-Workshop/blob/main/modules/00%20-%20Pre-Requisites.md">Make sure you check out the <b>Pre-Requisites</b> page before you start</a>. You'll need all of the items loaded there before you can proceed with the workshop.)

If Module 02 was "build the agent" and Module 03 was "use the agent," this module is the uncomfortable but useful bit in the middle: making sure the agent has something coherent to reason over. A data agent can generate SQL, DAX, or KQL, but it still needs a model that tells it what the business actually means by customer, product, order, active account, churn risk, margin, and all the other apparently simple words people fight about in meetings.

You'll cover these topics in the module:

<dl>

  <dt><a href="#5-1">5.1 - Why AI Needs a Data Model</a></dt>
  <dt><a href="#5-2">5.2 - Entities, Properties, and Relationships</a></dt>
  <dt><a href="#5-3">5.3 - Binding Business Concepts to Physical Data</a></dt>
  <dt><a href="#5-4">5.4 - Instructions, Examples, and Evaluation</a></dt>

</dl>

<p style="border-bottom: 1px solid lightgrey;"></p>

<h2 id="5-1"><img style="float: left; margin: 0px 15px 15px 0px;" src="../graphics/pencil2.png">5.1 - Why AI Needs a Data Model</h2>

Natural language feels flexible because people carry context around in their heads. Agents do not. When a user asks, "Which customers are at risk?" the data agent has to translate that sentence into a scoped, read-only query against specific data sources. Without a model, it has to infer too much: which customer table, which date range, which measure, which relationships, and what "at risk" means this week.

Fabric data agents improve answers by combining selected sources with metadata, instructions, and examples. Microsoft Learn describes the supported source pattern as lakehouses, warehouses, Power BI semantic models, KQL databases, mirrored databases, and ontologies. The important workshop point is that these are not just connection types. They are different ways of matching a user question to the right level of business meaning.

Choosing the right data source is one of the most important design decisions you make for a Fabric data agent. Start with the simplest governed source that can answer the question clearly.

For most organizations, the first data agent should connect to a **lakehouse, warehouse, mirrored database, or KQL database**. These sources give the agent direct access to tables, columns, relationships, and queryable structures. They are the best starting point when users need grounded answers over well-understood operational, analytical, or event data.

Use a **Power BI semantic model** when the business logic already lives there. If a business group has invested in certified measures, relationships, hierarchies, friendly names, and row-level security, the semantic model can help the agent answer questions in the same language the business already uses. This is especially useful for questions about approved KPIs, financial metrics, or curated departmental reporting areas.

Use an **ontology** when the question is less about a single dataset and more about business concepts and relationships. Ontologies help describe entities, properties, and relationships across a business domain, so the agent can reason over concepts such as stores, products, assets, incidents, suppliers, customers, and how those things connect.

A practical way to think about this is:

| If the user needs to ask... | Start with... | Why |
| --- | --- | --- |
| Questions over tables, transactions, facts, dimensions, or curated data | Lakehouse, warehouse, or mirrored database | Direct access to structured data with clear tables, columns, and joins |
| Questions over logs, telemetry, events, or time-series patterns | KQL database | Designed for high-volume event and time-based analysis |
| Questions over approved business metrics and reporting definitions | Power BI semantic model | Reuses measures, relationships, metadata, and security already defined for the business |
| Questions over business concepts, entity relationships, dependencies, or impact paths | Ontology | Describes the business domain above the physical storage layer |

The hierarchy is not about which source is "best." It is about matching the source to the question.

Start with lakehouse, warehouse, mirrored database, or KQL when the question can be answered from the data structure itself. Move to a semantic model when the question depends on curated business logic. Move to an ontology when the question depends on business concepts and relationships that span across tables, models, or operational domains.

Also note an important configuration difference: data agent query examples and query instructions are not available for every source type in the same way. Today, SQL and KQL-backed sources give you the most direct path for adding example queries and shaping how the agent translates natural language into queries. Semantic models and ontologies bring stronger business meaning, but they do not currently support the same query-instruction pattern inside data agents. That means your design work shifts from writing query examples to making the model, metadata, definitions, and relationships as clear as possible.

Microsoft's ontology tutorial uses a Lakeshore Retail scenario to create entities such as stores, products, sales events, and freezer telemetry. Before you can talk about modeling choices, you need a working tutorial environment with the sample data loaded and the required Fabric items created.

<p><img style="float: left; margin: 0px 15px 15px 0px;" src="../graphics/point1.png"><b>Activity: Complete Tutorial Part 0 - Introduction and Environment Setup</b></p>

<p><img style="margin: 0px 15px 15px 0px;" src="../graphics/checkmark.png"><b>Description</b></p>

Prepare the Microsoft Learn ontology tutorial environment so you have a real scenario to use for the rest of this module. Do not copy the Microsoft tutorial steps into this repository; use the tutorial as the hands-on lab source.

<p><img style="margin: 0px 15px 15px 0px;" src="../graphics/checkmark.png"><b>Steps</b></p>

1. Right-click and open <a href="https://learn.microsoft.com/en-us/fabric/iq/ontology/tutorial-0-introduction">Tutorial Part 0: Introduction and Environment Setup</a> in a new browser tab.
2. Follow the tutorial steps to choose either the semantic model path or the OneLake path.
3. Prepare the Lakeshore Retail sample data, lakehouse, semantic model if selected, and eventhouse items described in the tutorial.
4. When the tutorial environment is ready, write down which Fabric items you created and which data source each one represents.
5. Keep the tutorial tab open. Section 5.2 continues with Part 1 of the same tutorial.

<p style="border-bottom: 1px solid lightgrey;"></p>

<h2 id="5-2"><img style="float: left; margin: 0px 15px 15px 0px;" src="../graphics/pencil2.png">5.2 - Entities, Properties, and Relationships</h2>

Ontologies start with the language of the business. An entity is the thing the business talks about. A property describes that thing. A relationship explains how one thing connects to another.

Think about the difference between these two descriptions:

- Table view: `SalesOrderHeader` joins to `Customer` on `CustomerKey`.
- Business view: A **Customer** places **Orders**, and each **Order** contains **Products** sold through a **Sales Territory**.

Both statements can be true. The second one is the version an agent can use when a user asks a question in natural language.

For an AI-ready model, define:

| Modeling element | Workshop meaning | Example |
| --- | --- | --- |
| **Entity type** | A business object users ask about | Customer, Product, Store, Supplier, Shipment |
| **Property** | A descriptive attribute or metric | Customer segment, product category, order date, net sales |
| **Relationship** | How entities connect | Customer places Order, Product belongs to Category |
| **Synonym** | Alternate business language | Client = Customer, SKU = Product, Region = Territory |
| **Definition** | The approved meaning of an ambiguous term | Active customer = purchased in the last 12 months |

Do not start by modeling everything. Start with the questions the agent must answer, then model the entities and relationships those questions actually need. Data models created by committee tend to become museums. Agents need maps.

The Lakeshore Retail scenario is useful here because it shows both paths students need to understand: generating an ontology from a Power BI semantic model and building one directly from OneLake data. In Part 1 of the tutorial, you create the ontology item and start turning the prepared source data into named business entities.

<p><img style="float: left; margin: 0px 15px 15px 0px;" src="../graphics/point1.png"><b>Activity: Complete Tutorial Part 1 - Create an Ontology</b></p>

<p><img style="margin: 0px 15px 15px 0px;" src="../graphics/checkmark.png"><b>Description</b></p>

Create the ontology item from the tutorial environment you prepared in section 5.1. Use the Microsoft Learn tutorial for the procedural steps, then come back here to connect the activity to the modeling concepts.

<p><img style="margin: 0px 15px 15px 0px;" src="../graphics/checkmark.png"><b>Steps</b></p>

1. Right-click and open <a href="https://learn.microsoft.com/en-us/fabric/iq/ontology/tutorial-1-create-ontology">Tutorial Part 1: Create an Ontology</a> in a new browser tab.
2. Follow the tutorial steps for the same creation method you selected in section 5.1.
3. Create the ontology item and review the generated or manually created entity types.
4. Write down the entity types, properties, and relationships you expect students to recognize from the tutorial scenario.
5. Identify any names that feel too technical and should be renamed into business language.

<p style="border-bottom: 1px solid lightgrey;"></p>

<h2 id="5-3"><img style="float: left; margin: 0px 15px 15px 0px;" src="../graphics/pencil2.png">5.3 - Binding Business Concepts to Physical Data</h2>

An ontology without bindings is a vocabulary exercise. Useful, but not enough. To help an agent answer questions, the business concepts must map back to the physical data: tables, columns, relationships, measures, and security boundaries.

This is where Fabric's source choices matter. If the source is a Power BI semantic model, many of the business relationships and measures may already exist. If the source is a lakehouse or warehouse, you may need stronger instructions and example queries because the agent sees tables and columns more directly. If the source is an ontology, the model can express business concepts and relationships that make multi-hop questions easier to reason about.

Use this pattern when binding concepts:

1. **Name the business concept.** Example: Customer.
2. **Identify the physical source.** Example: `dimcustomer` in a lakehouse or `Customer` in a semantic model.
3. **Define the key.** Example: `CustomerKey`.
4. **List the properties exposed to users.** Example: customer name, segment, geography.
5. **Map relationships.** Example: Customer to Sales through `factinternetsales`.
6. **Document security.** Example: row-level security by sales territory applies through the semantic model.

The data agent still respects the permissions of the user asking the question. Modeling does not grant access. It gives the agent a better map of what it is already allowed to query.

Parts 2 and 3 of the ontology tutorial are where this concept becomes practical. In Part 2, you enrich the ontology by adding a new *Freezer* entity type, binding static data from the lakehouse, binding time-series data from Eventhouse, and creating the relationship that connects stores to the freezers they operate. In Part 3, you inspect the resulting entity instances, relationship graphs, and graph queries to confirm the bindings are producing the business paths you expected.

<p><img style="float: left; margin: 0px 15px 15px 0px;" src="../graphics/point1.png"><b>Activity: Complete Tutorial Parts 2 and 3 - Enrich and View the Ontology</b></p>

<p><img style="margin: 0px 15px 15px 0px;" src="../graphics/checkmark.png"><b>Description</b></p>

Bind additional business concepts to physical data, then inspect the resulting instances and relationship graph so the ontology represents both relatively static business data and live operational context.

<p><img style="margin: 0px 15px 15px 0px;" src="../graphics/checkmark.png"><b>Steps</b></p>

1. Right-click and open <a href="https://learn.microsoft.com/en-us/fabric/iq/ontology/tutorial-2-enrich-ontology">Tutorial Part 2: Enrich the Ontology with Additional Data</a> in a new browser tab.
2. Follow the tutorial steps to add the *Freezer* entity type.
3. Bind the static freezer data from the lakehouse.
4. Bind the time-series freezer telemetry from Eventhouse.
5. Create the relationship type that connects *Store* to *Freezer*.
6. Right-click and open <a href="https://learn.microsoft.com/en-us/fabric/iq/ontology/tutorial-3-preview-ontology">Tutorial Part 3: View the Ontology</a> in a new browser tab.
7. Follow the tutorial steps to view entity instances, inspect time-series data, explore the relationship graph, and run graph queries.
8. When you finish, write down which business concept, source item, key, properties, relationship, and graph path were added or validated.

<p style="border-bottom: 1px solid lightgrey;"></p>

<h2 id="5-4"><img style="float: left; margin: 0px 15px 15px 0px;" src="../graphics/pencil2.png">5.4 - Agent Instructions, Example Queries, and Evaluation</h2>

The model is not done when the objects exist. After you validate the ontology, the next step is to expose it through an agent so users can ask natural-language questions against those concepts and relationships.

Two configuration levers matter here: **agent instructions** and **example queries**. Agent instructions describe how the data agent should behave, how it should interpret business language, and when it should prefer one source over another. Data source instructions add source-specific context such as table meaning, join logic, and business definitions. Example queries show the agent what a correct translation looks like for important questions.

These are not cosmetic settings. They are how you turn a generic conversational interface into an analyst that understands your domain. In the data agent setup experience, instructions can be written and formatted in Markdown, which makes them easier for authors and reviewers to maintain. Example queries let you pair a natural-language question with a validated SQL or KQL query, so the agent has a trusted pattern to learn from when similar questions arrive.

For this workshop, treat instructions and example queries as part of the model. Tables, columns, entity types, and relationships describe the data. Instructions and examples describe how the agent should use that data.

Part 4 of the ontology tutorial connects the ontology to a Fabric data agent. This is the point where the model becomes consumable: users ask questions in natural language, and the agent grounds the answer in the ontology's entity types, relationships, definitions, and bindings.

<p><a href="https://youtu.be/r18-STutAyE"><img src="https://img.youtube.com/vi/r18-STutAyE/0.jpg" height = 200></a></p>

<p><a href="https://youtu.be/v0mD01QP5gY"><img src="https://img.youtube.com/vi/v0mD01QP5gY/0.jpg" height = 200></a></p>

Useful instruction patterns:

- Route finance metrics to the semantic model when approved DAX measures exist.
- Route raw transaction exploration to the lakehouse or warehouse.
- Route event and telemetry questions to KQL sources.
- Prefer ontology concepts when the question asks about relationships, dependencies, ownership, lineage, or impact.
- Refuse or redirect questions that ask for data outside the selected sources.

Useful evaluation patterns:

- Test business definitions, not just raw counts.
- Include synonyms and messy phrasing.
- Include questions the agent should not answer.
- Include permission-sensitive cases if your environment has RLS or CLS.
- Re-run the same set after every modeling or instruction change.

<p><img style="float: left; margin: 0px 15px 15px 0px;" src="../graphics/point1.png"><b>Activity: Complete Tutorial Part 4 - Consume Ontology from Agents</b></p>

<p><img style="margin: 0px 15px 15px 0px;" src="../graphics/checkmark.png"><b>Description</b></p>

Create a Fabric data agent that uses the ontology as a source, then test whether natural-language questions return answers grounded in business entities and relationships instead of raw table structure.

<p><img style="margin: 0px 15px 15px 0px;" src="../graphics/checkmark.png"><b>Steps</b></p>

1. Right-click and open <a href="https://learn.microsoft.com/en-us/fabric/iq/ontology/tutorial-4-create-data-agent">Tutorial Part 4: Consume Ontology from Agents</a> in a new browser tab.
2. Follow the tutorial steps to create a data agent and add the ontology as its source.
3. Add the tutorial's recommended agent instruction when prompted.
4. Watch <a href="https://youtu.be/r18-STutAyE">Microsoft Fabric: Data Agents Agent Instructions</a> and note how agent instructions, data source instructions, and example queries are organized in the setup experience.
5. Watch <a href="https://youtu.be/v0mD01QP5gY">Microsoft Fabric: How to use Data Agent Example Queries</a> and note why a validated query pattern can change the answer the agent returns.
6. Ask the tutorial's natural-language questions and observe whether the answers reference ontology entities and relationships.
7. Write three additional natural-language questions a business user would ask this ontology-backed agent.
8. Write three questions that should still route to a lakehouse, warehouse, semantic model, or KQL database instead.
9. Save those questions for your evaluation set and source-routing notes.

<p style="border-bottom: 1px solid lightgrey;"></p>

<p><img style="margin: 0px 15px 15px 0px;" src="../graphics/owl.png"><b>For Further Study</b></p>
<ul>
  <li><a href="https://learn.microsoft.com/en-us/fabric/data-science/concept-data-agent">Fabric data agent creation - Microsoft Fabric</a></li>
  <li><a href="https://learn.microsoft.com/en-us/fabric/data-science/data-agent-end-to-end-tutorial">Fabric data agent scenario</a></li>
  <li><a href="https://learn.microsoft.com/en-us/fabric/iq/ontology/tutorial-0-introduction">Tutorial Part 0: Introduction and Environment Setup</a></li>
  <li><a href="https://learn.microsoft.com/en-us/fabric/iq/ontology/tutorial-1-create-ontology">Tutorial Part 1: Create an Ontology</a></li>
  <li><a href="https://learn.microsoft.com/en-us/fabric/iq/ontology/tutorial-2-enrich-ontology">Tutorial Part 2: Enrich the Ontology with Additional Data</a></li>
  <li><a href="https://learn.microsoft.com/en-us/fabric/iq/ontology/tutorial-3-preview-ontology">Tutorial Part 3: View the Ontology</a></li>
  <li><a href="https://learn.microsoft.com/en-us/fabric/iq/ontology/tutorial-4-create-data-agent">Tutorial Part 4: Consume Ontology from Agents</a></li>
  <li><a href="https://learn.microsoft.com/en-us/fabric/data-science/evaluate-data-agent">Evaluate your data agent</a></li>
  <li><a href="https://learn.microsoft.com/en-us/fabric/data-science/data-agent-sharing">Fabric data agent sharing and permission management</a></li>
  <li><a href="https://youtu.be/r18-STutAyE">Microsoft Fabric: Data Agents Agent Instructions</a></li>
  <li><a href="https://youtu.be/v0mD01QP5gY">Microsoft Fabric: How to use Data Agent Example Queries</a></li>
</ul>

Congratulations! You have completed this module on Data Modeling for AI &amp; Ontologies. You now have a practical map from business language to Fabric data sources, plus the instructions and evaluation patterns you need to build on the graph and ontology concepts introduced earlier in the workshop.
