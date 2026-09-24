# 11. Limits and honesty

A project you can defend is one whose weak spots you already know. Interviewers
respect "here is what this does not show" far more than a claim that collapses
under one follow-up question. This chapter lists every real limit, so none of
them can surprise you.

## What this project is

A working, tested demonstration of the **method**: an analytics workflow
(question, data, checks, SQL, statistics, a model, a dashboard) plus an AI
agent layer that follows it. Every number in this guide comes from running the
real code.

## What it is not, and how to say it

| Limit | What is true | How to say it |
|---|---|---|
| **The data is fake.** | A script generates it. Same seed, same data, every time. | "It's a generated dataset. What it shows is the method, not a business result." |
| **The churn model is modest and fragile.** | AUC 0.6675, but 0.57 to 0.69 across different splits. It caught 5 of 23 real churners. | "It's a rough way to rank accounts. I'd say about 0.6 to 0.7 from a small test set." |
| **Possible leakage in the model.** | Features use one fixed date for all accounts, so days since last login partly reflects having already left. | "It's documented in the code. A stricter version would measure each account before its own cutoff date." |
| **The integration result is not proven.** | 27.1% versus 17.5%, p = 0.075, 59 accounts in the small group, and it is observational. | "Promising, not proven. It needs a real randomized test." |
| **NRR is simplified.** | Current versus starting MRR for accounts at least 90 days old, not a fixed 12-month window. | "It's a simplified version of NRR." |
| **The funnel is not a cohort.** | It counts everyone who ever reached each step, so recent signups pull rates down. | "It's a snapshot funnel. A cohort version would be fairer." |
| **dbt is a parallel layer.** | The agents and dashboard read the SQLite warehouse. dbt builds a separate DuckDB copy. | "dbt shows the pattern. It isn't what answers questions today." |
| **"40 dbt checks."** | 40 steps pass, of which 28 are data tests. | "40 of 40 dbt steps pass, 28 of them data tests." |
| **Never run on a real warehouse.** | The connector is built to point at Postgres, Snowflake or BigQuery, but this repo only shows it working on the sample SQLite file. | "It's designed for a real warehouse. I've only run it on the sample one." |
| **Agents can be wrong.** | They are instructions followed by an AI. | "That's why there's a QA step, tests, and me checking the output." |

## Numbers you can quote

All verified while writing this guide.

| Number | Where it comes from | Chapter |
|---|---|---|
| 500 accounts, 3,206 users, about 50K events | The sample warehouse | 2 |
| Weekly active users 234 to 411 over 26 weeks, up 75.6% | `weekly_active_users()` | 5 |
| Net revenue retention 108.5% | 117,525 / 108,275 | 4 |
| Churn: Starter 28.8%, Team 20.7%, Enterprise 6.7% | `churn_by_plan_tier()` | 4, 8 |
| Funnel: 3,206 to 2,295 to 1,421 (44.3% activate) | `onboarding_funnel()` | 5 |
| Integration gap: 27.1% versus 17.5%, p = 0.0748 | `experiments/ab_test.py` | 6 |
| Churn model AUC 0.6675, precision 45.5%, recall 21.7% | `ml/train_churn_model.py` | 7 |
| 48 tests pass | `pytest` | 9 |
| 40 dbt steps pass (28 data tests) | `dbt build` | 9 |

If asked for a number that is not on this list, say "let me check the repo and
get back to you". That is a stronger answer than a confident wrong one.

## What you would do next

A good closing answer to "what would you improve?":

1. Run a real randomized experiment on the integration idea instead of
   reading an observational gap.
2. Rebuild the churn features as of a cutoff date before each account's
   outcome, then re-measure how good the model really is.
3. Turn the funnel into cohorts.
4. Point it at a real (or public real-world) dataset and see what breaks.

## Where to go from here

- The interview practice sheet: [`docs/EXPLAIN_THIS_PROJECT.md`](../EXPLAIN_THIS_PROJECT.md).
- The other half of the project, if you want the operations side:
  [DevOps and SRE from scratch](../devops-from-scratch/README.md).
- The [glossary](glossary.md) for any word that slipped past you.

## Check yourself

Answer each out loud without looking:

- Is the data real? What is real about the project?
- What is the model's AUC, and what should you add when you say it?
- Why is the integration result "not proven" in two different ways?
- What does "40 dbt checks" actually contain?
- Name two things you would improve.
