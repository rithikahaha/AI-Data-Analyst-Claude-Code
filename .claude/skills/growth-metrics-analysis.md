---
name: growth-metrics-analysis
description: Standard playbook for "how is engagement/revenue trending" questions — WAU/MAU trend, MRR trend, and net revenue retention. Use for any question about active users, engagement, MRR, or account expansion/contraction over time.
---

# Growth Metrics Analysis

SaaS growth has two axes that get conflated too easily — check which one the
question is actually asking about before picking a query.

## Engagement (WAU/MAU)

1. Confirm the definition: an "active user" here means a `login` event in
   `product_events` within the window (see `knowledge/metrics_glossary.md`).
2. Aggregate by the right grain — weekly for most engagement questions:
   ```sql
   SELECT strftime('%Y-%W', event_date) AS week, COUNT(DISTINCT user_id) AS wau
   FROM product_events
   WHERE event_type = 'login'
   GROUP BY 1
   ORDER BY 1;
   ```
3. Drop the current partial week/month before reporting a trend — an
   in-progress period will look like a fake drop-off otherwise.
4. Compute week-over-week or month-over-month change alongside the raw trend,
   not just the raw numbers.

## Revenue (MRR / net revenue retention)

1. MRR per account is `current_seat_count * price_per_seat`
   (`subscriptions.mrr`, already computed by `pipelines/etl.py`) — 0 for
   churned accounts.
2. A plain MRR trend mixes new-account revenue with existing-account growth.
   If the question is really "are our existing customers happy" rather than
   "are we growing," compute **net revenue retention** instead:
   `SUM(mrr) / SUM(initial_mrr)` among established accounts (started ≥90 days
   before the most recent activity) — see `knowledge/metrics_glossary.md`.
3. Break NRR into its components when the number looks surprising: how much
   came from expansion (`current_seat_count > initial_seat_count`) versus how
   much was lost to contraction and churn — a business can't act on a single
   blended percentage.

## Answer format

State which of the two axes (engagement or revenue) the question is actually
about before answering — they can move in opposite directions and conflating
them is a common way to give a misleading answer. Lead with the direction and
magnitude, then the trend chart, then the query.
