# 5. Incidents

## What an incident is

Something broke, or is about to, and users are affected. Incidents happen to
every team. What separates good teams is how calmly and quickly they handle
them, and whether the same one ever happens twice.

## The lifecycle

1. **Detect.** Something tells you: a health check, an alert, a user.
2. **Triage.** How bad is it, and who is affected? Decide how urgent it is.
3. **Mitigate.** Stop the bleeding first. A quick workaround that restores
   service beats a perfect fix that takes hours.
4. **Fix.** Find and remove the real cause.
5. **Verify.** Prove it is actually fixed, with the same check that caught it.
6. **Learn.** Write it down so it does not happen again.

## Health checks

To detect problems, the system needs a definition of "healthy" that a machine
can check. In this project that is
[`reliability/healthcheck.py`](../../reliability/healthcheck.py). It asks in
order:

1. Can I reach the database?
2. Are the expected tables there?
3. Is the data fresh, with no gaps?

It prints the result and exits `0` (healthy) or `1` (not). Notice it stops
early: if the database is unreachable it does not also report "tables missing",
because that is just noise on top of the real cause.

## Runbooks

A **runbook** is step-by-step instructions for one specific problem, written for
someone who is tired, stressed and maybe not the person who built the system.
Good runbooks name the symptom, how to diagnose, how to fix, and how to verify.

Read the three in [`docs/runbooks/`](../runbooks/):

- [`dashboard-down.md`](../runbooks/dashboard-down.md)
- [`stale-data.md`](../runbooks/stale-data.md)
- [`slo-breach.md`](../runbooks/slo-breach.md)

## Postmortems

A **postmortem** is a written review after an incident. The important word is
**blameless**: it asks "how did the system allow this?" and not "whose fault
was it?". If people fear blame, they hide mistakes, and hidden mistakes repeat.

A good postmortem has: a summary, a timeline, the root cause, what went well,
what went badly, and **actions that change something** (a new check, a new
alert), not just "be more careful".

Read the real one from this project:
[`postmortem-fresh-deploy-crash.md`](../runbooks/postmortem-fresh-deploy-crash.md).
Notice the table at the end that turns each problem into an action.

## Try it

**An incident drill.** Pretend the warehouse is broken. Point the health check
at an empty database:

```bash
DATABASE_URL=sqlite:///scratch_empty.db python -m reliability.healthcheck
echo "exit code: $?"
rm scratch_empty.db
```

Read the output. `warehouse reachable` is `ok: true` and `expected tables
present` is `ok: false`. That tells you where to look: the database is up but
empty, so the load did not run. Now open [`stale-data.md`](../runbooks/stale-data.md)
and read its "Fix" section as if it were real: re-run the pipeline that fills
the database, then re-run the check. In a real incident that would be against
the broken database. Here, prove the normal state is healthy (this uses the
real sample warehouse, since `DATABASE_URL` is not set):

```bash
python -m reliability.healthcheck      # healthy: true, exit code 0
```

That was detect (the check failed), triage (which layer is broken), and verify
(the same check, now passing), following a runbook.

**Write your own.** Pick one thing that could go wrong that is not in the
runbooks, for example "the dashboard is very slow". Write a runbook for it in
the same format: symptom, impact, diagnose, fix, verify. Writing one is the
best way to know you understand it.

## Check yourself

- Why mitigate before you fix?
- What does "blameless" mean and why does it matter?
- Why does the health check stop early instead of running every check?
- What makes a postmortem action good?
