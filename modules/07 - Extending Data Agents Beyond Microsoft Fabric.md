![](../graphics/microsoftlogo.png)

# Workshop: Microsoft Fabric Data Agents and Beyond

#### <i>A workshop from the Tales from the Field team</i>

<p style="border-bottom: 1px solid lightgrey;"></p>

<img style="float: left; margin: 0px 15px 15px 0px;" src="../graphics/textbubble.png"> <h2> 07 - Extending Data Agents Beyond Microsoft Fabric </h2>

In this module you'll cover taking the Fabric data agent you built in the previous modules and putting it in front of the people who actually need it - in Microsoft Foundry, in Copilot Studio and Teams, in your own Python applications, in Microsoft 365 Copilot, and through the open Model Context Protocol - and how Microsoft Entra ID keeps the security model intact the whole way. You'll finish by putting the whole thing under source control so it can be promoted like any other production asset.

In each module you'll get more references, which you should follow up on to learn more. Also watch for links within the text - click on each one to explore that topic.

(<a href="https://github.com/TalesFromTheField/Fabric-Data-Agents-Workshop/blob/main/modules/00%20-%20Pre-Requisites.md">Make sure you check out the <b>Pre-Requisites</b> page before you start</a>. You'll need all of the items loaded there before you can proceed with the workshop.) *Note that every integration in this module requires a paid **F2 or higher** Fabric capacity (or a P1 or higher Power BI Premium capacity with Fabric enabled), a **published** data agent, and the AI cross-geo tenant settings turned on. All of these consumption paths are currently in **preview**.

Here's the thing nobody tells you when you build your first data agent: the hard part is already done. You picked the data sources. You wrote the instructions. You added the example queries and argued with the model about what "active customer" actually means. That work - the semantics, the grounding, the security model - is the agent. The Fabric portal is just the first place you happened to talk to it.

This module is about all the other places. And the good news is you don't rebuild anything. A published Fabric data agent is an endpoint with an identity attached, and every integration in this module is a different front door to that same endpoint. Row-level security still applies. Column-level security still applies. If a user can't see the table in the lakehouse, they can't get an answer about it from Teams either. That's not a limitation, that's the whole point.

You'll cover these topics in this Module on Extending Data Agents Beyond Microsoft Fabric:

<dl>

  <dt><a href="#7-1">7.1 - Connecting to Data Agents via Microsoft Foundry</a></dt>
  <dt><a href="#7-2">7.2 - Connecting to Data Agents via Copilot Studio &amp; Teams</a></dt>
  <dt><a href="#7-3">7.3 - Connecting to Data Agents via the Python SDK</a></dt>
  <dt><a href="#7-4">7.4 - Connecting to Data Agents via Microsoft 365</a></dt>
  <dt><a href="#7-5">7.5 - Data Agents &amp; Security - How Entra ID Holds the Line</a></dt>
  <dt><a href="#7-6">7.6 - Data Agent as a Model Context Protocol (MCP) Server</a></dt>
  <dt><a href="#7-7">7.7 - Source Control, CI/CD, and ALM for Data Agents</a></dt>

</dl>

<p style="border-bottom: 1px solid lightgrey;"></p>

<h2 id="7-0"><img style="float: left; margin: 0px 15px 15px 0px;" src="../graphics/pencil2.png">Before You Start - Three Things That Break Everything</h2>

Every single integration in this module fails in exactly the same three ways, so let's get them out of the way once instead of five times.

**1. The agent has to be published.** A data agent that only exists in draft is invisible to every service outside Fabric. If your agent doesn't appear in a picker list in Foundry, Copilot Studio, or the Microsoft 365 Agent Store, this is the reason about 80% of the time. Publish it, and give it a *rich, detailed description* while you're at it - the downstream orchestrators read that description to decide when to call your agent. A description that says "data agent" gets called never.

**2. Same tenant, same account.** Fabric and the consuming service must live in the same tenant, and you must be signed in to both with the same account. Cross-tenant is not a supported story here.

**3. The tenant switches.** Consuming a data agent outside Fabric means responses may leave Fabric's compliance boundary or geographic region. Microsoft makes you opt in to that on purpose. Your Fabric admin needs to enable **cross-geo processing for AI** and **cross-geo storing for AI**. Read the details here before you go arguing with your admin: <a href="https://learn.microsoft.com/en-us/fabric/data-science/data-agent-tenant-settings">Fabric data agent tenant settings</a>.

<p><img style="margin: 0px 15px 15px 0px;" src="../graphics/checkmark.png"><b>Say this part out loud to your security team</b></p>

When a data agent is consumed outside of Fabric, the response content is processed and stored under *that service's* terms and data-handling policies - Foundry's, Copilot Studio's, or Microsoft 365's. The data access itself is still governed by Fabric and by the end user's own permissions. Both of those statements are true at the same time, and your compliance people will want to hear both of them.

<p style="border-bottom: 1px solid lightgrey;"></p>

<h2 id="7-1"><img style="float: left; margin: 0px 15px 15px 0px;" src="../graphics/pencil2.png">7.1 - Connecting to Data Agents via Microsoft Foundry</h2>

Microsoft Foundry is where you go when the data agent isn't the whole application - it's one specialist on a team. Foundry Agent Service lets you build an Azure AI agent that can reason, call tools, take actions, and pull grounding from multiple knowledge sources. Your Fabric data agent becomes one of those knowledge sources.

The mental model that helps here: in Foundry, the Fabric data agent is registered as a **tool**. The Foundry agent has its own model doing orchestration and response generation, and when a question comes in it decides whether the Fabric tool is the right one to call. If it is, Foundry calls into Fabric, Fabric generates and runs the query, and the results come back for the Foundry agent to weave into its answer.

<p><img style="margin: 0px 15px 15px 0px;" src="../graphics/checkbox.png"><b>Two things people get wrong immediately:</b></p>

- **The model you pick in Foundry does not change the model your Fabric data agent uses.** The Foundry deployment handles orchestration and phrasing. Fabric still does the query generation on its side with its own model.
- **You get one Fabric data agent per Azure AI agent.** Today, a single Azure AI agent can have exactly one Fabric data agent attached as a knowledge source. If you need three subject areas, you're either building three Foundry agents or consolidating in Fabric first. Plan for it now rather than discovering it in a demo.

Security here is handled by **Identity Passthrough (On-Behalf-Of)**. The end user's identity flows through Foundry into Fabric, so the queries that get generated only ever touch data that specific user is allowed to see. You are not creating a service account that quietly sees everything - which, if you've ever inherited someone else's analytics platform, you will appreciate.

<p><img style="margin: 0px 15px 15px 0px;" src="../graphics/checkmark.png"><b>Connecting through the portal</b></p>

In the Foundry portal, under **Build and Customize**, go to **Agents**, then either pick an existing agent or select **New Agent**. Select **Add** to add a knowledge source, choose **Microsoft Fabric**, and either reuse an existing connection or select **New Connection**.

The connection wants two values, both entered as custom keys with **Is Secret** checked:

- `workspace-id`
- `artifact-id`

Both come out of your published data agent's endpoint URL, which looks like this:

```
https://fabric.microsoft.com/groups/<workspace_id>/aiskills/<artifact-id>
```

Yes, the path still says `aiskills`. Data agents were called AI Skills in preview, and the URL never got the memo. If you presented on this back when it was AI Skills, congratulations - your old slides have one accurate line left.

Finally, write **instructions** for your Foundry agent telling it when and why to use the Fabric tool. From the Foundry agent's perspective this thing is just a tool, so describe it like one: what subject area it covers, what kinds of questions it can answer, and - just as important - when *not* to reach for it. Then hit **Try in playground**.

You'll need at least the `AI Developer` RBAC role in Foundry, both for you and for your end users.

<p><img style="margin: 0px 15px 15px 0px;" src="../graphics/checkmark.png"><b>Connecting programmatically</b></p>

If you'd rather do it in code, install the preview SDKs:

```bash
pip install azure-identity
pip install --pre azure-ai-projects
```

Set `PROJECT_ENDPOINT`, `MODEL_DEPLOYMENT_NAME`, and `FABRIC_CONNECTION_NAME`, then wire the connection into a `FabricTool`:

```python
import os
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.agents.models import FabricTool, ListSortOrder

project_client = AIProjectClient(
    endpoint=os.environ["PROJECT_ENDPOINT"],
    credential=DefaultAzureCredential(),
)

# Look up the Fabric connection by name
conn_id = project_client.connections.get(os.environ["FABRIC_CONNECTION_NAME"]).id

# Initialize the Fabric tool with the connection ID
fabric = FabricTool(connection_id=conn_id)

with project_client:
    agents_client = project_client.agents

    agent = agents_client.create_agent(
        model=os.environ["MODEL_DEPLOYMENT_NAME"],
        name="my-agent",
        instructions="You are a helpful agent",
        tools=fabric.definitions,
    )
    print(f"Created agent, ID: {agent.id}")
```

From there it's the standard threads-and-runs pattern - create a thread, add a message, process the run, read the messages back:

```python
    thread = agents_client.threads.create()

    message = agents_client.messages.create(
        thread_id=thread.id,
        role="user",
        content="What is the top sold product in Contoso last month?",
    )

    run = agents_client.runs.create_and_process(thread_id=thread.id, agent_id=agent.id)
    print(f"Run finished with status: {run.status}")

    if run.status == "failed":
        print(f"Run failed: {run.last_error}")

    messages = agents_client.messages.list(thread_id=thread.id, order=ListSortOrder.ASCENDING)
    for msg in messages:
        if msg.text_messages:
            print(f"{msg.role}: {msg.text_messages[-1].text.value}")
```

<p><a href="https://youtu.be/7ccFIUfjiIc"><img src="https://img.youtube.com/vi/7ccFIUfjiIc/0.jpg" height = 200></a></p>

<p><img style="float: left; margin: 0px 15px 15px 0px;" src="../graphics/point1.png"><b>Activity: Add your Fabric data agent to a Foundry agent</b></p>

<p><img style="margin: 0px 15px 15px 0px;" src="../graphics/checkmark.png"><b>Steps</b></p>

- Confirm your data agent is **published**, then copy its endpoint URL and pull out the `workspace-id` and `artifact-id`.
- Open the following link in another tab and follow the instructions: <a href="https://learn.microsoft.com/en-us/fabric/data-science/data-agent-foundry">Consume a data agent in Microsoft Foundry (preview)</a>
- Create a new Azure AI agent, add **Microsoft Fabric** as a knowledge source, and create the connection using your two IDs as secret custom keys.
- Write instructions that describe when the agent should reach for the Fabric tool.
- Test in the playground with three questions: one your Fabric agent should clearly answer, one it clearly should not, and one ambiguous. Watch what the orchestrator decides to do with each.
- Also review <a href="https://learn.microsoft.com/en-us/fabric/data-science/fabric-data-agent-foundry-observability">Observe a Fabric data agent with Microsoft Foundry</a> so you can see what the agent actually did, not just what it said.

> If you only reviewed the documentation in this Activity, ensure you bookmark each of these references and then perform the Activity in full once you do have your deployment.

<p style="border-bottom: 1px solid lightgrey;"></p>

<h2 id="7-2"><img style="float: left; margin: 0px 15px 15px 0px;" src="../graphics/pencil2.png">7.2 - Connecting to Data Agents via Copilot Studio &amp; Teams</h2>

Microsoft Copilot Studio is the low-code path. If Foundry is where developers assemble agents, Copilot Studio is where the rest of the organization does - and critically, it's the shortest supported route from "my data agent lives in Fabric" to "my colleague asks it a question in Teams without knowing what Fabric is."

The pattern is **connected agents**, or agent-to-agent collaboration. You build a custom AI agent in Copilot Studio - it has its own name, description, topics, trigger phrases, and knowledge sources like SharePoint or uploaded files - and then you connect your Fabric data agent to it. When a question comes in that needs enterprise data, the Copilot Studio agent hands off to the Fabric data agent, gets a grounded answer, and brings it back.

<p><img style="margin: 0px 15px 15px 0px;" src="../graphics/checkmark.png"><b>Wiring it up</b></p>

1. Go to <a href="https://copilotstudio.microsoft.com">Microsoft Copilot Studio</a> and pick your environment. Environments matter - pick the wrong one and you'll spend twenty minutes wondering where your agent went.
2. Select **Create**, then **+ New agent**, and give it a **Name** and **Description**. Save.
3. From the top pane, go to **Agents** and select **+ Add**.
4. Under **Choose how you want to extend your agent**, select **Microsoft Fabric**.
5. Reuse an existing connection or select **Create new connection**.
6. Pick your Fabric data agent from the list, adjust its description, and select **Add agent**.
7. Select the connected agent and choose its authentication mode.
8. Turn on **generative AI orchestration** under **Settings** → **Orchestration**.
9. Test in the built-in chat pane on the right.
10. **Publish**, then go to **Channels**, add the **Teams and Microsoft 365 Copilot** channel, and select **See agent in Teams**.

<p><img style="margin: 0px 15px 15px 0px;" src="../graphics/checkbox.png"><b>Step 7 is the one that matters</b></p>

When you select the connected Fabric data agent, you choose between:

- **User authentication** - every user's own identity is used against the data agent and its sources. This is what you want for anything touching real business data. Everyone sees exactly what they're entitled to see and nothing else.
- **Agent author authentication** - the agent runs with *your* credentials. Convenient. Also means every person in that Teams channel is now effectively looking at data through your eyes. Choose this deliberately or not at all.

<p><img style="margin: 0px 15px 15px 0px;" src="../graphics/checkbox.png"><b>Step 8 is the one people skip</b></p>

If you don't enable generative AI orchestration, your custom agent won't reliably route questions to the connected Fabric data agent. The single most common "it's connected but it never answers from my data" complaint traces straight back to this setting.

<p><img style="margin: 0px 15px 15px 0px;" src="../graphics/checkbox.png"><b>Two constraints worth writing down</b></p>

- A Copilot Studio agent with a connected Fabric data agent is **only validated for Microsoft Teams**. Other channels may work but have not been formally tested, and using this custom-agent-plus-connected-Fabric-agent pattern is **not currently supported in Microsoft 365 Copilot**. If Microsoft 365 Copilot is your target, that's section 7.4, which uses a completely different route.
- If you share the custom agent, every recipient needs at least read access to the Fabric data agent **and** the necessary permissions on all underlying data sources. Sharing the agent does not share the data. This is a feature, but it does mean "I shared it and they got no results" is usually a permissions conversation, not a bug report.

If your data agent doesn't appear in the picker list in step 6, walk the checklist: published? correct account? same tenant? workspace permissions? It's always one of those four.

<p><a href="https://youtu.be/7ccFIUfjiIc"><img src="https://img.youtube.com/vi/7ccFIUfjiIc/0.jpg" height = 200></a></p>

<p><img style="float: left; margin: 0px 15px 15px 0px;" src="../graphics/point1.png"><b>Activity: Surface your data agent in Microsoft Teams</b></p>

<p><img style="margin: 0px 15px 15px 0px;" src="../graphics/checkmark.png"><b>Steps</b></p>

- Open the following link in another tab and follow the instructions: <a href="https://learn.microsoft.com/en-us/fabric/data-science/data-agent-microsoft-copilot-studio">Consume a data agent in Microsoft Copilot Studio (preview)</a>
- Build a custom AI agent in Copilot Studio and connect your published Fabric data agent to it.
- Set authentication to **User authentication** and enable **generative AI orchestration**.
- Add a topic with trigger phrases that match how your business users actually talk. Not how the data model talks.
- Publish to the **Teams and Microsoft 365 Copilot** channel and ask it a question from inside Teams.
- Bonus round: have a colleague with *different* data permissions ask the same question. Compare the answers. This is the demo that makes security teams relax.
- Review <a href="https://learn.microsoft.com/en-us/fabric/data-science/data-agent-sharing">Fabric data agent sharing and permission management</a> before you share broadly.

> If you only reviewed the documentation in this Activity, ensure you bookmark each of these references and then perform the Activity in full once you do have your deployment.

<p style="border-bottom: 1px solid lightgrey;"></p>

<h2 id="7-3"><img style="float: left; margin: 0px 15px 15px 0px;" src="../graphics/pencil2.png">7.3 - Connecting to Data Agents via the Python SDK</h2>

Sometimes you don't want a chat window at all. You want the answer inside your own application - an internal web app, a scheduled report, a Slack-style bot your team already lives in, a notebook that does something clever at 3am. That's what the Python client SDK is for.

This path gives you the data agent's capability while you keep total control of the user experience and the app architecture. Authentication uses `InteractiveBrowserCredential` from `azure-identity`, which means the user signs in through a browser with their Microsoft Entra ID credentials and the agent runs **with their permissions**. Same governance story as everywhere else in this module.

<p><img style="margin: 0px 15px 15px 0px;" src="../graphics/checkmark.png"><b>Setting up</b></p>

Clone the <a href="https://github.com/microsoft/fabric_data_agent_client/tree/main">Fabric Data Agent External Client repository</a>, open it in VS Code, and set up a virtual environment:

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS / Linux
pip install -r requirements.txt
```

Configure two values - `TENANT_ID` and `DATA_AGENT_URL` - via environment variables, a `.env` file, or directly in your script:

```bash
TENANT_ID=<your-azure-tenant-id>
DATA_AGENT_URL=<your-fabric-data-agent-url>
```

<p><img style="margin: 0px 15px 15px 0px;" src="../graphics/checkmark.png"><b>Authenticate, connect, and ask</b></p>

```python
from azure.identity import InteractiveBrowserCredential
from fabric_data_agent_client import FabricDataAgentClient

credential = InteractiveBrowserCredential()
client = FabricDataAgentClient(credential=credential)

response = client.ask("What were the total sales last quarter?")
print(f"Response: {response}")
```

That's the whole thing. Three lines of setup and a question.

<p><img style="margin: 0px 15px 15px 0px;" src="../graphics/checkmark.png"><b>The part that's actually the most useful</b></p>

`client.get_run_details()` is where this path earns its keep. Every other integration in this module gives you an answer. This one shows you the work:

```python
run_details = client.get_run_details("What were the total sales last quarter?")

messages = run_details.get('messages', {}).get('data', [])
assistant_messages = [msg for msg in messages if msg.get('role') == 'assistant']
print("Answer:", assistant_messages[-1])

for step in run_details['run_steps']['data']:
    tool_name = "N/A"
    if 'step_details' in step and step['step_details'] and 'tool_calls' in step['step_details']:
        tool_calls = step['step_details']['tool_calls']
        if tool_calls and len(tool_calls) > 0 and 'function' in tool_calls[0]:
            tool_name = tool_calls[0]['function'].get('name', 'N/A')
    print(f"Step ID: {step.get('id')}, Type: {step.get('type')}, Status: {step.get('status')}, Tool Name: {tool_name}")
    if 'error' in step:
        print(f"  Error: {step['error']}")
```

You get the steps the agent took, which tool it called, whether each step succeeded, and the errors when they didn't. When someone tells you "the agent gave me a wrong number," this is how you find out whether the model picked the wrong table, wrote a bad join, or got a perfectly correct answer to a question nobody meant to ask. Use this path during tuning even if you never ship a Python app.

<p><img style="margin: 0px 15px 15px 0px;" src="../graphics/checkbox.png"><b>Important - there is a clock on this one</b></p>

The current client SDK and sample repository use the **OpenAI Assistants API** (`beta.assistants`, `beta.threads`, `beta.threads.runs`), which OpenAI has deprecated with a shutdown date of **August 26, 2026**. The code works until then. Plan your migration to the <a href="https://learn.microsoft.com/en-us/fabric/data-science/data-agent-mcp-server">Fabric data agent MCP endpoint</a> before that date.

If you are starting a brand new project today, look hard at the MCP server route first. If you have something already running on the client SDK, you have a deadline on your calendar and now you know about it.

<p><a href="https://youtu.be/YJu9NQB3MuU"><img src="https://img.youtube.com/vi/YJu9NQB3MuU/0.jpg" height = 200></a></p>

<p><img style="float: left; margin: 0px 15px 15px 0px;" src="../graphics/point1.png"><b>Activity: Call your data agent from your own code</b></p>

<p><img style="margin: 0px 15px 15px 0px;" src="../graphics/checkmark.png"><b>Steps</b></p>

- Open the following link in another tab and follow the instructions: <a href="https://learn.microsoft.com/en-us/fabric/data-science/consume-data-agent-python">Consume a Fabric data agent from external applications with the Python client SDK</a>
- Clone the <a href="https://github.com/microsoft/fabric_data_agent_client/tree/main">Fabric Data Agent External Client repository</a> and get the sample running against your own agent.
- Ask a question with `client.ask()`.
- Ask the *same* question with `client.get_run_details()` and read the run steps. Find the generated query.
- Now ask a deliberately ambiguous question and read the run steps again. This is the single fastest way to learn what your agent's instructions are missing.
- Read <a href="https://learn.microsoft.com/en-us/fabric/data-science/data-agent-mcp-server">Consume a data agent as a Model Context Protocol Server (preview)</a> and sketch what your migration looks like.

> If you only reviewed the documentation in this Activity, ensure you bookmark each of these references and then perform the Activity in full once you do have your deployment.

<p style="border-bottom: 1px solid lightgrey;"></p>

<h2 id="7-4"><img style="float: left; margin: 0px 15px 15px 0px;" src="../graphics/pencil2.png">7.4 - Connecting to Data Agents via Microsoft 365</h2>

This is the one that makes executives sit up.

Microsoft 365 Copilot is where a huge portion of your organization already spends its day. Publishing a Fabric data agent to the **Agent Store** in Microsoft 365 Copilot means a business user can get a governed, grounded answer from OneLake without opening Fabric, without knowing what a lakehouse is, and without filing a ticket. They just ask.

And unlike section 7.2, there's no Copilot Studio agent in the middle. This is a direct publish.

<p><img style="margin: 0px 15px 15px 0px;" src="../graphics/checkmark.png"><b>How it works</b></p>

When you publish your Fabric data agent, select **Publish to Agent Store**. That's it - that's the integration. Within a few seconds your agent shows up in the Agent Store in Microsoft 365 Copilot and users can interact with it from Teams.

If it doesn't appear right away, select the **Expand Navigation** button on the left to refresh the agent list. If it still doesn't appear, your Microsoft 365 admin needs to confirm that **Copilot extensibility** is enabled for your account.

Users have two ways to work with it:

- **Chat directly** with the Fabric data agent as its own conversation.
- **`@`-mention it** from the main Copilot chat. Type `@`, pick your agent from the list, and it attaches to the current chat.

Users can also share the agent by selecting the agent name → **Share** → copy link, then dropping that link into a 1:1 chat, group chat, or Teams channel. And again: recipients need access to the data agent **and** to its underlying data sources. Row-level and column-level security are fully respected - every user only sees results their own access permits.

One genuinely nice bonus: the **code interpreter** in Microsoft 365 Copilot can take the results your Fabric data agent returns and generate visualizations from them. Users get charts and trend exploration right there in Teams, off live governed data, without anybody building a report.

<p><img style="margin: 0px 15px 15px 0px;" src="../graphics/checkbox.png"><b>Now the part that will bite you in a demo</b></p>

When you publish to Microsoft 365 Copilot, your data agent runs inside the Microsoft 365 Copilot environment - **which has its own orchestrator**. That orchestrator uses the chat context, the user's intent, and its own model's reasoning to shape the final response. Meaning: the answer the user sees is not necessarily verbatim what your Fabric data agent produced. It may be summarized, rephrased, or contextualized.

For a lot of conversational questions, that's an improvement. For a regulated number that has to match the quarterly filing exactly, it very much is not.

You have one lever, and it's the **publishing description**. That description becomes `description_for_model` in Microsoft 365 Copilot and directly influences how the orchestrator handles your agent's output. You can state in that description that output from the Fabric data agent should be delivered **as-is, without summarizing, rephrasing, or adding extra interpretation**.

Be honest with your stakeholders about what that buys you: it *reduces variation*. It does not eliminate it. The Microsoft 365 Copilot orchestrator still reasons over the grounding data your agent returns, and some level of change is inevitable. If a number must be byte-for-byte exact every time, that number belongs in a report, not in a chat response. Knowing which questions belong in which surface is most of the skill here.

Also note the compliance angle one more time, because this is the surface where it's most likely to come up: responses returned by Fabric data agents in Microsoft 365 may be sent outside Fabric's compliance boundary or geographic region, and are processed and stored according to Microsoft 365's terms and data handling policies.

<p><img style="margin: 0px 15px 15px 0px;" src="../graphics/checkbox.png"><b>Licensing, briefly</b></p>

You need a Microsoft 365 Copilot license or Office 365 commercial subscription, plus user licenses for **each individual** using the Fabric data agent in Microsoft 365 Copilot. Fabric and Microsoft 365 Copilot must be on the same tenant, signed in with the same account.

<p><a href="https://youtu.be/yCD8-qAIT2I"><img src="https://img.youtube.com/vi/yCD8-qAIT2I/0.jpg" height = 200></a></p>

<p><img style="float: left; margin: 0px 15px 15px 0px;" src="../graphics/point1.png"><b>Activity: Publish your data agent to the Microsoft 365 Agent Store</b></p>

<p><img style="margin: 0px 15px 15px 0px;" src="../graphics/checkmark.png"><b>Steps</b></p>

- Open the following link in another tab and follow the instructions: <a href="https://learn.microsoft.com/en-us/fabric/data-science/data-agent-microsoft-365-copilot">Consume a data agent from Microsoft 365 Copilot (preview)</a>
- Write a publishing description that covers what the agent knows, what questions it handles, and explicit instructions about how its output should be presented.
- Publish your data agent and select **Publish to Agent Store**.
- Find it in the Agent Store in Microsoft 365 Copilot. Chat with it directly, then `@`-mention it from the main Copilot chat.
- Ask it a question with a hard number in the answer. Compare the Microsoft 365 Copilot response to the same question asked in the Fabric portal. Note every difference.
- Now revise your publishing description to ask for as-is output, republish, and run the comparison again. Did the variation drop?
- Use the **code interpreter** to turn a result into a chart.
- Share the agent with a colleague who has different data permissions and confirm the security boundary holds.

> If you only reviewed the documentation in this Activity, ensure you bookmark each of these references and then perform the Activity in full once you do have your deployment.

<p style="border-bottom: 1px solid lightgrey;"></p>

<h2 id="7-5"><img style="float: left; margin: 0px 15px 15px 0px;" src="../graphics/pencil2.png">7.5 - Data Agents &amp; Security - How Entra ID Holds the Line</h2>

Every conversation about data agents eventually arrives at the same question, usually asked by someone in the back of the room with their arms folded: *"So you've built a thing that writes its own queries against my warehouse and hands the answers to anybody who asks it nicely. What could possibly go wrong?"*

It's a fair question. And the answer is the single most important concept in this entire module, so it gets its own section.

**A Fabric data agent has no data access of its own.** None. It is not a service that holds credentials to your lakehouse. It doesn't have a privileged account quietly reading everything so it can be helpful later. When a question comes in, the agent generates a query and runs it **as the identity of the caller**, using that caller's Microsoft Entra ID token. If the person asking can't read the table, the query fails for them the same way it would fail in SQL. Row-level security applies. Column-level security applies. Workspace permissions apply. Data source permissions apply.

This is why the agent is safe to put in Teams. Not because we bolted a filter onto the chat window - because there was never a second, more powerful path to the data in the first place.

<p><img style="margin: 0px 15px 15px 0px;" src="../graphics/checkbox.png"><b>Two people, one agent, two different answers</b></p>

Say this out loud in your next design review, because it reframes the whole thing: two users can ask a shared data agent the *exact same question* and correctly receive *different answers*. The regional manager sees their region. The VP sees all regions. Nobody configured that in the agent. It falls out of the identity model.

That also means "the agent gave my colleague no results" is almost never a bug. It's a permissions conversation. Sharing the **agent** does not share the **data** - a point worth repeating because it's the number one support ticket across every integration in this module.

<p><img style="margin: 0px 15px 15px 0px;" src="../graphics/checkmark.png"><b>How identity flows through each integration</b></p>

The mechanism has a different name in each service, but it's the same idea every time:

| Integration | How identity reaches Fabric |
| --- | --- |
| **Microsoft Foundry** | Identity Passthrough (On-Behalf-Of). The end user's identity flows through the Azure AI agent into Fabric. |
| **Copilot Studio / Teams** | **User authentication** mode passes each user's identity. **Agent author authentication** runs as *you* - choose deliberately. |
| **Python client SDK** | `InteractiveBrowserCredential` - the user signs in with their own Entra ID credentials in a browser. |
| **Microsoft 365 Copilot** | The signed-in Microsoft 365 user's identity, same tenant, same account. |
| **MCP server** | A bearer token in the `Authorization` header, representing a user **or** a service principal. |

Notice the one row that can break the pattern: **Agent author authentication** in Copilot Studio. That mode is legitimate - it's how you build an agent over data your users can't individually access but are allowed to see aggregated. But it moves the security boundary from Entra to *your agent's instructions*, and instructions are not a security control. Use it on purpose, document it, and never use it as a shortcut around a permissions request you didn't feel like filing.

<p><img style="margin: 0px 15px 15px 0px;" src="../graphics/checkmark.png"><b>When there is no user - service principal authentication</b></p>

Identity passthrough is elegant right up until 3am, when there is no human to pass through. Scheduled jobs, background services, CI/CD pipelines, and unattended applications need a non-interactive identity - and for that, Fabric data agents support **Microsoft Entra service principals (SPN)**.

An SPN is a non-interactive, application-based identity that you can grant precise permissions on Azure and Fabric resources. Critically, **the data agent treats an SPN exactly like any other Entra identity**. The rules don't relax because a robot is asking. The SPN only reads schemas and runs queries against the data sources *it* has been granted access to.

Setting one up is five steps:

1. **Register the application in Microsoft Entra ID.** In the <a href="https://entra.microsoft.com">Microsoft Entra admin center</a> go to **Entra ID** → **App registrations** → **New registration**. Name it something you'll recognize in an audit log six months from now - `fabric-data-agent-spn` beats `test2`. Set **Supported account types** to *Accounts in this organizational directory only*. Copy the **Application (client) ID** and **Directory (tenant) ID**, then add a credential - a certificate or federated identity credential if your security policy allows, a client secret if it doesn't. You need at least the **Cloud Application Administrator** role to do this yourself; otherwise ask your Entra admin for the App ID, secret, and tenant ID.
2. **Enable service principals to use Fabric APIs.** A Fabric tenant admin goes to the <a href="https://learn.microsoft.com/en-us/fabric/admin/admin-center">Fabric admin portal</a> → **Tenant settings** → **Developer settings** and enables **Service principals can use Fabric APIs**. Scope it to a security group containing your SPN rather than the entire organization, unless you enjoy explaining that decision later.
3. **Grant the SPN access to the workspace.** A workspace **Admin** or **Member** opens the workspace → **Manage access** → **Add people or groups**, searches for the SPN by app name, and assigns **Member** or **Contributor**. Only give it **Admin** if it genuinely needs to manage the workspace.
4. **Grant the SPN access to the data sources.** This is the step people miss. At minimum read access on *every* source attached to the agent. Sharing the data agent item is not enough.
5. **Acquire a token and call the agent.** The SPN authenticates to Entra using the <a href="https://learn.microsoft.com/en-us/entra/identity-platform/v2-oauth2-client-creds-grant-flow">client credentials flow</a>, requesting a token for the Fabric resource (`https://analysis.windows.net/powerbi/api/.default`), and passes the result as a bearer token when asking the agent questions. That endpoint is for *querying* the agent with natural language - it isn't for managing or configuring it.

<p><img style="margin: 0px 15px 15px 0px;" src="../graphics/checkbox.png"><b>Three limitations to write on the whiteboard now</b></p>

- **Managed identities are not currently supported.** You have to use a service principal. If your platform standard is "managed identity everywhere," this is a conversation to have before you commit to a delivery date.
- **The SPN needs explicit access to every data source.** Again. Because it's the one that gets you.
- **Service principal authentication is not yet supported for data agents connected to a KQL database (Kusto).** If your agent has a KQL source, unattended access is off the table for now.

<p><img style="margin: 0px 15px 15px 0px;" src="../graphics/checkmark.png"><b>Finally - watch what it actually did</b></p>

Security isn't only about prevention, it's about being able to answer "who asked what, and what did the system do about it" after the fact. Fabric data agent interactions can be audited through Microsoft Purview, and Foundry gives you observability on the agent side. Wire both up before you go to production, not after someone asks for them in an incident review. Links are in the activity below.

<p><a href="https://youtu.be/1OOe9-EteL0"><img src="https://img.youtube.com/vi/1OOe9-EteL0/0.jpg" height = 200></a></p>

<p><img style="float: left; margin: 0px 15px 15px 0px;" src="../graphics/point1.png"><b>Activity: Prove the security boundary, then automate it</b></p>

<p><img style="margin: 0px 15px 15px 0px;" src="../graphics/checkmark.png"><b>Steps</b></p>

- Apply row-level security to one of your data agent's underlying sources if it doesn't already have it.
- Have two users with different entitlements ask the agent the *same* question. Confirm they get different, correct answers. This is the demo that ends the argument.
- Open the following link in another tab and follow the instructions: <a href="https://learn.microsoft.com/en-us/fabric/data-science/data-agent-service-principal">Use service principal authentication with Fabric data agent</a>
- Register a service principal, enable **Service principals can use Fabric APIs**, and grant it workspace **and** data source access.
- Call your data agent with the SPN using the client credentials flow. Then *deliberately* remove its access to one data source and call it again - watch it fail exactly the way it should.
- Review <a href="https://learn.microsoft.com/en-us/fabric/data-science/data-agent-purview-governance">Audit data agent interactions with Microsoft Purview</a> and confirm you can see the interactions.
- Review <a href="https://learn.microsoft.com/en-us/fabric/data-science/data-agent-sharing">Fabric data agent sharing and permission management</a> and document who has which role on your agent.

> If you only reviewed the documentation in this Activity, ensure you bookmark each of these references and then perform the Activity in full once you do have your deployment.

<p style="border-bottom: 1px solid lightgrey;"></p>

<h2 id="7-6"><img style="float: left; margin: 0px 15px 15px 0px;" src="../graphics/pencil2.png">7.6 - Data Agent as a Model Context Protocol (MCP) Server</h2>

Everything in sections 7.1 through 7.4 is a *named* integration. Microsoft built a connector for Foundry, one for Copilot Studio, one for Microsoft 365. That's great - right up until you want to use something Microsoft didn't build a connector for.

The **Model Context Protocol (MCP)** is the answer to that problem. It's an emerging open standard that defines how an AI system discovers what tools are available and interacts with them in a consistent way. Instead of writing a bespoke integration for every client, you expose your capability once and any MCP-speaking client can use it.

MCP has two halves:

- An **MCP client** is the app the user interacts with - where you ask questions or trigger actions. Visual Studio Code acts as an MCP client when it connects to external tools.
- An **MCP server** exposes tools, data, or services and tells the client what's available and how to use it.

Your published Fabric data agent can be an MCP server. And when it is, the agent stops being "a thing with four supported front ends" and becomes a standard endpoint. That's why this section exists even though it's listed last - strategically it may end up being the most important one on this page.

<p><img style="margin: 0px 15px 15px 0px;" src="../graphics/checkmark.png"><b>How it works</b></p>

A published data agent exposes exactly **one MCP tool**, and that tool *is* the agent. A client sends a question to the tool and gets back an answer grounded in the data the agent can reach in OneLake.

Because the client decides when to call the tool, **your published description becomes the tool description the MCP server advertises**. Third time this module has told you to write a good description, and this is the most literal version of it: orchestrators read that text to decide whether to call your agent at all. A vague description means your beautifully tuned agent sits there never being invoked, and you'll blame the model.

<p><img style="margin: 0px 15px 15px 0px;" src="../graphics/checkbox.png"><b>"MCP client" doesn't mean a product</b></p>

Anything that speaks MCP is an MCP client. It doesn't have to be VS Code, and it doesn't have to use a particular SDK - it just has to follow the protocol. That matters because **this is not a plain REST API**. A connection follows the MCP message flow: an `initialize` handshake, a `tools/list` call to discover the tool, then `tools/call` to ask a question. An SDK like the <a href="https://pypi.org/project/mcp/">MCP Python SDK</a> handles that for you; you can also implement it yourself over HTTP. What won't work is firing a generic HTTP POST at the endpoint and skipping the handshake. If you take one troubleshooting note from this section, take that one.

Also note: the data agent MCP server **doesn't support dynamic client registration**. Your client can't register itself and obtain credentials through the protocol. You acquire a Fabric token through your own auth flow and attach it to every request.

<p><img style="margin: 0px 15px 15px 0px;" src="../graphics/checkmark.png"><b>Getting the endpoint</b></p>

After you publish the agent, open its **Settings** and go to the **Model Context Protocol** tab. You'll find the MCP server name, the **MCP server URL**, the MCP tool name, and the tool description. You can also download an **mcp.json** file from that tab for clients that read that format - VS Code, for instance.

Or build the URL yourself:

```http
https://api.fabric.microsoft.com/v1/mcp/workspaces/{WorkspaceId}/dataagents/{DataAgentId}/agent
```

A hand-built URL only works **after** the agent is published. If it isn't, the endpoint returns an error even when the URL is perfectly correct - which is a fun forty minutes if you don't know that going in.

<p><img style="margin: 0px 15px 15px 0px;" src="../graphics/checkmark.png"><b>Authentication</b></p>

Every request needs a bearer token in the `Authorization` header, with permission on the target workspace and data agent. The token can represent a **user** or a **service principal** - which is exactly where section 7.5 comes back around. Request the token for the `https://api.fabric.microsoft.com/.default` scope. VS Code prompts you to sign in interactively; in a script you acquire the token yourself with <a href="https://pypi.org/project/azure-identity/">azure-identity</a>.

<p><img style="margin: 0px 15px 15px 0px;" src="../graphics/checkmark.png"><b>Connecting from Python</b></p>

You'll need Python 3.10+, the packages, and a way to sign in to Fabric. This example uses the Azure CLI - run `az login` first with an account that has access to the workspace and agent.

```bash
pip install mcp azure-identity
```

```python
import asyncio

from azure.identity import AzureCliCredential
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

workspace_id = "<your-workspace-id>"
data_agent_id = "<your-data-agent-id>"
question = "<your question>"

mcp_url = (
    f"https://api.fabric.microsoft.com/v1/mcp/workspaces/{workspace_id}"
    f"/dataagents/{data_agent_id}/agent"
)

credential = AzureCliCredential()

def get_auth_headers():
    token = credential.get_token("https://api.fabric.microsoft.com/.default")
    return {"Authorization": f"Bearer {token.token}"}
```

Now open the connection, run the handshake, discover the tool, and ask:

```python
async def query_data_agent(question):
    headers = get_auth_headers()

    async with streamablehttp_client(mcp_url, headers=headers) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # The data agent exposes a single tool. Discover it, then call it.
            tools = await session.list_tools()
            tool = tools.tools[0]
            question_arg = next(iter(tool.inputSchema["properties"]))

            result = await session.call_tool(tool.name, {question_arg: question})

            answers = [block.text for block in result.content if block.type == "text"]
            return "\n".join(answers)

answer = asyncio.run(query_data_agent(question))
print(answer)
```

Note the small piece of good engineering in there: the script reads the *first* tool the server advertises and pulls the question argument name out of the tool's input schema instead of hard-coding it. If the tool name or argument name changes, your code keeps working. Steal that pattern.

`AzureCliCredential` reuses your `az login` session, which is fine for development. To run unattended, swap in `ClientSecretCredential` or `DefaultAzureCredential` with a service principal - **the rest of the code is identical**. That's the whole payoff of section 7.5.

<p><img style="margin: 0px 15px 15px 0px;" src="../graphics/checkmark.png"><b>Connecting from Visual Studio Code</b></p>

1. Open a folder in VS Code and create a **.vscode** folder inside it.
2. Create a file named `mcp.json` in **.vscode**.
3. Select the blue **Add Server** button at the bottom right, choose **HTTP**, and paste the **MCP server URL**.
4. Press **Enter** and give the server a display name.
5. VS Code attempts to authenticate - select **Allow** and sign in.

Then turn on agent mode: **Command Palette** (Ctrl+Shift+P) → **Enable Agent Mode** → confirm the prompts. Pick an orchestrator - in preview the list includes GPT-5, GPT-4.1, Claude Sonnet 4.5, and Gemini 2.5 Pro among others - and start asking questions right in the editor. The orchestrator routes each question to the data agent MCP server and the agent answers from OneLake.

Sit with that for a second. Your governed enterprise data, grounded and permission-checked, answering questions inside the editor while a developer is writing code against it. No export. No copy of the data. No screenshot pasted into a chat.

<p><img style="margin: 0px 15px 15px 0px;" src="../graphics/checkbox.png"><b>The compliance note, one last time</b></p>

When you consume a data agent as an MCP server, responses may be sent outside Fabric's compliance boundary or geographic region and are processed and stored according to the terms and data-handling policies of **whichever MCP client you use**. With named integrations you at least know whose policy applies. With an open protocol, that's now a question you have to ask about every client your organization adopts. Add it to your review checklist.

<p><img style="float: left; margin: 0px 15px 15px 0px;" src="../graphics/point1.png"><b>Activity: Stand up your data agent as an MCP server</b></p>

<p><img style="margin: 0px 15px 15px 0px;" src="../graphics/checkmark.png"><b>Steps</b></p>

- Open the following link in another tab and follow the instructions: <a href="https://learn.microsoft.com/en-us/fabric/data-science/data-agent-mcp-server">Data agent as Model Context Protocol server (preview)</a>
- Publish your data agent, then open **Settings** → **Model Context Protocol** and copy the **MCP server URL**. Download the **mcp.json** while you're there.
- Connect from Python with the MCP SDK. Run `az login` first, then ask a question and print the answer.
- Add the same server to Visual Studio Code, enable **Agent Mode**, and ask the same question from the editor. Compare the two answers.
- Swap `AzureCliCredential` for a service principal credential from section 7.5 and run the Python client unattended.
- Read your agent's published description as though you were an orchestrator deciding whether to call it. If you wouldn't call it, rewrite it.
- If you built anything on the Python client SDK in section 7.3, sketch your migration to this endpoint. Remember the **August 26, 2026** Assistants API shutdown date.

> If you only reviewed the documentation in this Activity, ensure you bookmark each of these references and then perform the Activity in full once you do have your deployment.

<p style="border-bottom: 1px solid lightgrey;"></p>

<h2 id="7-7"><img style="float: left; margin: 0px 15px 15px 0px;" src="../graphics/pencil2.png">7.7 - Source Control, CI/CD, and ALM for Data Agents</h2>

Here's a question that separates a demo from a production system: **where does your data agent's configuration actually live?**

If the honest answer is "in the Fabric portal, in the workspace, where Dave configured it," then you don't have a data agent. You have a very expensive tribal knowledge artifact with a single point of failure named Dave. Someone edits the AI instructions on a Thursday, the answers get worse on Friday, and there is no way to see what changed or roll it back.

The fix is the same fix it's always been for everything else in your platform: put it in source control and promote it through environments. Fabric supports both, and it does it in a way that will feel completely familiar to anyone who's ever managed a codebase. Source control for Fabric data agents is currently in **preview**.

You have two complementary tools:

- **Git integration** - sync an entire workspace with a Git repository (Azure DevOps or GitHub) for version control, branch-based collaboration, and history.
- **Deployment pipelines** - promote content between separate workspaces representing development, test, and production.

Together those give you end-to-end ALM. Use both.

<p><img style="margin: 0px 15px 15px 0px;" src="../graphics/checkmark.png"><b>Git integration</b></p>

You connect a workspace to a Git repo from **Workspace settings**. Once connected, your workspace items - data agents included - show up in the **Source control** pane, and the status bar at the bottom left shows the connected branch, last sync time, and Git commit ID.

The Git folder structure mirrors the workspace structure, with each data agent in its own folder. That means you get diffs, history, reverts, and pull requests on your data agent, exactly like any other artifact.

Recent enhancements worth knowing: Fabric now supports **selective branching**, so you can switch the connected branch at the workspace level to line up with feature branch workflows, and the Source control pane has a built-in **diff experience** so you can see exactly what changed before you commit or pull.

<p><img style="margin: 0px 15px 15px 0px;" src="../graphics/checkbox.png"><b>What counts as a change</b></p>

Once the workspace is Git-connected, the data agent flips to **Uncommitted changes** when you:

- Change the schema selection
- Update AI instructions or data source instructions
- Edit example queries
- Publish the data agent, or update its publishing description

Note that last one. **Editing the publishing description is a tracked change.** Given how much this module has hammered on writing a good description - it drives the Copilot Studio picker, the M365 `description_for_model`, and the MCP tool description - it's genuinely good news that description edits are versioned like code. When somebody "improves" the description and your agent stops getting invoked, you can diff it.

The flow goes both directions. Change something in Fabric, and it appears under the **Changes** tab to review and commit. Change something in the repo and push it, and Fabric shows an **Updates available** notification with the item under the **Updates** tab, where you review and accept.

<p><img style="margin: 0px 15px 15px 0px;" src="../graphics/checkmark.png"><b>What the files actually look like</b></p>

This is the part worth understanding properly, because once you can read these files you can review a data agent change in a pull request without opening Fabric at all.

At the root, data agent content lives under a **files** folder, which contains a **config** folder holding:

```
files/
└── config/
    ├── data_agent.json
    ├── publish_info.json
    ├── draft/
    └── published/
```

- **publish_info.json** holds the publishing description. Edit this file to change the description that appears when the agent is published.
- **draft/** holds the configuration for the draft version.
- **published/** mirrors the draft structure but represents the published version.

Inside **draft/** you get **stage_config.json** - which contains `aiInstructions`, your agent instructions - plus one folder per data source, named by type:

| Data source | Folder prefix |
| --- | --- |
| Lakehouse | `lakehouse-tables-` |
| Warehouse | `warehouse-tables-` |
| Semantic model | `semantic-model-` |
| KQL database | `kusto-` |
| Ontology | `ontology-` |

Each data source folder contains **datasource.json** and **fewshots.json**. (Semantic models don't support example queries, so those folders only get **datasource.json**.)

**datasource.json** defines the source config:

- `dataSourceInstructions` - the instructions for that specific source
- `displayName` - the source name
- `elements` - the schema map, a complete list of tables and columns

Each table and column carries an `is_selected` property, and there's a wrinkle here you need to know: **column-level selection isn't currently supported.** If a table is selected, *all* of its columns are included regardless of what the column-level `is_selected` says. If the table is `false`, none of its columns are considered even if they're individually marked `true`. Don't spend an afternoon toggling column flags expecting them to do something.

Types follow a simple convention: `"lakehouse_tables"` for the source, `"lakehouse_tables.table"` for a table, `"lakehouse_tables.column"` for a column.

**fewshots.json** stores your example queries, each with an `id`, a `question` in natural language, and the `query` text (SQL or KQL depending on source type). Your carefully tuned few-shot examples are now reviewable text files. Put them through code review like anything else that determines whether the answer is right.

<p><img style="margin: 0px 15px 15px 0px;" src="../graphics/checkbox.png"><b>Do not edit the published folder</b></p>

Make your changes in **draft/**. When you publish the agent, those changes flow into **published/**. Editing **published/** directly bypasses the controlled draft state, which is the entire point of having two folders. Treat it as generated output.

<p><img style="margin: 0px 15px 15px 0px;" src="../graphics/checkmark.png"><b>Deployment pipelines</b></p>

Deployment pipelines move data agents between workspaces mapped to lifecycle stages:

1. Build or update the agent in the **development** workspace.
2. Promote to **test** for validation.
3. Promote to **production** where end users consume it.

Assign a workspace to each stage first. If you skip test or production, Fabric creates them for you, named after the development workspace with `[test]` or `[prod]` appended. To deploy, open the stage you're deploying from, select the items, and select **Deploy**. You can review a deployment plan before applying so only intended updates get promoted. Source and target workspaces must be **in the same tenant**.

<p><img style="margin: 0px 15px 15px 0px;" src="../graphics/checkbox.png"><b>Publishing and the dev/prod boundary</b></p>

This is the single most important operational rule in this section, and it trips up teams who otherwise have great ALM discipline.

**An unpublished data agent is not consumable - even in the production workspace.** Every channel in this module (Power BI Copilot, Copilot Studio, Foundry, M365, MCP) requires a published agent. Sitting in prod is not enough.

Which creates an obvious tension: you also need to publish in *development* to evaluate performance across those same channels. Both things are true, so handle it deliberately:

- **Publishing from development should be restricted to authorized users** who are actively developing the agent and assessing it. Lock that workspace down so half-finished, experimental agents don't leak to a broad audience.
- **End users should only ever consume agents published from production.** Stable, approved versions only.

If you don't draw that line, someone's going to `@`-mention your Tuesday afternoon experiment in a Teams channel full of executives.

<p><img style="margin: 0px 15px 15px 0px;" src="../graphics/checkmark.png"><b>Automating it</b></p>

If Fabric's built-in deployment pipelines aren't enough - or you want data agent promotion sitting in the same pipeline as everything else you ship - the <a href="https://marketplace.visualstudio.com/items?itemName=ms-fabric.fabric-devops-pipelines">Azure DevOps Pipelines extension for Fabric</a> provides native tasks that run <a href="https://go.microsoft.com/fwlink/?linkid=2313665">Fabric CLI</a> commands in pipeline jobs. Install the extension from the Marketplace, set up a service connection in your Azure DevOps project, and add Fabric CLI tasks to your pipeline definition. You can use this alongside Fabric deployment pipelines or instead of them.

For large-scale synchronization, the **Import/Export Item Definitions Batch APIs** (preview) let you export and import data agent definitions in bulk to streamline promotion across environments. See the <a href="https://learn.microsoft.com/en-us/rest/api/fabric/">Fabric REST API documentation</a>.

<p><img style="margin: 0px 15px 15px 0px;" src="../graphics/checkbox.png"><b>One preview wrinkle to verify yourself</b></p>

The ALM documentation states that service principals are supported in the Fabric data agent **only** as part of ALM scenarios - Git integration and deployment pipelines - and not for other data agent features. Meanwhile the service principal documentation covered back in section 7.5 walks you through using an SPN to call a published agent with a bearer token.

Both pages are current, both features are in preview, and preview surface areas move fast. Before you architect an unattended solution around SPN *querying*, validate it in your own tenant and check both docs for updates. This is exactly the kind of thing that changes between when a workshop is written and when you deliver it - and now you know to look.

<p><img style="margin: 0px 15px 15px 0px;" src="../graphics/checkmark.png"><b>Best practices</b></p>

Straight from the field, and none of these will surprise you:

- Use a **dedicated branch** for data agent development and merge to main after code review.
- Keep related resources - data sources, data agents, notebooks, pipelines - **in the same workspace** so they promote together.
- **Test in the test workspace** before promoting to production.
- Write **descriptive commit messages**. "updated instructions" tells future-you nothing.
- **Never edit the published folder directly.**
- Use **environment-agnostic configuration** - connection references via Variable Library where supported - instead of hardcoding environment-specific values into data source configs. This is what makes branch merges and dev→test→prod deployments stop hurting.

<p><img style="margin: 0px 15px 15px 0px;" src="../graphics/checkbox.png"><b>Limitations and considerations</b></p>

- Only workspaces **connected to a Git repository** can use Git-based ALM features.
- Service principals in data agents are supported **only for ALM scenarios** (see the wrinkle above).
- Deployment pipelines require source and target workspaces **in the same tenant**.
- Large numbers of frequent commits can impact repository size and performance.

<p><img style="float: left; margin: 0px 15px 15px 0px;" src="../graphics/point1.png"><b>Activity: Put your data agent under source control and promote it</b></p>

<p><img style="margin: 0px 15px 15px 0px;" src="../graphics/checkmark.png"><b>Steps</b></p>

- Open the following link in another tab and follow the instructions: <a href="https://learn.microsoft.com/en-us/fabric/data-science/data-agent-source-control">Source Control, CI/CD, and ALM for Fabric data agent</a>
- Review <a href="https://learn.microsoft.com/en-us/fabric/cicd/git-integration/git-get-started?tabs=azure-devops,Azure,commit-to-git">Get started with Git integration</a> and connect your workspace to Azure DevOps or GitHub.
- Commit your data agent. Then go read the files in the repo - open **stage_config.json**, a **datasource.json**, and a **fewshots.json**. Make sure you can find your AI instructions and your example queries in there.
- Make a change *in Fabric* - add an example query - and review the diff in the **Source control** pane before committing.
- Now make a change *in the repo* - edit `dataSourceInstructions` in a text editor - push it, and accept the update in Fabric. Confirm the agent's behavior actually changed.
- Review <a href="https://learn.microsoft.com/en-us/fabric/cicd/deployment-pipelines/get-started-with-deployment-pipelines?tabs=from-fabric,new-ui">Get started with deployment pipelines</a>, then build a dev → test → prod pipeline and promote your agent.
- Publish from **production** and confirm it's consumable through one of the channels from sections 7.1 - 7.6. Then confirm an unpublished agent in prod is *not*.
- Stretch goal: install the <a href="https://marketplace.visualstudio.com/items?itemName=ms-fabric.fabric-devops-pipelines">Azure DevOps Pipelines extension for Fabric</a> and automate the promotion with Fabric CLI tasks.

> If you only reviewed the documentation in this Activity, ensure you bookmark each of these references and then perform the Activity in full once you do have your deployment.

<p style="border-bottom: 1px solid lightgrey;"></p>

<h2 id="7-8"><img style="float: left; margin: 0px 15px 15px 0px;" src="../graphics/pencil2.png">Choosing Between Them</h2>

Five doors, one agent. Here's the short version to steal for your own architecture review:

| If you need... | Use | Watch out for |
| --- | --- | --- |
| A developer-built AI agent with multiple tools and actions | **Microsoft Foundry** | One Fabric data agent per Azure AI agent; needs `AI Developer` RBAC |
| Low-code, business-built agents delivered in Teams | **Copilot Studio** | Only validated for Teams; must enable generative AI orchestration; not supported in M365 Copilot |
| Your own app, custom UX, or automation | **Python client SDK** | Assistants API shuts down **Aug 26, 2026** - plan the MCP migration |
| Broad reach to business users already in Teams | **Microsoft 365 Copilot** | M365 orchestrator reshapes responses; per-user licensing |
| Any MCP-speaking client, or a future-proof endpoint | **MCP server** | Must follow the MCP handshake; no dynamic client registration; client's data policy applies |
| Unattended jobs, pipelines, background services | **Service principal** (with any of the above) | No managed identity support; not supported with KQL sources |

And the thing that's true of all of them: publish the agent, write a genuinely good description, keep everyone on one tenant, get the tenant switches enabled, and let Entra ID carry the security. Do those five things and the rest is mostly clicking - and once it works, get it into Git so it stays working.

<p style="border-bottom: 1px solid lightgrey;"></p>

<p><img style="margin: 0px 15px 15px 0px;" src="../graphics/owl.png"><b>For Further Study</b></p>
<ul>
  <li><a href="https://learn.microsoft.com/en-us/fabric/data-science/concept-data-agent">What is the Fabric data agent?</a></li>
  <li><a href="https://learn.microsoft.com/en-us/fabric/data-science/data-agent-tenant-settings">Fabric data agent tenant settings</a></li>
  <li><a href="https://learn.microsoft.com/en-us/fabric/data-science/data-agent-sharing">Fabric data agent sharing and permission management</a></li>
  <li><a href="https://learn.microsoft.com/en-us/fabric/data-science/data-agent-foundry">Consume a data agent in Microsoft Foundry (preview)</a></li>
  <li><a href="https://learn.microsoft.com/en-us/fabric/data-science/data-agent-microsoft-copilot-studio">Consume a data agent in Microsoft Copilot Studio (preview)</a></li>
  <li><a href="https://learn.microsoft.com/en-us/fabric/data-science/consume-data-agent-python">Consume a data agent using the Python SDK (preview)</a></li>
  <li><a href="https://learn.microsoft.com/en-us/fabric/data-science/data-agent-microsoft-365-copilot">Consume a data agent from Microsoft 365 Copilot (preview)</a></li>
  <li><a href="https://learn.microsoft.com/en-us/fabric/data-science/data-agent-mcp-server">Consume a data agent as a Model Context Protocol Server (preview)</a></li>
  <li><a href="https://learn.microsoft.com/en-us/fabric/data-science/data-agent-copilot-powerbi">Consume a data agent from Copilot in Power BI (preview)</a></li>
  <li><a href="https://learn.microsoft.com/en-us/fabric/data-science/fabric-data-agent-foundry-observability">Observe a Fabric data agent with Microsoft Foundry</a></li>
  <li><a href="https://learn.microsoft.com/en-us/fabric/data-science/data-agent-purview-governance">Audit data agent interactions with Microsoft Purview</a></li>
  <li><a href="https://learn.microsoft.com/en-us/fabric/data-science/data-agent-service-principal">Service principal support for Fabric data agents</a></li>
  <li><a href="https://learn.microsoft.com/en-us/fabric/data-science/data-agent-source-control">Source control, CI/CD, and ALM for Fabric data agents</a></li>
  <li><a href="https://learn.microsoft.com/en-us/fabric/cicd/git-integration/intro-to-git-integration">What is Microsoft Fabric Git integration?</a></li>
  <li><a href="https://learn.microsoft.com/en-us/fabric/cicd/deployment-pipelines/get-started-with-deployment-pipelines">Get started with deployment pipelines</a></li>
  <li><a href="https://marketplace.visualstudio.com/items?itemName=ms-fabric.fabric-devops-pipelines">Azure DevOps Pipelines extension for Fabric</a></li>
  <li><a href="https://www.youtube.com/@Tales-from-the-Field">Tales from the Field on YouTube</a></li>
  <li><a href="https://learn.microsoft.com/en-us/fabric/fundamentals/whats-new">As always, this is a fast-changing technology, so ensure you check this reference to find the latest improvements.</a></li>
</ul>

<p style="border-bottom: 1px solid lightgrey;"></p>

Congratulations! You have completed this Module. Your data agent is no longer something that lives in a portal - it's an endpoint your organization can reach from wherever they already work, with Entra ID keeping the governance intact at every door. You now have the tools, assets, and processes you need to extrapolate this information into other applications.
