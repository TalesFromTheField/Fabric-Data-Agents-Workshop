![](../graphics/microsoftlogo.png)

# Workshop: Microsoft Fabric Data Agents and Beyond

#### <i>A workshop from the Tales from the Field team</i>

<p style="border-bottom: 1px solid lightgrey;"></p>

<h2 id="03"><img style="float: left; margin: 0px 15px 15px 0px;" src="../graphics/textbubble.png">03 - Fabric Data Agents - In Use</h2>

You finished Module 02 with a published data agent. It runs, it answers questions, and - if you're honest about it - it probably answers some of them wrong.

That gap is the subject of this module. A data agent that has been created and published is not a finished product; it's a starting configuration. Tuning a data agent isn't a one-time setup, it's an ongoing process of experimentation, observation, and refinement. Every environment is different, and you should expect cycles of trial and error before the agent behaves the way your business needs it to.

This module covers the four levers you pull to close that gap - **agent instructions**, **example queries**, **data source instructions**, and **data source routing** - and then the two disciplines that turn a tuned agent into a managed asset: **security** and **CI/CD**. The module closes with a consolidated set of best practices you can take back to your own tenant.

In each section you'll get more references, which you should follow up on to learn more. Also watch for links within the text - click on each one to explore that topic.

(<a href="00%20-%20Pre-Requisites.md">Make sure you check out the <b>Pre-Requisites</b> page before you start</a>. You'll need all of the items loaded there before you can proceed with the workshop.)

You'll cover these topics in this module:

<dl>

  <dt><a href="#3.1">3.1 - Data Agent Instructions</a></dt>
  <dt><a href="#3.2">3.2 - Using Example Queries</a></dt>
  <dt><a href="#3.3">3.3 - Data Source Instructions</a></dt>
  <dt><a href="#3.4">3.4 - Data Agents with Multiple Data Sources</a></dt>
  <dt><a href="#3.5">3.5 - Data Agents and Security</a></dt>
  <dt><a href="#3.6">3.6 - Data Agents and CI/CD</a></dt>

</dl>

<p style="border-bottom: 1px solid lightgrey;"></p>

<h2 id="3.1"><img style="float: left; margin: 0px 15px 15px 0px;" src="../graphics/pencil2.png">3.1 Data Agent Instructions</h2>

Instructions are how you put *business context* into an agent that only has *schema*. The agent can read your table and column names, but it has no idea that your fiscal year starts in July, that "GMV" means Gross Merchandise Value, or that when someone in your company says "sales" they mean net of returns.

[Data agent instructions](https://learn.microsoft.com/en-us/fabric/data-science/data-agent-configurations#data-agent-instructions) guide the agent in generating accurate and relevant responses to user questions. They operate at the **agent level**, above any individual data source, and they're the right place for three kinds of guidance:

- Which data sources to prioritize, and in what order.
- How to handle certain types of queries.
- Terminology and context that help the agent interpret user intent.

Instructions live in the agent's configuration pane, alongside the data source explorer you used in Module 02.

<p><img style="box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.19);" src="https://learn.microsoft.com/en-us/fabric/data-science/media/how-to-create-data-agent/configuration-agent-instructions.png" height="400"></p>

### A starting format

Microsoft publishes a recommended starting format for agent-level instructions. Don't treat it as a form to fill in - treat it as a checklist of the things an agent needs to know that it can't learn from a schema.

```md
## Objective
// Describe the overall goal of the agent.
// Example: "Help users analyze retail sales performance and customer behavior across regions."

## Data sources
// Specify which data sources the agent should consider, and in what order of priority.
// Example: "Use 'SalesLakehouse' for product and transaction data. Use 'CRMModel' for customer demographics."

## Key terminology
// Define terms or acronyms the agent may encounter in user queries.
// Example: "'GMV' refers to Gross Merchandise Value."

## Response guidelines
// Set expectations for how the agent should format or present answers.

## Handling common topics
// Provide special handling rules or context for frequently asked topics.
// Example: "When asked about customers, use the 'ChurnModelScoring' Lakehouse to get customer details. Then, list any open support tickets"
```

### Agent-level or data source-level?

You have two places to write instructions, and choosing wrongly is one of the most common reasons tuning doesn't stick. The rule is scope:

- **Agent-level instructions** carry definitions and behavior that apply *across all* data sources and queries - for example, what a "quarter" represents in your organization.
- **Data source instructions** (section 3.3) carry definitions that are specific to *how a term is used within one dataset* - for example, "sales" being defined differently in two source systems.

A useful test when you're writing agent instructions: *would someone unfamiliar with these data sources be able to understand which sources to use, and how to use them, from these instructions alone?* If not, you're missing context the agent is also missing.

### Say what to do, not what to avoid

Negative instructions leave the agent with nowhere to go. Give it the correct path instead.

❌ **Less effective:** Do not provide outdated pay information or make assumptions about missing data.

✅ **Better:** Always provide the most recent pay information available from the official payroll system. If the pay is missing or incomplete, inform the employee that you cannot locate current records and recommend they contact HR for further assistance.

The second version does everything the first one does, and it also tells the agent what to do when the data isn't there - which is the case the first version was actually worried about.

### Define your terms

Define anything ambiguous, organization-specific, or domain-specific, so the agent applies consistent logic:

- **Similar concepts** - `"calendar year"` vs. `"fiscal year"`
- **Common business terms** - `"quarter"`, `"sales"`, `"SKU"`, `"shoes"`
- **Abbreviations and acronyms** - `"NPS"` (Net Promoter Score), `"MAU"` (Monthly Active Users)

### A worked example: the multiple date column problem

This is the classic case where an agent is technically right and practically wrong, and it's worth walking through because it shows exactly what instructions are for.

A typical sales fact table carries several dates - `OrderDate`, `ShipDate`, `DueDate`, and `ModifiedDate`. A user asks: *"What were sales in March?"* Every one of those columns is a defensible answer to "in March," and the agent has no basis in the schema for preferring one. So it picks one. It may well pick a different one next week, and your users get two different numbers for the same question.

Nothing about that is a bug - the ambiguity is real, and it lives in your business definition, not in your data. The fix is to state the definition where the agent can read it:

```md
## Key terminology
- "Sales" always means completed sales measured by **OrderDate**. Never use ShipDate,
  DueDate, or ModifiedDate to answer a question about when a sale happened.
- "Shipped" or "delivered" questions use **ShipDate**.
- "Late" or "on time" questions compare **ShipDate** to **DueDate**.
- ModifiedDate is an audit column. Never use it to answer a business question.
- A "quarter" is a fiscal quarter beginning 1 July, not a calendar quarter.
```

Two things to notice. First, this belongs at the **agent level** because it's a business definition that should hold no matter which source answers the question - if the definition were specific to one dataset's quirks, it would belong in that source's instructions instead. Second, it's written as *what to do*, with the wrong choices named explicitly. Naming `ModifiedDate` as an audit column is more useful than leaving it unmentioned and hoping.

### Keep instructions focused

Instructions should be concise and purposeful. Broad scope, unreliable sources, unnecessary history, and vague fallbacks like "just do your best" all dilute the agent's focus. Compare:

❌ **Less effective:**

```md
You are an HR data agent who should try to help employees with all kinds of questions about work. You have access to many systems, like the HRIS platform, old payroll databases from previous vendors, archived employee files, scanned PDF policy documents, and maybe even some spreadsheets that HR used in the past. If someone asks about their pay, you might want to look in one of the old systems if needed. Also, sometimes data isn't updated immediately, so just do your best.
```

✅ **Better:**

```md
You are an HR Assistant Agent responsible for answering employee questions about employment status, job details, pay history, and leave balances.
Use the official HR data warehouse to retrieve current and accurate records.
If data is missing or unclear, inform the user and recommend they contact HR for further support.
Keep responses concise, professional, and easy for employees to understand.
```

The better version has a clear scope, points at the correct source without overloading technical detail, defines fallback behavior, sets tone - and leaves table-level specifics to the data source instructions, where they belong.

Here's what a well-structured set of agent instructions looks like once you put those pieces together:

```md
## Tone and style
Use clear, simple, and professional language.
Sound friendly and helpful, like an internal HR support agent.
Avoid technical jargon unless it's part of the business terminology used in the data.

## General knowledge
You are an HR Assistant Agent designed to help employees access accurate information about
their employment, benefits, and pay.
Only answer questions using the official HR data sources provided.
If multiple records exist, prioritize the most recent and most official source.
Do not guess or assume answers - if information is missing or unclear, advise the employee
to contact HR directly.

## Data source descriptions
- **Employee Data Warehouse**: Contains employment records including status, role, start date, and department.
- **Payroll System**: Contains pay history, compensation details, and tax withholding information.
- **Benefits Enrollment Database**: Includes information about health insurance, retirement plans, and other employee benefits.
- **HR Policy Lakehouse**: Stores official company policies, including holidays, leave policies, and onboarding documents.

## When asked about
- **Employment status (e.g., active, on leave, terminated)**: Use the *Employee Data Warehouse*
- **Pay history or compensation**: Use the *Payroll System*
- **Benefits and enrollment details**: Use the *Benefits Enrollment Database*
- **Company holidays and leave of absence policies**: Use the *HR Policy Lakehouse*
```

### Tune from evidence, not from guesses

Rewriting instructions because an answer "felt off" is how agents get worse. Work from a **benchmark set** instead - a table of questions, the query you expect, and the answer you expect:

<table style="tr:nth-child(even) {background-color: #f2f2f2;}; text-align: left; display: table; border-collapse: collapse; border-spacing: 2px; border-color: gray;">

  <tr><th style="background-color: #1b20a1; color: white;">Question</th> <th style="background-color: #1b20a1; color: white;">Expected Query</th> <th style="background-color: #1b20a1; color: white;">Expected Answer</th></tr>

  <tr><td>How many employees work in the HR team?</td><td><code>SELECT COUNT(*) FROM EmployeeDim WHERE DepartmentName = 'HR'</code></td><td>25</td></tr>
  <tr><td>What is the average salary in Marketing?</td><td><code>SELECT AVG(Salary) FROM EmployeeCompensation WHERE Department = 'Marketing'</code></td><td>$85,000</td></tr>
  <tr><td>Which products had sales last month?</td><td><code>SELECT ProductName FROM Sales WHERE SaleDate &gt;= '2024-05-01'</code></td><td>[Product A, Product B]</td></tr>

</table>

<br>

When a response is wrong, diagnose *why* before you change anything. Is an instruction missing? Are the instructions vague or misleading? Is the example query unrepresentative? Is the user's question genuinely ambiguous given your schema naming? Are values inconsistently formatted - `"ca"` vs. `"CA"` vs. `"Ca"` - so filters can't match? Each of those has a different fix, and only one of them is "rewrite the instructions."

Expand the benchmark set over time so it covers the questions your users actually ask.

<br>

<p style="border-bottom: 1px solid lightgrey;"></p>

<h2 id="3.2"><img style="float: left; margin: 0px 15px 15px 0px;" src="../graphics/pencil2.png">3.2 Using Example Queries</h2>

Instructions tell the agent things in prose. [Example queries](https://learn.microsoft.com/en-us/fabric/data-science/data-agent-example-queries) - also called *few-shot examples* - show it instead. They're pairs of a natural language question and the query that correctly answers it, and they are frequently the fastest way to fix a class of wrong answers.

The reason is simple: a well-formed query is often clearer and more efficient than trying to explain complex logic in text. If you find yourself writing three paragraphs of instructions to describe a join, write the join.

<p><img style="box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.19);" src="https://learn.microsoft.com/en-us/fabric/data-science/media/how-to-create-data-agent/data-agent-adding-examples-sql.png" height="400"></p>

### How the agent uses them

When a user asks a question, the agent performs a **vector similarity search** across your examples for that data source, retrieves the most relevant ones - on the order of the top three or four - and passes them into its augmented prompt to guide query generation. The principle matters more than the exact number: only your *most similar* examples influence any given answer.

Two consequences follow from that, and both are easy to miss:

1. You don't need an example for every question. Examples demonstrate **intent and structure**, and the agent generalizes from them - they don't have to match user questions verbatim.
2. A large pile of vaguely similar examples is worse than a small set of distinct ones, because near-duplicates compete to be retrieved.

Every example query is **validated against the schema** of the selected data source. Queries that fail validation are never sent to the agent - so an example with a typo in a table name isn't a weak example, it's an absent one.

### Not every source supports them

<table style="tr:nth-child(even) {background-color: #f2f2f2;}; text-align: left; display: table; border-collapse: collapse; border-spacing: 2px; border-color: gray;">

  <tr><th style="background-color: #1b20a1; color: white;">Data source type</th> <th style="background-color: #1b20a1; color: white;">Supports example queries?</th></tr>

  <tr><td>Lakehouse</td><td>✅ Yes</td></tr>
  <tr><td>Warehouse</td><td>✅ Yes</td></tr>
  <tr><td>Eventhouse KQL Database</td><td>✅ Yes</td></tr>
  <tr><td>Semantic model</td><td>❌ No</td></tr>
  <tr><td>Ontology</td><td>❌ No</td></tr>

</table>

<br>

This shapes your tuning strategy. For a semantic model or an ontology, instructions and the data source description are the levers you have - which is also why those sources depend more heavily on the guidance in section 3.3.

### What makes a good example

<table style="tr:nth-child(even) {background-color: #f2f2f2;}; text-align: left; display: table; border-collapse: collapse; border-spacing: 2px; border-color: gray;">

  <tr><th style="background-color: #1b20a1; color: white;">Best practice</th> <th style="background-color: #1b20a1; color: white;">Why it matters</th></tr>

  <tr><td><b>Ensure questions clearly map to the query</b></td><td>The agent learns the pattern between the question and the resulting SQL/KQL. Ambiguity reduces accuracy.</td></tr>
  <tr><td><b>Include comments in the query to guide the agent</b></td><td>Comments such as <code>-- substitute customer_id here</code> tell the agent where to substitute values or apply important logic.</td></tr>
  <tr><td><b>Highlight join logic or complex patterns</b></td><td>Use examples to show multi-table joins, aggregations, or advanced logic that's hard to describe in plain instructions.</td></tr>
  <tr><td><b>Avoid overlap or contradictions</b></td><td>Each example should be distinct and non-conflicting, to give the agent a clean signal.</td></tr>
  <tr><td><b>Use run steps to debug which examples are passed</b></td><td>If the wrong examples are being retrieved, adjust your questions or add more specific examples.</td></tr>
  <tr><td><b>Reflect real user behavior</b></td><td>Examples that mirror the questions your users actually ask maximize relevance and accuracy.</td></tr>

</table>

<br>

Focus your examples where the logic is hard: filtering, joins, aggregations, and date handling. Those are the cases where prose fails and a query succeeds.

### Debug with run steps

The **run steps** view shows which example queries were retrieved and applied to a user's question. This is the difference between guessing and knowing - it confirms the right examples are being used, and when results look wrong it tells you whether the examples were even part of the picture.

<p><img style="box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.19);" src="https://learn.microsoft.com/en-us/fabric/data-science/media/how-to-evaluate-data-agent/example-queries-run-steps.png" height="400"></p>

If the wrong examples appear, refine your questions or add clearer, more targeted ones.

### Validate examples with the SDK

The Fabric data agent SDK can evaluate your examples programmatically. `evaluate_few_shots` runs each natural language/query pair through the agent's evaluation process and returns a summary of what passed and what needs work.

```python
# Evaluate few-shot examples using the Data Agent SDK.
# This runs validation on your natural-language/SQL pairs and returns a summary of results.
result = datasource.evaluate_few_shots(batch_size=20)

# Print out the overall success rate of your examples.
print(f"Success rate: {result.success_rate:.2f}% ({result.success_count}/{result.total_examples})")
```

Results come back as pre-computed Pandas DataFrames, so you can inspect both sides of the outcome:

```python
success_df = result.success_cases
failure_df = result.failure_cases

print("Success Cases:")
display(success_df)   # Examples where the SQL matched the user question

print("Failure Cases:")
display(failure_df)   # Examples that need review or improvement
```

<p><img style="box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.19);" src="https://learn.microsoft.com/en-us/fabric/data-science/media/how-to-evaluate-data-agent/fabric-data-agent-sdk-validator.png" height="400"></p>

> **Note:** This evaluation utility is currently available **only for SQL-based example queries**. KQL and other query types aren't yet supported.

### Understand the three scores

The validator scores each example on three dimensions, and an example is considered **high quality only if all three are positive**:

- **Clarity** - is the natural language question clear and unambiguous? It should be specific and include the necessary metrics, timeframes, and filters. *Good:* "Total revenue by region for 2024." *Needs improvement:* "Show performance."
- **Relatedness** - does the query match the *intent* of the question? *Good:* a question asking for a count of customers in March 2025 produces SQL that counts customers with `WHERE month='2025-03'`. *Needs improvement:* the question asks for a count, but the SQL returns `SUM(revenue)` or filters a different period.
- **Mapping** - does every literal in the question appear in the query? *Good:* "Orders over 100 in March 2025 for 'West'" produces SQL containing `> 100`, `2025-03`, and `'West'`. *Needs improvement:* the month filter is missing.

### Detect conflicts

After quality validation, the SDK automatically performs **conflict detection** across your approved examples. A conflict is flagged when two or more examples:

- Represent the **same intent** but reference **different tables or views**.
- Compute the **same metric** using **different aggregation logic** or **different granularity**.
- Would return **materially different results** for the same business question.

This is the mechanism that catches the failure mode nobody notices manually: two examples that each look fine on their own and quietly disagree with each other. Each conflict comes back with the examples involved, their questions and SQL, a description of how they diverge, and a confidence score.

```python
# Display conflict summary
print(f"\nConflicts Detected: {result.conflict_count}")
print("Confidence Ratings: 5=High, 4=Medium, 3=Low, 2=Very Low, 1=Speculative\n")

if result.conflict_count > 0:
    conflict_details_df = result.conflict_details
    display(conflict_details_df)
else:
    print("No conflict details to display.")
```

<p><img style="box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.19);" src="https://learn.microsoft.com/en-us/fabric/data-science/media/how-to-evaluate-data-agent/evaluation-conflict-detection.png" height="400"></p>

Resolving conflicts improves query determinism - which is usually what a business stakeholder means when they say they want the agent to be "reliable."

<p><a href="https://www.youtube.com/watch?v=v0mD01QP5gY" target="_blank"><img src="https://img.youtube.com/vi/v0mD01QP5gY/0.jpg" height="200"></a></p>

<i>Microsoft Fabric: How to use Data Agent Example Queries - Tales From The Field</i>

<br>

<p style="border-bottom: 1px solid lightgrey;"></p>

<h2 id="3.3"><img style="float: left; margin: 0px 15px 15px 0px;" src="../graphics/pencil2.png">3.3 Data Source Instructions</h2>

[Data source instructions](https://learn.microsoft.com/en-us/fabric/data-science/data-agent-configurations#data-source-instructions) are applied when the agent routes a question to a *specific* data source. Where agent instructions shape reasoning, these shape **query construction** - they give the agent the context it needs to write precise SQL, DAX, or KQL against that particular source.

The rule of thumb: agent instructions describe the *business*; data source instructions describe the *data*.

<p><img style="box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.19);" src="https://learn.microsoft.com/en-us/fabric/data-science/media/how-to-create-data-agent/configuration-data-source-instructions.png" height="400"></p>

### A starting format

```md
## General knowledge
// Share general background information the agent should consider when querying this data source.

## Table descriptions
// Describe key tables and important columns within those tables.

## When asked about
// Provide query-specific logic or table preferences for certain topics.
// Example: "When asked about shoe sales, always use the SalesProduct table."
```

The more context you provide here, the more effectively the agent generates accurate queries. Cover:

- The **purpose** of the data source.
- Which **types of questions** it's intended to answer.
- **Required columns** to include in responses.
- **Join logic** between tables.
- **Typical value formats** - abbreviations vs. full names.

A good test: *imagine a new team member using this dataset for the first time - could they write a correct query just by following these instructions?* If not, add the missing context.

### The agent can't see your data

This is the single most important thing to internalize in this section, and it explains a whole category of confusing failures.

**The data agent cannot see individual row values before it executes a query.** It sees table names, column names, and types - and nothing else. So when a user asks for customers in California, the agent has to guess whether your `State` column holds `"CA"` or `"California"`, and if it guesses wrong the query runs perfectly and returns zero rows. No error, no warning, just an empty answer.

The fix is to tell it:

```md
Example values:
- EmploymentStatus: "Active", "On Leave", "Terminated"
- DepartmentName: "Finance", "HR", "Engineering"
- State: Use U.S. state abbreviations like "CA", "NY", "TX"
```

Be explicit about filter behavior too - whether filters should use exact matches, ranges, or pattern matching - and keep formatting consistent across your instructions and examples. Mixing `"ca"`, `"CA"`, and `"Ca"` in your guidance teaches the agent that casing doesn't matter, right up until it does.

### Leading words

You can nudge query generation by embedding fragments of SQL, DAX, or KQL syntax directly in your instructions. These "leading words" help the model infer the correct logic when translating natural language into code.

❌ **Less effective:** Find all the products with names containing "bike".

✅ **Better:** Find all the products with names containing "bike" LIKE '%bike%'

Including `LIKE '%...%'` signals that a pattern-matching clause is expected. The same technique works for date ranges, casing requirements, and join hints.

### Joins are where agents fail

Join logic is a common source of query-generation failure, and it's worth attacking deliberately:

- **Document join relationships clearly.** Name the related tables, the keys used to join them (`EmployeeID`, `ProductKey`), and the direction of the relationship (one-to-many).
- **Include join examples.** Demonstrate correct join behavior for the most common or most complex relationships - this is exactly the case section 3.2 exists for.
- **Clarify required columns across joined tables**, especially when similar column names exist in more than one table.
- **Simplify when necessary.** If required joins are too complex or error-prone, consider flattening the structure into a denormalized table. Changing the data is sometimes cheaper than instructing around it.

### Putting it together

❌ **Less effective:**

```md
## General instructions
Use the EmployeeData warehouse to find answers about employees.
Try to get useful employee details when needed.

### Employment status
You can use the EmployeeStatusFact table.
Join to EmployeeDim if necessary.
```

✅ **Better:**

```md
## General instructions
Use the EmployeeData data warehouse to answer questions related to employee details,
employment status, pay history, and organizational structure.

When generating queries:
* Use EmployeeDim as the primary table for employee details.
* Always include the following columns in the response (if available):
  - EmployeeID
  - EmployeeName
  - EmploymentStatus
  - JobTitle
  - DepartmentName
* Join other tables to EmployeeDim using EmployeeID unless otherwise specified.
* Filter for the most recent records when applicable.

Example values:
- EmploymentStatus: "Active", "On Leave", "Terminated"
- DepartmentName: "Finance", "HR", "Engineering"
- State: Use U.S. state abbreviations like "CA", "NY", "TX"

## When asked about

When asked about **employee status**, use the `EmployeeStatusFact` table.
Join it to `EmployeeDim` on `EmployeeID`.
Filter by the most recent `StatusEffectiveDate` and return the following columns:
`EmploymentStatus`, `StatusEffectiveDate`, `EmployeeName`, and `DepartmentName`.

When asked about **current job title or department**, use the `EmployeeDim` table.
Return `JobTitle` and `DepartmentName`.
If multiple records exist, filter for the record where `IsCurrent = True`.
```

The second version answers the questions the first one leaves open: which table leads, how tables join, which columns come back, what the values look like, and what to do when there's more than one matching row. Notice too how the date ambiguity from section 3.1 gets resolved *here* at the schema level - "filter by the most recent `StatusEffectiveDate`" - while the business definition of which date *means* what stays at the agent level.

Keep these instructions current. When new tables, columns, or business rules appear in a source, update the instructions and examples to match, or the agent keeps answering from a model of your data that no longer exists.

<br>

<p style="border-bottom: 1px solid lightgrey;"></p>

<h2 id="3.4"><img style="float: left; margin: 0px 15px 15px 0px;" src="../graphics/pencil2.png">3.4 Data Agents with Multiple Data Sources</h2>

In Module 02 you learned that a data agent supports up to five data sources in any combination. The moment you attach the second one, a new failure mode appears: the agent has to decide *which source* should answer each question. That decision is called [data source routing](https://learn.microsoft.com/en-us/fabric/data-science/data-agent-routing), and when it goes wrong you get incorrect, incomplete, or empty answers.

If your agent has a single data source, you can skip this section - routing only matters with more than one.

### How routing works

Every data agent has an **orchestrator** that selects tools and data sources. When a question arrives, it:

1. Builds a plan for answering the question.
2. Picks the data source most likely to contain the answer, based on each source's metadata - **name, description, selected schema, and example queries**.
3. Calls that source's query-generation tool and reviews the results.
4. Repeats with another source or another step if more information is needed.

Read step 2 again, because it's the whole section in one line. Those four pieces of metadata are the *only* things the orchestrator has to work with - so they're also the only four levers you have.

For speed, the orchestrator routes from a **subset** of each source's metadata. When that subset isn't enough - the schema is large, source names are similar, or the question is ambiguous - it can call a **routing tool** to inspect the full schema and example queries before committing to a source.

### Signs your routing needs work

- The agent picks the wrong source for a question you expect a specific source to answer.
- The agent says it can't find an answer when the data exists in one of the connected sources.
- The agent gives **different answers to similar questions**, because it picks a different source each time.

That third symptom is the diagnostic one. Inconsistency across near-identical questions is almost always routing, not query generation.

### Inspect routing decisions in run steps

After the agent answers, expand the run steps to see which source it routed to and what context drove the decision. If the orchestrator called the routing tool, that appears as its own step, showing the metadata it reviewed - descriptions, schema, and example queries - before committing.

<p><img style="box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.19);" src="https://learn.microsoft.com/en-us/fabric/data-science/media/data-agent-routing/data-agent-routing.png" height="400"></p>

A routing tool call is itself a signal: the orchestrator couldn't decide from the metadata subset and had to go look. Frequent routing tool calls tell you your source metadata is too thin or too similar.

### Improve routing, in this order

Work through these in sequence. Each step adds more signal for the orchestrator, and each is cheaper and more durable than the one after it.

**1. Tighten your schema selection.** The tables, views, and columns you select on each source are a primary signal of what that source covers. Select only the entities the agent should consider, and make sure object names are descriptive. Large or noisy selections make it harder for the orchestrator to tell what each source is *for*.

**2. Add a data source description.** A description tells the orchestrator at a glance what the source contains and when to use it. Keep it short and focused on the topics or entities the source covers:

> *"Sales fact data for North America retail, including transactions, returns, and store metadata."*

<p><img style="box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.19);" src="https://learn.microsoft.com/en-us/fabric/data-science/media/how-to-create-data-agent/configuration-data-source-description.png" height="400"></p>

A good description summarizes what the source contains, the types of questions it can answer, and any business-specific nuances that distinguish it from your other sources. That last part carries the most weight when two sources overlap.

**3. Add example queries.** Beyond improving query generation (section 3.2), examples show the orchestrator what kinds of questions a source is *meant* to answer. Add representative questions for each source - especially questions that previously routed to the wrong place. Note the constraint from section 3.2: semantic models and ontologies don't support example queries, so for those sources steps 1 and 2 have to carry the load.

**4. Add routing rules to agent instructions.** Only if a question still routes wrongly after the first three steps. Declare explicit rules, grouped by topic:

```md
## Topics

- When asked about logistics trends, shipment delays, or carrier performance, use **FabrikamLogisticsLH**.
- When asked about marketing campaigns, ad spend, or channel performance, use **FabrikamMarketingDW**.
- When asked about customer support tickets or SLA breaches, use **FabrikamSupportKQL**.
```

This is deliberately last. Explicit rules are maintenance debt: keep them concise, because long lists crowd out your other instructions, and you have to update them every time you add or rename a data source. A good description (step 2) keeps working when the questions change; a hardcoded rule doesn't.

<br>

<p><img style="float: left; margin: 0px 15px 15px 0px;" src="../graphics/point1.png"><b>Activity: Instructions Please</b></p>

You are going to play a little game, courtesy of Sandeep Pawar and the Fabric CAT team.

<p><img style="margin: 0px 15px 15px 0px;" src="../graphics/checkmark.png"><b>Description</b></p>

Instruction documents arrive at your booth. Route each one to PREP FOR AI or AGENT INSTRUCTIONS — or feed anti-patterns to the SHREDDER. Misrouted documents earn a citation.

<p><img style="margin: 0px 15px 15px 0px;" src="../graphics/checkmark.png"><b>Steps</b></p>

Follow the in-game instructions and see how you do => [The INSTRUCTIONS game](https://pawarbi.github.io/instructions-please)

<p style="border-bottom: 1px solid lightgrey;"></p>

<h2 id="3.5"><img style="float: left; margin: 0px 15px 15px 0px;" src="../graphics/pencil2.png">3.5 Data Agents and Security</h2>

Security for a data agent splits into two independent questions, and confusing them is the source of most access problems you'll hit:

1. **Who can reach the agent** - controlled by data agent sharing permissions.
2. **What data they can see through it** - controlled by permissions on the underlying data sources.

Sharing an agent does *not* grant access to data. As you saw in Module 02, the agent runs as the person asking and never elevates anyone's access, so when you share an agent you must **also** ensure recipients have access to the underlying data it uses. The agent honors all user permissions on that data, including **Row-Level Security (RLS)** and **Column-Level Security (CLS)**.

That's why two colleagues can ask the same published agent the same question and legitimately get different answers.

<p><img style="box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.19);" src="https://learn.microsoft.com/en-us/fabric/data-science/media/data-agent-sharing/sharing-main.png" height="400"></p>

### The three permission tiers

[Fabric data agent sharing](https://learn.microsoft.com/en-us/fabric/data-science/data-agent-sharing) gives you three levels of access to the agent itself:

<table style="tr:nth-child(even) {background-color: #f2f2f2;}; text-align: left; display: table; border-collapse: collapse; border-spacing: 2px; border-color: gray;">

  <tr><th style="background-color: #1b20a1; color: white;">Permission</th> <th style="background-color: #1b20a1; color: white;">What the user can do</th> <th style="background-color: #1b20a1; color: white;">Use it for</th></tr>

  <tr><td><b>No permission selected</b> (default)</td><td>Query the <b>published</b> version only. No access to edit, or even view, any configuration or details.</td><td>Everyday consumers. This is the tier that protects the integrity of your setup.</td></tr>
  <tr><td><b>View details</b></td><td>View the details and configurations of both the published and draft versions, and query the agent - but change nothing.</td><td>Reviewers, auditors, and analysts who need to understand how an answer was produced.</td></tr>
  <tr><td><b>Edit and view details</b></td><td>Full access to view and edit all details and configurations of both published and draft versions, plus query the agent.</td><td>Co-builders. Ideal for collaborative work.</td></tr>

</table>

<br>

<p><img style="box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.19);" src="https://learn.microsoft.com/en-us/fabric/data-science/media/data-agent-sharing/permission-models.png" height="400"></p>

### Sharing before you publish

You can share an agent that hasn't been published yet, but the behavior surprises people:

<p><img style="box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.19);" src="https://learn.microsoft.com/en-us/fabric/data-science/media/data-agent-sharing/share-without-publish.png" height="400"></p>

Users with **default permissions can't query it at all** - the default tier only allows querying the *published* version, and there isn't one yet. Users with **View details** or **Edit and view details** can access only the draft version. If a colleague reports that a freshly shared agent does nothing for them, check whether it has ever been published before you go looking for a permissions bug.

### Minimum permissions on the underlying sources

For a user to successfully query through an agent, they need at least these effective permissions on each connected source. With anything less, queries fail or return empty results.

<table style="tr:nth-child(even) {background-color: #f2f2f2;}; text-align: left; display: table; border-collapse: collapse; border-spacing: 2px; border-color: gray;">

  <tr><th style="background-color: #1b20a1; color: white;">Data source type</th> <th style="background-color: #1b20a1; color: white;">Minimum permission to query via data agent</th> <th style="background-color: #1b20a1; color: white;">Notes</th></tr>

  <tr><td>Power BI semantic model</td><td>Read</td><td>Read is sufficient to query a semantic model via a data agent. Build/Write is only required to modify the model or use capabilities such as Prep for AI. Workspace access isn't required.</td></tr>
  <tr><td>Lakehouse</td><td>Read on the lakehouse item (and table access if enforced)</td><td>Write not required unless modifying data.</td></tr>
  <tr><td>Warehouse</td><td>Read (SELECT on relevant tables)</td><td>Higher permissions only for DML/DDL operations.</td></tr>
  <tr><td>KQL database</td><td>Reader role on the database</td><td>Higher roles only for management commands.</td></tr>
  <tr><td>Ontology</td><td>Read on the ontology item, and Read on the underlying semantic model, lakehouse, or KQL database bound to the ontology</td><td></td></tr>
  <tr><td>Microsoft Graph in Fabric</td><td>Read on the graph item and the underlying data</td><td></td></tr>
  <tr><td>Other supported sources</td><td>Query/read-level access</td><td>Must allow metadata and data retrieval.</td></tr>

</table>

<br>

> **Important:** Read permission on a semantic model is sufficient for queries initiated through a data agent - Build and workspace roles aren't required for these interactions. This applies **only** to data agent interactions. Other entry points, such as Analyze in Excel or direct report authorship, may still require Build.

That exception is worth remembering, because it lets you follow least privilege properly: grant Read when users only need to *ask questions* through an agent, and grant Build or broader workspace roles only when they genuinely need to modify the model or use features such as Prep for AI.

### The failure mode to recognize

If a user can open the agent but lacks the minimum permission on one or more underlying sources, queries that touch those sources **fail with an authorization error or return empty results**, depending on that source's security model.

The empty-result case is the dangerous one. An agent returning "no records found" looks identical whether the answer is genuinely zero, RLS filtered every row, or the user has no access at all. When a user reports missing data, check permissions before you start rewriting instructions.

<p><a href="https://www.youtube.com/watch?v=1OOe9-EteL0" target="_blank"><img src="https://img.youtube.com/vi/1OOe9-EteL0/0.jpg" height="200"></a></p>

<i>Microsoft Fabric: Data Security & Data Agents - Tales From The Field</i>

<br>

<p style="border-bottom: 1px solid lightgrey;"></p>

<h2 id="3.6"><img style="float: left; margin: 0px 15px 15px 0px;" src="../graphics/pencil2.png">3.6 Data Agents and CI/CD</h2>

Everything you've tuned in this module - instructions, example queries, data source instructions, table selections - is *configuration*. Configuration that lives in exactly one workspace, with no history, no review, and no way back if someone breaks it, is a production risk.

[Source control, CI/CD, and ALM for Fabric data agents](https://learn.microsoft.com/en-us/fabric/data-science/data-agent-source-control) solves that with two complementary capabilities:

- **Git integration** - sync an entire workspace with a Git repository (Azure DevOps or GitHub) for version control, branch-based collaboration, and history tracking of individual items, including data agents.
- **Deployment pipelines** - promote content between separate workspaces representing development, test, and production stages.

> **Note:** Source control for Fabric data agents is currently in **preview**.

### Git integration

Git integration synchronizes a Fabric workspace with a Git repository, so you can use your existing development processes and tools directly in Fabric. It's configured at the **workspace** level from **Workspace settings**. Key capabilities:

- Full backup and version control of workspace items.
- The folder structure in Git mirrors the workspace structure.
- Data agent configurations - schema selection, AI instructions, data source instructions, and example queries - are stored in structured files in dedicated folders.
- View differences, review history, and revert to prior states.
- Branch-based collaboration with feature branches and main.

Recent enhancements add **selective branching**, letting you switch the connected branch at the workspace level to align with feature branch workflows, and a built-in **diff experience** in the Source control pane so you can review exactly what changed before committing or pulling.

<p><img style="box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.19);" src="https://learn.microsoft.com/en-us/fabric/data-science/media/data-agent-cicd/data-agent-git-source-control.png" height="400"></p>

Once connected, the status bar at the bottom left shows the connected branch, the time of the last sync, and the Git commit ID. Each data agent is stored in its own folder in the repository, so you can review changes, track version history, and use standard Git workflows such as pull requests to merge updates into main.

<p><img style="box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.19);" src="https://learn.microsoft.com/en-us/fabric/data-science/media/data-agent-cicd/git-repo.png" height="400"></p>

### What counts as a change

In a Git-connected workspace, the agent's status changes to **Uncommitted changes** when you:

- Change the schema selection.
- Update AI instructions or data source instructions.
- Edit example queries.
- Publish the agent, or update its publishing description.

Any change - functional or descriptive - puts the agent out of sync with the repository. Changed items appear under the **Changes** tab in the Source control pane, where you can review them, compare against the committed version, and commit.

<p><img style="box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.19);" src="https://learn.microsoft.com/en-us/fabric/data-science/media/data-agent-cicd/source-control-data-agent.png" height="400"></p>

The flow works in both directions. When updates are made directly in the repository - modifying AI instructions, changing example queries, editing publishing descriptions - Fabric detects them and shows an **Updates available** notification. The changed items appear under the **Updates** tab, where you review and accept them to apply the repository state to your workspace.

### How a data agent is stored in Git

Understanding this layout is what makes a data agent diff readable in a pull request. At the root, agent content lives under a **files** folder, which contains a **config** folder holding **data_agent.json**, **publish_info.json**, a **draft** folder, and a **published** folder.

- **publish_info.json** contains the publishing description - the one from Module 02. You can edit this file to change the description that appears when the agent is published.
- The **draft** folder holds the configuration of the draft version; the **published** folder holds the published version.

<p><img style="box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.19);" src="https://learn.microsoft.com/en-us/fabric/data-science/media/data-agent-cicd/git-config-draft.png" height="400"></p>

Inside the **draft** folder you'll find **stage_config.json**, which contains `aiInstructions` - your agent-level instructions from section 3.1 - plus one folder per data source, named by source type:

<table style="tr:nth-child(even) {background-color: #f2f2f2;}; text-align: left; display: table; border-collapse: collapse; border-spacing: 2px; border-color: gray;">

  <tr><th style="background-color: #1b20a1; color: white;">Data source</th> <th style="background-color: #1b20a1; color: white;">Folder name prefix</th></tr>

  <tr><td>Lakehouse</td><td><code>lakehouse-tables-</code> followed by the lakehouse name</td></tr>
  <tr><td>Warehouse</td><td><code>warehouse-tables-</code> followed by the warehouse name</td></tr>
  <tr><td>Semantic model</td><td><code>semantic-model-</code> followed by the model name</td></tr>
  <tr><td>KQL database</td><td><code>kusto-</code> followed by the KQL database name</td></tr>
  <tr><td>Ontology</td><td><code>ontology-</code> followed by the ontology name</td></tr>

</table>

<br>

Each data source folder contains **datasource.json** and **fewshots.json** - except semantic models, which don't support example queries and therefore have only **datasource.json**.

**datasource.json** defines that source's configuration:

- `dataSourceInstructions` - the instructions you wrote in section 3.3.
- `displayName` - the name of the data source.
- `elements` - the schema map, listing every table and column in the source.

Each table carries an `is_selected` property: `true` means the agent can use it, `false` means it can't. Column entries also show `is_selected`, but **column-level selection isn't currently supported** - if a table is selected, all of its columns are included regardless of the column value, and if a table isn't selected, none of its columns are considered even when their `is_selected` is `true`. Types follow a convention: a data source is its own type (`"type": "lakehouse_tables"`), a table ends in `.table`, and a column ends in `.column`.

**fewshots.json** stores the example queries from section 3.2. Each entry has an `id`, the natural language `question`, and the `query` text, which may be SQL or KQL depending on the source type.

<p><img style="box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.19);" src="https://learn.microsoft.com/en-us/fabric/data-science/media/data-agent-cicd/git-configure-lakehouse-few-shots.png" height="400"></p>

Step back and look at what that structure means: every lever from sections 3.1 through 3.4 now has a file behind it. `aiInstructions` is section 3.1, `fewshots.json` is 3.2, `dataSourceInstructions` is 3.3, and `elements` with its `is_selected` flags is your schema selection from 3.4. Tuning an agent stops being an untracked change someone made in a UI one afternoon and becomes a reviewable diff.

The **published** folder mirrors the draft structure. **Don't modify files in the published folder directly** - make changes in draft and publish them, so the published version is always generated from a controlled draft state.

### Deployment pipelines

Deployment pipelines move agents between workspaces mapped to lifecycle stages:

1. Develop a new agent, or update an existing one, in the **development** workspace.
2. Promote the changes to the **test** workspace for validation.
3. Promote the tested changes to the **production** workspace, where end users consume them.

<p><img style="box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.19);" src="https://learn.microsoft.com/en-us/fabric/data-science/media/data-agent-cicd/select-deployment-pipeline.png" height="400"></p>

Assign a workspace to each stage before deploying. If you don't assign one to test or production, Fabric creates it automatically, named after the development workspace with `[test]` or `[prod]` appended. To deploy, go to the stage you're deploying from, select the items to promote, and select **Deploy**. You can review a deployment plan before applying changes, so only intended updates are promoted.

<p><img style="box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.19);" src="https://learn.microsoft.com/en-us/fabric/data-science/media/data-agent-cicd/deployment-test.png" height="400"></p>

### Automating deployment

The **Azure DevOps Pipelines extension for Fabric** provides native tasks that run **Fabric CLI** commands in Azure DevOps pipeline jobs, so teams can orchestrate CI/CD for data agent updates alongside or instead of Fabric deployment pipelines. To get started, install the extension from the Visual Studio Marketplace, set up a service connection in your Azure DevOps project, and add Fabric CLI tasks to your pipeline definition.

For large-scale synchronization, the **Import/Export Item Definitions Batch APIs** (preview) let you export and import data agent definitions in batch to streamline promotion across environments.

> **Important:** Service principals are supported in the Fabric data agent **only** as part of ALM scenarios - Git integration and deployment pipelines. That support doesn't extend to other data agent features. If you need to interact with a data agent outside of ALM workflows, service principal isn't supported.

### Publishing in a promoted world

Publishing (Module 02) takes on extra weight once you have multiple workspaces. A data agent must be **published** to be consumable through any channel - Copilot in Power BI, Microsoft Copilot Studio, or Foundry tools. An unpublished agent isn't accessible for consumption **even if it sits in the production workspace**.

That creates two rules worth enforcing:

- **Limit publishing from the development workspace to authorized users** who are actively building and assessing the agent, and restrict access to that workspace so unfinished or experimental agents aren't exposed to a broader audience.
- **End users should only access agents published from the production workspace**, so they interact with stable, approved versions.

### Best practices and limitations

<table style="tr:nth-child(even) {background-color: #f2f2f2;}; text-align: left; display: table; border-collapse: collapse; border-spacing: 2px; border-color: gray;">

  <tr><th style="background-color: #1b20a1; color: white;">Do this</th> <th style="background-color: #1b20a1; color: white;">Why</th></tr>

  <tr><td>Use a dedicated branch for data agent development, and merge to main after code review</td><td>Instruction and example query changes get the same scrutiny as code.</td></tr>
  <tr><td>Keep related resources - data sources, agents, notebooks, pipelines - in the same workspace</td><td>Makes promotion far simpler.</td></tr>
  <tr><td>Test changes in the test workspace before promoting to production</td><td>Your benchmark set from section 3.1 is exactly what to run there.</td></tr>
  <tr><td>Use descriptive commit messages</td><td>"Updated instructions" tells a future reviewer nothing.</td></tr>
  <tr><td>Never change files in the published folder directly</td><td>The published version should always be generated from a controlled draft.</td></tr>
  <tr><td>Use environment-agnostic configuration patterns, such as connection references via Variable Library where supported</td><td>Avoids hardcoding environment-specific values, easing branch merges and cross-stage deployments.</td></tr>

</table>

<br>

Known limitations to plan around:

- Only workspaces connected to a Git repository can use Git-based ALM features.
- Service principals are supported only for ALM scenarios.
- Deployment pipelines require the source and target workspaces to be in the **same tenant**.
- Large numbers of frequent commits can impact repository size and performance.

<br>

<p style="border-bottom: 1px solid lightgrey;"></p>

<h2><img style="float: left; margin: 0px 15px 15px 0px;" src="../graphics/bulletlist.png">Data Agent Best Practices</h2>

Everything in this module comes back to a short list of practices that Microsoft publishes as [best practices for configuring your data agent](https://learn.microsoft.com/en-us/fabric/data-science/data-agent-configuration-best-practices). Use this as your review checklist when an agent isn't performing - work down it in order, because the early items are the ones people skip and then spend weeks compensating for with instructions.

<table style="tr:nth-child(even) {background-color: #f2f2f2;}; text-align: left; display: table; border-collapse: collapse; border-spacing: 2px; border-color: gray;">

  <tr><th style="background-color: #1b20a1; color: white;">#</th> <th style="background-color: #1b20a1; color: white;">Practice</th> <th style="background-color: #1b20a1; color: white;">What it means in practice</th> <th style="background-color: #1b20a1; color: white;">Section</th></tr>

  <tr><td>1</td><td><b>Get your data AI ready</b></td><td>Use clear, descriptive table and column names. <code>CustomerOrders</code> and <code>order_submission_date</code>, not <code>Table1</code> and <code>col1</code>. The agent reads your schema as documentation - so make it readable.</td><td>-</td></tr>
  <tr><td>2</td><td><b>Create specialized agents for specific domains</b></td><td>A focused agent beats a general-purpose one. Narrowing scope improves precision and reduces ambiguity in query interpretation.</td><td>3.1</td></tr>
  <tr><td>3</td><td><b>Minimize the data source scope</b></td><td>Attach only the sources you need, and select only the relevant tables and columns. Aim for <b>25 tables or fewer</b> per data source.</td><td>3.4</td></tr>
  <tr><td>4</td><td><b>Be specific about what to do, not just what not to do</b></td><td>Give the agent the correct path, including what to do when data is missing.</td><td>3.1</td></tr>
  <tr><td>5</td><td><b>Define business terms, abbreviations, and synonyms</b></td><td>Calendar vs. fiscal year, "quarter", "SKU", "NPS", "MAU". Cross-source definitions go in agent instructions; dataset-specific ones go in data source instructions.</td><td>3.1, 3.3</td></tr>
  <tr><td>6</td><td><b>Use leading words to nudge query generation</b></td><td>Embed syntax fragments such as <code>LIKE '%bike%'</code> to signal the expected query shape.</td><td>3.3</td></tr>
  <tr><td>7</td><td><b>Write clear, focused instructions; avoid unnecessary detail</b></td><td>Cut broad scope, unreliable sources, stale history, and vague fallbacks. They dilute the agent's focus.</td><td>3.1</td></tr>
  <tr><td>8</td><td><b>Write detailed data agent instructions</b></td><td>Cover role, expected behavior, tone, use cases, preferred sources, and fallback behavior when information is missing.</td><td>3.1</td></tr>
  <tr><td>9</td><td><b>Provide detailed data source instructions</b></td><td>Purpose, question types, required columns, join logic, and typical value formats - remembering the agent can't see row values before it queries.</td><td>3.3</td></tr>
  <tr><td>10</td><td><b>Use example queries to express complex query logic</b></td><td>When logic involves filtering, joins, aggregations, or date handling, a well-formed query is clearer and more efficient than prose.</td><td>3.2</td></tr>

</table>

<br>

Two habits tie the list together. First, **tune from evidence** - keep a benchmark set, diagnose why a response was wrong before changing anything, and use run steps to see what the agent actually did. Second, **treat the agent as an evolving system**, not a configuration you set once and forget. Schemas change, business rules change, and the questions your users ask change with them.

<p style="border-bottom: 1px solid lightgrey;"></p>

<p><img style="margin: 0px 15px 15px 0px;" src="../graphics/owl.png"><b>For Further Study</b></p>
<ul>
  <li><a href="https://learn.microsoft.com/en-us/fabric/data-science/data-agent-configurations" target="_blank">Data agent configurations</a></li>
  <li><a href="https://learn.microsoft.com/en-us/fabric/data-science/data-agent-configuration-best-practices" target="_blank">Best practices for configuring your data agent</a></li>
  <li><a href="https://learn.microsoft.com/en-us/fabric/data-science/data-agent-example-queries" target="_blank">Data agent example queries</a></li>
  <li><a href="https://learn.microsoft.com/en-us/fabric/data-science/develop-iterative-process-data-agent" target="_blank">Adopting an iterative process for improving your data agent</a></li>
  <li><a href="https://learn.microsoft.com/en-us/fabric/data-science/data-agent-routing" target="_blank">Improve data source routing</a></li>
  <li><a href="https://learn.microsoft.com/en-us/fabric/data-science/data-agent-sharing" target="_blank">Fabric data agent sharing and permission management</a></li>
  <li><a href="https://learn.microsoft.com/en-us/fabric/data-science/data-agent-source-control" target="_blank">Source Control, CI/CD, and ALM for Fabric data agent</a></li>
  <li><a href="https://learn.microsoft.com/en-us/fabric/data-science/evaluate-data-agent" target="_blank">Evaluate a Fabric data agent</a></li>
  <li><a href="https://learn.microsoft.com/en-us/fabric/data-science/fabric-data-agent-sdk" target="_blank">Fabric data agent SDK</a></li>
  <li><a href="https://learn.microsoft.com/en-us/fabric/data-science/semantic-model-best-practices" target="_blank">Semantic model sources for a Fabric data agent</a></li>
  <li><a href="https://learn.microsoft.com/en-us/fabric/cicd/git-integration/intro-to-git-integration" target="_blank">What is Microsoft Fabric Git integration?</a></li>
  <li><a href="https://learn.microsoft.com/en-us/fabric/cicd/deployment-pipelines/get-started-with-deployment-pipelines" target="_blank">Get started with deployment pipelines</a></li>
  <li><a href="https://learn.microsoft.com/en-us/fabric/get-started/whats-new" target="_blank">As always, this is a fast-changing technology, so check this reference for the latest improvements</a></li>
</ul>

<p style="border-bottom: 1px solid lightgrey;"></p>

Congratulations! You have completed this Module. You can now tune a data agent with agent-level instructions and example queries, write data source instructions that produce correct queries, diagnose and fix data source routing across multiple sources, share an agent under the right permission model while respecting RLS and CLS, and manage an agent's configuration through Git and deployment pipelines.

If you understand the concepts here and have completed all of the Activities, you can [proceed to the next Module](04%20-%20Fabric%20Graph%20and%20Fabric%20Ontologies.md).
