"""A/B test design and readout helpers for the data-scientist agent.

Covers the three things an experiment readout needs that a plain significance
test doesn't: whether the sample was even big enough to detect the effect size
that matters, a proportions-specific significance test, and a guardrail check
so a "win" on the primary metric isn't quietly a loss somewhere else.
"""

from dataclasses import dataclass

import numpy as np
from scipy import stats


def required_sample_size_per_group(
    baseline_rate: float,
    minimum_detectable_effect: float,
    power: float = 0.8,
    alpha: float = 0.05,
) -> int:
    """Sample size needed per group to detect an absolute change of
    `minimum_detectable_effect` on a baseline conversion rate, via a two-proportion
    z-test power calculation.
    """
    z_alpha = stats.norm.ppf(1 - alpha / 2)
    z_power = stats.norm.ppf(power)

    p1 = baseline_rate
    p2 = baseline_rate + minimum_detectable_effect
    p_bar = (p1 + p2) / 2

    numerator = (
        z_alpha * np.sqrt(2 * p_bar * (1 - p_bar)) + z_power * np.sqrt(p1 * (1 - p1) + p2 * (1 - p2))
    ) ** 2
    denominator = minimum_detectable_effect**2
    return int(np.ceil(numerator / denominator))


@dataclass
class ABTestResult:
    control_rate: float
    treatment_rate: float
    absolute_lift: float
    relative_lift_pct: float
    z_statistic: float
    p_value: float
    significant_at_05: bool
    control_n: int
    treatment_n: int
    underpowered: bool


def two_proportion_z_test(
    control_successes: int,
    control_n: int,
    treatment_successes: int,
    treatment_n: int,
    minimum_detectable_effect: float = 0.02,
) -> ABTestResult:
    """Two-proportion z-test for an A/B test readout on a binary metric
    (converted/not, churned/not, clicked/not).
    """
    p1 = control_successes / control_n
    p2 = treatment_successes / treatment_n
    p_pool = (control_successes + treatment_successes) / (control_n + treatment_n)

    se = np.sqrt(p_pool * (1 - p_pool) * (1 / control_n + 1 / treatment_n))
    z = (p2 - p1) / se if se > 0 else 0.0
    p_value = 2 * (1 - stats.norm.cdf(abs(z)))

    required_n = required_sample_size_per_group(p1, minimum_detectable_effect)
    underpowered = min(control_n, treatment_n) < required_n

    return ABTestResult(
        control_rate=round(p1, 4),
        treatment_rate=round(p2, 4),
        absolute_lift=round(p2 - p1, 4),
        relative_lift_pct=round((p2 - p1) / p1 * 100, 2) if p1 > 0 else float("nan"),
        z_statistic=round(float(z), 3),
        p_value=round(float(p_value), 4),
        significant_at_05=p_value < 0.05,
        control_n=control_n,
        treatment_n=treatment_n,
        underpowered=underpowered,
    )


def check_guardrail(
    metric_name: str,
    control_value: float,
    treatment_value: float,
    max_acceptable_regression_pct: float = 5.0,
) -> dict:
    """Flag whether a secondary/guardrail metric regressed beyond an acceptable
    threshold, even if the primary metric looks like a win.
    """
    if control_value == 0:
        pct_change = float("nan")
    else:
        pct_change = (treatment_value - control_value) / abs(control_value) * 100

    breached = pct_change < -max_acceptable_regression_pct
    return {
        "metric": metric_name,
        "control_value": control_value,
        "treatment_value": treatment_value,
        "pct_change": round(pct_change, 2) if pct_change == pct_change else pct_change,
        "guardrail_breached": bool(breached),
    }


if __name__ == "__main__":
    # Worked example: treat subscription plan as a proxy "experiment arm" and
    # compare churn rates the way an A/B test readout would, against the sample
    # warehouse seeded by scripts/seed_sample_data.py.
    from connectors.warehouse import run_query

    df = run_query(
        """
        SELECT plan,
               SUM(CASE WHEN status = 'churned' THEN 1 ELSE 0 END) AS churned,
               COUNT(*) AS total
        FROM subscriptions
        GROUP BY plan
        """
    )
    print(df)

    starter = df[df["plan"] == "Starter"].iloc[0]
    scale = df[df["plan"] == "Scale"].iloc[0]

    result = two_proportion_z_test(
        control_successes=int(starter["churned"]),
        control_n=int(starter["total"]),
        treatment_successes=int(scale["churned"]),
        treatment_n=int(scale["total"]),
    )
    print("\nStarter (control) vs Scale (treatment) churn rate:")
    print(result)
    if result.underpowered:
        print(
            "\nNote: sample size is below what's needed to reliably detect a "
            "2pp difference at 80% power — treat a non-significant result here "
            "as inconclusive, not as proof of no effect."
        )
