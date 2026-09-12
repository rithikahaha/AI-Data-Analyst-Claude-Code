# Agent evaluation cases

Golden business questions for `ai-engineer` to periodically check agent output
against, not an automated pass/fail harness, but a fixed set of cases so "is the
system still answering well" has a concrete check instead of a vague impression.
When adding a new agent, skill, or data source, add a case here that would have
caught a regression it could plausibly introduce.

For each case: run the question through `analyst-lead` as a stakeholder would, and
compare the actual output against the expected shape below. A miss on any expected
element is a finding, not necessarily a failure, but it should be explainable.

---

### Case 1, descriptive, unambiguous

**Question:** "Is product engagement growing or shrinking?"

**Expected:**
- Routed to `sql-engineer` directly (no `data-scientist` needed, purely descriptive).
- Cites the active-user definition (a `login` event in `product_events`), should
  match `knowledge/metrics_glossary.md`'s "Active user" entry.
- Shows the SQL and a WAU trend chart.
- Excludes the current partial week from the trend, or explicitly flags it if included.

### Case 2, ambiguous term, should trigger glossary grounding

**Question:** "How many active users do we have?"

**Expected:**
- `ai-engineer`/`rag/retrieve.py` grounds "active user" against the glossary
  (weekly-login-based definition) rather than the agent guessing "any user with
  an account."
- The answer states which definition was used and the time window (a week), since
  this is exactly the kind of ambiguity `qa-reviewer`'s checklist calls out.

### Case 3, needs statistical judgment, not just a number

**Question:** "Does using integrations actually correlate with accounts staying longer?"

**Expected:**
- Routed to `data-scientist`, not answered as a plain SQL comparison.
- Runs a significance test (`experiments/ab_test.py`'s two-proportion z-test) and
  reports the confidence interval / significance, not just "adopters churn at X%,
  non-adopters at Y%."
- If underpowered (small control group), says so explicitly rather than presenting
  a non-significant result as proof of no effect.

### Case 4, predictive, needs the ML model and its limitations stated

**Question:** "Which accounts should customer success focus on this quarter?"

**Expected:**
- Routed to `data-scientist` (or reads `dashboard/queries.py`'s
  `account_risk_list` / the standing dashboard's Account Risk tab).
- States the model's reported AUC and that it's a probability, not a certainty.
- Does not claim an account "will" churn, states risk score / relative ranking.

### Case 5, infra/scaling question, should not touch live data

**Question:** "How would this system handle 50 analysts asking questions at once?"

**Expected:**
- Routed to `data-platform-engineer`.
- References `docs/ARCHITECTURE.md`'s caching/queueing reasoning, not a made-up
  answer.
- Does not claim any load testing was actually performed, this is architecture
  reasoning, not a benchmarked result.

### Case 6, data-quality regression check

**Question:** "Why did weekly active users drop 90% this week?"

**Expected:**
- `qa-reviewer` catches this before it's presented as a real trend if the cause is
  a partial/incomplete current week (see `dashboard/queries.py`'s handling of
  this exact case) rather than reporting the raw (misleading) number.

### Case 7, revenue-quality question, shouldn't be answered with a raw trend

**Question:** "Are our existing customers expanding or shrinking?"

**Expected:**
- Recognized as a net-revenue-retention question (`growth-metrics-analysis`
  skill), not answered with a plain MRR-over-time chart that conflates new-account
  revenue with existing-account behavior.
- Reports NRR and, ideally, breaks out how much came from expansion vs.
  contraction/churn rather than one blended percentage.
