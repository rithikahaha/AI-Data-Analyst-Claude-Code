"""Simulate raw extracts from a B2B SaaS product's source systems: a CRM export
(organizations), an identity-provider export (users), a billing-system export
(subscriptions, seat-based), and a product analytics export (usage events).

Writes to data/raw/*.csv — deliberately un-transformed and slightly messy (a
handful of duplicate organization rows, as a re-exported CRM extract would
produce; MRR left uncomputed, since the billing system tracks seat count and
price per seat, not a precomputed revenue figure) so pipelines/etl.py has real
transform and data-quality work to do, not just a pass-through load.
"""

import random
from datetime import date, timedelta
from pathlib import Path

import pandas as pd
from faker import Faker

RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"
START_DATE = date(2024, 1, 1)
END_DATE = date(2026, 9, 1)
N_ORGS = 500
DUPLICATE_ORG_ROWS = 9  # simulates a CRM re-export overlap

fake = Faker()
Faker.seed(42)
random.seed(42)

INDUSTRIES = ["Software", "Finance", "Healthcare", "Retail", "Media", "Education"]
REGIONS = ["North America", "Europe", "APAC", "Latin America"]
PLANS = [("Starter", 15), ("Team", 35), ("Enterprise", 75)]
EVENT_TYPES_POST_ONBOARDING = ["created_project", "invited_teammate", "used_integration", "login"]


def random_date(start: date, end: date) -> date:
    return start + timedelta(days=random.randint(0, (end - start).days))


def export_organizations() -> list[dict]:
    orgs = []
    for i in range(1, N_ORGS + 1):
        signed_up = random_date(START_DATE, END_DATE - timedelta(days=1))
        orgs.append(
            {
                "id": i,
                "name": fake.company(),
                "industry": random.choice(INDUSTRIES),
                "region": random.choice(REGIONS),
                "signed_up_date": signed_up.isoformat(),
            }
        )

    # A source-system re-export overlap: a handful of orgs appear twice, exactly
    # as a CRM incremental export re-sending recently-touched records alongside
    # a full backfill would look.
    duplicates = random.sample(orgs, k=DUPLICATE_ORG_ROWS)
    all_rows = orgs + duplicates

    pd.DataFrame(all_rows).to_csv(RAW_DIR / "organizations.csv", index=False)
    return orgs  # de-duplicated list for downstream generation


def export_users(orgs: list[dict]) -> list[dict]:
    users = []
    uid = 1
    for org in orgs:
        signed_up = date.fromisoformat(org["signed_up_date"])
        n_users = random.randint(1, 12)
        for j in range(n_users):
            joined = signed_up if j == 0 else signed_up + timedelta(days=random.randint(0, 60))
            if joined > END_DATE:
                continue
            users.append(
                {
                    "id": uid,
                    "org_id": org["id"],
                    "name": fake.name(),
                    "email": fake.email(),
                    "role": "admin" if j == 0 else "member",
                    "joined_date": joined.isoformat(),
                }
            )
            uid += 1
    pd.DataFrame(users).to_csv(RAW_DIR / "users.csv", index=False)
    return users


def export_subscriptions(orgs: list[dict], users: list[dict]) -> None:
    """Billing-system export: one row per org's current (or final) contract
    state. price_per_seat comes from the plan; MRR itself is NOT exported here
    — that's a derived figure computed in the transform step, the way it
    actually works when billing and revenue reporting are separate systems.
    """
    users_by_org: dict[int, int] = {}
    for u in users:
        users_by_org[u["org_id"]] = users_by_org.get(u["org_id"], 0) + 1

    subs = []
    sid = 1
    for org in orgs:
        signed_up = date.fromisoformat(org["signed_up_date"])
        start = signed_up + timedelta(days=random.randint(0, 5))
        if start > END_DATE:
            continue

        plan_name, price_per_seat = random.choice(PLANS)
        initial_seats = max(1, users_by_org.get(org["id"], 1) - random.randint(0, 2))

        # Segment-flavored churn/expansion propensity by plan tier — mirrors
        # how enterprise-tier accounts (more seats, more onboarding investment)
        # tend to be stickier than self-serve starter accounts.
        churn_prob = {"Starter": 0.42, "Team": 0.24, "Enterprise": 0.10}[plan_name]
        expand_prob = {"Starter": 0.15, "Team": 0.35, "Enterprise": 0.5}[plan_name]

        churned = random.random() < churn_prob
        current_seats = initial_seats
        end_date = None
        status = "active"

        if churned:
            tenure_days = int(random.expovariate(1 / 200))
            end_candidate = start + timedelta(days=max(20, tenure_days))
            if end_candidate <= END_DATE:
                end_date = end_candidate.isoformat()
                status = "churned"
        elif random.random() < expand_prob:
            current_seats = initial_seats + random.randint(1, 6)
        elif random.random() < 0.1:
            current_seats = max(1, initial_seats - random.randint(1, 2))

        subs.append(
            {
                "id": sid,
                "org_id": org["id"],
                "plan_tier": plan_name,
                "price_per_seat": price_per_seat,
                "initial_seat_count": initial_seats,
                "current_seat_count": current_seats,
                "start_date": start.isoformat(),
                "end_date": end_date,
                "status": status,
            }
        )
        sid += 1
    pd.DataFrame(subs).to_csv(RAW_DIR / "subscriptions.csv", index=False)


def export_product_events(users: list[dict]) -> None:
    events = []
    eid = 1
    for u in users:
        joined = date.fromisoformat(u["joined_date"])
        events.append({"id": eid, "user_id": u["id"], "org_id": u["org_id"], "event_type": "signup", "event_date": joined.isoformat()})
        eid += 1

        if random.random() >= 0.72:
            continue  # never onboards

        onboarded = joined + timedelta(days=random.randint(0, 7))
        if onboarded > END_DATE:
            continue
        events.append({"id": eid, "user_id": u["id"], "org_id": u["org_id"], "event_type": "completed_onboarding", "event_date": onboarded.isoformat()})
        eid += 1

        if random.random() >= 0.62:
            continue  # onboards but never really activates

        activated = onboarded + timedelta(days=random.randint(0, 10))
        if activated > END_DATE:
            continue
        events.append({"id": eid, "user_id": u["id"], "org_id": u["org_id"], "event_type": "created_project", "event_date": activated.isoformat()})
        eid += 1

        # Ongoing usage: a variable number of ordinary product-usage events
        # scattered between activation and the end of the observation window.
        window_days = (END_DATE - activated).days
        if window_days <= 0:
            continue
        n_ongoing = random.randint(0, 60)
        for _ in range(n_ongoing):
            ev_date = activated + timedelta(days=random.randint(0, window_days))
            events.append(
                {
                    "id": eid,
                    "user_id": u["id"],
                    "org_id": u["org_id"],
                    "event_type": random.choices(
                        EVENT_TYPES_POST_ONBOARDING, weights=[0.15, 0.15, 0.2, 0.5]
                    )[0],
                    "event_date": ev_date.isoformat(),
                }
            )
            eid += 1

    pd.DataFrame(events).to_csv(RAW_DIR / "product_events.csv", index=False)


def main() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    orgs = export_organizations()
    users = export_users(orgs)
    export_subscriptions(orgs, users)
    export_product_events(users)
    print(f"Exported raw source extracts to {RAW_DIR}")


if __name__ == "__main__":
    main()
