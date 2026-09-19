# Access control (IAM and RBAC)

Who and what can touch the data, and why each layer exists. The rule
throughout is least privilege: every identity gets only what its job needs.

| Layer | Identity | Access | Where |
|---|---|---|---|
| Database role | `analyst_readonly` (dashboard and agents) | `SELECT` only, 30s statement timeout, 10 connections | [`infra/rbac/readonly_role.sql`](../infra/rbac/readonly_role.sql) |
| Application guard | `run_query()` | Rejects anything but `SELECT` / `WITH` / `EXPLAIN`, and logs every rejection | [`connectors/warehouse.py`](../connectors/warehouse.py) |
| Secrets | Cloud secret manager | `DATABASE_URL` is read at runtime, never in code, image or git | [`infra/aws/main.tf`](../infra/aws/main.tf), [`k8s/deployment.yaml`](../k8s/deployment.yaml) |
| Container | UID 10001, non-root | No privilege escalation, all capabilities dropped, read-only root filesystem | [`Dockerfile`](../Dockerfile), [`k8s/deployment.yaml`](../k8s/deployment.yaml) |
| ETL job | Separate scheduler role | Can write, dashboard cannot | [`infra/aws/main.tf`](../infra/aws/main.tf) |

## Why two layers guard writes

The database role is the real control: even if the application guard had a
bug, the database would refuse the write. The application guard exists so a
bad query fails fast with a clear message, and so every attempt is visible in
the query log as `status: "blocked"`. A spike in blocked queries is worth
investigating, it means something (or someone) is trying to write.

## Access reviews

A compliance check for this setup is small enough to run by hand:

1. `SELECT` privileges only for `analyst_readonly`
   (`\du+ analyst_readonly` and `\dp` in psql).
2. No credentials in git: `git log -p | grep -i "password\|postgresql://"`
   should find only placeholders.
3. Blocked-query count in the last week, from
   `logs/queries.jsonl` (`status == "blocked"`).

## What this repo does not claim

The Terraform and SQL here are illustrative and have not been applied to a
real cloud account. The container hardening and the application guard are
implemented and tested.
