"""Single connection point between the agents/skills and the data warehouse.

Defaults to the local sample SQLite warehouse so the project works with zero
external credentials. Point DATABASE_URL at a real warehouse (Postgres, Snowflake,
BigQuery via their SQLAlchemy dialects) to swap it in without touching any agent
or skill.
"""

import os
import re
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

_engine: Engine | None = None


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

    Rejects anything that isn't a SELECT/WITH/EXPLAIN statement — this project
    never writes to the warehouse from an agent.
    """
    if not _ALLOWED_STATEMENT.match(sql):
        raise ValueError(
            "Only read-only SELECT/WITH/EXPLAIN statements are allowed through "
            "connectors.warehouse.run_query()."
        )
    engine = get_engine()
    with engine.connect() as conn:
        return pd.read_sql(text(sql), conn)


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
