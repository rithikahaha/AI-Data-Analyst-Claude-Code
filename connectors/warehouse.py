"""Single connection point between the agents/skills and the data warehouse.

Defaults to the local sample SQLite warehouse so the project works with zero
external credentials. Point DATABASE_URL at a real warehouse (Postgres, Snowflake,
BigQuery via their SQLAlchemy dialects) to swap it in without touching any agent
or skill.
"""

import json
import os
import re
import time
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

DEFAULT_SQLITE_PATH = Path(__file__).resolve().parent.parent / "data" / "sample_warehouse.db"

_ALLOWED_STATEMENT = re.compile(r"^\s*(WITH|SELECT|EXPLAIN)\b", re.IGNORECASE)

DEFAULT_QUERY_LOG_PATH = Path(__file__).resolve().parent.parent / "logs" / "queries.jsonl"

_engine: Engine | None = None


def _log_query(sql: str, status: str, duration_ms: float, rows: int | None = None, error: str | None = None) -> None:
    """Append one JSON line per query so reliability/sli.py can compute
    availability and latency from real traffic. Logging must never be the
    reason a query fails, so any filesystem problem is swallowed.
    """
    record = {
        "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "status": status,
        "duration_ms": round(duration_ms, 2),
        "rows": rows,
        "sql_preview": " ".join(sql.split())[:120],
    }
    if error:
        record["error"] = error[:200]
    path = Path(os.environ.get("QUERY_LOG_PATH", DEFAULT_QUERY_LOG_PATH))
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")
    except OSError:
        pass


def get_engine() -> Engine:
    """Return a cached SQLAlchemy engine for the configured warehouse."""
    global _engine
    if _engine is not None:
        return _engine

    database_url = os.environ.get("DATABASE_URL")
    if database_url:
        _engine = create_engine(database_url)
    else:
        _engine = create_engine(f"sqlite:///{DEFAULT_SQLITE_PATH}")
    return _engine


def run_query(sql: str) -> pd.DataFrame:
    """Run a read-only SQL query and return the result as a DataFrame.

    Rejects anything that isn't a SELECT/WITH/EXPLAIN statement, this project
    never writes to the warehouse from an agent.
    """
    if not _ALLOWED_STATEMENT.match(sql):
        _log_query(sql, "blocked", 0.0)
        raise ValueError(
            "Only read-only SELECT/WITH/EXPLAIN statements are allowed through "
            "connectors.warehouse.run_query()."
        )
    started = time.perf_counter()
    try:
        engine = get_engine()
        with engine.connect() as conn:
            df = pd.read_sql(text(sql), conn)
    except Exception as exc:
        _log_query(sql, "error", (time.perf_counter() - started) * 1000, error=str(exc))
        raise
    _log_query(sql, "ok", (time.perf_counter() - started) * 1000, rows=len(df))
    return df


def list_tables() -> list[str]:
    """List table names in the current warehouse, regardless of dialect."""
    engine = get_engine()
    if engine.dialect.name == "sqlite":
        df = run_query("SELECT name FROM sqlite_master WHERE type='table'")
    else:
        df = run_query(
            "SELECT table_name AS name FROM information_schema.tables "
            "WHERE table_schema NOT IN ('pg_catalog', 'information_schema')"
        )
    return df["name"].tolist()
