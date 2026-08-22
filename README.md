![](graphics/microsoftlogo.png)

# Workshop: Microsoft Fabric Data Agents and Beyond

#### <i>A Microsoft Workshop from the Tales from the Field Team</i>

<p style="border-bottom: 1px solid lightgrey;"></p>

<img style="float: left; margin: 0px 15px 15px 0px;" src="https://raw.githubusercontent.com/microsoft/sqlworkshops/master/graphics/textbubble.png"> <h2>About this Workshop</h2>

Welcome to this Microsoft solutions workshop on *Fabric Data Agents and Beyond*. Microsoft Fabric brings analytical, operational, and real-time data together on a single platform, and Fabric IQ adds the business context layer on top of it, so that people *and* AI agents can reason over that data using a shared business vocabulary instead of raw technical structures.

In this workshop, you'll learn how a Fabric data agent turns a plain-language question into a governed, traceable answer, and what it takes to move an agent from a working demo to something your organization can trust in production.

The focus of this workshop is to understand how to design, build, govern, and operate Fabric data agents over your organization's governed data.

You'll start with an introduction to Fabric IQ and its components - semantic models, ontologies, graph, data agents, operations agents, and Plan. From there you'll build your first Fabric data agent, then learn what separates a demo agent from a production one: agent and data source instructions, example queries, multi-source routing, security, and CI/CD. You'll then move into data modeling for AI, Fabric Graph and ontologies, and real-time scenarios where operations agents act on streaming data. You'll end by extending data agents beyond Microsoft Fabric, with a focus on how to extrapolate what you have learned to create other solutions for your organization.

