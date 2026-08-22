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

<p><img style="float: left; margin: 0px 15px 15px 0px;" src="../graphics/point1.png"><b>Activity: TODO: Activity Name</b></p>

TODO: Activity Description and tasks

<p><img style="margin: 0px 15px 15px 0px;" src="../graphics/checkmark.png"><b>Description</b></p>

TODO: Enter activity description with checkbox

<p><img style="margin: 0px 15px 15px 0px;" src="../graphics/checkmark.png"><b>Steps</b></p>

TODO: Enter activity steps description with checkbox

<p style="border-bottom: 1px solid lightgrey;"></p>

<h2 id="3.2"><img style="float: left; margin: 0px 15px 15px 0px;" src="../graphics/pencil2.png">3.2 Using Example Queries</h2>

Instructions tell the agent things in prose. [Example queries](https://learn.microsoft.com/en-us/fabric/data-science/data-agent-example-queries) - also called *few-shot examples* - show it instead. They're pairs of a natural language question and the query that correctly answers it, and they are frequently the fastest way to fix a class of wrong answers.

The reason is simple: a well-formed query is often clearer and more efficient than trying to explain complex logic in text. If you find yourself writing three paragraphs of instructions to describe a join, write the join.

<p><img style="box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.19);" src="https://learn.microsoft.com/en-us/fabric/data-science/media/how-to-create-data-agent/data-agent-adding-examples-sql.png" height="400"></p>

### How the agent uses them

When a user asks a question, the agent performs a **vector similarity search** across your examples for that data source, retrieves the most relevant ones, and passes them into its augmented prompt to guide query generation. (Microsoft Learn cites the top three to four examples depending on the article - the number matters less than the principle: only your *most similar* examples influence any given answer.)

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

<p><img style="float: left; margin: 0px 15px 15px 0px;" src="../graphics/point1.png"><b>Activity: TODO: Activity Name</b></p>

TODO: Activity Description and tasks

<p><img style="margin: 0px 15px 15px 0px;" src="../graphics/checkmark.png"><b>Description</b></p>

TODO: Enter activity description with checkbox

<p><img style="margin: 0px 15px 15px 0px;" src="../graphics/checkmark.png"><b>Steps</b></p>

TODO: Enter activity steps description with checkbox

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

<p><img style="float: left; margin: 0px 15px 15px 0px;" src="../graphics/point1.png"><b>Activity: TODO: Activity Name</b></p>

TODO: Activity Description and tasks

<p><img style="margin: 0px 15px 15px 0px;" src="../graphics/checkmark.png"><b>Description</b></p>

TODO: Enter activity description with checkbox

<p><img style="margin: 0px 15px 15px 0px;" src="../graphics/checkmark.png"><b>Steps</b></p>

TODO: Enter activity steps description with checkbox

<p style="border-bottom: 1px solid lightgrey;"></p>
