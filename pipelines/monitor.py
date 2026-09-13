"""Ongoing warehouse health checks, owned by data-platform-engineer.

Different job from pipelines/data_quality.py: those checks validate one load
at ETL time (nulls, uniqueness, referential integrity) and run inline with the
pipeline. These checks watch the warehouse's steady state over time, so a
silently broken pipeline or a metric that's drifted gets caught before a
stakeholder asks a question and gets a wrong answer from it, not after.

Checks compare the newest data against its own recent history rather than
against wall-clock "now": a batch sample warehouse (rebuilt from a fixed date
range) has no live clock to be stale against the way a real production feed
would, so a wall-clock check here would just be noise. Point this at a real
warehouse and the same functions still work, "now" would just also become a
meaningful reference point there.

Like `data_quality.py`, checks take data in and return a report, they don't
query the warehouse themselves, that's what makes "what does a broken
pipeline look like" testable with a few rows of synthetic data instead of a
live database.
"""

from dataclasses import dataclass

import pandas as pd

from connectors.warehouse import run_query


@dataclass
class Alert:
    check: str
    severity: str  # "ok" or "warning"
    detail: str

    def __str__(self) -> str:
        tag = "OK" if self.severity == "ok" else "ALERT"
        return f"[{tag}] {self.check}: {self.detail}"


def check_freshness_lag(
    lagging_dates: pd.Series,
    reference_dates: pd.Series,
    lagging_name: str,
    reference_name: str,
    max_lag_days: int = 30,
) -> Alert:
    """Flags when a series of dates is suspiciously far behind a reference
    series it should track closely. Product usage events falling behind the
    newest account signups usually means the events pipeline stalled while
    signups kept flowing in from a different source, exactly the kind of gap
    a one-off data-quality check at load time wouldn't catch.
    """
    lagging_latest = pd.to_datetime(lagging_dates).max()
    reference_latest = pd.to_datetime(reference_dates).max()
    lag_days = (reference_latest - lagging_latest).days

    breached = lag_days > max_lag_days
    return Alert(
        check=f"{lagging_name} freshness vs {reference_name}",
        severity="warning" if breached else "ok",
        detail=f"{lagging_name} is {lag_days} day(s) behind {reference_name}'s latest (limit {max_lag_days})",
    )


def check_calendar_gaps(dates: pd.Series, name: str) -> Alert:
    """Flags any calendar month inside the series' own observed date range
    that has zero rows. A silent pipeline failure usually shows up as exactly
    this, a clean gap, not an error message anyone would notice.
    """
    parsed = pd.to_datetime(dates)
    months_present = set(parsed.dt.to_period("M"))
    full_range = pd.period_range(parsed.min(), parsed.max(), freq="M")
    missing = sorted(str(m) for m in full_range if m not in months_present)

    return Alert(
        check=f"{name} calendar-gap check",
        severity="warning" if missing else "ok",
        detail="no gaps in the observed date range" if not missing else f"no rows in: {missing}",
    )


def check_month_over_month_volume(dates: pd.Series, name: str, max_drop_pct: float = 40.0) -> Alert:
    """Flags a sharp drop in row volume for the most recently *completed*
    month versus its trailing 3-month average. The current, still-filling-in
    month is excluded, comparing a partial month against full ones would
    flag a false alarm every single time it's run.
    """
    counts = pd.to_datetime(dates).dt.to_period("M").value_counts().sort_index()
    counts = counts.iloc[:-1]  # drop the current, still-filling-in month
    if len(counts) < 4:
        return Alert(
            check=f"{name} month-over-month volume",
            severity="ok",
            detail="not enough completed months of history to compare",
        )

    latest_n = counts.iloc[-1]
    baseline = counts.iloc[-4:-1].mean()
    drop_pct = (baseline - latest_n) / baseline * 100 if baseline > 0 else 0.0
    breached = drop_pct > max_drop_pct

    return Alert(
        check=f"{name} month-over-month volume",
        severity="warning" if breached else "ok",
        detail=f"latest completed month ({counts.index[-1]}): {latest_n} rows vs "
        f"trailing 3-month average {baseline:.0f} ({drop_pct:+.1f}%)",
    )


def run_all_checks() -> list[Alert]:
    events = run_query("SELECT event_date FROM product_events")["event_date"]
    orgs = run_query("SELECT signed_up_date FROM organizations")["signed_up_date"]

    return [
        check_freshness_lag(events, orgs, "product_events.event_date", "organizations.signed_up_date"),
        check_calendar_gaps(events, "product_events.event_date"),
        check_month_over_month_volume(events, "product_events.event_date"),
    ]


def report(alerts: list[Alert]) -> bool:
    print("\n--- Ongoing monitoring ---")
    for a in alerts:
        print(a)
    healthy = all(a.severity == "ok" for a in alerts)
    print("ALL CLEAR" if healthy else "ALERTS RAISED")
    return healthy


if __name__ == "__main__":
    import sys

    ok = report(run_all_checks())
    sys.exit(0 if ok else 1)
