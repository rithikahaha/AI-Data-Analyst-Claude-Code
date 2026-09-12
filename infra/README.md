# Infrastructure-as-code (illustrative)

These Terraform configurations show how `data-platform-engineer` would deploy this
system to each major cloud, for the three things that actually need to run
somewhere once you're past a local sample warehouse:

1. A managed Postgres database (replaces the local SQLite file — set
   `connectors/warehouse.py`'s `DATABASE_URL` to point at it, nothing else changes).
2. The dashboard (`dashboard/app.py`) as a small containerized web service.
3. The ETL pipeline (`scripts/export_raw_sources.py` + `pipelines/etl.py`, or in a
   real deployment, the real source-system extraction) as a scheduled job.

**These have not been applied and no live cloud account is wired up.** They're
meant to be read and adapted, not run as-is — variables like `db_password` and
container image references are placeholders. See `docs/cloud-deployment.md` for
the reasoning behind each choice and how they compare.

| Provider | Database | Dashboard | Scheduled ETL |
|---|---|---|---|
| AWS (`aws/`) | RDS for PostgreSQL | ECS Fargate service | EventBridge Scheduler → ECS task |
| GCP (`gcp/`) | Cloud SQL for PostgreSQL | Cloud Run service | Cloud Scheduler → Cloud Run Job |
| Azure (`azure/`) | Azure Database for PostgreSQL (Flexible Server) | Container Apps | Container Apps Job (cron trigger) |
