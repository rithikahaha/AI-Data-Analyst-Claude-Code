from reliability.healthcheck import run as run_healthcheck
from reliability.sli import compute_slis, percentile


def _ok(ms):
    return {"status": "ok", "duration_ms": ms}


def test_percentile_nearest_rank():
    assert percentile([10, 20, 30, 40, 50], 50) == 30
    assert percentile([10, 20, 30, 40, 50], 95) == 50


def test_all_successful_fast_queries_meet_both_slos():
    report = compute_slis([_ok(50)] * 200)
    assert report.availability == 1.0
    assert report.error_budget_remaining_pct == 100.0
    assert report.healthy


def test_error_burst_breaches_availability_slo():
    records = [_ok(50)] * 90 + [{"status": "error", "duration_ms": 5}] * 10
    report = compute_slis(records)
    assert report.availability == 0.9
    assert not report.availability_ok
    assert report.error_budget_remaining_pct == 0.0


def test_slow_tail_breaches_latency_slo_even_when_average_is_fine():
    # 90 fast queries and 10 very slow ones: the mean looks acceptable,
    # the p95 is what a user waiting on a dashboard actually experiences.
    report = compute_slis([_ok(100)] * 90 + [_ok(5000)] * 10)
    assert report.availability_ok
    assert not report.latency_ok


def test_blocked_writes_do_not_count_as_downtime():
    records = [_ok(50)] * 100 + [{"status": "blocked", "duration_ms": 0}] * 20
    report = compute_slis(records)
    assert report.total_requests == 100
    assert report.availability == 1.0


def test_empty_log_is_not_a_failure():
    assert compute_slis([]).healthy


def test_healthcheck_passes_against_sample_warehouse():
    result = run_healthcheck()
    assert result["healthy"], result
