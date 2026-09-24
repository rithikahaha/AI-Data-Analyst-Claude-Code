# 1. The big picture

## What a data analyst does

Someone in a company asks a question: "Is our product growing?" "Why are
customers leaving?" "Which accounts should we call this week?" A data analyst
turns that question into a trustworthy answer, using data, and explains what
to do about it.

The hard part is rarely the code. It is asking the right question, trusting
the data, and saying what the answer means without overselling it.

## What this project is

An **AI analyst** that answers those questions in plain English. You type a
business question. A team of AI agents (built on Claude Code) works out
whether it needs a database query, a statistics test or a prediction model,
and returns an answer with the numbers, the query that produced them, and
honest caveats.

Two things to be clear about:

- The AI agents are **instructions written in text files**, not clever
  software. Chapter 10 shows them.
- The **method** underneath is normal analytics: SQL, statistics, a
  machine-learning model, a dashboard. That is what this guide teaches.

## The fake company

The data describes an invented software company that sells a team-collaboration
tool to other businesses (this is called **B2B SaaS**: software as a service,
sold business to business).

- Customers are **organizations** (called "accounts"). 500 of them.
- Each account has **users**, the people who log in. 3,206 of them.
- Each account pays a monthly **subscription**, priced per seat (per person).
  Three plans: Starter ($15 per seat), Team ($35), Enterprise ($75).
- Every click that matters is recorded as an **event**: signed up, logged in,
  created a project, and so on. About 50,000 of them.

The company's worries are the ones every subscription business has: are people
using it, is revenue growing, and who is about to cancel?

## The six phases

Every question, from the simplest to the hardest, goes through six steps. This
is the standard way analysts work, and the agents follow it:

| Phase | What happens | Example |
|---|---|---|
| **Ask** | Understand the real question | "Is engagement growing" means weekly active users, over what period? |
| **Prepare** | Find the right data and check it is usable | Which table has logins? |
| **Process** | Clean and validate | Are there duplicates or gaps? |
| **Analyze** | The actual SQL, statistics or model | Count weekly logins |
| **Share** | Show it clearly | A line chart |
| **Act** | Say what it means and what to do | "Up 75.6%, keep doing what we're doing" |

Notice that the actual calculation is only one of six steps. Most mistakes
happen in the other five.

## Map of the repo

| You want to see | Look in | Chapter |
|---|---|---|
| The fake data being made | `scripts/export_raw_sources.py` | 2 |
| Cleaning and loading it | `pipelines/etl.py`, `pipelines/data_quality.py` | 2 |
| Talking to the database | `connectors/warehouse.py` | 3 |
| What the metrics mean | `knowledge/metrics_glossary.md` | 4 |
| The trend and funnel queries | `dashboard/queries.py` | 5 |
| Statistics | `stats/tests.py`, `experiments/ab_test.py` | 6 |
| The churn model | `ml/features.py`, `ml/train_churn_model.py` | 7 |
| The dashboard | `dashboard/app.py` | 8 |
| Governed metric definitions and tests | `dbt/`, `tests/` | 9 |
| The AI agents | `.claude/agents/`, `.claude/skills/` | 10 |

## Try it

Look at two real answers before learning how they were made. Open
[`examples/example_qna.md`](../../examples/example_qna.md) and read examples 1
and 2. For each one, find: the plain-English answer, the SQL, and the caveat.
Those three parts (answer, evidence, honesty) are the shape of every good
analysis, and the rest of this guide explains how each part is produced.

## Check yourself

- In your own words, what is the difference between an account and a user?
- Which of the six phases do people most often skip?
- Are the agents software or text? (Read chapter 10 if unsure.)
