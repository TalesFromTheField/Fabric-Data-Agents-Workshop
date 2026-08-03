![](../graphics/microsoftlogo.png)

# Workshop: Microsoft Fabric Data Agents and Beyond

#### <i>A workshop from the Tales from the Field team</i>

<p style="border-bottom: 1px solid lightgrey;"></p>

<img style="float: left; margin: 0px 15px 15px 0px;" src="../graphics/textbubble.png"> <h2> 07 - Extending Data Agents Beyond Microsoft Fabric </h2>

In this module you'll cover taking the Fabric data agent you built in the previous modules and putting it in front of the people who actually need it - in Microsoft Foundry, in Copilot Studio and Teams, in your own Python applications, and in Microsoft 365 Copilot.

In each module you'll get more references, which you should follow up on to learn more. Also watch for links within the text - click on each one to explore that topic.

(<a href="https://github.com/TalesFromTheField/Fabric-Data-Agents-Workshop/blob/main/modules/00%20-%20Pre-Requisites.md">Make sure you check out the <b>Pre-Requisites</b> page before you start</a>. You'll need all of the items loaded there before you can proceed with the workshop.) *Note that every integration in this module requires a paid **F2 or higher** Fabric capacity (or a P1 or higher Power BI Premium capacity with Fabric enabled), a **published** data agent, and the AI cross-geo tenant settings turned on. All four of these consumption paths are currently in **preview**.

Here's the thing nobody tells you when you build your first data agent: the hard part is already done. You picked the data sources. You wrote the instructions. You added the example queries and argued with the model about what "active customer" actually means. That work - the semantics, the grounding, the security model - is the agent. The Fabric portal is just the first place you happened to talk to it.

This module is about the second, third, fourth, and fifth places. And the good news is you don't rebuild anything. A published Fabric data agent is an endpoint with an identity attached, and every integration in this module is a different front door to that same endpoint. Row-level security still applies. Column-level security still applies. If a user can't see the table in the lakehouse, they can't get an answer about it from Teams either. That's not a limitation, that's the whole point.

You'll cover these topics in this Module on Extending Data Agents Beyond Microsoft Fabric:

<dl>

  <dt><a href="#7-1">7.1 - Connecting to Data Agents via Microsoft Foundry</a></dt>
  <dt><a href="#7-2">7.2 - Connecting to Data Agents via Copilot Studio &amp; Teams</a></dt>
  <dt><a href="#7-3">7.3 - Connecting to Data Agents via the Python SDK</a></dt>
  <dt><a href="#7-4">7.4 - Connecting to Data Agents via Microsoft 365</a></dt>

</dl>

<p style="border-bottom: 1px solid lightgrey;"></p>

<h2 id="7-0"><img style="float: left; margin: 0px 15px 15px 0px;" src="../graphics/pencil2.png">Before You Start - Three Things That Break Everything</h2>

Every single integration in this module fails in exactly the same three ways, so let's get them out of the way once instead of four times.

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

<h2 id="7-5"><img style="float: left; margin: 0px 15px 15px 0px;" src="../graphics/pencil2.png">Choosing Between Them</h2>

Four doors, one agent. Here's the short version to steal for your own architecture review:

| If you need... | Use | Watch out for |
| --- | --- | --- |
| A developer-built AI agent with multiple tools and actions | **Microsoft Foundry** | One Fabric data agent per Azure AI agent; needs `AI Developer` RBAC |
| Low-code, business-built agents delivered in Teams | **Copilot Studio** | Only validated for Teams; must enable generative AI orchestration; not supported in M365 Copilot |
| Your own app, custom UX, or automation | **Python client SDK** | Assistants API shuts down **Aug 26, 2026** - plan the MCP migration |
| Broad reach to business users already in Teams | **Microsoft 365 Copilot** | M365 orchestrator reshapes responses; per-user licensing |

And the thing that's true of all four: publish the agent, write a genuinely good description, keep everyone on one tenant, get the tenant switches enabled, and let user identity carry the security. Do those five things and the rest is mostly clicking.

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
  <li><a href="https://www.youtube.com/@Tales-from-the-Field">Tales from the Field on YouTube</a></li>
  <li><a href="https://learn.microsoft.com/en-us/fabric/fundamentals/whats-new">As always, this is a fast-changing technology, so ensure you check this reference to find the latest improvements.</a></li>
</ul>

<p style="border-bottom: 1px solid lightgrey;"></p>

Congratulations! You have completed this Module. Your data agent is no longer something that lives in a portal - it's an endpoint your organization can reach from wherever they already work, with the governance intact. You now have the tools, assets, and processes you need to extrapolate this information into other applications.
