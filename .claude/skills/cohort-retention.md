---
name: cohort-retention
description: Standard playbook for cohort-based retention analysis, grouping users or accounts by signup period and tracking whether they're still active over subsequent periods. Use for engagement retention, account retention, or "do users/accounts stick around" questions.
---

# Cohort Retention Analysis

## Steps

1. Define the cohort: group users by the month they signed up.
   ```sql
   WITH cohort AS (
     SELECT id AS user_id, org_id, strftime('%Y-%m', joined_date) AS cohort_month
     FROM users
   )
   ```
2. Join to `product_events` and compute, for each subsequent calendar month,
   whether that user logged any activity (not just `login`, "retained" for
   product usage is broader than the strict WAU definition used for engagement
   trend), then compute the period offset from the cohort month (0 = same
   month, 1 = one month later, etc.).
3. Build a cohort x period-offset matrix of active-user counts, then convert to
   retention % of the original cohort size.
4. Watch for right-censoring: recent cohorts haven't had time to reach later
   period offsets, don't compare a cohort's month-6 retention if it's only 2
   months old. Flag this in QA rather than silently truncating.
5. Report both the retention curve shape (steep early drop-off vs. gradual) and
   whether it's improving or worsening across successive cohorts.
6. If the question is really about revenue retention rather than usage
   retention, use `growth-metrics-analysis`'s net-revenue-retention method
   instead, they answer different questions and shouldn't be conflated.

## Answer format

State whether retention is improving/worsening across cohorts first, then show
the cohort table or heatmap, then the query. Explicitly note which cohorts are
too young to compare on later-period retention.
