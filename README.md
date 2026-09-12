# AI Data Analyst with Claude Code

Ask a business question in plain English. Get back a real answer — backed by
actual SQL, a real chart, or a real model, with the caveats that make it
trustworthy — in the time it takes to read this sentence, not an afternoon.

This is the natural next step from [Credit-Risk-Portfolio-Analytics](https://github.com/rithikahaha/Credit-Risk-Portfolio-Analytics),
a static Power BI dashboard: instead of pre-building a fixed set of visuals, this
answers whatever question actually gets asked, on demand.

## See it in action

Two real runs against the sample warehouse in this repo — full write-ups with
queries and caveats in [`examples/example_qna.md`](examples/example_qna.md).

### "Where are we losing customers, and what's that costing us?"

Of 800 signups, only 322 (40%) ever buy anything. The leak isn't at signup —
it's the step after: **48% of everyone who activates the product still never
buys**, nearly double the drop-off at signup itself. At an average $315 first
order, closing even 10 points of that gap is worth roughly **$19,500 in new
revenue**. One query found the leak; a second number turned it into a dollar
figure a stakeholder can act on.

### "Is our premium plan actually earning its price through better retention?"

Scale customers pay 10x Starter's price. Their churn rate looks a little better
— but a significance test shows that gap is **noise, not a real effect** (p =
0.69). What *is* real: scoring every active subscription with a churn model
shows the actual risk is concentrated in one slice — SMB customers are 51% of
Scale's base but **80% of its highest-risk accounts**. The plan isn't the
problem; one customer segment inside it is.

That second example needed more than a lookup — a significance test to avoid
chasing a fake pattern, and a model to find the specific customers worth
worrying about. Answering it is what the rest of this README is about.

## What this actually is

You ask one thing — `analyst-lead` — a question, the same way you'd ask a human
analyst. Internally, it routes to whichever specialist actually owns that kind
of work, the way asking a real analytics team funnels to the right person:

```mermaid
flowchart LR
    Q["Business question"] --> Lead[analyst-lead]
    Lead -->|descriptive| SQL[sql-engineer]
    Lead -->|significance / ML| DS[data-scientist]
    Lead -->|infra / scaling| DPE[data-platform-engineer]
    Lead -->|ambiguous term| AI[ai-engineer]
    SQL --> WH[(Warehouse)]
    DS --> WH
    DS --> Model[ml/train_churn_model.py]
    WH --> QA[qa-reviewer]
    QA --> Viz[data-visualizer]
    Viz --> Lead
    Lead --> A["Plain-English answer\n+ SQL + chart + caveats"]
```

That split exists for one reason: a single prompt trying to be equally good at
SQL, statistical rigor, ML, cloud architecture, and QA all at once gets mushy.
Splitting it internally is what lets *one analyst* credibly cover the full 2026
data-analyst range — SQL, statistics, A/B testing, ML, data engineering, cloud,
dashboards, LLM/RAG — without becoming a jack-of-all-trades prompt that's
mediocre at everything.

## Quickstart

```bash
pip install -r requirements.txt
python -m scripts.export_raw_sources
python -m pipelines.etl
```

This generates a realistic sample warehouse (`data/sample_warehouse.db`) modeling
a small subscription e-commerce business over ~2.5 years: customers, orders,
subscriptions (for churn/retention), and signup→activation→purchase funnel
events — enough to exercise the whole system with no external credentials.

Then open this repo in Claude Code and ask a business question, e.g.:

- "How has revenue been trending over the last few months?"
- "Where in the signup-to-purchase funnel are we losing the most customers?"
- "Does the Scale plan actually have lower churn than Starter, or is that noise?"
- "Which of our current customers are most likely to churn?"

See [`examples/example_qna.md`](examples/example_qna.md) for three full runs, and
[`evals/eval_cases.md`](evals/eval_cases.md) for the golden questions used to
check answer quality as the system grows.

### Try the other pieces directly

```bash
python -m experiments.ab_test          # A/B readout worked example
python -m ml.train_churn_model         # train + register the churn model
python -m rag.retrieve                 # glossary grounding worked example
streamlit run dashboard/app.py         # live dashboard
pytest                                 # full test suite
```

## Under the hood: how the work is split

One agent per real team role, not one per individual skill — so an ML question
doesn't get answered by the same prompt that writes SQL, but you never have to
know or care which one you're "talking to":

| Agent | Covers | Backing code |
|---|---|---|
| [`analyst-lead`](.claude/agents/analyst-lead.md) | Understands the question, routes it, synthesizes the answer | — |
| [`sql-engineer`](.claude/agents/sql-engineer.md) | Schema discovery, query writing | `connectors/warehouse.py` |
| [`data-scientist`](.claude/agents/data-scientist.md) | Statistics, A/B test readouts, predictive modeling | `stats/`, `experiments/`, `ml/train_churn_model.py` |
| [`data-visualizer`](.claude/agents/data-visualizer.md) | Ad-hoc charts and the standing dashboard | `dashboard/` |
| [`data-platform-engineer`](.claude/agents/data-platform-engineer.md) | Pipelines, data quality, cloud deployment, system design | `pipelines/`, `infra/`, `docs/ARCHITECTURE.md` |
| [`ai-engineer`](.claude/agents/ai-engineer.md) | Grounding ambiguous metric definitions, agent/skill quality | `rag/`, `knowledge/`, `evals/` |
| [`qa-reviewer`](.claude/agents/qa-reviewer.md) | Per-answer sanity checks, test suite, CI | `tests/`, `.github/workflows/ci.yml` |

`.claude/skills/` holds the reusable playbooks these agents follow: schema
exploration, revenue trend analysis, cohort retention, funnel analysis, anomaly
detection, executive-summary formatting.

- **`connectors/warehouse.py`** — the one place all SQL goes through. Read-only
  by construction (rejects anything but `SELECT`/`WITH`/`EXPLAIN`). Defaults to
  the local sample warehouse; point `DATABASE_URL` at Postgres/Snowflake/BigQuery
  to run against a real one with no agent/skill changes — see
  [`docs/cloud-deployment.md`](docs/cloud-deployment.md).
- **`infra/` + `docs/`** — illustrative Terraform for AWS/GCP/Azure and
  [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) covering security, observability,
  and scaling — documentation and IaC only, nothing applied against a live
  account.

## Connecting a real warehouse

Copy `.env.example` to `.env` and set `DATABASE_URL` to your warehouse's
SQLAlchemy connection string. Nothing else changes: every agent, skill,
pipeline, and the dashboard talk to the warehouse only through
`connectors/warehouse.py`.

## Why this instead of a fixed dashboard

A BI dashboard answers the questions it was built to answer. This answers the
question that actually gets asked — including the follow-up ("okay, now break
that down by region," "is that actually significant?") — because it knows *how
to investigate*, not just which chart to draw. The tradeoff: it needs guardrails
(read-only queries, mandatory QA, explicit caveats, a real test suite) so
flexibility doesn't come at the cost of trustworthy numbers — see the ground
rules in [`CLAUDE.md`](CLAUDE.md).

## License

MIT
