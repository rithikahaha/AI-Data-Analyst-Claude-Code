# Runbook: dashboard down or unhealthy

**Symptom:** the dashboard URL fails to load, the container shows `unhealthy`,
or a Kubernetes pod is in `CrashLoopBackOff` or not Ready.
**Impact:** stakeholders cannot see engagement, revenue or account-risk numbers.
**Severity:** medium. It is a read-only reporting tool, no data is at risk.

## Diagnose

1. Is the process up? Streamlit answers its own liveness endpoint:
   ```bash
   curl -fsS http://localhost:8501/_stcore/health     # prints "ok" when healthy
   docker ps --format "{{.Names}} {{.Status}}"         # look for (unhealthy)
   kubectl get pods -l app=ai-data-analyst-dashboard   # Ready column, RESTARTS count
   ```
2. Read the last logs before it died:
   ```bash
   docker logs --tail 50 <container>
   kubectl logs -l app=ai-data-analyst-dashboard --tail=50
   ```
3. Is the data layer the cause? The health check separates "app is broken"
   from "warehouse or data is broken":
   ```bash
   docker compose run --rm healthcheck
   python -m reliability.healthcheck
   ```

## Common causes and fixes

| What you see | Cause | Fix |
|---|---|---|
| Health check fails on `warehouse reachable` | Wrong or expired `DATABASE_URL`, or the database is down | Check the secret, then the database. Rotate the credential if it expired. |
| Health check fails on `expected tables present` | The ETL job did not run or wrote to a different schema | Re-run `python -m pipelines.etl`, see [stale-data](stale-data.md) |
| `FileNotFoundError` for `sample_warehouse.db` or the churn model | A fresh deploy without generated files. Fixed in `ensure_sample_data()`, see the [postmortem](postmortem-fresh-deploy-crash.md) | Confirm you are running a build that includes that fix |
| Pod `OOMKilled` | Memory limit (512Mi) too low for the dataset | Raise the limit in `k8s/deployment.yaml`, then check p95 latency afterwards |

## Verify it is fixed

The health endpoint returns `ok`, `python -m reliability.healthcheck` exits 0,
and `python -m reliability.sli` shows availability back above 99.5%.

## Escalate

If the cause is the warehouse itself and not this app, hand over to whoever
owns the database, with the health-check JSON output attached.
