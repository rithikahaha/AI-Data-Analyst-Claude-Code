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
        "customers": pd.read_csv(RAW_DIR / "customers.csv"),
        "products": pd.read_csv(RAW_DIR / "products.csv"),
        "orders": pd.read_csv(RAW_DIR / "orders.csv"),
        "order_items": pd.read_csv(RAW_DIR / "order_items.csv"),
        "subscriptions": pd.read_csv(RAW_DIR / "subscriptions.csv"),
        "events": pd.read_csv(RAW_DIR / "events.csv"),
    }


def validate_raw(raw: dict[str, pd.DataFrame]) -> None:
    results = [
        check_nulls(raw["customers"], ["id", "email", "signup_date"], "raw.customers"),
        check_uniqueness(raw["customers"], ["id"], "raw.customers"),
        check_nulls(raw["orders"], ["id", "customer_id", "order_date"], "raw.orders"),
        check_referential_integrity(raw["orders"], "customer_id", raw["customers"], "id", "raw.orders -> raw.customers"),
        check_referential_integrity(raw["order_items"], "order_id", raw["orders"], "id", "raw.order_items -> raw.orders"),
        check_referential_integrity(raw["subscriptions"], "customer_id", raw["customers"], "id", "raw.subscriptions -> raw.customers"),
    ]
    # Raw customers is EXPECTED to fail uniqueness here — that's the simulated
    # source-system overlap this pipeline exists to clean up in transform().
    run_checks_and_report(results, "raw extracts (pre-transform)")


def transform(raw: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    customers = raw["customers"].drop_duplicates(subset=["id"]).reset_index(drop=True)

    order_totals = (
        raw["order_items"].assign(line_total=lambda df: df["quantity"] * df["unit_price"])
        .groupby("order_id")["line_total"]
        .sum()
        .rename("total_amount")
    )
    orders = raw["orders"].merge(order_totals, left_on="id", right_index=True, how="left")
    orders["total_amount"] = orders["total_amount"].fillna(0.0).round(2)

    return {
        "customers": customers,
        "products": raw["products"],
        "orders": orders,
        "order_items": raw["order_items"],
        "subscriptions": raw["subscriptions"],
        "events": raw["events"],
    }


def validate_transformed(tables: dict[str, pd.DataFrame]) -> bool:
    results = [
        check_uniqueness(tables["customers"], ["id"], "transformed.customers"),
        check_nulls(tables["orders"], ["total_amount"], "transformed.orders"),
        check_referential_integrity(tables["order_items"], "product_id", tables["products"], "id", "order_items -> products"),
    ]
    return run_checks_and_report(results, "transformed tables (pre-load)")


def load(tables: dict[str, pd.DataFrame]) -> None:
    if DB_PATH.exists():
        DB_PATH.unlink()
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.executescript(
            """
            CREATE TABLE customers (id INTEGER PRIMARY KEY, name TEXT, email TEXT, signup_date TEXT, region TEXT, segment TEXT);
            CREATE TABLE products (id INTEGER PRIMARY KEY, name TEXT, category TEXT, price REAL);
            CREATE TABLE orders (id INTEGER PRIMARY KEY, customer_id INTEGER REFERENCES customers(id), order_date TEXT, status TEXT, total_amount REAL);
            CREATE TABLE order_items (id INTEGER PRIMARY KEY, order_id INTEGER REFERENCES orders(id), product_id INTEGER REFERENCES products(id), quantity INTEGER, unit_price REAL);
            CREATE TABLE subscriptions (id INTEGER PRIMARY KEY, customer_id INTEGER REFERENCES customers(id), plan TEXT, monthly_price REAL, start_date TEXT, end_date TEXT, status TEXT);
            CREATE TABLE events (id INTEGER PRIMARY KEY, customer_id INTEGER REFERENCES customers(id), event_type TEXT, event_date TEXT);
            """
        )
        tables["customers"].to_sql("customers", conn, if_exists="append", index=False)
        tables["products"].to_sql("products", conn, if_exists="append", index=False)
        tables["orders"][["id", "customer_id", "order_date", "status", "total_amount"]].to_sql(
            "orders", conn, if_exists="append", index=False
        )
        tables["order_items"].to_sql("order_items", conn, if_exists="append", index=False)
        tables["subscriptions"].to_sql("subscriptions", conn, if_exists="append", index=False)
        tables["events"].to_sql("events", conn, if_exists="append", index=False)
        conn.commit()
    finally:
        conn.close()


def validate_loaded() -> bool:
    from connectors.warehouse import run_query

    customers = run_query("SELECT * FROM customers")
    orders = run_query("SELECT * FROM orders")
    results = [
        check_uniqueness(customers, ["id"], "warehouse.customers"),
        check_nulls(orders, ["total_amount"], "warehouse.orders"),
    ]
    return run_checks_and_report(results, "warehouse (post-load)")


def main() -> None:
    raw = extract()
    validate_raw(raw)
    tables = transform(raw)
    if not validate_transformed(tables):
        raise SystemExit("Transformed data failed validation — aborting load.")
    load(tables)
    if not validate_loaded():
        raise SystemExit("Post-load validation failed on the warehouse.")
    print(f"\nLoaded warehouse at {DB_PATH}")


if __name__ == "__main__":
    main()
