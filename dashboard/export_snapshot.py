"""Precompute the same metrics the Streamlit app shows into a static JSON file,
for the published Artifact dashboard (a client-side-only HTML page with no
backend to run live queries against). Re-run after any change to the warehouse
or the dashboard's queries so the two versions don't drift apart.
"""

import json
from datetime import datetime, timezone
from pathlib import Path

from dashboard.queries import (
    account_risk_list,
    churn_by_plan_tier,
    net_revenue_retention,
    onboarding_funnel,
    weekly_active_users,
)

OUTPUT_PATH = Path(__file__).resolve().parent / "metrics.json"
WAU_TRAILING_WEEKS = 26


def main() -> None:
    wau_df = weekly_active_users().tail(WAU_TRAILING_WEEKS)
    nrr_df = net_revenue_retention()
    funnel_df = onboarding_funnel()
    tier_df = churn_by_plan_tier()
    risk_df = account_risk_list(top_n=15)

    wow_change_pct = None
    if len(wau_df) >= 2:
        prev, latest = wau_df["wau"].iloc[-2], wau_df["wau"].iloc[-1]
        wow_change_pct = round((latest - prev) / prev * 100, 1)

    overall_conversion_pct = None
    if len(funnel_df) == 3 and funnel_df["users"].iloc[0] > 0:
        overall_conversion_pct = round(
            funnel_df["users"].iloc[-1] / funnel_df["users"].iloc[0] * 100, 1
        )

    snapshot = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "wau": {
            "weeks": wau_df["week"].tolist(),
            "values": wau_df["wau"].tolist(),
            "wow_change_pct": wow_change_pct,
        },
        "nrr": nrr_df.to_dict(orient="records")[0] if not nrr_df.empty else None,
        "funnel": funnel_df.to_dict(orient="records"),
        "overall_conversion_pct": overall_conversion_pct,
        "churn_by_plan_tier": tier_df.to_dict(orient="records"),
        "account_risk_top": (
            risk_df[["name", "industry", "region", "plan_tier", "churn_risk"]]
            .assign(churn_risk=lambda d: d["churn_risk"].round(4))
            .to_dict(orient="records")
            if not risk_df.empty
            else []
        ),
    }

    OUTPUT_PATH.write_text(json.dumps(snapshot, indent=2))
    print(f"Wrote snapshot to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
