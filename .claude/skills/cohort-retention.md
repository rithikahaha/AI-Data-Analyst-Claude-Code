---
name: cohort-retention
description: Standard playbook for cohort-based retention or repeat-purchase analysis — grouping customers by signup/first-order period and tracking activity over subsequent periods. Use for churn, retention, or "do customers come back" questions.
---

# Cohort Retention Analysis

## Steps

1. Define the cohort: group customers by the period of their first qualifying event
   (e.g., first order month, signup month).
   ```sql
   WITH first_order AS (
     SELECT customer_id, MIN(strftime('%Y-%m', order_date)) AS cohort_month
     FROM orders
     WHERE status = 'completed'
     GROUP BY customer_id
   )
   ```
2. Join back to all activity and compute the period offset from the cohort month
   (0 = same month, 1 = one month later, etc.).
3. Build a cohort x period-offset matrix of active-customer counts, then convert to
   retention % of the original cohort size.
4. Watch for right-censoring: recent cohorts haven't had time to reach later period
   offsets — don't compare a cohort's month-6 retention if it's only 2 months old.
   Flag this in QA rather than silently truncating.
5. Report both the retention curve shape (steep early drop-off vs. gradual) and
   whether it's improving or worsening across successive cohorts.

## Answer format

State whether retention is improving/worsening across cohorts first, then show the
cohort table or heatmap, then the query. Explicitly note which cohorts are too young
to compare on later-period retention.
