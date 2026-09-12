"""Statistical significance testing helpers for the data-scientist agent.

Each function returns a plain dict with the effect size and confidence interval
alongside the p-value, a p-value alone doesn't tell a stakeholder whether an
effect is big enough to matter.
"""

from dataclasses import dataclass, asdict

import numpy as np
from scipy import stats


@dataclass
class TestResult:
    test: str
    statistic: float
    p_value: float
    significant_at_05: bool
    effect_size: float
    effect_label: str
    ci_95: tuple[float, float]
    n_total: int

    def to_dict(self) -> dict:
        return asdict(self)


def two_sample_ttest(group_a: np.ndarray, group_b: np.ndarray) -> TestResult:
    """Welch's t-test for a difference in means between two independent groups."""
    group_a = np.asarray(group_a, dtype=float)
    group_b = np.asarray(group_b, dtype=float)

    stat, p_value = stats.ttest_ind(group_a, group_b, equal_var=False)
    mean_diff = float(group_a.mean() - group_b.mean())

    pooled_std = np.sqrt((group_a.var(ddof=1) + group_b.var(ddof=1)) / 2)
    cohens_d = mean_diff / pooled_std if pooled_std > 0 else 0.0

    se_diff = np.sqrt(group_a.var(ddof=1) / len(group_a) + group_b.var(ddof=1) / len(group_b))
    ci_low, ci_high = stats.norm.interval(0.95, loc=mean_diff, scale=se_diff)

    return TestResult(
        test="welch_ttest",
        statistic=float(stat),
        p_value=float(p_value),
        significant_at_05=p_value < 0.05,
        effect_size=round(float(cohens_d), 3),
        effect_label=_cohens_d_label(cohens_d),
        ci_95=(round(float(ci_low), 4), round(float(ci_high), 4)),
        n_total=len(group_a) + len(group_b),
    )


def chi_square_test(contingency_table: np.ndarray) -> TestResult:
    """Chi-square test of independence for a categorical x categorical table."""
    contingency_table = np.asarray(contingency_table)
    stat, p_value, dof, _expected = stats.chi2_contingency(contingency_table)

    n = contingency_table.sum()
    min_dim = min(contingency_table.shape) - 1
    cramers_v = np.sqrt(stat / (n * min_dim)) if min_dim > 0 and n > 0 else 0.0

    return TestResult(
        test="chi_square",
        statistic=float(stat),
        p_value=float(p_value),
        significant_at_05=p_value < 0.05,
        effect_size=round(float(cramers_v), 3),
        effect_label=_cramers_v_label(cramers_v),
        ci_95=(float("nan"), float("nan")),  # not defined for chi-square
        n_total=int(n),
    )


def proportion_confidence_interval(successes: int, n: int, confidence: float = 0.95) -> tuple[float, float]:
    """Wilson score interval, more reliable than the normal approximation for
    small samples or proportions near 0/1."""
    if n == 0:
        return (float("nan"), float("nan"))
    z = stats.norm.ppf(1 - (1 - confidence) / 2)
    p_hat = successes / n
    denom = 1 + z**2 / n
    center = (p_hat + z**2 / (2 * n)) / denom
    margin = (z * np.sqrt(p_hat * (1 - p_hat) / n + z**2 / (4 * n**2))) / denom
    return (round(center - margin, 4), round(center + margin, 4))


def _cohens_d_label(d: float) -> str:
    d = abs(d)
    if d < 0.2:
        return "negligible"
    if d < 0.5:
        return "small"
    if d < 0.8:
        return "medium"
    return "large"


def _cramers_v_label(v: float) -> str:
    if v < 0.1:
        return "negligible"
    if v < 0.3:
        return "small"
    if v < 0.5:
        return "medium"
    return "large"