This github README.MD file explains how the workshop is laid out, what you will learn, and the technologies you will use in this solution. To download this Lab to your local computer, click the **Clone or Download** button you see at the top right side of this page. [More about that process is here](https://help.github.com/en/github/creating-cloning-and-archiving-repositories/cloning-a-repository). 

You can view all of the [courses and other workshops our team has created at this link - open in a new tab to find out more.](https://microsoft.github.io/sqlworkshops/)

<p style="border-bottom: 1px solid lightgrey;"></p>

<img style="float: left; margin: 0px 15px 15px 0px;" src="https://raw.githubusercontent.com/microsoft/sqlworkshops/master/graphics/checkmark.png"> <h3>Learning Objectives</h3>

In this workshop you'll cover these topics:
<br>

- **Introduction and Overview - Fabric IQ:** Why business context matters for AI, and how Power BI semantic models, ontologies, graph, data agents, operations agents, and Plan work together.
- **Fabric Data Agents:** What a data agent is and how it routes a question to NL2SQL, NL2DAX, or NL2KQL; capacity and Copilot tenant prerequisites; creating an agent, adding data sources, selecting tables, and publishing for consumers.
- **Fabric Data Agents in Use:** Writing agent and data source instructions, tuning accuracy with example queries, routing across multiple data sources, the permission tiers that govern access, and managing agents through Git and deployment pipelines.
- **Data Modeling for AI and Ontologies:** Shaping and describing data so that agents and ontologies can reason over it reliably.
- **Fabric Graph and Fabric Ontologies:** Representing business concepts and their relationships for connected, multi-hop reasoning.
- **Real-Time Intelligence, Operations Agents, and Data Agents:** Eventstreams and Eventhouse, KQL querysets and Real-Time Dashboards, conversational analytics over live data, and Activator rules that turn detection into action.
- **Extending Data Agents Beyond Microsoft Fabric:** Surfacing a published data agent outside of the Fabric portal so other applications and agent experiences can consume its governed answers.

Microsoft Fabric can already answer your questions - the hard part is making sure it answers them correctly, safely, and the same way twice. This workshop takes you past the demo. You'll build a Fabric data agent against governed data, then spend real time on the things that decide whether anyone trusts it: instructions that encode your business rules, example queries that prove the agent gets the hard questions right, routing across multiple data sources, the permission model that stops it from oversharing, and the source control and deployment story that lets it ship like any other asset. Along the way you'll connect agents to Fabric IQ - ontologies, graph, and real-time operations agents - so your agents reason in business language and act on live conditions, not just historical tables.

The goal of this workshop is to train data and analytics professionals to determine when a data agent is the right solution, how to design and build one against governed data, how to make its answers trustworthy, and how to secure, deploy, monitor, and maintain it.

The concepts and skills taught in this workshop form the starting points for:

    Data Engineers and Analytics Engineers, to build and govern the Fabric data estate that agents reason over, and to make that data answerable in natural language.
    Data Architects and Solution Architects, to design the semantic models, ontologies, graph relationships, and real-time architectures that give agents their business context.
    Data Analysts, BI Developers, and Fabric Administrators, to consume, evaluate, secure, and operate published agents in production.

<p style="border-bottom: 1px solid lightgrey;"></p>
<img style="float: left; margin: 0px 15px 15px 0px;" src="https://raw.githubusercontent.com/microsoft/sqlworkshops/master/graphics/building1.png"> <h2>Business Applications of this Workshop</h2>

Businesses require answers from their data faster than a reporting backlog can deliver them. Most organizations have already invested in governed data - a lakehouse, a warehouse, semantic models, streaming telemetry - but the people who need answers still have to file a request and wait, because reaching the data means writing SQL, DAX, or KQL. Fabric data agents close that gap by letting business users ask questions in plain language against data that remains governed, permissioned, and traceable back to its source. Just as importantly, this workshop covers the parts that determine whether an agent is trusted in production: instructions that encode business rules, example queries that prove the agent gets the hard questions right, permission tiers that prevent oversharing, and source control that makes agents deployable like any other asset.

Some industry examples of natural-language analytics and agentic operations are supply chain and logistics, where an operations agent detects a cold-chain temperature violation on live telemetry while a data agent answers which customers and shipments are affected; retail, for self-service sales and inventory questions against a governed semantic model; manufacturing, for equipment and sensor analysis over real-time data; financial services, where row-level security must be preserved on every answer; and healthcare, where operational reporting must remain explainable and auditable, to name just a few.

<p style="border-bottom: 1px solid lightgrey;"></p>

<img style="float: left; margin: 0px 15px 15px 0px;" src="https://raw.githubusercontent.com/microsoft/sqlworkshops/master/graphics/listcheck.png"> <h2>Technologies used in this Workshop</h2>

The solution includes the following technologies - although you are not limited to these, they form the basis of the workshop. At the end of the workshop you will learn how to extrapolate these components into other solutions. You will cover these at an overview level, with references to much deeper training provided.

 <table style="tr:nth-child(even) {background-color: #f2f2f2;}; text-align: left; display: table; border-collapse: collapse; border-spacing: 2px; border-color: gray;">

  <tr><th style="background-color: #1b20a1; color: white;">Technology</th> <th style="background-color: #1b20a1; color: white;">Description</th></tr>

  <tr><td>Microsoft Fabric and OneLake</td><td>The unified SaaS analytics platform, and the single storage foundation every other service in this workshop reads from.</td></tr>
  <tr><td>Fabric Data Agent</td><td>The natural-language interface over your governed data. It selects the right data source and generates NL2SQL, NL2DAX, or NL2KQL on the student's behalf.</td></tr>
  <tr><td>Fabric IQ</td><td>The business context layer - ontologies, graph, and Plan - that lets people and agents reason using business concepts rather than table and column names.</td></tr>
  <tr><td>Power BI Semantic Models</td><td>Trusted business measures, KPIs, and hierarchies that a data agent queries with DAX, so agent answers match the numbers already used for reporting.</td></tr>
  <tr><td>Lakehouse and Warehouse</td><td>The SQL-addressable data sources a data agent queries, and where table selection and data source instructions are applied.</td></tr>
  <tr><td>Real-Time Intelligence</td><td>Eventstreams, Eventhouse, and KQL databases for streaming and event data, along with KQL Querysets and Real-Time Dashboards.</td></tr>
  <tr><td>Operations Agents and Activator</td><td>Continuous evaluation of operational conditions, and the rules that turn a detected condition into a governed action.</td></tr>
  <tr><td>Git Integration and Deployment Pipelines</td><td>Source control and environment promotion for data agents, so an agent ships and is versioned like any other Fabric item.</td></tr>

</table>

<p style="border-bottom: 1px solid lightgrey;"></p>

<img style="float: left; margin: 0px 15px 15px 0px;" src="https://raw.githubusercontent.com/microsoft/sqlworkshops/master/graphics/owl.png"> <h2>Before Taking this Workshop</h2>

Microsoft Fabric is a Software as a Service (SaaS) platform, so every activity in this workshop is performed in a web browser. You do not need to install a local server or provision a virtual machine.

**Two requirements block everything else in this workshop. Confirm both before class starts:**

- **A Microsoft Fabric capacity.** This can be a provisioned Fabric capacity (an F SKU purchased through Azure) or an active [Microsoft Fabric trial capacity](https://learn.microsoft.com/en-us/fabric/fundamentals/fabric-trial). Your tenant must also have [Fabric enabled](https://learn.microsoft.com/en-us/fabric/admin/fabric-switch) by an administrator. Without a capacity you cannot create the Lakehouse, Eventhouse, or data agent items used throughout the workshop.
- **An empty Fabric workspace assigned to that capacity.** [Create a new workspace](https://learn.microsoft.com/en-us/fabric/fundamentals/create-workspaces) and, under **Workspace settings > License info**, confirm its license mode points at your Fabric capacity or trial capacity - a workspace on a Pro or Personal license mode will not work. Start from an empty workspace so the items you build during the workshop stay isolated from anything else in your tenant, and so you can delete the whole workspace afterward to stop incurring charges.

The remaining prerequisites are:

- A Microsoft 365 account with the permissions needed to create assets.
- A Power BI license.
- The Copilot and data agent tenant settings enabled, so that data agents can be created and used in your tenant.
- A computer with an internet browser and a working internet connection, to work through the examples, access the workshop materials, and take notes.
- Optionally, a Microsoft Azure account with the ability to create assets, if you plan to provision a Fabric capacity rather than use a trial.

This workshop expects that you understand relational data and data modeling, working with large data sets, data security and permissions, and basic analytics and reporting concepts. Reading familiarity with SQL, DAX, or KQL is helpful, but you will not be asked to write them from scratch.

If you are new to these, here are a few references you can complete prior to class:

-  [Get started with Microsoft Fabric](https://learn.microsoft.com/en-us/training/paths/get-started-fabric/)
-  [Microsoft Fabric licenses and capacity](https://learn.microsoft.com/en-us/fabric/enterprise/licenses)
-  [OneLake, the OneDrive for data](https://learn.microsoft.com/en-us/fabric/onelake/onelake-overview)
-  [Semantic models in Power BI](https://learn.microsoft.com/en-us/power-bi/connect-data/service-datasets-understand)
-  [Security in Microsoft Fabric](https://learn.microsoft.com/en-us/fabric/security/security-overview)
-  [What is Real-Time Intelligence?](https://learn.microsoft.com/en-us/fabric/real-time-intelligence/overview)
-  [Fabric data agent concepts](https://learn.microsoft.com/en-us/fabric/data-science/concept-data-agent)


<img style="float: left; margin: 0px 15px 15px 0px;" src="https://raw.githubusercontent.com/microsoft/sqlworkshops/master/graphics/bulletlist.png"> <h3>Setup</h3>

<a href="modules/00%20-%20Pre-Requisites.md" >A full pre-requisites document is located here</a>. These instructions should be completed before the workshop starts, since you will not have time to cover these in class - that includes standing up your Fabric capacity and creating the empty workspace attached to it. <i>If you provision a Microsoft Fabric capacity in Azure rather than using a trial, remember to pause it from the Azure Portal when you are not taking the class so that you do not incur charges.</i>

<p style="border-bottom: 1px solid lightgrey;"></p>

<img style="float: left; margin: 0px 15px 15px 0px;" src="https://raw.githubusercontent.com/microsoft/sqlworkshops/master/graphics/education1.png"> <h2>Workshop Details</h2>

This workshop uses Microsoft Fabric, Fabric IQ, and Fabric data agents, with a focus on design, implementation, governance, and day-two operation of agents over governed enterprise data.

<table style="tr:nth-child(even) {background-color: #f2f2f2;}; text-align: left; display: table; border-collapse: collapse; border-spacing: 5px; border-color: gray;">

  <tr><td style="background-color: Cornsilk; color: black; padding: 5px 5px;">Primary Audience:</td><td style="background-color: Cornsilk; color: black; padding: 5px 5px;">Data Engineers, Analytics Engineers, and BI Developers tasked with building and governing data in Microsoft Fabric and making that data answerable in natural language</td></tr>
  <tr><td>Secondary Audience:</td><td> Data Architects and Solution Architects designing the semantic models, ontologies, graph relationships, and real-time architectures that AI agents reason over, along with Data Analysts and Microsoft Fabric Administrators who consume, secure, and operate published agents</td></tr>
  <tr><td style="background-color: Cornsilk; color: black; padding: 5px 5px;">Level: </td><td style="background-color: Cornsilk; color: black; padding: 5px 5px;"> 200 </td></tr>
  <tr><td>Type:</td><td>In-Person</td></tr>
  <tr><td style="background-color: Cornsilk; color: black; padding: 5px 5px;">Length: </td><td style="background-color: Cornsilk; color: black; padding: 5px 5px;">Full day (8 hours)</td></tr>

</table>

<p style="border-bottom: 1px solid lightgrey;"></p>

<img style="float: left; margin: 0px 15px 15px 0px;" src="https://raw.githubusercontent.com/microsoft/sqlworkshops/master/graphics/pinmap.png"> <h2>Related Workshops</h2>

 - [Fabric for the Data Professional](https://github.com/TalesFromTheField/Fabric-DataPro-Overview-Workshop)
 - [You can find a full Learning Path on Microsoft Fabric from Microsoft Learn at this reference](https://learn.microsoft.com/en-us/training/paths/get-started-fabric/)

<p style="border-bottom: 1px solid lightgrey;"></p>

<img style="float: left; margin: 0px 15px 15px 0px;" src="https://raw.githubusercontent.com/microsoft/sqlworkshops/master/graphics/bookpencil.png"> <h2>Workshop Modules</h2>

This is a modular workshop, and in each section, you'll learn concepts, technologies and processes to help you complete the solution.

<table style="tr:nth-child(even) {background-color: #f2f2f2;}; text-align: left; display: table; border-collapse: collapse; border-spacing: 5px; border-color: gray;">

  <tr><td style="background-color: AliceBlue; color: black;"><b>Module</b></td><td style="background-color: AliceBlue; color: black;"><b>Topics</b></td></tr>

  <tr><td><a href="modules/00%20-%20Pre-Requisites.md" >00 - Pre-Requisites </a></td><td> Microsoft 365 and Power BI licensing; provisioning a Microsoft Fabric capacity or trial capacity; the administrator roles you need; and creating and validating an empty Fabric workspace assigned to that capacity before class begins.</td></tr>

  <tr><td style="background-color: AliceBlue; color: black;"><a href="modules/01%20-%20Introduction%20and%20Overview.md" >01 - Introduction and Overview: Fabric IQ</a></td><td style="background-color: AliceBlue; color: black;"> Why business context matters for AI, and how the Fabric IQ components - Power BI semantic models, ontologies, graph, data agents, operations agents, and Plan - combine to move an organization from data to meaning, insights, decisions, and actions.</td></tr>

  <tr><td><a href="modules/02%20-%20Fabric%20Data%20Agents.md" >02 - Fabric Data Agents</a></td><td> What a Fabric data agent is and how it routes questions to NL2SQL, NL2DAX, and NL2KQL; prerequisites and Copilot tenant settings; creating an agent, adding data sources, and selecting tables; publishing a draft agent for consumers.</td></tr>

  <tr><td style="background-color: AliceBlue; color: black;"><a href="modules/03%20-%20Fabric%20Data%20Agents%20-%20In%20Use.md" >03 - Fabric Data Agents - In Use</a></td><td style="background-color: AliceBlue; color: black;"> Writing agent and data source instructions; tuning accuracy with example queries and evaluation scores; routing questions across multiple data sources; the permission tiers and sharing behavior that govern access; and managing agents with Git integration and deployment pipelines.</td></tr>

  <tr><td><a href="modules/04%20-%20Data%20Modeling%20for%20AI%20and%20Ontologies.md" >04 - Data Modeling for AI & Ontologies</a></td><td> Shaping and describing data so agents and ontologies can reason over it reliably - entity types, properties, relationships, and the data bindings that connect business concepts to the physical tables underneath them.</td></tr>

  <tr><td style="background-color: AliceBlue; color: black;"><a href="modules/05%20-%20Fabric%20Graph%20and%20Fabric%20Ontologies.md" >05 - Fabric Graph & Fabric Ontologies</a></td><td style="background-color: AliceBlue; color: black;"> Using Fabric Graph and ontologies together for relationship traversal, dependency and impact analysis, and multi-hop reasoning across connected business information.</td></tr>

  <tr><td><a href="modules/06%20-%20RTI%2C%20Operations%20Agents%2C%20and%20Data%20Agents.md" >06 - RTI, Operations Agents, and Data Agents </a></td><td> Real-Time Intelligence architecture with the Real-Time hub, Eventstreams, and Eventhouse; analyzing streams with KQL Querysets and Real-Time Dashboards; a data agent over live Eventhouse data; and Activator rules that let an operations agent take automated action.</td></tr>

  <tr><td style="background-color: AliceBlue; color: black;"><a href="modules/07%20-%20Extending%20Data%20Agents%20Beyond%20Microsoft%20Fabric.md" >07 - Extending Data Agents Beyond Microsoft Fabric </a></td><td style="background-color: AliceBlue; color: black;"> Taking a published data agent beyond the Fabric portal, so its governed answers can be consumed by other applications and agent experiences across your organization.</td></tr>

</table>

<p style="border-bottom: 1px solid lightgrey;"></p>

<p><img style="float: left; margin: 0px 15px 15px 0px;" src="https://raw.githubusercontent.com/microsoft/sqlworkshops/master/graphics/geopin.png"><b>Next Steps</b></p>


Next, Continue to <a href="modules/00%20-%20Pre-Requisites.md" ><i> Pre-Requisites</i></a>

# Contributing

This project welcomes contributions and suggestions.  Most contributions require you to agree to a
Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us
the rights to use your contribution. For details, visit https://cla.opensource.microsoft.com.

When you submit a pull request, a CLA bot will automatically determine whether you need to provide
a CLA and decorate the PR appropriately (e.g., status check, comment). Simply follow the instructions
provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or
contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.

# Legal Notices

### License
Microsoft and any contributors grant you a license to the Microsoft documentation and other content in this repository under the [Creative Commons Attribution 4.0 International Public License](https://creativecommons.org/licenses/by/4.0/legalcode), and grant you a license to any code in the repository under [the MIT License](https://opensource.org/licenses/MIT).

Microsoft, Windows, Microsoft Azure and/or other Microsoft products and services referenced in the documentation
may be either trademarks or registered trademarks of Microsoft in the United States and/or other countries.
The licenses for this project do not grant you rights to use any Microsoft names, logos, or trademarks.
Microsoft's general trademark guidelines can be found at http://go.microsoft.com/fwlink/?LinkID=254653.

Privacy information can be found at https://privacy.microsoft.com/en-us/

Microsoft and any contributors reserve all other rights, whether under their respective copyrights, patents,
or trademarks, whether by implication, estoppel or otherwise.
