# Example sessions

Three real runs against the warehouse produced by
`scripts/export_raw_sources.py` → `pipelines/etl.py`, ordered from simplest to
most involved. Each one is a question you'd actually ask a data analyst, answered
by actually running the agents/skills against real data — not a mocked-up example.

---

## 1. "Where are we losing customers, and what's that costing us?"

*Agents: `analyst-lead` + `sql-engineer`, skill: `funnel-analysis`.*

Of 800 people who sign up, only 322 (40%) ever buy anything. The leak isn't where
you'd guess — it's not people bailing right after signup.

| Stage | Customers | Drop from previous stage |
|---|---|---|
| Signed up | 800 | — |
| Activated (used the product) | 617 | lost 183 (23%) |
| Made a first purchase | 322 | **lost 295 (48%)** |

**Why it matters:** almost half of everyone who activates — meaning they got in,
tried it, presumably liked it enough to keep going — still never buys. That's a
bigger, more fixable leak than the signup step, and the opposite of where most
teams look first.

**What it's worth:** the average first purchase is about $315. Closing even 10
points of that activation→purchase gap (52% → 62%) is roughly **62 more paying
customers and ~$19,500 in new revenue** from first orders alone.

**Query used:**

```sql
SELECT event_type, COUNT(DISTINCT customer_id) AS customers
FROM events
WHERE event_type IN ('signup', 'activated', 'first_purchase')
GROUP BY event_type;
```

**Caveats:** this is a snapshot of who *has* reached each stage, not a cohort
followed over time — a customer who signed up last week hasn't had time to reach
"first purchase" yet, so very recent signups slightly understate the true
eventual conversion rate.

---

## 2. "How has revenue been trending over the last few months?"

*Agents: `analyst-lead` + `sql-engineer`, skill: `revenue-trend-analysis`.*

**Revenue grew 23.1% month-over-month in August 2026, the fastest growth rate in
the last six months** — growth has been accelerating each month since April, not
slowing.

| Month | Revenue |
|---|---|
| 2026-03 | $118,503.53 |
| 2026-04 | $125,044.31 |
| 2026-05 | $147,408.54 |
| 2026-06 | $154,633.30 |
| 2026-07 | $204,715.98 |
| 2026-08 | $252,104.59 |

![Monthly revenue trend](output/revenue_trend.png)

**Query used:**

```sql
WITH monthly AS (
  SELECT strftime('%Y-%m', order_date) AS month, SUM(total_amount) AS revenue
  FROM orders
  WHERE status = 'completed'
  GROUP BY 1
)
SELECT * FROM monthly ORDER BY month;
```

**Caveats:** September 2026 is a partial month and was excluded to avoid reading
a false drop-off. Monthly order counts are small enough that a handful of large
orders can meaningfully move the number — see `.claude/skills/anomaly-detection.md`.

---

## 3. "Is our premium plan actually earning its price through better retention?"

*Agents: `analyst-lead` → `data-scientist` (stats + ML), skill: `executive-summary`.*

This one goes a step further than a lookup — it needed a significance test and a
model, not just a query, so it's included to show what "wears multiple hats"
looks like in practice.

Scale customers pay 10x what Starter customers pay (\$299 vs \$29/mo). Their churn
rate (34.2%) looks a little better than Starter's (36.5%) — but a two-proportion
significance test on that gap comes back **p = 0.69, not real, just noise** at
this sample size. The premium price isn't buying meaningfully better retention.

What *is* real: scoring every active Scale subscription with the churn model shows
**21.6% of Scale's monthly revenue is risk-weighted-exposed**, and it's
concentrated in one place — SMB customers are 51% of Scale's base but **80% of
the highest-risk accounts**. Retention spend aimed at "all Scale customers" is
diluted; aimed at that specific SMB slice, it's targeted.

**Method:** `sql-engineer` pulled plan-level churn/revenue;
`experiments/ab_test.py`'s two-proportion z-test checked whether the churn gap
was real; `ml/train_churn_model.py`'s classifier scored every active subscription,
weighted by `monthly_price`, to find where the actual dollars are at risk.

**Caveats:** the churn model's accuracy is modest (AUC ~0.55–0.63 depending on
training run) — good enough to rank relative risk and target outreach, not
good enough to treat any single customer's score as certain. The significance
test is also underpowered at this sample size, so "not significant" here means
"no evidence of a difference," not "proven equal."
