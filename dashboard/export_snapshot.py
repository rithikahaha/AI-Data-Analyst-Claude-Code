"""Precompute the same metrics the Streamlit app shows into a static JSON file,
for the published Artifact dashboard (a client-side-only HTML page with no
backend to run live queries against). Re-run after any change to the warehouse
or the dashboard's queries so the two versions don't drift apart.
"""

import json
from datetime import datetime, timezone
from pathlib import Path

from dashboard.queries import churn_by_segment, churn_risk_list, funnel_counts, monthly_revenue

OUTPUT_PATH = Path(__file__).resolve().parent / "metrics.json"


def main() -> None:
    revenue_df = monthly_revenue()
    churn_df = churn_by_segment()
    funnel_df = funnel_counts()
    risk_df = churn_risk_list(top_n=15)

    mom_growth_pct = None
    if len(revenue_df) >= 2:
        prev, latest = revenue_df["revenue"].iloc[-2], revenue_df["revenue"].iloc[-1]
        mom_growth_pct = round((latest - prev) / prev * 100, 1)

    overall_conversion_pct = None
    if len(funnel_df) == 3 and funnel_df["customers"].iloc[0] > 0:
        overall_conversion_pct = round(
            funnel_df["customers"].iloc[-1] / funnel_df["customers"].iloc[0] * 100, 1
        )

    snapshot = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "revenue": {
            "months": revenue_df["month"].tolist(),
            "values": revenue_df["revenue"].round(2).tolist(),
            "mom_growth_pct": mom_growth_pct,
        },
        "churn_by_segment": churn_df.to_dict(orient="records"),
        "funnel": funnel_df.to_dict(orient="records"),
        "overall_conversion_pct": overall_conversion_pct,
        "churn_risk_top": (
            risk_df[["name", "segment", "region", "plan", "churn_risk"]]
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
