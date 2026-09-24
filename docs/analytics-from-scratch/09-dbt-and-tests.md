# 9. dbt and tests

## The problem: how do you know the numbers are right?

A wrong number that looks confident is the worst outcome in analytics. Two
tools in this project exist to catch mistakes before anyone sees them:
**dbt**, which defines metrics once and tests the data, and **pytest**, which
tests the code.

## dbt in plain words

**dbt** (data build tool) lets you write your metric definitions as SQL files
that build on each other, and then runs them in the right order and tests the
results.

Why bother? Without it, the same metric, say weekly active users, gets
re-written in a dashboard, a notebook and a report, slightly differently each
time. Then two people quote two different numbers. With dbt you define it
**once**, test it, and everything reads from that one definition.

### The two layers

Look in [`dbt/models/`](../../dbt/models/):

- **`staging/`**: one file per raw table. It does the same cleaning as the
  Python ETL (removing duplicate organizations, working out MRR).
- **`marts/`**: the finished metrics: `fct_weekly_active_users`,
  `fct_onboarding_funnel`, `fct_account_mrr` (net revenue retention) and
  `mart_account_health` (the churn model's features).

A model refers to another with `{{ ref('stg_product_events') }}`. That is how
dbt knows the order to build them in. Open
[`fct_weekly_active_users.sql`](../../dbt/models/marts/fct_weekly_active_users.sql)
and compare it to the dashboard query in chapter 5. It is the same logic.

### dbt tests

In [`_staging.yml`](../../dbt/models/staging/_staging.yml), each column lists
checks that must hold:

| Test | Means |
|---|---|
| `unique` | No value appears twice |
| `not_null` | Never blank |
| `relationships` | Every `org_id` here exists in the organizations table |
| `accepted_values` | Only allowed values (for example status is `active` or `churned`) |

If a test fails, `dbt build` reports it. Same idea as the pipeline's quality
checks in chapter 2, but declared next to the metric definition.

### What "40" means, exactly

`dbt build` reports **40 passing**. Be precise about what that counts, because
an interviewer may ask: it is 4 seeds (loaded input tables) + 4 tables + 4
views (the models) + **28 data tests**. So there are 28 actual data tests, and
40 total steps that all succeeded. Say "40 of 40 dbt steps pass, including 28
data tests" and you are exact. Calling all 40 "checks" overstates it.

### One relationship to be clear on

dbt here is a **parallel** layer. The agents and the dashboard still read the
SQLite warehouse the Python pipeline builds. dbt builds a separate DuckDB
database (`data/analytics.duckdb`) from the same raw data to **show the
pattern**, and its results match the Python ones (for example, NRR 108.5%).
It is not what answers questions today.

## pytest: testing the code

[`tests/`](../../tests/) holds 48 tests. Each one is a small function that
checks one behaviour and fails loudly if it breaks:

| File | Tests | What it protects |
|---|---|---|
| `test_warehouse.py` | 6 | The read-only guard blocks writes; MRR equals seats x price |
| `test_data_quality.py` | 5 | The null, duplicate and reference checks catch bad data |
| `test_stats.py` | 4 | The statistics functions give right answers |
| `test_ab_test.py` | 8 | Sample size, the z-test, guardrails, test duration |
| `test_ml.py` | 4 | The model trains and scores sensibly |
| `test_monitor.py` | 7 | The freshness and gap checks catch a broken pipeline |
| `test_reliability.py` | 7 | Availability and speed calculations, health check |
| `test_k8s_manifests.py` | 7 | Deployment file safety rules |

A good test states something you **expect to be true forever**, for example
"a `DROP TABLE` is always rejected". When someone changes code later, the tests
tell them straight away if they broke it. CI runs them on every push
([DevOps guide, chapter 3](../devops-from-scratch/03-ci-cd.md)).

## Try it

Build the dbt layer and see the tests run:

```bash
cd dbt
DBT_PROFILES_DIR=$(pwd) dbt build
cd ..
```

You should see `PASS=40 WARN=0 ERROR=0`. Read the list above it and count the
tests.

Compare dbt to the Python answer:

```bash
python - <<'PY'
import duckdb
c = duckdb.connect("data/analytics.duckdb", read_only=True)
print(c.execute("select round(100.0*sum(mrr)/sum(initial_mrr),1) from fct_account_mrr where is_established").fetchall())
print(c.execute("select week, wau from fct_weekly_active_users order by week desc limit 2").fetchall())
PY
```

Expected: `[(108.5,)]`, and weeks 2026-35 (169) and 2026-34 (411). Same NRR and
same weekly number as the dashboard. One difference to spot: dbt keeps the
partial week 35, while the dashboard drops it. Two layers can disagree on
presentation while agreeing on the data, and you should know why.

Run the code tests, then break one on purpose:

```bash
python -m pytest -q
```

Now open `connectors/warehouse.py`, find `_ALLOWED_STATEMENT`, and change
`SELECT` in the pattern to `SELECTX`. Run the tests again. Six tests fail
(the guard now rejects even normal queries, so anything that reads the
database breaks). Undo with `git checkout connectors/warehouse.py` and run
the tests once more to see all 48 pass. You just proved the tests are
watching.

## Check yourself

- Why define a metric in one place instead of in every report?
- What are staging and marts?
- What does "40 passing" actually include?
- Which layer do the agents read, dbt or the SQLite warehouse?
- What makes a good test?
