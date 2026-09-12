# dbt: the semantic layer

This is a self-contained analytics-engineering layer, separate from
`pipelines/etl.py`. It exists to show the pattern a growing data team actually
adopts: once more than one thing (a dashboard, a model, an ad-hoc query) needs
the same metric, defining it once — in dbt, tested — beats redefining it in SQL
or Python every time it's needed. `mart_account_health.sql` is the clearest
example: it's the *same* feature definitions as `ml/features.py`, expressed as
a governed model instead of inline Python.

This does **not** replace `pipelines/etl.py`, and the agents don't query it —
`connectors/warehouse.py` still points at the SQLite warehouse the Python
pipeline builds. This is deliberately a parallel demonstration of the dbt
pattern against the same raw data, not a production dependency, so it's safe to
explore without touching how the agent team actually answers questions. In a
real migration, this is the layer that would eventually replace the transform
step of `pipelines/etl.py` once the warehouse outgrows one Python script.

## Structure

- `models/staging/` — one model per raw source, doing exactly what
  `pipelines/etl.py`'s `transform()` does in Python: dedupe organizations,
  derive `mrr`/`initial_mrr` from seat count × price. `_staging.yml` has
  schema tests (`unique`, `not_null`, `relationships`, `accepted_values`) on
  every key column.
- `models/marts/` — the metrics: `fct_weekly_active_users`,
  `fct_onboarding_funnel`, `fct_account_mrr` (net revenue retention and its
  components), `mart_account_health` (the churn model's feature set).

## Running it

```bash
python -m scripts.export_raw_sources   # from the repo root, if not already run
cd dbt
export DBT_PROFILES_DIR=$(pwd)         # or set it in your shell profile
dbt build                              # seed + run + test in one command
```

Builds into a local DuckDB file at `data/analytics.duckdb` — no external
warehouse or credentials needed. `dbt build` seeded, ran, and tested cleanly
(40/40 checks) against this repo's sample data, and its `fct_account_mrr` and
`fct_onboarding_funnel` outputs match `dashboard/queries.py`'s Python-computed
numbers exactly — the same transform, expressed two ways, agreeing.
