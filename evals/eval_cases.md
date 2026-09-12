# Agent evaluation cases

Golden business questions for `ai-engineer` to periodically check agent output
against — not an automated pass/fail harness, but a fixed set of cases so "is the
system still answering well" has a concrete check instead of a vague impression.
When adding a new agent, skill, or data source, add a case here that would have
caught a regression it could plausibly introduce.

For each case: run the question through `analyst-lead` as a stakeholder would, and
compare the actual output against the expected shape below. A miss on any expected
element is a finding, not necessarily a failure — but it should be explainable.

---

### Case 1 — descriptive, unambiguous

**Question:** "How has revenue been trending over the last few months?"

**Expected:**
- Routed to `sql-engineer` directly (no `data-scientist` needed — purely descriptive).
- Cites the revenue definition (gross value of `completed` orders) — should match
  `knowledge/metrics_glossary.md`'s "Revenue" entry.
- Shows the SQL and a chart.
- Excludes the current partial month from the trend, or explicitly flags it if included.

### Case 2 — ambiguous term, should trigger glossary grounding

**Question:** "How many active customers do we have?"

**Expected:**
- `ai-engineer`/`rag/retrieve.py` grounds "active customer" against the glossary
  (subscription-based definition) rather than the agent guessing "customer who
  ordered recently."
- The answer states which definition was used, since this is exactly the kind of
  ambiguity `qa-reviewer`'s checklist calls out.

### Case 3 — needs statistical judgment, not just a number

**Question:** "Does the Scale plan have lower churn than the Starter plan?"

**Expected:**
- Routed to `data-scientist`, not answered as a plain SQL comparison.
- Runs a significance test (`experiments/ab_test.py`'s two-proportion z-test) and
  reports the confidence interval / significance, not just "Scale is X%, Starter
  is Y%."
- If underpowered (small sample), says so explicitly rather than presenting a
  null result as proof of no difference.

### Case 4 — predictive, needs the ML model and its limitations stated

**Question:** "Which of our current customers are most likely to churn?"

**Expected:**
- Routed to `data-scientist` (or reads `dashboard/queries.py`'s
  `churn_risk_list` / the standing dashboard's Churn Risk tab).
- States the model's reported AUC and that it's a probability, not a certainty.
- Does not claim a customer "will" churn — states risk score / relative ranking.

### Case 5 — infra/scaling question, should not touch live data

**Question:** "How would this system handle 50 analysts asking questions at once?"

**Expected:**
- Routed to `data-platform-engineer`.
- References `docs/ARCHITECTURE.md`'s caching/queueing reasoning, not a made-up
  answer.
- Does not claim any load testing was actually performed — this is architecture
  reasoning, not a benchmarked result.

### Case 6 — data-quality regression check

**Question:** "Why did total revenue drop 90% this month?"

**Expected:**
- `qa-reviewer` catches this before it's presented as a real trend if the cause is
  a partial/incomplete current month (see `dashboard/queries.py`'s handling of
  this exact case) rather than reporting the raw (misleading) number.
