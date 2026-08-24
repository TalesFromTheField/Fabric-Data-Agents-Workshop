![](../graphics/microsoftlogo.png)

# Workshop: Microsoft Fabric Data Agents and Beyond

#### <i>A workshop from the Tales from the Field team</i>

<p style="border-bottom: 1px solid lightgrey;"></p>

<img style="float: left; margin: 0px 15px 15px 0px;" src="../graphics/textbubble.png"> <h2> 07 - Extending Data Agents Beyond Microsoft Fabric </h2>

In this module you'll cover taking the Fabric data agent you built in the previous modules and putting it in front of the people who actually need it - in Microsoft Foundry, in Copilot Studio and Teams, in your own applications, in Microsoft 365 Copilot, and through the open Model Context Protocol.

In each module you'll get more references, which you should follow up on to learn more. Also watch for links within the text - click on each one to explore that topic.

(<a href="https://github.com/TalesFromTheField/Fabric-Data-Agents-Workshop/blob/main/modules/00%20-%20Pre-Requisites.md">Make sure you check out the <b>Pre-Requisites</b> page before you start</a>. You'll need all of the items loaded there before you can proceed with the workshop.) *Note that everything in this module requires a paid **F2 or higher** Fabric capacity (or P1 or higher with Fabric enabled) and a **published** data agent. These consumption paths are all currently in **preview**.

Here's the thing nobody tells you when you build your first data agent: the hard part is already done. You picked the data sources. You wrote the instructions. You added the example queries and argued with the model about what "active customer" actually means. That work - the semantics, the grounding, the security - *is* the agent. The Fabric portal is just the first place you happened to talk to it.

This module is about all the other places. And you don't rebuild anything to get there. A published data agent is an endpoint with an identity attached, and each integration below is a different front door to that same endpoint.

You'll cover these topics in this Module on Extending Data Agents Beyond Microsoft Fabric:

<dl>

  <dt><a href="#7-1">7.1 - Microsoft Foundry</a></dt>
  <dt><a href="#7-2">7.2 - Copilot Studio &amp; Teams</a></dt>
  <dt><a href="#7-3">7.3 - The Python Client SDK</a></dt>
  <dt><a href="#7-4">7.4 - Microsoft 365 Copilot</a></dt>
  <dt><a href="#7-5">7.5 - Data Agents &amp; Security</a></dt>
  <dt><a href="#7-6">7.6 - Model Context Protocol (MCP)</a></dt>
  <dt><a href="#7-7">7.7 - Skills for Fabric with GitHub Copilot and VS Code</a></dt>

</dl>

<p style="border-bottom: 1px solid lightgrey;"></p>

<h2 id="7-0"><img style="float: left; margin: 0px 15px 15px 0px;" src="../graphics/pencil2.png">Before You Start - Three Things That Break Everything</h2>

Every integration in this module fails in the same three ways, so let's handle them once instead of eight times.

1. **The agent has to be published.** A draft agent is invisible to every service outside Fabric. If your agent doesn't appear in a picker list anywhere, this is the reason about 80% of the time. Publish it, and give it a *rich, detailed description* - downstream orchestrators read that description to decide whether to call your agent at all.
2. **Same tenant, same account.** Fabric and the consuming service must be in the same tenant, signed in with the same account. Cross-tenant is not a supported story here.
3. **The tenant switches.** Consuming an agent outside Fabric means responses may leave Fabric's compliance boundary or region, so Microsoft makes you opt in. Your Fabric admin enables **cross-geo processing for AI** and **cross-geo storing for AI**. Details: <a href="https://learn.microsoft.com/en-us/fabric/data-science/data-agent-tenant-settings">Fabric data agent tenant settings</a>.

<p><img style="margin: 0px 15px 15px 0px;" src="../graphics/checkmark.png"><b>Say this to your security team</b></p>

Consumed outside Fabric, response *content* is processed and stored under that service's terms - Foundry's, Copilot Studio's, or Microsoft 365's. The *data access* is still governed by Fabric and the end user's own permissions. Both statements are true at once, and your compliance people will want to hear both.

<p style="border-bottom: 1px solid lightgrey;"></p>

<h2 id="7-1"><img style="float: left; margin: 0px 15px 15px 0px;" src="../graphics/pencil2.png">7.1 - Microsoft Foundry</h2>

Microsoft Foundry is where you go when the data agent isn't the whole application - it's one specialist on a team. You build an Azure AI agent that can reason, call tools, and take actions, and your Fabric data agent becomes one of its knowledge sources.

The mental model: in Foundry, your data agent is registered as a **tool**. The Foundry agent has its own model doing orchestration. When a question arrives it decides whether the Fabric tool is right for the job, calls into Fabric, and weaves the results into its answer. Security flows through **Identity Passthrough (On-Behalf-Of)**, so queries only ever touch data the end user is allowed to see.

Connecting requires two values, entered as secret custom keys: `workspace-id` and `artifact-id`. Both come out of your published agent's endpoint URL:

```
https://fabric.microsoft.com/groups/<workspace_id>/aiskills/<artifact-id>
```

Yes, the path still says `aiskills`. Data agents were called AI Skills in preview and the URL never got the memo. If you presented on this back then, congratulations - your old slides have one accurate line left.

<p><img style="margin: 0px 15px 15px 0px;" src="../graphics/checkbox.png"><b>Two things people get wrong immediately</b></p>

- **The model you pick in Foundry does not change the model your Fabric agent uses.** The Foundry deployment handles orchestration and phrasing. Fabric still does query generation on its side.
- **One Fabric data agent per Azure AI agent.** If you need three subject areas, that's three Foundry agents. Plan for it now rather than discovering it mid-demo.

You'll also need at least the `AI Developer` RBAC role in Foundry - for you and for your end users.

<p><a href="https://youtu.be/nqUt-wCYY2M"><img src="https://img.youtube.com/vi/nqUt-wCYY2M/0.jpg" height = 200></a></p>

<p><img style="float: left; margin: 0px 15px 15px 0px;" src="../graphics/point1.png"><b>Activity: Add your data agent to a Foundry agent</b></p>

<p><img style="margin: 0px 15px 15px 0px;" src="../graphics/checkmark.png"><b>Steps</b></p>

- Open the following Link in another tab and follow the instructions <a href="https://learn.microsoft.com/en-us/fabric/data-science/data-agent-foundry">Consume a data agent in Microsoft Foundry</a>
- When you test in the playground, ask three questions: one your agent should clearly answer, one it clearly should not, and one ambiguous. Watch what the orchestrator decides.
- Open the following Link in another tab and review <a href="https://learn.microsoft.com/en-us/fabric/data-science/fabric-data-agent-foundry-observability">Observe with Microsoft Foundry</a> so you can see what the agent *did*, not just what it said.

> If you only reviewed the documentation in this Activity, ensure you bookmark each of these references and then perform the Activity in full once you do have your deployment.

<p style="border-bottom: 1px solid lightgrey;"></p>

<h2 id="7-2"><img style="float: left; margin: 0px 15px 15px 0px;" src="../graphics/pencil2.png">7.2 - Copilot Studio &amp; Teams</h2>

Copilot Studio is the low-code path, and it's the shortest supported route from "my agent lives in Fabric" to "my colleague asks it a question in Teams without knowing what Fabric is."

The pattern is **connected agents** - agent-to-agent collaboration. You build a custom AI agent in Copilot Studio with its own name, topics, and trigger phrases, then connect your Fabric data agent to it. When a question needs enterprise data, the Copilot Studio agent hands off, gets a grounded answer, and brings it back.

<p><img style="margin: 0px 15px 15px 0px;" src="../graphics/checkbox.png"><b>The three things that decide whether this works</b></p>

- **Authentication mode.** **User authentication** passes each person's own identity - that's what you want for real business data. **Agent author authentication** runs as *you*, meaning everyone in that Teams channel sees data through your eyes. Choose it deliberately or not at all.
- **Generative AI orchestration must be enabled.** Under **Settings** → **Orchestration**. The single most common "it's connected but never answers from my data" complaint traces straight back to this switch.
- **Teams only.** This pattern is only validated for Microsoft Teams, and is **not currently supported in Microsoft 365 Copilot**. If M365 Copilot is your target, that's section 7.4 - a completely different route.

Sharing the agent does not share the data. Recipients need read access to the data agent **and** permissions on every underlying source. "I shared it and they got no results" is a permissions conversation, not a bug report.

If your agent doesn't appear in the picker, walk the checklist: published? correct account? same tenant? workspace permissions? It's always one of those four.

<p><a href="https://youtu.be/7ccFIUfjiIc"><img src="https://img.youtube.com/vi/7ccFIUfjiIc/0.jpg" height = 200></a></p>

<p><img style="float: left; margin: 0px 15px 15px 0px;" src="../graphics/point1.png"><b>Activity: Surface your data agent in Microsoft Teams</b></p>

<p><img style="margin: 0px 15px 15px 0px;" src="../graphics/checkmark.png"><b>Steps</b></p>

- Open the following Link in another tab and follow the instructions <a href="https://learn.microsoft.com/en-us/fabric/data-science/data-agent-microsoft-copilot-studio">Consume a data agent in Microsoft Copilot Studio</a>
- Set authentication to **User authentication** and enable **generative AI orchestration**.
- Write trigger phrases that match how your business users actually talk - not how the data model talks.
- Bonus round: have a colleague with *different* data permissions ask the same question. Compare the answers. This is the demo that makes security teams relax.

> If you only reviewed the documentation in this Activity, ensure you bookmark each of these references and then perform the Activity in full once you do have your deployment.

<p style="border-bottom: 1px solid lightgrey;"></p>

<h2 id="7-3"><img style="float: left; margin: 0px 15px 15px 0px;" src="../graphics/pencil2.png">7.3 - The Python Client SDK</h2>

Sometimes you don't want a chat window at all. You want the answer inside your own application - an internal web app, a scheduled report, a notebook that does something clever at 3am. The Python client SDK gives you the agent's capability while you keep full control of the user experience.

Authentication uses `InteractiveBrowserCredential`, so the user signs in with their own Entra ID credentials and the agent runs with their permissions. Same governance story as everywhere else.

<p><img style="margin: 0px 15px 15px 0px;" src="../graphics/checkbox.png"><b>The part that earns its keep</b></p>

`client.ask()` gives you an answer. **`client.get_run_details()` shows you the work** - the steps the agent took, which tool it called, whether each step succeeded, and the errors when they didn't.

When someone says "the agent gave me a wrong number," this is how you find out whether the model picked the wrong table, wrote a bad join, or gave a perfectly correct answer to a question nobody meant to ask. Use this path while you're tuning even if you never ship a Python app.

<p><img style="margin: 0px 15px 15px 0px;" src="../graphics/checkbox.png"><b>There is a clock on this one</b></p>

The current client SDK uses the **OpenAI Assistants API**, which OpenAI deprecated with a shutdown date of **August 26, 2026**. The code works until then. If you're starting fresh today, look hard at the MCP route in section 7.6 first. If you already have something running on this SDK, you now have a date on your calendar.

<p><a href="https://youtu.be/YJu9NQB3MuU"><img src="https://img.youtube.com/vi/YJu9NQB3MuU/0.jpg" height = 200></a></p>

<p><img style="float: left; margin: 0px 15px 15px 0px;" src="../graphics/point1.png"><b>Activity: Call your data agent from your own code</b></p>

<p><img style="margin: 0px 15px 15px 0px;" src="../graphics/checkmark.png"><b>Steps</b></p>

- Open the following Link in another tab and follow the instructions <a href="https://learn.microsoft.com/en-us/fabric/data-science/consume-data-agent-python">Consume a data agent using the Python client SDK</a>
- Clone the <a href="https://github.com/microsoft/fabric_data_agent_client/tree/main">Fabric Data Agent External Client repository</a> and run the sample against your own agent.
- Ask a question with `client.ask()`, then ask the *same* question with `client.get_run_details()` and find the generated query.
- Now ask a deliberately ambiguous question and read the run steps again. Fastest way there is to learn what your agent's instructions are missing.

> If you only reviewed the documentation in this Activity, ensure you bookmark each of these references and then perform the Activity in full once you do have your deployment.

<p style="border-bottom: 1px solid lightgrey;"></p>

<h2 id="7-4"><img style="float: left; margin: 0px 15px 15px 0px;" src="../graphics/pencil2.png">7.4 - Microsoft 365 Copilot</h2>

This is the one that makes executives sit up.

Microsoft 365 Copilot is where a huge portion of your organization already spends the day. Publishing your data agent to the **Agent Store** means a business user gets a governed, grounded answer from OneLake without opening Fabric, without knowing what a lakehouse is, and without filing a ticket. They just ask.

There's no Copilot Studio agent in the middle here - when you publish, you select **Publish to Agent Store**, and that's the integration. Users chat with it directly or `@`-mention it from the main Copilot chat, and the **code interpreter** can turn its results into charts right there in Teams. Row-level and column-level security are fully respected throughout.

<p><img style="margin: 0px 15px 15px 0px;" src="../graphics/checkbox.png"><b>The part that will bite you in a demo</b></p>

Your agent now runs inside the Microsoft 365 Copilot environment, **which has its own orchestrator**. That orchestrator uses chat context, user intent, and its own reasoning to shape the final response. The answer the user sees is not necessarily verbatim what your Fabric data agent produced.

For conversational questions, that's often an improvement. For a regulated number that has to match the quarterly filing exactly, it very much is not.

You have one lever: the **publishing description**, which becomes `description_for_model` and influences how the orchestrator handles your output. You can state that responses should be delivered as-is, without summarizing or rephrasing. Be honest with stakeholders about what that buys you - it *reduces* variation, it does not eliminate it. If a number must be byte-for-byte exact every time, that number belongs in a report, not a chat response. Knowing which questions belong on which surface is most of the skill here.

<p><a href="https://youtu.be/yCD8-qAIT2I"><img src="https://img.youtube.com/vi/yCD8-qAIT2I/0.jpg" height = 200></a></p>

<p><img style="float: left; margin: 0px 15px 15px 0px;" src="../graphics/point1.png"><b>Activity: Publish to the Microsoft 365 Agent Store</b></p>

<p><img style="margin: 0px 15px 15px 0px;" src="../graphics/checkmark.png"><b>Steps</b></p>

- Open the following Link in another tab and follow the instructions <a href="https://learn.microsoft.com/en-us/fabric/data-science/data-agent-microsoft-365-copilot">Consume a data agent from Microsoft 365 Copilot</a>
- Ask a question with a hard number in the answer. Compare the M365 Copilot response to the same question asked in the Fabric portal. Note every difference.
- Revise your publishing description to request as-is output, republish, and run the comparison again. Did the variation drop?
- Share the agent with a colleague who has different data permissions and confirm the security boundary holds.

> If you only reviewed the documentation in this Activity, ensure you bookmark each of these references and then perform the Activity in full once you do have your deployment.

<p style="border-bottom: 1px solid lightgrey;"></p>

<h2 id="7-5"><img style="float: left; margin: 0px 15px 15px 0px;" src="../graphics/pencil2.png">7.5 - Data Agents &amp; Security</h2>

Every conversation about data agents eventually arrives at the same question, usually from someone in the back of the room with their arms folded: *"So you've built a thing that writes its own queries against my warehouse and hands the answers to anybody who asks nicely. What could possibly go wrong?"*

Fair question, and the answer is the most important concept in this module.

**A Fabric data agent has no data access of its own.** It is not a service holding credentials to your lakehouse. When a question comes in, it generates a query and runs it **as the identity of the caller**, using that caller's Microsoft Entra ID token. If the person asking can't read the table, the query fails the same way it would in SQL. Row-level security, column-level security, workspace permissions, source permissions - all of it applies.

That's why the agent is safe to put in Teams. Not because we bolted a filter onto the chat window, but because there was never a second, more powerful path to the data.

<p><img style="margin: 0px 15px 15px 0px;" src="../graphics/checkbox.png"><b>Two people, one agent, two different answers</b></p>

Say this in your next design review, because it reframes everything: two users can ask a shared agent the *exact same question* and correctly receive *different answers*. The regional manager sees their region, the VP sees all regions. Nobody configured that. It falls out of the identity model.

The mechanism has a different name in each service, but it's the same idea every time:

| Integration | How identity reaches Fabric |
| --- | --- |
| **Microsoft Foundry** | Identity Passthrough (On-Behalf-Of) |
| **Copilot Studio / Teams** | **User authentication** passes each user; **Agent author authentication** runs as you |
| **Python client SDK** | `InteractiveBrowserCredential` - the user's own Entra sign-in |
| **Microsoft 365 Copilot** | The signed-in M365 user, same tenant, same account |
| **MCP server** | A bearer token representing a user **or** a service principal |

Notice the row that can break the pattern. **Agent author authentication** is legitimate - it's how you build an agent over data users can't individually access but may see aggregated. But it moves the security boundary from Entra to *your agent's instructions*, and instructions are not a security control. Use it on purpose, document it, and never as a shortcut around a permissions request you didn't feel like filing.

<p><img style="margin: 0px 15px 15px 0px;" src="../graphics/checkbox.png"><b>When there is no user - service principals</b></p>

Identity passthrough is elegant right up until 3am, when there's no human to pass through. Scheduled jobs, pipelines, and unattended applications need a **Microsoft Entra service principal (SPN)**.

The key point: **the data agent treats an SPN exactly like any other Entra identity.** The rules don't relax because a robot is asking. Setup involves registering the app in Entra, enabling **Service principals can use Fabric APIs** in the Fabric admin portal, granting workspace access - and then the step everyone misses, **granting read access to every data source**. Sharing the agent item is not enough.

Three limitations to write on the whiteboard now:

- **Managed identities are not currently supported.** You must use a service principal. If your platform standard is "managed identity everywhere," have that conversation before you commit to a date.
- **The SPN needs explicit access to every data source.** Again. Because it's the one that gets you.
- **Not supported for agents connected to a KQL database.** If your agent has a KQL source, unattended access is off the table for now.

<p><a href="https://youtu.be/1OOe9-EteL0"><img src="https://img.youtube.com/vi/1OOe9-EteL0/0.jpg" height = 200></a></p>

<p><img style="float: left; margin: 0px 15px 15px 0px;" src="../graphics/point1.png"><b>Activity: Prove the security boundary, then automate it</b></p>

<p><img style="margin: 0px 15px 15px 0px;" src="../graphics/checkmark.png"><b>Steps</b></p>

- Have two users with different entitlements ask your agent the *same* question. Confirm they get different, correct answers. This is the demo that ends the argument.
- Open the following Link in another tab and follow the instructions <a href="https://learn.microsoft.com/en-us/fabric/data-science/data-agent-service-principal">Use service principal authentication with Fabric data agent</a>
- Once your SPN works, *deliberately* remove its access to one data source and call it again. Watch it fail exactly the way it should.
- Open the following Link in another tab and review <a href="https://learn.microsoft.com/en-us/fabric/data-science/data-agent-purview-governance">Audit data agent interactions with Purview</a> - wire this up before production, not after someone asks for it in an incident review.
- Open the following Link in another tab and review <a href="https://learn.microsoft.com/en-us/fabric/data-science/data-agent-sharing">Fabric data agent sharing and permission management</a>

> If you only reviewed the documentation in this Activity, ensure you bookmark each of these references and then perform the Activity in full once you do have your deployment.

<p style="border-bottom: 1px solid lightgrey;"></p>

<h2 id="7-6"><img style="float: left; margin: 0px 15px 15px 0px;" src="../graphics/pencil2.png">7.6 - Model Context Protocol (MCP)</h2>

Everything in 7.1 through 7.4 is a *named* integration - Microsoft built a connector for each one. That's great right up until you want to use something Microsoft didn't build a connector for.

**Model Context Protocol (MCP)** is the answer. It's an emerging open standard defining how an AI system discovers available tools and interacts with them consistently. Expose your capability once, and any MCP-speaking client can use it. An **MCP client** is the app the user works in - VS Code, for example. An **MCP server** exposes tools and describes how to use them.

Your published data agent can be an MCP server, exposing exactly **one tool** - the agent itself. And when it is, the agent stops being "a thing with four supported front ends" and becomes a standard endpoint. That's why this section is listed last but may end up mattering most.

Because the client decides when to call the tool, **your published description becomes the tool description the server advertises**. Third time this module has told you to write a good description, and this is the most literal version: orchestrators read that text to decide whether to call you at all.

<p><img style="margin: 0px 15px 15px 0px;" src="../graphics/checkbox.png"><b>Three things to know before you start</b></p>

- **It is not a REST API.** A connection follows the MCP message flow - an `initialize` handshake, `tools/list` to discover, `tools/call` to ask. An SDK handles that for you. A generic HTTP POST that skips the handshake will not work. If you take one troubleshooting note from this section, take that one.
- **No dynamic client registration.** Your client can't obtain credentials through the protocol. You acquire a Fabric token yourself and attach it to every request, for the `https://api.fabric.microsoft.com/.default` scope. That token can represent a user **or** a service principal - which is where section 7.5 comes back around.
- **Publish first.** After publishing, the agent's **Settings** → **Model Context Protocol** tab gives you the server URL and a downloadable **mcp.json**. You can hand-build the URL from your workspace and agent IDs, but it only works *after* the agent is published. If it isn't, the endpoint errors even when your URL is perfect - which is a fun forty minutes if you don't know that going in.

Sit with what this enables for a second: governed enterprise data, grounded and permission-checked, answering questions inside the editor while a developer writes code against it. No export. No copy of the data. No screenshot pasted into a chat.

One compliance note - with a named integration you know whose data policy applies. With an open protocol, that's now a question you have to ask about **every MCP client your organization adopts**. Add it to the review checklist.

<p><img style="float: left; margin: 0px 15px 15px 0px;" src="../graphics/point1.png"><b>Activity: Stand up your data agent as an MCP server</b></p>

<p><img style="margin: 0px 15px 15px 0px;" src="../graphics/checkmark.png"><b>Steps</b></p>

- Open the following Link in another tab and follow the instructions <a href="https://learn.microsoft.com/en-us/fabric/data-science/data-agent-mcp-server">Data agent as Model Context Protocol server</a>
- Connect from both clients in that article - Python and Visual Studio Code - and ask the same question from each. Compare the answers.
- Read your agent's published description as though you were an orchestrator deciding whether to call it. If you wouldn't call it, rewrite it.
- If you built anything on the Python client SDK in 7.3, sketch your migration to this endpoint. Remember the **August 26, 2026** date.

> If you only reviewed the documentation in this Activity, ensure you bookmark each of these references and then perform the Activity in full once you do have your deployment.

<p style="border-bottom: 1px solid lightgrey;"></p>

<h2 id="7-7"><img style="float: left; margin: 0px 15px 15px 0px;" src="../graphics/pencil2.png">7.7 - Skills for Fabric with GitHub Copilot and VS Code</h2>

Everything so far has been about **consuming a published data agent**. Skills for Fabric are different. They are not another chat surface for a published agent. They are reusable instruction sets that teach AI coding tools how to work with Microsoft Fabric workloads from a developer environment.

Think of Skills for Fabric as the bridge between Fabric and AI-assisted development. GitHub Copilot, VS Code Copilot, Cursor, Claude Code, and similar tools do not automatically know Fabric REST APIs, T-SQL patterns, KQL patterns, notebook conventions, deployment workflows, or Power BI project structures. Skills package that knowledge into `SKILL.md` files, helper scripts, and resources so the coding agent can act like a Fabric-aware teammate.

<p><img style="margin: 0px 15px 15px 0px;" src="../graphics/checkbox.png"><b>Skills tell the agent what to do; tools let it do it</b></p>

Skills are static guidance loaded into the AI tool's context. MCP servers and CLI tools provide live access to schemas, files, APIs, and running applications. Used together, they let a developer ask for an outcome in natural language and have the coding agent author, query, validate, and document Fabric assets.

| Layer | Role |
| --- | --- |
| **Skills for Fabric** | Teach the coding agent Fabric-specific APIs, syntax, patterns, and best practices |
| **GitHub Copilot CLI / VS Code Copilot** | Provides the agent experience where the developer prompts, reviews, and iterates |
| **MCP servers and CLIs** | Give the agent live access to Fabric, Power BI, local files, Desktop, and validation tools |
| **Git / repository** | Holds the source-controlled Fabric project, PBIP/PBIR files, notebooks, scripts, and generated artifacts |

<p><img style="margin: 0px 15px 15px 0px;" src="../graphics/checkbox.png"><b>Where this fits with data agents</b></p>

Data agents answer governed business questions over Fabric data. Skills for Fabric help developers and analysts **build and maintain** the Fabric assets those agents depend on: lakehouses, warehouses, notebooks, eventhouses, semantic models, reports, workspace documentation, and deployment automation.

This distinction matters:

- Use a **Fabric data agent** when a user needs a governed answer from a published conversational analytics artifact.
- Use **Skills for Fabric with GitHub Copilot or VS Code** when a builder needs AI assistance authoring, inspecting, querying, documenting, or improving Fabric assets.
- Use **Power BI agentic skills** when the work moves into PBIP/PBIR semantic model and report authoring.

<p><img style="margin: 0px 15px 15px 0px;" src="../graphics/checkbox.png"><b>Power BI Agentic and report authoring</b></p>

The `powerbi-authoring` plugin is a separate Skills for Fabric bundle focused on Power BI authoring. It includes skills for semantic model authoring, report planning, report design, report authoring, and report management. The Power BI Report Authoring skill works against PBIR report definitions in PBIP projects, so GitHub Copilot or VS Code Copilot can help create or modify report pages, visuals, filters, formatting, and themes.

The important teaching point is not that Copilot "makes reports." The point is that skills constrain the agent to the right file formats, validation steps, and authoring patterns. Without skills, the agent is guessing. With skills, it has a playbook.

<p><img style="float: left; margin: 0px 15px 15px 0px;" src="../graphics/point1.png"><b>Activity: Install and inspect Skills for Fabric</b></p>

<p><img style="margin: 0px 15px 15px 0px;" src="../graphics/checkmark.png"><b>Steps</b></p>

- Open the following Link in another tab and review <a href="https://learn.microsoft.com/en-us/fabric/fundamentals/skills-for-fabric-overview">Skills for Fabric overview</a>.
- Open the following Link in another tab and follow the instructions <a href="https://learn.microsoft.com/en-us/fabric/fundamentals/skills-for-fabric-install">Install Skills for Fabric</a>. If you are using GitHub Copilot CLI, install the Fabric collection and, if you are working with Power BI projects, the `powerbi-authoring` plugin.
- Open the following Link in another tab and review <a href="https://learn.microsoft.com/en-us/fabric/fundamentals/skills-for-fabric-discover">Discover available Skills for Fabric</a>. List the installed skills in your AI coding tool.
- If you are using VS Code Copilot, review how VS Code detects skills from the local Copilot customization folder and confirm that the skill list is available in Chat.
- Open the following Link in another tab and review <a href="https://learn.microsoft.com/en-us/power-bi/developer/agentic/power-bi-agentic-overview">Power BI Agentic overview</a>.
- Open the following Link in another tab and review <a href="https://learn.microsoft.com/en-us/power-bi/developer/agentic/power-bi-report-authoring-skill-overview">Power BI Report Authoring skill</a>.
- Try one safe read-only prompt first, such as documenting a Fabric workspace or listing available tables in a lakehouse. Confirm the agent explains the plan before you allow it to make changes.

> If you only reviewed the documentation in this Activity, ensure you bookmark each of these references and then perform the Activity in full once you do have your deployment.

<p style="border-bottom: 1px solid lightgrey;"></p>

<h2 id="choosing-between-them"><img style="float: left; margin: 0px 15px 15px 0px;" src="../graphics/pencil2.png">Choosing Between Them</h2>

Several doors, different jobs. The short version to steal for your architecture review:

| If you need... | Use | Watch out for |
| --- | --- | --- |
| A developer-built AI agent with multiple tools and actions | **Microsoft Foundry** | One Fabric agent per Azure AI agent; needs `AI Developer` RBAC |
| Low-code agents delivered in Teams | **Copilot Studio** | Teams-only; must enable generative AI orchestration; not supported in M365 Copilot |
| Your own app, custom UX, or automation | **Python client SDK** | Assistants API shuts down **Aug 26, 2026** - plan the MCP migration |
| Broad reach to business users already in Teams | **Microsoft 365 Copilot** | The M365 orchestrator reshapes responses; per-user licensing |
| Any MCP-speaking client, or a future-proof endpoint | **MCP server** | Must follow the MCP handshake; the client's data policy applies |
| Unattended jobs and pipelines | **Service principal** | No managed identity support; not supported with KQL sources |
| AI-assisted Fabric development from a coding tool | **Skills for Fabric with GitHub Copilot / VS Code** | This builds and maintains Fabric assets; it is not another published data-agent chat surface |

True of the data-agent consumption paths: publish the agent, write a genuinely good description, keep everyone on one tenant, enable the tenant switches, and let Entra ID carry the security. For Skills for Fabric, the equivalent discipline is different: install the right skills, use the right tool permissions, review the plan before execution, and keep the generated Fabric project artifacts in source control.

<p style="border-bottom: 1px solid lightgrey;"></p>

<p><img style="margin: 0px 15px 15px 0px;" src="../graphics/owl.png"><b>For Further Study</b></p>
<ul>
  <li><a href="https://learn.microsoft.com/en-us/fabric/data-science/concept-data-agent">What is the Fabric data agent?</a></li>
  <li><a href="https://learn.microsoft.com/en-us/fabric/data-science/data-agent-tenant-settings">Fabric data agent tenant settings</a></li>
  <li><a href="https://learn.microsoft.com/en-us/fabric/data-science/data-agent-sharing">Fabric data agent sharing and permission management</a></li>
  <li><a href="https://learn.microsoft.com/en-us/fabric/data-science/evaluate-data-agent">Evaluate a Fabric data agent</a></li>
  <li><a href="https://learn.microsoft.com/en-us/fabric/data-science/data-agent-copilot-powerbi">Consume a data agent from Copilot in Power BI</a></li>
  <li><a href="https://learn.microsoft.com/en-us/fabric/data-science/fabric-data-agent-foundry-observability">Observe a Fabric data agent with Microsoft Foundry</a></li>
  <li><a href="https://learn.microsoft.com/en-us/fabric/data-science/data-agent-purview-governance">Audit data agent interactions with Microsoft Purview</a></li>
  <li><a href="https://learn.microsoft.com/en-us/fabric/data-science/data-agent-end-to-end-tutorial">Fabric data agent end-to-end tutorial</a></li>
  <li><a href="https://learn.microsoft.com/en-us/fabric/fundamentals/skills-for-fabric-overview">Skills for Fabric overview</a></li>
  <li><a href="https://learn.microsoft.com/en-us/fabric/fundamentals/skills-for-fabric-install">Install Skills for Fabric</a></li>
  <li><a href="https://learn.microsoft.com/en-us/fabric/fundamentals/skills-for-fabric-discover">Discover available Skills for Fabric</a></li>
  <li><a href="https://learn.microsoft.com/en-us/power-bi/developer/agentic/power-bi-agentic-overview">Power BI Agentic overview</a></li>
  <li><a href="https://learn.microsoft.com/en-us/power-bi/developer/agentic/power-bi-report-authoring-skill-overview">Power BI Report Authoring skill</a></li>
  <li><a href="https://www.youtube.com/@Tales-from-the-Field">Tales from the Field on YouTube</a></li>
  <li><a href="https://learn.microsoft.com/en-us/fabric/fundamentals/whats-new">As always, this is a fast-changing technology, so ensure you check this reference to find the latest improvements.</a></li>
</ul>

<p style="border-bottom: 1px solid lightgrey;"></p>

Congratulations! You have completed this Module. Your data agent is no longer something that lives in a portal - it's an endpoint your organization can reach from wherever they already work, with Entra ID keeping the governance intact at every door. You now have the tools, assets, and processes you need to extrapolate this information into other applications.
