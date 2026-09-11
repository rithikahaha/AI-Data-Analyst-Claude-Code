"""Generate a realistic sample warehouse so the agents/skills work out of the box.

Models a small subscription e-commerce business over ~2 years: customers, products,
orders/order_items, subscriptions (for churn/retention), and a signup->activation->
purchase funnel (as events) — enough breadth to exercise every skill in
.claude/skills/ without needing a real warehouse connection.
"""

import random
import sqlite3
from datetime import date, timedelta
from pathlib import Path

from faker import Faker

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "sample_warehouse.db"
START_DATE = date(2024, 1, 1)
END_DATE = date(2026, 9, 1)
N_CUSTOMERS = 800

fake = Faker()
Faker.seed(42)
random.seed(42)

REGIONS = ["North America", "Europe", "APAC", "Latin America"]
SEGMENTS = ["SMB", "Mid-Market", "Enterprise"]
PLANS = [("Starter", 29), ("Growth", 99), ("Scale", 299)]
CATEGORIES = ["Software Add-on", "Professional Services", "Data Export", "Support Plan"]


def random_date(start: date, end: date) -> date:
    return start + timedelta(days=random.randint(0, (end - start).days))


def build_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        DROP TABLE IF EXISTS customers;
        DROP TABLE IF EXISTS products;
        DROP TABLE IF EXISTS orders;
        DROP TABLE IF EXISTS order_items;
        DROP TABLE IF EXISTS subscriptions;
        DROP TABLE IF EXISTS events;

        CREATE TABLE customers (
            id INTEGER PRIMARY KEY,
            name TEXT,
            email TEXT,
            signup_date TEXT,
            region TEXT,
            segment TEXT
        );

        CREATE TABLE products (
            id INTEGER PRIMARY KEY,
            name TEXT,
            category TEXT,
            price REAL
        );

        CREATE TABLE orders (
            id INTEGER PRIMARY KEY,
            customer_id INTEGER REFERENCES customers(id),
            order_date TEXT,
            status TEXT,
            total_amount REAL
        );

        CREATE TABLE order_items (
            id INTEGER PRIMARY KEY,
            order_id INTEGER REFERENCES orders(id),
            product_id INTEGER REFERENCES products(id),
            quantity INTEGER,
            unit_price REAL
        );

        CREATE TABLE subscriptions (
            id INTEGER PRIMARY KEY,
            customer_id INTEGER REFERENCES customers(id),
            plan TEXT,
            monthly_price REAL,
            start_date TEXT,
            end_date TEXT,
            status TEXT
        );

        CREATE TABLE events (
            id INTEGER PRIMARY KEY,
            customer_id INTEGER REFERENCES customers(id),
            event_type TEXT,
            event_date TEXT
        );
        """
    )


def seed_customers(conn: sqlite3.Connection) -> list[dict]:
    customers = []
    for i in range(1, N_CUSTOMERS + 1):
        signup = random_date(START_DATE, END_DATE - timedelta(days=1))
        customers.append(
            {
                "id": i,
                "name": fake.name(),
                "email": fake.email(),
                "signup_date": signup.isoformat(),
                "region": random.choice(REGIONS),
                "segment": random.choices(SEGMENTS, weights=[0.6, 0.3, 0.1])[0],
            }
        )
    conn.executemany(
        "INSERT INTO customers VALUES (:id, :name, :email, :signup_date, :region, :segment)",
        customers,
    )
    return customers


def seed_products(conn: sqlite3.Connection) -> list[dict]:
    products = []
    pid = 1
    for category in CATEGORIES:
        for _ in range(3):
            products.append(
                {
                    "id": pid,
                    "name": f"{category} - {fake.word().capitalize()}",
                    "category": category,
                    "price": round(random.uniform(15, 250), 2),
                }
            )
            pid += 1
    conn.executemany(
        "INSERT INTO products VALUES (:id, :name, :category, :price)", products
    )
    return products


def seed_funnel_events(conn: sqlite3.Connection, customers: list[dict]) -> None:
    events = []
    eid = 1
    for c in customers:
        signup = date.fromisoformat(c["signup_date"])
        events.append({"id": eid, "customer_id": c["id"], "event_type": "signup", "event_date": signup.isoformat()})
        eid += 1
        # Not everyone activates, and not everyone who activates buys.
        if random.random() < 0.75:
            activated = signup + timedelta(days=random.randint(0, 14))
            if activated <= END_DATE:
                events.append({"id": eid, "customer_id": c["id"], "event_type": "activated", "event_date": activated.isoformat()})
                eid += 1
                if random.random() < 0.55:
                    purchased = activated + timedelta(days=random.randint(0, 30))
                    if purchased <= END_DATE:
                        events.append({"id": eid, "customer_id": c["id"], "event_type": "first_purchase", "event_date": purchased.isoformat()})
                        eid += 1
    conn.executemany(
        "INSERT INTO events VALUES (:id, :customer_id, :event_type, :event_date)", events
    )


def seed_orders(conn: sqlite3.Connection, customers: list[dict], products: list[dict]) -> None:
    orders = []
    order_items = []
    oid = 1
    item_id = 1
    for c in customers:
        signup = date.fromisoformat(c["signup_date"])
        if random.random() >= 0.55:
            continue  # matches the "first_purchase" funnel drop-off above
        n_orders = random.randint(1, 12)
        for _ in range(n_orders):
            order_date = random_date(signup, END_DATE)
            status = random.choices(
                ["completed", "refunded", "cancelled"], weights=[0.9, 0.06, 0.04]
            )[0]
            chosen_products = random.sample(products, k=random.randint(1, 3))
            total = 0.0
            for p in chosen_products:
                qty = random.randint(1, 4)
                order_items.append(
                    {
                        "id": item_id,
                        "order_id": oid,
                        "product_id": p["id"],
                        "quantity": qty,
                        "unit_price": p["price"],
                    }
                )
                total += qty * p["price"]
                item_id += 1
            orders.append(
                {
                    "id": oid,
                    "customer_id": c["id"],
                    "order_date": order_date.isoformat(),
                    "status": status,
                    "total_amount": round(total, 2),
                }
            )
            oid += 1
    conn.executemany(
        "INSERT INTO orders VALUES (:id, :customer_id, :order_date, :status, :total_amount)",
        orders,
    )
    conn.executemany(
        "INSERT INTO order_items VALUES (:id, :order_id, :product_id, :quantity, :unit_price)",
        order_items,
    )


def seed_subscriptions(conn: sqlite3.Connection, customers: list[dict]) -> None:
    subs = []
    sid = 1
    for c in customers:
        if random.random() >= 0.5:
            continue
        signup = date.fromisoformat(c["signup_date"])
        plan_name, plan_price = random.choice(PLANS)
        start = signup + timedelta(days=random.randint(0, 10))
        # Segment-weighted churn: Enterprise churns least, SMB churns most.
        churn_prob = {"SMB": 0.5, "Mid-Market": 0.3, "Enterprise": 0.12}[c["segment"]]
        churned = random.random() < churn_prob
        end = None
        status = "active"
        if churned:
            tenure_days = int(random.expovariate(1 / 180))
            end_candidate = start + timedelta(days=max(15, tenure_days))
            if end_candidate <= END_DATE:
                end = end_candidate.isoformat()
                status = "churned"
        if start > END_DATE:
            continue
        subs.append(
            {
                "id": sid,
                "customer_id": c["id"],
                "plan": plan_name,
                "monthly_price": plan_price,
                "start_date": start.isoformat(),
                "end_date": end,
                "status": status,
            }
        )
        sid += 1
    conn.executemany(
        "INSERT INTO subscriptions VALUES (:id, :customer_id, :plan, :monthly_price, :start_date, :end_date, :status)",
        subs,
    )


def main() -> None:
    DB_PATH.parent.mkdir(exist_ok=True)
    if DB_PATH.exists():
        DB_PATH.unlink()
    conn = sqlite3.connect(DB_PATH)
    try:
        build_schema(conn)
        customers = seed_customers(conn)
        products = seed_products(conn)
        seed_funnel_events(conn, customers)
        seed_orders(conn, customers, products)
        seed_subscriptions(conn, customers)
        conn.commit()
    finally:
        conn.close()
    print(f"Seeded sample warehouse at {DB_PATH}")


if __name__ == "__main__":
    main()
