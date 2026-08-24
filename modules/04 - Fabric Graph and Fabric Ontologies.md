![](../graphics/microsoftlogo.png)

# Workshop: Microsoft Fabric Data Agents and Beyond

#### <i>A workshop from the Tales from the Field team</i>

<p style="border-bottom: 1px solid lightgrey;"></p>

<img style="float: left; margin: 0px 15px 15px 0px;" src="../graphics/textbubble.png"> <h2>04 - Fabric Graph &amp; Fabric Ontologies</h2>

In this module you'll cover how Fabric Graph and Fabric ontologies work together to reason across connected business information. The focus is relationship traversal: finding dependency chains, ownership paths, upstream and downstream impact, and the "how did we get here?" questions that are awkward to answer from one table at a time.

In each section you'll get more references, which you should follow up on to learn more. Also watch for links within the text - click on each one to explore that topic.

(<a href="https://github.com/TalesFromTheField/Fabric-Data-Agents-Workshop/blob/main/modules/00%20-%20Pre-Requisites.md">Make sure you check out the <b>Pre-Requisites</b> page before you start</a>. You'll need all of the items loaded there before you can proceed with the workshop.)

Relational models are excellent at storing facts. Graphs are excellent at explaining how things are connected. Ontologies are excellent at naming those things in a way the business recognizes. Put the three together and a data agent has a much better chance of answering questions that require more than a single lookup.

This module starts with Graph because Graph explains the foundation. Fabric IQ is not a single item you create in a workspace. It is a collection of capabilities - Graph, ontologies, data agents, operations agents, semantic models, digital twin builder, and planning experiences - that work together to provide business context. Graph is the easiest way to see the mechanics: nodes represent things, edges represent relationships, and queries traverse those relationships.

But that does not mean every team should start by building raw graphs. For most business-facing scenarios, the preferred abstraction is an ontology. An ontology is built on graph concepts, but it adds the business vocabulary, properties, relationships, bindings, and semantic meaning that people and agents need. In other words: learn Graph so you understand what is happening underneath; use Ontology when you want the business to reason over it.

You'll cover these topics in the module:

<dl>

  <dt><a href="#4-1">4.1 - Why Connected Data Changes the Question</a></dt>
  <dt><a href="#4-2">4.2 - Nodes, Edges, and Business Relationships</a></dt>
  <dt><a href="#4-3">4.3 - Fabric Ontologies as an Agent Source</a></dt>
  <dt><a href="#4-4">4.4 - Multi-Hop Reasoning, Dependency, and Impact Analysis</a></dt>

</dl>

<p style="border-bottom: 1px solid lightgrey;"></p>

<h2 id="4-1"><img style="float: left; margin: 0px 15px 15px 0px;" src="../graphics/pencil2.png">4.1 - Why Connected Data Changes the Question</h2>

Some questions are not really about rows. They are about paths.

- Which supplier affects this product line?
- Which reports are impacted if this table changes?
- Which customers are connected to this incident through contracts, assets, locations, and support cases?
- Which operational signals point to the same root cause?

You can answer these questions with joins, but the query gets ugly fast because the shape of the question is not flat. It is connected. A graph model makes the relationship itself a first-class thing, and an ontology gives those relationships business names the agent can reason over.

For data agents, this matters because Fabric already supports ontologies as a data source. That means the agent can use an ontology alongside lakehouses, warehouses, semantic models, mirrored databases, and KQL databases. The agent still runs under the user's permissions and remains read-only, but the ontology gives it a more business-aware route through the data.

For most Fabric data agent scenarios, the practical answer is to use an **ontology**. Graph is still important because it explains how connected data works underneath the covers, but the ontology is the model you want business users, applications, and agents to share.

| Approach | When it matters | What it gives you |
| --- | --- | --- |
| **Graph directly** | Useful for learning or inspecting the mechanics of connected data, including nodes, edges, keys, graph queries, and relationship traversal. It is also useful for highly technical scenarios where the team is comfortable modeling relationships explicitly and querying them with GQL. | A lower-level view of how connected data is represented and traversed. |
| **Ontology** | Use when the goal is a business-facing model that agents, applications, and users can share. | Graph-style relationships packaged with business names, properties, data bindings, and concepts that are easier to explain, govern, and reuse. |

Related video: <a href="https://youtu.be/N6hkxnuOQ8k">Microsoft Fabric: Fabric IQ Graph Tutorial</a>

The Microsoft Learn graph tutorial starts with the Adventure Works dataset and a new graph model. That setup is useful here because it lets you see why connected questions need a connected model before you decide whether the final business-facing implementation belongs in an ontology.

<p><img style="float: left; margin: 0px 15px 15px 0px;" src="../graphics/point1.png"><b>Activity: Prepare the graph tutorial environment</b></p>

<p><img style="margin: 0px 15px 15px 0px;" src="../graphics/checkmark.png"><b>Description</b></p>

Prepare the Adventure Works sample data and create the graph model used throughout this module.

<p><img style="margin: 0px 15px 15px 0px;" src="../graphics/checkmark.png"><b>Steps</b></p>

1. Right-click and open <a href="https://learn.microsoft.com/en-us/fabric/graph/tutorial-introduction">Tutorial: Introduction to Graph in Microsoft Fabric</a> in a new browser tab.
2. Review the tutorial scenario and the Adventure Works relationships it models.
3. Right-click and open <a href="https://learn.microsoft.com/en-us/fabric/graph/tutorial-load-data">Tutorial: Load Sample Data for Graph in Microsoft Fabric</a> in a new browser tab, then follow the steps to download and load the sample data into a lakehouse.
4. Right-click and open <a href="https://learn.microsoft.com/en-us/fabric/graph/tutorial-create-graph">Tutorial: Create a graph model in Microsoft Fabric</a> in a new browser tab, then follow the steps to create the graph model and load the lakehouse data into it.
5. Write down the business entities in the sample data: customers, orders, employees, products, product categories, product subcategories, vendors, and vendor products.
6. Keep the tutorial tabs open. The next sections use the same graph model.

<p style="border-bottom: 1px solid lightgrey;"></p>

<h2 id="4-2"><img style="float: left; margin: 0px 15px 15px 0px;" src="../graphics/pencil2.png">4.2 - Nodes, Edges, and Business Relationships</h2>

Graph modeling changes the center of gravity. Instead of starting with tables, start with:

- **Nodes** - the things in the business: Customer, Product, Supplier, Report, Table, Asset, Incident.
- **Edges** - the relationships between those things: purchased, supplied by, depends on, located in, owns, uses, impacts.
- **Properties** - the attributes that describe nodes or relationships: effective date, status, role, confidence, quantity, severity.

The relationship deserves design time. "Customer bought Product" is not the same as "Customer owns Product," and "Report uses Table" is not the same as "Report is certified from Table." If those verbs matter to the business, they should be explicit.

A practical graph design for agent scenarios should include:

| Design choice | Why it matters for agents |
| --- | --- |
| Clear node labels | Helps the agent map user language to the right object type |
| Verb-based edge names | Helps the agent reason over paths and explain answers |
| Direction where meaningful | Supports upstream/downstream and owner/dependent questions |
| Properties on edges | Captures dates, quantities, status, or confidence of a relationship |
| Synonyms and definitions | Handles real user language instead of schema-only vocabulary |

In a direct graph build, you create these pieces explicitly. In the Fabric IQ Graph tutorial, each source table becomes a node: customers, employees, orders, products, product categories, product subcategories, vendors, and so on. Each relationship becomes an edge: customers purchase orders, employees sell orders, orders contain products, products belong to categories, and vendors produce products.

That exercise is valuable because it shows the pattern clearly. It also shows why a raw graph can become a lot of manual design work. You need to create the nodes, map the keys, define the edges, name the relationships, and validate the path. If the model cannot explain the path in English, the agent probably should not explain the answer to a user yet.

Graph also introduces its own query surface. Fabric Graph supports visual exploration and GQL-style querying, and those queries can be case-sensitive. That is powerful, but it is not the same thing as a business user asking a natural-language question. This is another reason ontology becomes important: it lets you keep the relationship power of Graph while presenting a higher-level business model to agents and users.

<p><img style="float: left; margin: 0px 15px 15px 0px;" src="../graphics/point1.png"><b>Activity: Add nodes and edges to the graph</b></p>

<p><img style="margin: 0px 15px 15px 0px;" src="../graphics/checkmark.png"><b>Description</b></p>

Create the explicit graph structure: nodes for entities and edges for the relationships between them.

<p><img style="margin: 0px 15px 15px 0px;" src="../graphics/checkmark.png"><b>Steps</b></p>

1. Right-click and open <a href="https://learn.microsoft.com/en-us/fabric/graph/tutorial-model-nodes">Tutorial: Add node types to your graph</a> in a new browser tab, then follow the steps to add the Adventure Works node types.
2. As you create each node, note the source table and key column used to identify the entity.
3. Right-click and open <a href="https://learn.microsoft.com/en-us/fabric/graph/tutorial-model-edges">Tutorial: Add edge types to your graph</a> in a new browser tab, then follow the steps to add the relationship edges.
4. As you create each edge, note the business verb: sells, purchases, contains, isOfType, belongsTo, and produces.
5. Save the graph model after the nodes and edges are configured.
6. Write one sentence explaining how each edge changes the question the graph can answer.

<p style="border-bottom: 1px solid lightgrey;"></p>

<h2 id="4-3"><img style="float: left; margin: 0px 15px 15px 0px;" src="../graphics/pencil2.png">4.3 - Fabric Ontologies as an Agent Source</h2>

Fabric data agents can use an ontology as a selected data source. That is the key connection for this workshop: the ontology is not just documentation sitting next to the system. It becomes part of the agent's answer path.

This is the reason we do not want students walking away thinking, "I need to build a graph for every business problem." Graph is the foundation. Ontology is the business-facing layer built on top of that foundation.

In the video example, a small ontology is created with customers and orders, then a *purchases* relationship connects them. The result still behaves like a graph: you can see customers, orders, and the relationship path between them. But now the model is expressed as business concepts and relationships that can be reused by data agents.

When you add an ontology to a data agent, treat it with the same discipline as any other governed source:

- Add only the subject area needed for the workshop scenario.
- Describe when the agent should use the ontology instead of a table or semantic model.
- Define synonyms that users actually say.
- Keep definitions short, precise, and business-approved.
- Test questions that require the ontology and questions that should route somewhere else.

This is also where permissions matter. The data agent does not magically bypass access controls because the source is more semantic. Users still need read access to the data source, and downstream answers still respect Fabric governance.

The graph tutorial also shows one more modeling move: a single source table can contain more than one business concept. In the tutorial, the Employees table contains a `Country` value. You can leave country as an employee property, or you can promote it into its own `Country` node and connect employees to countries with a `livesIn` edge. That is the exact kind of modeling decision that helps explain why ontologies become valuable: the more the model starts representing business concepts, the more you want a business-facing abstraction instead of a raw graph canvas.

<p><img style="float: left; margin: 0px 15px 15px 0px;" src="../graphics/point1.png"><b>Activity: Compare direct Graph modeling to ontology modeling</b></p>

<p><img style="margin: 0px 15px 15px 0px;" src="../graphics/checkmark.png"><b>Description</b></p>

Use the tutorial's one-table modeling step to decide when direct Graph is only teaching the mechanics and when the business-facing model should be an ontology.

<p><img style="margin: 0px 15px 15px 0px;" src="../graphics/checkmark.png"><b>Steps</b></p>

1. Right-click and open <a href="https://learn.microsoft.com/en-us/fabric/graph/tutorial-model-node-edge-from-same-table">Tutorial: Create Node and Edge Types from One Source Table</a> in a new browser tab.
2. Follow the tutorial steps to create the `Country` node and `livesIn` edge from the Employees table.
3. Compare the two designs: country as a property on Employee versus country as its own business concept.
4. Write down when the direct Graph model is useful for understanding the relationship.
5. Write down how the same idea would appear in an ontology: entity type, properties, relationship, and data binding.
6. Capture the design lesson: Graph shows the mechanics; ontology packages the same connected idea for business and agent reuse.

<p style="border-bottom: 1px solid lightgrey;"></p>

<h2 id="4-4"><img style="float: left; margin: 0px 15px 15px 0px;" src="../graphics/pencil2.png">4.4 - Multi-Hop Reasoning, Dependency, and Impact Analysis</h2>

The reason to bring graph thinking into this workshop is multi-hop reasoning. A single-hop question asks for a direct relationship: "Which products did this customer buy?" A multi-hop question follows a path: "Which suppliers could affect revenue for customers in this region if this product line is delayed?"

That second question crosses several concepts. It may touch customer, geography, product, supplier, order, and revenue. If the model understands those relationships, an agent can explain the path instead of only returning a number.

For workshop scenarios, use three repeatable demo patterns:

1. **Dependency analysis** - What depends on this thing?
2. **Impact analysis** - If this thing changes, what might be affected?
3. **Relationship explanation** - Why are these two things connected?

The answer should include the path. If the agent says "Supplier A affects Region B," ask it to explain how. The explanation is what tells you whether the model reasoned over the graph or guessed from nearby labels.

This is where the Graph/Ontology distinction matters most. Graph teaches you how the path is built. Ontology helps you package that path so a business user can ask about it naturally and a data agent can answer using governed business meaning.

<p><img style="float: left; margin: 0px 15px 15px 0px;" src="../graphics/point1.png"><b>Activity: Query the graph visually and with GQL</b></p>

<p><img style="margin: 0px 15px 15px 0px;" src="../graphics/checkmark.png"><b>Description</b></p>

Use the tutorial's visual query builder and GQL examples to validate whether the graph can answer connected-data questions.

<p><img style="margin: 0px 15px 15px 0px;" src="../graphics/checkmark.png"><b>Steps</b></p>

1. Right-click and open <a href="https://learn.microsoft.com/en-us/fabric/graph/tutorial-query-builder">Tutorial: Query the Graph with the Query Builder</a> in a new browser tab, then follow the steps to visually query what products Carla Adams purchased.
2. Observe the path: `Customer` to `Order` to `Product`.
3. Right-click and open <a href="https://learn.microsoft.com/en-us/fabric/graph/tutorial-query-code-editor">Tutorial: Query the Graph with GQL</a> in a new browser tab, then follow the steps to run the GQL examples.
4. Compare the visual query builder experience with the GQL code editor experience.
5. Write down which parts are useful for a technical modeler and which parts a business user should never need to see.
6. Translate one GQL result into a natural-language question that would be better served through an ontology-backed agent.
7. Save that question for the ontology and data-agent work in Module 05.

<p style="border-bottom: 1px solid lightgrey;"></p>

<p><img style="margin: 0px 15px 15px 0px;" src="../graphics/owl.png"><b>For Further Study</b></p>
<ul>
  <li><a href="https://learn.microsoft.com/en-us/fabric/data-science/concept-data-agent">Fabric data agent creation - Microsoft Fabric</a></li>
  <li><a href="https://learn.microsoft.com/en-us/fabric/data-science/data-agent-end-to-end-tutorial">Fabric data agent scenario</a></li>
  <li><a href="https://learn.microsoft.com/en-us/fabric/data-science/evaluate-data-agent">Evaluate your data agent</a></li>
  <li><a href="https://learn.microsoft.com/en-us/fabric/data-science/data-agent-tenant-settings">Fabric data agent tenant settings</a></li>
  <li><a href="https://learn.microsoft.com/en-us/fabric/graph/tutorial-introduction">Tutorial: Introduction to Graph in Microsoft Fabric</a></li>
  <li><a href="https://learn.microsoft.com/en-us/fabric/graph/tutorial-load-data">Tutorial: Load Sample Data for Graph in Microsoft Fabric</a></li>
  <li><a href="https://learn.microsoft.com/en-us/fabric/graph/tutorial-create-graph">Tutorial: Create a graph model in Microsoft Fabric</a></li>
  <li><a href="https://learn.microsoft.com/en-us/fabric/graph/tutorial-model-nodes">Tutorial: Add node types to your graph</a></li>
  <li><a href="https://learn.microsoft.com/en-us/fabric/graph/tutorial-model-edges">Tutorial: Add edge types to your graph</a></li>
  <li><a href="https://learn.microsoft.com/en-us/fabric/graph/tutorial-model-node-edge-from-same-table">Tutorial: Create Node and Edge Types from One Source Table</a></li>
  <li><a href="https://learn.microsoft.com/en-us/fabric/graph/tutorial-query-builder">Tutorial: Query the Graph with the Query Builder</a></li>
  <li><a href="https://learn.microsoft.com/en-us/fabric/graph/tutorial-query-code-editor">Tutorial: Query the Graph with GQL</a></li>
  <li><a href="https://youtu.be/N6hkxnuOQ8k">Microsoft Fabric: Fabric IQ Graph Tutorial</a></li>
</ul>

Congratulations! You have completed this module on Fabric Graph &amp; Fabric Ontologies. You now have a starter pattern for relationship traversal, dependency analysis, and multi-hop reasoning that can feed the extension scenarios in the next modules.
