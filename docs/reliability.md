# Reliability: SLIs, SLOs and error budget

A service level indicator (SLI) is a number that measures how the service is
behaving. A service level objective (SLO) is the target for that number. The
error budget is how much failure the SLO allows before it is breached.

## What is measured

Every query through [`connectors/warehouse.py`](../connectors/warehouse.py)
writes one JSON line to `logs/queries.jsonl`: timestamp, status, duration, row
count and the first 120 characters of the SQL. That log is the single source
for the numbers below.

| SLI | Definition | SLO |
|---|---|---|
| Availability | successful queries / (successful + failed). Queries blocked by the read-only guard are excluded, a refused `DROP` is the guard working, not an outage. | 99.5% |
| Latency | 95th percentile duration of successful queries | under 1000 ms |

p95 rather than the average, because an average hides the slow queries a user
actually waits on. A test in [`tests/test_reliability.py`](../tests/test_reliability.py)
shows a case where the mean looks fine and the p95 breaches.

## Error budget

At 99.5% availability, 1 query in 200 may fail. Over 10,000 queries that is 50
failures of budget. `python -m reliability.sli` prints how much is left. When
the budget is spent, the working rule is to stop shipping features and fix
reliability first.

## Running it

```bash
python -m reliability.sli          # SLI report, exit code 1 if an SLO is breached
python -m reliability.healthcheck  # is it up, are the tables there, is data fresh
```

Both exit non-zero on failure, so CI, a container orchestrator or a cron job
can act on them without parsing text. The health check runs inside the built
container in [CI](../.github/workflows/ci.yml).

## Alerts to set up on a real deployment

Not implemented here, since there is no live service to alert on:

- Page when the error budget burn rate would spend the whole month's budget in
  a day.
- Ticket (not page) when p95 latency stays above the SLO for an hour.
- Ticket when `monitor.py` reports a stale or gapped table.

Runbooks for each are in [`docs/runbooks/`](runbooks/).
