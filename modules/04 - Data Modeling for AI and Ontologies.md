![](../graphics/microsoftlogo.png)

# Workshop: Microsoft Fabric Data Agents and Beyond

#### <i>A workshop from the Tales from the Field team</i>

<p style="border-bottom: 1px solid lightgrey;"></p>

<img style="float: left; margin: 0px 15px 15px 0px;" src="../graphics/textbubble.png"> <h2>04 - Data Modeling for AI &amp; Ontologies</h2>

In this module you'll cover how to shape and describe data so agents and ontologies can reason over it reliably. The goal is not to make the model fancy. The goal is to make the business meaning obvious: entity types, properties, relationships, synonyms, approved calculations, and the bindings that connect business concepts to the physical tables underneath them.

In each section you'll get more references, which you should follow up on to learn more. Also watch for links within the text - click on each one to explore that topic.

(<a href="https://github.com/TalesFromTheField/Fabric-Data-Agents-Workshop/blob/main/modules/00%20-%20Pre-Requisites.md">Make sure you check out the <b>Pre-Requisites</b> page before you start</a>. You'll need all of the items loaded there before you can proceed with the workshop.)

If Module 02 was "build the agent" and Module 03 was "use the agent," this module is the uncomfortable but useful bit in the middle: making sure the agent has something coherent to reason over. A data agent can generate SQL, DAX, or KQL, but it still needs a model that tells it what the business actually means by customer, product, order, active account, churn risk, margin, and all the other apparently simple words people fight about in meetings.

You'll cover these topics in the module:

<dl>

  <dt><a href="#4-1">4.1 - Why AI Needs a Data Model</a></dt>
  <dt><a href="#4-2">4.2 - Entities, Properties, and Relationships</a></dt>
  <dt><a href="#4-3">4.3 - Binding Business Concepts to Physical Data</a></dt>
  <dt><a href="#4-4">4.4 - Instructions, Examples, and Evaluation</a></dt>

</dl>

<p style="border-bottom: 1px solid lightgrey;"></p>

<h2 id="4-1"><img style="float: left; margin: 0px 15px 15px 0px;" src="../graphics/pencil2.png">4.1 - Why AI Needs a Data Model</h2>

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

<p><img style="float: left; margin: 0px 15px 15px 0px;" src="../graphics/point1.png"><b>Activity: Translate business questions into modeling requirements</b></p>

<p><img style="margin: 0px 15px 15px 0px;" src="../graphics/checkmark.png"><b>Description</b></p>

Take a small set of business questions and identify what the agent would need to know before it could answer them safely and consistently.

<p><img style="margin: 0px 15px 15px 0px;" src="../graphics/checkmark.png"><b>Steps</b></p>

1. Pick five questions a business user would ask your data agent. Use real language, not table names.
2. For each question, write down the core noun: customer, order, product, region, asset, incident, employee, or another entity.
3. Write down the measures or facts needed to answer the question.
4. Mark any phrase that requires a business definition, such as active, late, high value, current quarter, at risk, or compliant.
5. Identify the source that should answer each question: lakehouse, warehouse, semantic model, KQL database, mirrored database, or ontology.
6. Save this list. You will reuse it when you define instructions, example queries, and evaluation tests.

<p style="border-bottom: 1px solid lightgrey;"></p>

<h2 id="4-2"><img style="float: left; margin: 0px 15px 15px 0px;" src="../graphics/pencil2.png">4.2 - Entities, Properties, and Relationships</h2>

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

Microsoft's ontology tutorial uses a Lakeshore Retail scenario to create entities such as stores, products, sales events, and freezer telemetry. That scenario is useful here because it shows both paths students need to understand: generating an ontology from a Power BI semantic model and building one directly from OneLake data.

<p><img style="float: left; margin: 0px 15px 15px 0px;" src="../graphics/point1.png"><b>Activity: Prepare the ontology tutorial environment</b></p>

<p><img style="margin: 0px 15px 15px 0px;" src="../graphics/checkmark.png"><b>Description</b></p>

Prepare the Microsoft Learn ontology tutorial environment so you have a real ontology scenario to examine in this module. Do not copy the Microsoft tutorial steps into this repository; use the tutorial as the hands-on lab source.

<p><img style="margin: 0px 15px 15px 0px;" src="../graphics/checkmark.png"><b>Steps</b></p>

1. Right-click and open <a href="https://learn.microsoft.com/en-us/fabric/iq/ontology/tutorial-0-introduction">Tutorial Part 0: Introduction and Environment Setup</a> in a new browser tab.
2. Follow the tutorial steps to choose either the semantic model path or the OneLake path.
3. Prepare the Lakeshore Retail sample data, lakehouse, semantic model if selected, and eventhouse items described in the tutorial.
4. When the tutorial environment is ready, write down the entity types, properties, and relationships you expect the ontology to expose.
5. Keep the tutorial tab open. Later activities in this module use the same scenario to discuss bindings, instructions, and evaluation.

<p style="border-bottom: 1px solid lightgrey;"></p>

<h2 id="4-3"><img style="float: left; margin: 0px 15px 15px 0px;" src="../graphics/pencil2.png">4.3 - Binding Business Concepts to Physical Data</h2>

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

<p><img style="float: left; margin: 0px 15px 15px 0px;" src="../graphics/point1.png"><b>Activity: Create a concept-to-source binding table</b></p>

<p><img style="margin: 0px 15px 15px 0px;" src="../graphics/checkmark.png"><b>Description</b></p>

Build the mapping table that connects business terms to the Fabric source the data agent should use.

<p><img style="margin: 0px 15px 15px 0px;" src="../graphics/checkmark.png"><b>Steps</b></p>

1. Create a table with these columns: Business concept, Definition, Source item, Physical table or model object, Key, Important properties, Relationships, Security note.
2. Fill in at least five business concepts from your ontology map.
3. For each concept, identify whether the preferred answer path is SQL, DAX, KQL, or ontology traversal.
4. Add one security note per concept: public reference data, role-filtered data, column-restricted data, or sensitive data.
5. Use the table to decide which Fabric source should be added to the data agent first.

<p style="border-bottom: 1px solid lightgrey;"></p>

<h2 id="4-4"><img style="float: left; margin: 0px 15px 15px 0px;" src="../graphics/pencil2.png">4.4 - Instructions, Examples, and Evaluation</h2>

The model is not done when the objects exist. The agent needs guidance on how to use them.

Microsoft Learn calls out two configuration levers that matter here: **data agent instructions** and **example queries**. Instructions tell the data agent how to choose sources and interpret business language. Example queries show the agent what a correct translation looks like for common questions. Evaluation gives you a repeatable way to test whether the agent is improving or just becoming more confident while being wrong, which is the worst kind of wrong.

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

<p><img style="float: left; margin: 0px 15px 15px 0px;" src="../graphics/point1.png"><b>Activity: Write instructions and a starter evaluation set</b></p>

<p><img style="margin: 0px 15px 15px 0px;" src="../graphics/checkmark.png"><b>Description</b></p>

Turn your model into practical data agent configuration by drafting instructions and evaluation questions.

<p><img style="margin: 0px 15px 15px 0px;" src="../graphics/checkmark.png"><b>Steps</b></p>

1. Open your Fabric data agent draft.
2. Add instructions that define your top ambiguous business terms.
3. Add source-routing guidance for at least three question types.
4. Add three example question/query pairs for SQL or KQL-backed sources where examples are supported.
5. Create an evaluation list with at least ten questions and expected answers.
6. Include two questions the agent should refuse, redirect, or answer with a clear limitation.
7. Run the evaluation process described in <a href="https://learn.microsoft.com/en-us/fabric/data-science/evaluate-data-agent">Evaluate your data agent</a>, or save the list for the Module 07 SDK path if your tenant is not ready yet.

<p style="border-bottom: 1px solid lightgrey;"></p>

<p><img style="margin: 0px 15px 15px 0px;" src="../graphics/owl.png"><b>For Further Study</b></p>
<ul>
  <li><a href="https://learn.microsoft.com/en-us/fabric/data-science/concept-data-agent">Fabric data agent creation - Microsoft Fabric</a></li>
  <li><a href="https://learn.microsoft.com/en-us/fabric/data-science/data-agent-end-to-end-tutorial">Fabric data agent scenario</a></li>
  <li><a href="https://learn.microsoft.com/en-us/fabric/iq/ontology/tutorial-0-introduction">Tutorial Part 0: Introduction and Environment Setup</a></li>
  <li><a href="https://learn.microsoft.com/en-us/fabric/data-science/evaluate-data-agent">Evaluate your data agent</a></li>
  <li><a href="https://learn.microsoft.com/en-us/fabric/data-science/data-agent-sharing">Fabric data agent sharing and permission management</a></li>
</ul>

Congratulations! You have completed this module on Data Modeling for AI &amp; Ontologies. You now have a practical map from business language to Fabric data sources, plus the instructions and evaluation patterns you need before moving into graph traversal and ontology-driven reasoning.
