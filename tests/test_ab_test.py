from experiments.ab_test import (
    check_guardrail,
    estimated_weeks_to_reach_sample_size,
    required_sample_size_per_group,
    two_proportion_z_test,
)


def test_required_sample_size_increases_for_smaller_effects():
    n_large_effect = required_sample_size_per_group(0.3, 0.10)
    n_small_effect = required_sample_size_per_group(0.3, 0.02)
    assert n_small_effect > n_large_effect


def test_two_proportion_z_test_flags_underpowered_small_sample():
    result = two_proportion_z_test(control_successes=5, control_n=20, treatment_successes=7, treatment_n=20)
    assert result.underpowered


def test_two_proportion_z_test_detects_large_clear_difference():
    result = two_proportion_z_test(
        control_successes=100, control_n=1000, treatment_successes=250, treatment_n=1000
    )
    assert result.significant_at_05
    assert result.absolute_lift > 0


def test_guardrail_flags_regression_beyond_threshold():
    result = check_guardrail("support_tickets", control_value=100, treatment_value=80, max_acceptable_regression_pct=5.0)
    assert result["guardrail_breached"]


def test_guardrail_allows_small_regression():
    result = check_guardrail("support_tickets", control_value=100, treatment_value=98, max_acceptable_regression_pct=5.0)
    assert not result["guardrail_breached"]


def test_estimated_weeks_scales_inversely_with_traffic():
    slow = estimated_weeks_to_reach_sample_size(1000, weekly_eligible_units=10)
    fast = estimated_weeks_to_reach_sample_size(1000, weekly_eligible_units=100)
    assert fast < slow


def test_estimated_weeks_is_infinite_with_no_traffic():
    assert estimated_weeks_to_reach_sample_size(1000, weekly_eligible_units=0) == float("inf")


def test_estimated_weeks_respects_traffic_split():
    full_split = estimated_weeks_to_reach_sample_size(1000, weekly_eligible_units=100, traffic_split=1.0)
    half_split = estimated_weeks_to_reach_sample_size(1000, weekly_eligible_units=100, traffic_split=0.5)
    assert half_split == full_split * 2
