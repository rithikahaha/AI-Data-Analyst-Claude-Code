"""Load the raw source extracts (data/raw/*.csv, from
scripts/export_raw_sources.py) into the warehouse, with data-quality checks
before and after transform.

This is the reference pipeline data-platform-engineer maintains: land raw data
untouched, transform explicitly and re-runnably, validate on both sides of the
transform, and fail loudly rather than silently loading bad data.
"""

import sqlite3
from pathlib import Path

import pandas as pd

from pipelines.data_quality import (
    check_nulls,
    check_referential_integrity,
    check_uniqueness,
    run_checks_and_report,
)

RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"
DB_PATH = Path(__file__).resolve().parent.parent / "data" / "sample_warehouse.db"


def extract() -> dict[str, pd.DataFrame]:
    return {
        "organizations": pd.read_csv(RAW_DIR / "organizations.csv"),
        "users": pd.read_csv(RAW_DIR / "users.csv"),
        "subscriptions": pd.read_csv(RAW_DIR / "subscriptions.csv"),
        "product_events": pd.read_csv(RAW_DIR / "product_events.csv"),
    }


def validate_raw(raw: dict[str, pd.DataFrame]) -> None:
    results = [
        check_nulls(raw["organizations"], ["id", "name", "signed_up_date"], "raw.organizations"),
        check_uniqueness(raw["organizations"], ["id"], "raw.organizations"),
        check_nulls(raw["users"], ["id", "org_id", "email"], "raw.users"),
        check_referential_integrity(raw["users"], "org_id", raw["organizations"], "id", "raw.users -> raw.organizations"),
        check_referential_integrity(raw["subscriptions"], "org_id", raw["organizations"], "id", "raw.subscriptions -> raw.organizations"),
        check_referential_integrity(raw["product_events"], "user_id", raw["users"], "id", "raw.product_events -> raw.users"),
    ]
    # Raw organizations is EXPECTED to fail uniqueness here, that's the
    # simulated source-system overlap this pipeline exists to clean up in
    # transform().
    run_checks_and_report(results, "raw extracts (pre-transform)")


def transform(raw: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    organizations = raw["organizations"].drop_duplicates(subset=["id"]).reset_index(drop=True)

    subscriptions = raw["subscriptions"].copy()
    subscriptions["mrr"] = (subscriptions["current_seat_count"] * subscriptions["price_per_seat"]).round(2)
    subscriptions.loc[subscriptions["status"] == "churned", "mrr"] = 0.0
    subscriptions["initial_mrr"] = (subscriptions["initial_seat_count"] * subscriptions["price_per_seat"]).round(2)

    return {
        "organizations": organizations,
        "users": raw["users"],
        "subscriptions": subscriptions,
        "product_events": raw["product_events"],
    }


def validate_transformed(tables: dict[str, pd.DataFrame]) -> bool:
    results = [
        check_uniqueness(tables["organizations"], ["id"], "transformed.organizations"),
        check_nulls(tables["subscriptions"], ["mrr", "initial_mrr"], "transformed.subscriptions"),
        check_referential_integrity(tables["product_events"], "org_id", tables["organizations"], "id", "product_events -> organizations"),
    ]
    return run_checks_and_report(results, "transformed tables (pre-load)")


def load(tables: dict[str, pd.DataFrame]) -> None:
    if DB_PATH.exists():
        DB_PATH.unlink()
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.executescript(
            """
            CREATE TABLE organizations (id INTEGER PRIMARY KEY, name TEXT, industry TEXT, region TEXT, signed_up_date TEXT);
            CREATE TABLE users (id INTEGER PRIMARY KEY, org_id INTEGER REFERENCES organizations(id), name TEXT, email TEXT, role TEXT, joined_date TEXT);
            CREATE TABLE subscriptions (
                id INTEGER PRIMARY KEY, org_id INTEGER REFERENCES organizations(id), plan_tier TEXT,
                price_per_seat REAL, initial_seat_count INTEGER, current_seat_count INTEGER,
                start_date TEXT, end_date TEXT, status TEXT, mrr REAL, initial_mrr REAL
            );
            CREATE TABLE product_events (id INTEGER PRIMARY KEY, user_id INTEGER REFERENCES users(id), org_id INTEGER REFERENCES organizations(id), event_type TEXT, event_date TEXT);
            """
        )
        tables["organizations"].to_sql("organizations", conn, if_exists="append", index=False)
        tables["users"].to_sql("users", conn, if_exists="append", index=False)
        tables["subscriptions"].to_sql("subscriptions", conn, if_exists="append", index=False)
        tables["product_events"].to_sql("product_events", conn, if_exists="append", index=False)
        conn.commit()
    finally:
        conn.close()


def validate_loaded() -> bool:
    from connectors.warehouse import run_query

    organizations = run_query("SELECT * FROM organizations")
    subscriptions = run_query("SELECT * FROM subscriptions")
    results = [
        check_uniqueness(organizations, ["id"], "warehouse.organizations"),
        check_nulls(subscriptions, ["mrr"], "warehouse.subscriptions"),
    ]
    return run_checks_and_report(results, "warehouse (post-load)")


def main() -> None:
    raw = extract()
    validate_raw(raw)
    tables = transform(raw)
    if not validate_transformed(tables):
        raise SystemExit("Transformed data failed validation, aborting load.")
    load(tables)
    if not validate_loaded():
        raise SystemExit("Post-load validation failed on the warehouse.")
    print(f"\nLoaded warehouse at {DB_PATH}")


if __name__ == "__main__":
    main()
