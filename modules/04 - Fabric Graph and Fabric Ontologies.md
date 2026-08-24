![](../graphics/microsoftlogo.png)

# Workshop: Microsoft Fabric Data Agents and Beyond

#### <i>A workshop from the Tales from the Field team</i>

<p style="border-bottom: 1px solid lightgrey;"></p>

<img style="float: left; margin: 0px 15px 15px 0px;" src="../graphics/textbubble.png"> <h2>04 - Fabric Graph &amp; Fabric Ontologies</h2>

In this module you'll cover how Fabric Graph and Fabric ontologies work together to reason across connected business information. The focus is relationship traversal: finding dependency chains, ownership paths, upstream and downstream impact, and the "how did we get here?" questions that are awkward to answer from one table at a time.

In each section you'll get more references, which you should follow up on to learn more. Also watch for links within the text - click on each one to explore that topic.

(<a href="https://github.com/TalesFromTheField/Fabric-Data-Agents-Workshop/blob/main/modules/00%20-%20Pre-Requisites.md">Make sure you check out the <b>Pre-Requisites</b> page before you start</a>. You'll need all of the items loaded there before you can proceed with the workshop.)

Relational models are excellent at storing facts. Graphs are excellent at explaining how things are connected. Ontologies are excellent at naming those things in a way the business recognizes. Put the three together and a data agent has a much better chance of answering questions that require more than a single lookup.

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

<p><a href="https://youtu.be/7ccFIUfjiIc"><img src="https://img.youtube.com/vi/7ccFIUfjiIc/0.jpg" height = 200></a></p>

<p><img style="float: left; margin: 0px 15px 15px 0px;" src="../graphics/point1.png"><b>Activity: Identify questions that need a graph</b></p>

<p><img style="margin: 0px 15px 15px 0px;" src="../graphics/checkmark.png"><b>Description</b></p>

Separate simple lookup questions from connected-data questions so you know where Fabric Graph and ontologies earn their keep.

<p><img style="margin: 0px 15px 15px 0px;" src="../graphics/checkmark.png"><b>Steps</b></p>

1. Start with the business questions from your workshop scenario.
2. Mark each question as lookup, aggregation, relationship, dependency, impact, or path.
3. For every relationship, dependency, impact, or path question, list the entities involved.
4. Draw the shortest relationship path that would answer each question.
5. Identify which questions would be painful to answer with a single SQL, DAX, or KQL query.
6. Put those questions into the graph candidate list.

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

If the model cannot explain the path in English, the agent probably should not explain the answer to a user yet.

<p><a href="https://youtu.be/yCD8-qAIT2I"><img src="https://img.youtube.com/vi/yCD8-qAIT2I/0.jpg" height = 200></a></p>

<p><img style="float: left; margin: 0px 15px 15px 0px;" src="../graphics/point1.png"><b>Activity: Convert the ontology map into a graph design</b></p>

<p><img style="margin: 0px 15px 15px 0px;" src="../graphics/checkmark.png"><b>Description</b></p>

Use the graph candidate list from section 4.1 as the starting point for a graph design.

<p><img style="margin: 0px 15px 15px 0px;" src="../graphics/checkmark.png"><b>Steps</b></p>

1. Copy the entity list from section 4.1.
2. Convert each entity type into a proposed node label.
3. Convert each relationship into an edge name using a business verb.
4. Decide whether each edge needs direction.
5. Add edge properties where the relationship changes over time or carries a value.
6. Write three example path questions the graph should answer.

<p style="border-bottom: 1px solid lightgrey;"></p>

<h2 id="4-3"><img style="float: left; margin: 0px 15px 15px 0px;" src="../graphics/pencil2.png">4.3 - Fabric Ontologies as an Agent Source</h2>

Fabric data agents can use an ontology as a selected data source. That is the key connection for this workshop: the ontology is not just documentation sitting next to the system. It becomes part of the agent's answer path.

When you add an ontology to a data agent, treat it with the same discipline as any other governed source:

- Add only the subject area needed for the workshop scenario.
- Describe when the agent should use the ontology instead of a table or semantic model.
- Define synonyms that users actually say.
- Keep definitions short, precise, and business-approved.
- Test questions that require the ontology and questions that should route somewhere else.

This is also where permissions matter. The data agent does not magically bypass access controls because the source is more semantic. Users still need read access to the data source, and downstream answers still respect Fabric governance.

<p><a href="https://youtu.be/YJu9NQB3MuU"><img src="https://img.youtube.com/vi/YJu9NQB3MuU/0.jpg" height = 200></a></p>

<p><img style="float: left; margin: 0px 15px 15px 0px;" src="../graphics/point1.png"><b>Activity: Add ontology routing guidance to the agent</b></p>

<p><img style="margin: 0px 15px 15px 0px;" src="../graphics/checkmark.png"><b>Description</b></p>

Create the instruction pattern that tells the data agent when ontology-backed reasoning should be used.

<p><img style="margin: 0px 15px 15px 0px;" src="../graphics/checkmark.png"><b>Steps</b></p>

1. Open your Fabric data agent draft.
2. Confirm the ontology source is available and that you have read access to it.
3. Add the ontology source to the data agent.
4. Add instructions that route relationship, dependency, ownership, lineage, and impact questions to the ontology.
5. Add instructions that route approved financial measures to the semantic model when those measures exist there.
6. Test one lookup question, one aggregation question, and one relationship question. Confirm the agent chooses the expected source.

<p style="border-bottom: 1px solid lightgrey;"></p>

<h2 id="4-4"><img style="float: left; margin: 0px 15px 15px 0px;" src="../graphics/pencil2.png">4.4 - Multi-Hop Reasoning, Dependency, and Impact Analysis</h2>

The reason to bring graph thinking into this workshop is multi-hop reasoning. A single-hop question asks for a direct relationship: "Which products did this customer buy?" A multi-hop question follows a path: "Which suppliers could affect revenue for customers in this region if this product line is delayed?"

That second question crosses several concepts. It may touch customer, geography, product, supplier, order, and revenue. If the model understands those relationships, an agent can explain the path instead of only returning a number.

For workshop scenarios, use three repeatable demo patterns:

1. **Dependency analysis** - What depends on this thing?
2. **Impact analysis** - If this thing changes, what might be affected?
3. **Relationship explanation** - Why are these two things connected?

The answer should include the path. If the agent says "Supplier A affects Region B," ask it to explain how. The explanation is what tells you whether the model reasoned over the graph or guessed from nearby labels.

<p><a href="https://youtu.be/1OOe9-EteL0"><img src="https://img.youtube.com/vi/1OOe9-EteL0/0.jpg" height = 200></a></p>

<p><img style="float: left; margin: 0px 15px 15px 0px;" src="../graphics/point1.png"><b>Activity: Test a multi-hop impact question</b></p>

<p><img style="margin: 0px 15px 15px 0px;" src="../graphics/checkmark.png"><b>Description</b></p>

Validate whether the model can answer and explain a connected-data question.

<p><img style="margin: 0px 15px 15px 0px;" src="../graphics/checkmark.png"><b>Steps</b></p>

1. Choose one graph candidate question from section 4.1.
2. Rewrite it as a direct business question a user would actually ask.
3. Ask the question in the Fabric data agent.
4. Ask a follow-up: "Show the relationship path you used to reach that answer."
5. Check whether the path uses the expected entities and relationships.
6. If the answer is wrong or vague, update the ontology terms, relationship names, or data agent instructions.
7. Save the corrected question and expected answer for the evaluation set you build in Module 05.

<p style="border-bottom: 1px solid lightgrey;"></p>

<p><img style="margin: 0px 15px 15px 0px;" src="../graphics/owl.png"><b>For Further Study</b></p>
<ul>
  <li><a href="https://learn.microsoft.com/en-us/fabric/data-science/concept-data-agent">Fabric data agent creation - Microsoft Fabric</a></li>
  <li><a href="https://learn.microsoft.com/en-us/fabric/data-science/data-agent-end-to-end-tutorial">Fabric data agent scenario</a></li>
  <li><a href="https://learn.microsoft.com/en-us/fabric/data-science/evaluate-data-agent">Evaluate your data agent</a></li>
  <li><a href="https://learn.microsoft.com/en-us/fabric/data-science/data-agent-tenant-settings">Fabric data agent tenant settings</a></li>
  <li><a href="https://www.youtube.com/@Tales-from-the-Field">Tales from the Field YouTube channel</a></li>
</ul>

Congratulations! You have completed this module on Fabric Graph &amp; Fabric Ontologies. You now have a starter pattern for relationship traversal, dependency analysis, and multi-hop reasoning that can feed the extension scenarios in the next modules.
