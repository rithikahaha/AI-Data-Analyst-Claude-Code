"""Simulate raw extracts from the business's source systems: a CRM export
(customers), a catalog export (products), an order-system export
(orders/order_items), a billing-system export (subscriptions), and a product
analytics export (events).

Writes to data/raw/*.csv — deliberately un-transformed and slightly messy (a
handful of duplicate customer rows, as a re-exported CRM extract would produce;
order totals left uncomputed, as the order system tracks line items, not
totals) so pipelines/etl.py has real transform and data-quality work to do,
not just a pass-through load.
"""

import random
from datetime import date, timedelta
from pathlib import Path

import pandas as pd
from faker import Faker

RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"
START_DATE = date(2024, 1, 1)
END_DATE = date(2026, 9, 1)
N_CUSTOMERS = 800
DUPLICATE_CUSTOMER_ROWS = 12  # simulates a CRM re-export overlap

fake = Faker()
Faker.seed(42)
random.seed(42)

REGIONS = ["North America", "Europe", "APAC", "Latin America"]
SEGMENTS = ["SMB", "Mid-Market", "Enterprise"]
PLANS = [("Starter", 29), ("Growth", 99), ("Scale", 299)]
CATEGORIES = ["Software Add-on", "Professional Services", "Data Export", "Support Plan"]


def random_date(start: date, end: date) -> date:
    return start + timedelta(days=random.randint(0, (end - start).days))


def export_customers() -> list[dict]:
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

    # A source-system re-export overlap: a handful of customers appear twice,
    # exactly as a CRM incremental export re-sending recently-touched records
    # alongside a full backfill would look.
    duplicates = random.sample(customers, k=DUPLICATE_CUSTOMER_ROWS)
    all_rows = customers + duplicates

    pd.DataFrame(all_rows).to_csv(RAW_DIR / "customers.csv", index=False)
    return customers  # de-duplicated list for downstream generation


def export_products() -> list[dict]:
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
    pd.DataFrame(products).to_csv(RAW_DIR / "products.csv", index=False)
    return products


def export_events(customers: list[dict]) -> None:
    events = []
    eid = 1
    for c in customers:
        signup = date.fromisoformat(c["signup_date"])
        events.append({"id": eid, "customer_id": c["id"], "event_type": "signup", "event_date": signup.isoformat()})
        eid += 1
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
    pd.DataFrame(events).to_csv(RAW_DIR / "events.csv", index=False)


def export_orders(customers: list[dict], products: list[dict]) -> None:
    """The order system exports orders (header) and order_items (line items)
    separately — total_amount is not a column here, it's derived downstream in
    the transform step from the line items, the way it actually works in most
    order-management systems.
    """
    orders = []
    order_items = []
    oid = 1
    item_id = 1
    for c in customers:
        signup = date.fromisoformat(c["signup_date"])
        if random.random() >= 0.55:
            continue
        n_orders = random.randint(1, 12)
        for _ in range(n_orders):
            order_date = random_date(signup, END_DATE)
            status = random.choices(
                ["completed", "refunded", "cancelled"], weights=[0.9, 0.06, 0.04]
            )[0]
            chosen_products = random.sample(products, k=random.randint(1, 3))
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
                item_id += 1
            orders.append(
                {
                    "id": oid,
                    "customer_id": c["id"],
                    "order_date": order_date.isoformat(),
                    "status": status,
                }
            )
            oid += 1
    pd.DataFrame(orders).to_csv(RAW_DIR / "orders.csv", index=False)
    pd.DataFrame(order_items).to_csv(RAW_DIR / "order_items.csv", index=False)


def export_subscriptions(customers: list[dict]) -> None:
    subs = []
    sid = 1
    for c in customers:
        if random.random() >= 0.5:
            continue
        signup = date.fromisoformat(c["signup_date"])
        plan_name, plan_price = random.choice(PLANS)
        start = signup + timedelta(days=random.randint(0, 10))
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
    pd.DataFrame(subs).to_csv(RAW_DIR / "subscriptions.csv", index=False)


def main() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    customers = export_customers()
    products = export_products()
    export_events(customers)
    export_orders(customers, products)
    export_subscriptions(customers)
    print(f"Exported raw source extracts to {RAW_DIR}")


if __name__ == "__main__":
    main()
