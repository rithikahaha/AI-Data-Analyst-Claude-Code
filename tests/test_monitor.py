import pandas as pd

from pipelines.monitor import check_calendar_gaps, check_freshness_lag, check_month_over_month_volume


def test_freshness_lag_ok_when_close_together():
    lagging = pd.Series(["2026-08-01", "2026-08-20"])
    reference = pd.Series(["2026-08-01", "2026-08-25"])
    result = check_freshness_lag(lagging, reference, "events", "signups", max_lag_days=30)
    assert result.severity == "ok"


def test_freshness_lag_flags_a_stalled_pipeline():
    lagging = pd.Series(["2026-01-01", "2026-02-01"])  # events stopped in Feb
    reference = pd.Series(["2026-01-01", "2026-08-25"])  # signups kept coming
    result = check_freshness_lag(lagging, reference, "events", "signups", max_lag_days=30)
    assert result.severity == "warning"


def test_calendar_gaps_passes_on_continuous_months():
    dates = pd.Series(["2026-01-15", "2026-02-01", "2026-03-20"])
    result = check_calendar_gaps(dates, "events")
    assert result.severity == "ok"


def test_calendar_gaps_flags_a_missing_month():
    dates = pd.Series(["2026-01-15", "2026-03-20"])  # no February rows at all
    result = check_calendar_gaps(dates, "events")
    assert result.severity == "warning"
    assert "2026-02" in result.detail


def test_month_over_month_volume_ok_when_stable():
    months = ["2026-01"] * 100 + ["2026-02"] * 100 + ["2026-03"] * 100 + ["2026-04"] * 100 + ["2026-05"] * 5
    dates = pd.Series([f"{m}-10" for m in months])
    result = check_month_over_month_volume(dates, "events")
    assert result.severity == "ok"


def test_month_over_month_volume_flags_a_sharp_drop():
    months = ["2026-01"] * 100 + ["2026-02"] * 100 + ["2026-03"] * 100 + ["2026-04"] * 10 + ["2026-05"] * 5
    dates = pd.Series([f"{m}-10" for m in months])
    result = check_month_over_month_volume(dates, "events")
    assert result.severity == "warning"


def test_month_over_month_volume_excludes_current_partial_month():
    # April looks like a huge drop, but it's excluded as the in-progress month.
    months = ["2026-01"] * 100 + ["2026-02"] * 100 + ["2026-03"] * 100 + ["2026-04"] * 1
    dates = pd.Series([f"{m}-10" for m in months])
    result = check_month_over_month_volume(dates, "events")
    assert result.severity == "ok"
    assert "not enough" in result.detail
