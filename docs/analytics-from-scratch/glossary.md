# Glossary

Plain meanings, sorted alphabetically. For DevOps words (container, CI/CD,
Kubernetes and so on) see the [DevOps glossary](../devops-from-scratch/glossary.md).

| Word | Meaning |
|---|---|
| **A/B test** | An experiment where a coin flip decides who gets a change, so the groups differ only by that change |
| **Account** | A customer company. In the data, one row in `organizations` |
| **Accuracy** | The share of predictions that were right. Misleading when one outcome is rare |
| **Activation** | A user creating a project, the point they use the core product |
| **Agent** | In this project, a text file of instructions that Claude Code follows for one specialty |
| **AUC** | How often a model scores a real churner higher than a non-churner. 0.5 is a coin flip, 1.0 is perfect |
| **B2B SaaS** | Software sold as a subscription, to businesses |
| **Cohort** | A group who started at the same time, followed together |
| **Confidence interval** | A range the true value plausibly sits in. Wide range means weak evidence |
| **Contraction** | An active account that reduced its seat count |
| **Correlation** | Two things moving together. Not proof that one causes the other |
| **CTE** | A named step in a SQL query, written with `WITH` |
| **Churn** | An account cancelling. Churn rate is churned divided by total |
| **dbt** | A tool that runs SQL metric definitions in order and tests them |
| **ETL** | Extract, transform, load: read raw data, clean it, store it |
| **Event** | One recorded user action, like a login |
| **Expansion** | An account that increased its seat count |
| **Fan-out** | A join repeating one row many times, which inflates counts if you count rows |
| **Feature** | A fact given to a model, like days since last login |
| **Foreign key** | A column pointing at another table's ID, like `org_id` |
| **Funnel** | A sequence of steps people pass through, with drop-offs between them |
| **Guardrail metric** | Something a "win" must not harm |
| **Join** | Combining two tables using a shared column |
| **Label** | The outcome a model learns to predict, here `churned` |
| **Leakage** | Information from after an outcome slipping into a model's inputs, making it look better than it is |
| **Metric** | A defined number used to track something |
| **MRR** | Monthly recurring revenue: seats times price per seat |
| **NRR** | Net revenue retention: what existing customers pay now versus when they started |
| **Null** | A blank, missing value |
| **Observational data** | Data where nobody controlled who got what. Cannot prove cause |
| **p-value** | If there were no real difference, how often luck alone would produce a gap this big |
| **Power** | The chance a test notices a real effect. Low with too little data |
| **Precision** | Of the accounts a model flags, the share that really churned |
| **Primary key** | A column that uniquely identifies each row, usually `id` |
| **pytest** | A tool that runs the project's automated code tests |
| **RAG** | Looking up relevant text first, then using it to ground an answer |
| **Randomization** | Assigning groups by chance, so groups start comparable |
| **Recall** | Of all the accounts that really churned, the share the model caught |
| **Sample size** | How many observations you have. More gives stronger evidence |
| **Skill** | A short reusable playbook for one kind of analysis |
| **SQL** | The language for querying databases |
| **Staging (dbt)** | Cleaned copies of the raw tables, one per source |
| **Statistical significance** | A result that luck alone would rarely produce. Conventionally p below 0.05 |
| **Streamlit** | A Python library that turns a script into a web page |
| **Test set** | Data held back from training, used only to grade a model |
| **TF-IDF** | A way to score how well a document matches a question by distinctive shared words |
| **Training set** | Data a model learns from |
| **Underpowered** | Too little data to reliably detect the effect you care about |
| **WAU** | Weekly active users: unique users who logged in during a week |
