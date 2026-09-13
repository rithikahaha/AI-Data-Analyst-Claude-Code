---
name: experiment-design
description: Design an experiment before running it, hypothesis, success metric, guardrails, and whether the available traffic can even reach a conclusive sample size in a reasonable time. Use whenever a stakeholder proposes "let's A/B test X," before any data is collected.
---

# Experiment Design

A significance test run on an experiment nobody designed properly first is how
teams end up with an inconclusive result after burning a quarter on it. This
runs before `experiments/ab_test.py`'s readout functions, not instead of them.

## Steps

1. **State the hypothesis and the one primary metric it moves.** "We think X
   will reduce Starter churn" is testable; "we think X will improve things" is
   not. Pick one primary metric up front, not a handful to be graded on
   whichever moved.
2. **Pick the smallest effect worth acting on** (the minimum detectable
   effect), not the effect you hope for. A test powered to detect a 20-point
   swing will call a real 6-point improvement "not significant," and that's a
   design mistake, not a finding.
3. **Compute the required sample size** via
   `experiments.ab_test.required_sample_size_per_group(baseline_rate, minimum_detectable_effect)`.
4. **Check whether the traffic exists to reach it** via
   `experiments.ab_test.estimated_weeks_to_reach_sample_size(required_n, weekly_eligible_units)`,
   using an actual query against the warehouse for `weekly_eligible_units`
   (new accounts, active users, whatever the randomization unit is), never an
   assumed number. If the estimate is longer than the business can wait
   (see `experiments/ab_test.py`'s worked example, a "580 weeks" result), the
   right move is to change the design, not run it anyway and hope: widen the
   minimum detectable effect, find a higher-volume proxy metric, or don't run
   it.
5. **Name guardrail metrics up front**, anything that a "win" on the primary
   metric shouldn't be allowed to break (see `check_guardrail`). Deciding
   these after seeing results is how a real regression gets explained away.
6. **State the randomization unit and decide it can't leak.** An account-level
   test where multiple users on the same account see different treatments is
   contaminated data, not a valid split.

## Output shape

- **Hypothesis:** one sentence, one primary metric.
- **Minimum detectable effect and required sample size.**
- **Feasibility:** estimated weeks to reach it, and a go/no-go call, not just
  the number.
- **Guardrails:** what would make this a "win we can't ship."

If the design isn't feasible as specified, say so plainly and propose the
smallest change (bigger effect size, different metric, longer window) that
would make it feasible, rather than quietly running an underpowered test.
