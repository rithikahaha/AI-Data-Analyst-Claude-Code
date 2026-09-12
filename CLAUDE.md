# AI Data Analyst — Project Guide

This repo turns Claude Code into a full agentic data team. A business user asks a
question in plain English; `analyst-lead` decomposes it, routes it to the
specialist agent that actually owns that kind of work, and returns a plain-English
answer backed by real SQL, statistics, a model, or a chart.

## How it fits together

- `.claude/agents/` — one agent per real team role: `analyst-lead` (orchestrator),
  `sql-engineer` (queries), `data-scientist` (stats/A-B testing/ML modeling),
  `data-platform-engineer` (pipelines/data quality/cloud/system design),
  `data-visualizer` (BI/dashboard), `ai-engineer` (RAG grounding + agent/skill
  governance), `qa-reviewer` (per-query QA + test suite/CI). Claude Code loads
  these automatically.
- `.claude/skills/` — reusable analysis playbooks (cohort retention, growth
  metrics, funnel analysis, anomaly detection, executive summary formatting). Invoke with
  `/skill-name` or let an agent invoke them.
- `connectors/warehouse.py` — single abstraction for talking to a warehouse. Defaults
  to the local SQLite sample warehouse at `data/sample_warehouse.db`; swap in a real
  warehouse by setting `DATABASE_URL` (see `.env.example` and
  `docs/cloud-deployment.md`).
- `scripts/export_raw_sources.py` + `pipelines/etl.py` — the data pipeline that
  generates raw source extracts and loads/transforms them into the sample
  warehouse, with `pipelines/data_quality.py` checks on both sides of the
  transform, so the whole system works out of the box with no external credentials.
- `stats/`, `experiments/` — significance testing and A/B test readouts, used by
  `data-scientist`.
- `ml/` — churn model training and feature building, used by `data-scientist`.
- `dbt/` — a parallel, tested semantic layer (see `dbt/README.md`) demonstrating
  the same transform/metric logic as governed dbt models; not wired into the
  agent-facing warehouse today.
- `dashboard/` — the standing Streamlit app and its published-Artifact companion,
  owned by `data-visualizer`.
- `rag/`, `knowledge/metrics_glossary.md` — grounds ambiguous metric definitions,
  used by `ai-engineer`.
- `infra/`, `docs/` — illustrative cloud IaC and architecture docs, owned by
  `data-platform-engineer`. Never applied against a live account from this repo.
- `tests/`, `.github/workflows/ci.yml` — owned by `qa-reviewer`; run `pytest`
  after any change to `connectors/`, `pipelines/`, `stats/`, or `ml/`.

## Ground rules for agents

- **Read-only.** Every query against the warehouse must be `SELECT`. Never emit
  `INSERT`/`UPDATE`/`DELETE`/`DROP`/`ALTER` against `connectors/warehouse.py`.
- **Show the work.** Always surface the SQL, test, or model that produced an
  answer alongside the plain-English summary — a stakeholder should be able to
  hand it to a data engineer.
- **Sanity-check before answering.** Row counts, null rates, and date ranges should
  be spot-checked (`qa-reviewer`, `anomaly-detection` skill) before a number is
  presented as fact.
- **Cite the definition used.** Ambiguity about *which* MRR, churn, or active-
  user definition was used is the most common way a "correct" query gives a
  misleading answer — check `knowledge/metrics_glossary.md` via `rag/retrieve.py`
  when a question uses one of these terms.
- **Statistical claims need a test, not a glance.** "X is higher than Y" from a
  significance question should go through `data-scientist`'s
  `stats/`/`experiments/` modules, with an effect size and confidence interval —
  not just a raw comparison of two numbers.
- **Infrastructure changes are proposals, not actions.** `data-platform-engineer`
  produces Terraform and docs under `infra/`/`docs/` — it never provisions, alters,
  or tears down real cloud resources from within this repo.
- **New agent/skill files follow the existing shape.** State when to use it, its
  process, and its output shape (see `ai-engineer`'s governance notes) — vague
  instructions produce inconsistent behavior.

## Local setup

```bash
pip install -r requirements.txt
python -m scripts.export_raw_sources
python -m pipelines.etl
pytest
```

Then just ask Claude Code a business question, e.g. "Which plan tier has the
highest churn, and is that difference actually significant or could it be noise?"
