# AI Data Analyst — Project Guide

This repo turns Claude Code into an agentic analytics team. A business user asks a
question in plain English; a lead agent decomposes it, delegates to specialist
subagents, and returns a plain-English answer backed by a real SQL query and a chart.

## How it fits together

- `.claude/agents/` — subagents for each role on the analytics team (lead analyst,
  SQL engineer, data visualizer, QA reviewer). Claude Code loads these automatically.
- `.claude/skills/` — reusable analysis playbooks (cohort retention, revenue trend,
  funnel analysis, anomaly detection, executive summary formatting). Invoke with
  `/skill-name` or let the lead agent invoke them.
- `connectors/warehouse.py` — single abstraction for talking to a warehouse. Defaults
  to the local SQLite sample warehouse at `data/sample_warehouse.db`; swap in a real
  warehouse by setting `DATABASE_URL` (see `.env.example`).
- `scripts/seed_sample_data.py` — generates the sample warehouse so the whole system
  works out of the box with no external credentials.

## Ground rules for agents

- **Read-only.** Every query against the warehouse must be `SELECT`. Never emit
  `INSERT`/`UPDATE`/`DELETE`/`DROP`/`ALTER` against `connectors/warehouse.py`.
- **Show the work.** Always surface the SQL that was run alongside the plain-English
  answer — a business user should be able to hand the query to a data engineer.
- **Sanity-check before answering.** Row counts, null rates, and date ranges should be
  spot-checked (see the `qa-reviewer` agent and `anomaly-detection` skill) before a
  number is presented as fact.
- **Cite the table/column names used.** Ambiguity about *which* revenue or *which*
  customer definition was used is the most common way a "correct" query gives a
  misleading answer.

## Local setup

```bash
pip install -r requirements.txt
python scripts/seed_sample_data.py
```

Then just ask Claude Code a business question, e.g. "Which customer segment has the
highest churn in the last two quarters, and is it getting worse?"
