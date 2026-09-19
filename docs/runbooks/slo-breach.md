# Runbook: SLO breach (availability or latency)

**Symptom:** `python -m reliability.sli` exits 1, or the error budget is
nearly spent.
**Impact:** queries are failing or slow, so dashboards and agents are
unreliable even though the app is technically up.

## Diagnose

1. See which SLO is breached:
   ```bash
   python -m reliability.sli
   ```
2. Availability breach, find what is failing:
   ```bash
   grep '"status": "error"' logs/queries.jsonl | tail -20
   ```
   The `error` field names the cause. One repeated message usually means one
   root cause (a dropped table, a timeout, a permission change).
3. Latency breach, find the five slowest queries:
   ```bash
   python -c "import json; rows=[json.loads(l) for l in open('logs/queries.jsonl')]; [print(r['duration_ms'], r['sql_preview']) for r in sorted(rows, key=lambda r: -r['duration_ms'])[:5]]"
   ```
   A few slow queries against a large table point at a missing filter or
   index. Many slow queries point at the database being under load.
4. Blocked queries are not downtime, but a spike is worth a look:
   ```bash
   grep -c '"status": "blocked"' logs/queries.jsonl
   ```

## Fix

- Slow query: add a date filter, or aggregate before joining (the fan-out rule
  in `.claude/agents/sql-engineer.md`), or ask the database owner for an index.
- Errors after a schema change: update the affected queries, then re-run the
  health check.
- Under load: scale out (`k8s/hpa.yaml` has the policy) before tuning code.

## After

If the budget was spent, write a short postmortem (use the
[existing one](postmortem-fresh-deploy-crash.md) as the template) and pause
feature work until the budget recovers.
