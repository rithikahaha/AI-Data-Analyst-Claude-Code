# Runbook: stale or missing data

**Symptom:** `pipelines/monitor.py` (or the health check) reports an ALERT:
a table is behind, a month has no rows, or volume dropped sharply.
**Impact:** dashboards and agent answers look normal but are wrong or out of
date. This is the dangerous kind of failure, because nothing visibly breaks.
**Severity:** high if a stakeholder is about to act on the numbers.

## Diagnose

1. Read the alert, it says which table and which check:
   ```bash
   python -m pipelines.monitor
   ```
2. Match the alert to a cause:

   | Alert | Most likely cause |
   |---|---|
   | `freshness` (events behind signups) | The events export stopped while signups kept flowing from another source |
   | `calendar-gap` (a month with zero rows) | A batch silently failed for that period |
   | `month-over-month volume` (sharp drop) | A partial load, or an upstream tracking change |

3. Check the ETL job's own data-quality output for the failing load:
   ```bash
   python -m pipelines.etl
   ```
   The checks print PASS or FAIL for nulls, duplicates and referential integrity.

## Fix

1. Fix the upstream cause (re-run the failed export, restore the tracking).
2. Re-run the pipeline: `python -m scripts.export_raw_sources && python -m pipelines.etl`.
3. Re-run the monitor. Do not close the incident just because the alert
   cleared, spot-check one number against the source system.

## Communicate

Tell anyone who used the affected numbers since the failure began. Being
wrong silently is worse than saying so early.
