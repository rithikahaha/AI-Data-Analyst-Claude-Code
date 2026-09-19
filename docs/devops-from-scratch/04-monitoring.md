# 4. Monitoring

## The problem

A service can be broken and nobody knows. Or it is slowly getting worse and
nobody notices until users complain. "It seems fine" is not a measurement.

## Three tools

| Tool | What it is | Everyday version |
|---|---|---|
| **Logs** | A diary: one line per thing that happened | A receipt for every order |
| **Metrics** | Numbers over time | Orders per hour, average wait |
| **Alerts** | A tap on the shoulder when a number goes bad | "The queue is over 20 minutes" |

In this project every database query writes one line to
`logs/queries.jsonl`. Look at one:

```json
{"ts": "2026-09-19T10:20:36+00:00", "status": "ok", "duration_ms": 42.4, "rows": 1, "sql_preview": "SELECT 1 AS x"}
```

That single log is the raw material. Metrics are computed from it.

## SLI, SLO, error budget

Three terms that sound scary and are simple.

- **SLI (Service Level Indicator):** a number that measures behaviour. "The
  share of queries that succeeded."
- **SLO (Service Level Objective):** the target for that number. "At least
  99.5%."
- **Error budget:** how much failure the target allows. The gap between 100%
  and the target.

Worked example. SLO is 99.5% success. Out of 10,000 queries:

- Allowed failures: 0.5% of 10,000 = **50**. That is the budget.
- If 20 failed, you have used 40% of the budget and have 60% left.
- If 60 failed, you are over budget, the SLO is breached.

**Why an error budget is clever:** it turns an argument into arithmetic. While
there is budget left, the team can ship new things. When it is spent, stop
shipping and fix reliability. Nobody has to argue about "is it stable enough".

This project's two SLOs, in [`docs/reliability.md`](../reliability.md):

| SLI | Target |
|---|---|
| Availability: share of queries that succeed | 99.5% |
| Latency: how long the slowest 5% take | under 1000 ms |

Queries the read-only guard blocked (someone tried a `DROP TABLE`) are not
counted as failures. The guard refusing is the system working.

## Why p95 and not the average

Ten customers wait: nine wait 1 minute, one waits 60 minutes. The average is
about 7 minutes, which sounds okay. But one person had a terrible time.

**p95** means "95% of requests were faster than this". It looks at the slow
tail, which is what unhappy users feel. There is a test that shows this exact
case: `test_slow_tail_breaches_latency_slo_even_when_average_is_fine` in
[`tests/test_reliability.py`](../../tests/test_reliability.py).

## Alerts: page or ticket

If every small thing wakes someone at 3am, people start ignoring alerts (alert
fatigue). A good rule:

- **Page** (wake someone): users are hurt right now, or the error budget will
  be gone very soon.
- **Ticket** (look tomorrow): something is drifting but nobody is hurt yet.

The list of alerts a real deployment would set is in
[`docs/reliability.md`](../reliability.md). None are wired up here, because
there is no live service to alert on.

## Where the real tools fit

The job posting mentions **Azure Monitor** and **CloudWatch**. They are the
cloud providers' managed versions of what `reliability/sli.py` does by hand:
collect logs and metrics, draw graphs, fire alerts. Learn the concepts here,
then the tool is mostly learning where the buttons are.

## Try it

Run the SLI report on your real log:

```bash
python -m reliability.sli
```

Now **fake an outage**. This writes 90 good queries and 10 failed ones into a
scratch file, so your real log is untouched:

```bash
python - <<'PY'
import json
rows = [{"status": "ok", "duration_ms": 40}] * 90 + [{"status": "error", "duration_ms": 5, "error": "no such table: users"}] * 10
open("scratch_log.jsonl", "w").write("\n".join(json.dumps(r) for r in rows) + "\n")
PY
QUERY_LOG_PATH=scratch_log.jsonl python -m reliability.sli
echo "exit code: $?"
```

You should see availability 90.00%, the error budget at 0.0%, and
`SLO BREACHED`. The exit code is `1`. Delete `scratch_log.jsonl` when done.

Then run the tests that cover it: `python -m pytest tests/test_reliability.py -v`.

## Check yourself

- What is the difference between an SLI and an SLO?
- With a 99% SLO and 1,000 requests, how many failures are allowed?
- Why can the average look fine while users are unhappy?
- Why are blocked queries not counted as downtime?
