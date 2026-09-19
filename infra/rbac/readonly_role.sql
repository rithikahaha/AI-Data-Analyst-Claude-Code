-- Least-privilege database role for the dashboard and the agents.
-- Illustrative for a Postgres warehouse; never applied from this repo.
-- Run once by a database admin, then put this role's connection string in the
-- secret manager as DATABASE_URL.

CREATE ROLE analyst_readonly LOGIN PASSWORD :'analyst_password';  -- pass via psql -v, never commit

GRANT CONNECT ON DATABASE analytics TO analyst_readonly;
GRANT USAGE ON SCHEMA public TO analyst_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO analyst_readonly;

-- Tables created later by the ETL job are readable too, without a new grant.
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO analyst_readonly;

-- Explicitly no write or DDL access. Belt and braces: the connector's
-- statement guard is the second layer, this is the first.
REVOKE CREATE ON SCHEMA public FROM analyst_readonly;

-- A runaway query should not be able to starve the ETL job.
ALTER ROLE analyst_readonly SET statement_timeout = '30s';
ALTER ROLE analyst_readonly CONNECTION LIMIT 10;
