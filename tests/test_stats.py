import numpy as np

from stats.tests import chi_square_test, proportion_confidence_interval, two_sample_ttest


def test_ttest_detects_a_real_difference():
    rng = np.random.default_rng(0)
    a = rng.normal(100, 5, 300)
    b = rng.normal(120, 5, 300)
    result = two_sample_ttest(a, b)
    assert result.significant_at_05
    assert result.effect_label in {"medium", "large"}


def test_ttest_does_not_flag_identical_distributions():
    rng = np.random.default_rng(1)
    a = rng.normal(50, 10, 500)
    b = rng.normal(50, 10, 500)
    result = two_sample_ttest(a, b)
    assert not result.significant_at_05


def test_chi_square_independence():
    # Perfectly independent-looking table (proportional rows).
    table = [[100, 100], [50, 50]]
    result = chi_square_test(table)
    assert result.p_value > 0.05
    assert not result.significant_at_05


def test_proportion_confidence_interval_contains_point_estimate():
    low, high = proportion_confidence_interval(45, 200)
    assert low < 45 / 200 < high
