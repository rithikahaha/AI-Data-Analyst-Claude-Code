# 6. Statistics

## The question statistics answers

You compare two groups and see a difference. Is the difference **real**, or
would you see something like it by luck?

The project's example. Accounts that used an integration (connecting the
product to another tool) versus accounts that never did:

| Group | Churned | Total | Churn rate |
|---|---|---|---|
| Never used an integration | 16 | 59 | 27.1% |
| Used an integration | 77 | 440 | 17.5% |

That looks like a big gap: 9.6 percentage points, or 35% lower churn. Tempting
headline: "integrations cut churn by a third". Statistics says slow down.

## Luck, in a coin-flip picture

Flip a coin 10 times and get 6 heads. Nobody thinks the coin is rigged. Flip it
1,000 times and get 600 heads, and you would strongly suspect it. Same
percentage, very different evidence. **The amount of data changes what a
difference means.**

A group of only 59 accounts is like the 10 flips. One or two accounts more or
less moves its percentage a lot.

## The p-value

The **p-value** answers one narrow question:

> If there were truly no difference between the groups, how often would random
> chance alone produce a gap at least this big?

Here p = **0.0748**. About 7.5% of the time. The usual cutoff is 0.05 (5%). So
this result is just short of "statistically significant".

Careful with what this does **not** mean:

- It is **not** "a 7.5% chance the finding is wrong".
- Missing the cutoff is **not** proof of no effect. The honest reading is
  "the data are consistent with a real effect, but 59 accounts is too few to
  be sure".
- 0.05 is a convention, not a law. 0.049 and 0.051 are basically the same
  evidence.

## Confidence intervals: the range, not just the point

A single percentage hides uncertainty. A **confidence interval** gives a range
the true value plausibly sits in. The project uses the Wilson method in
[`stats/tests.py`](../../stats/tests.py):

| Group | Observed | 95% interval |
|---|---|---|
| Never used an integration (59 accounts) | 27.1% | 17.4% to 39.6% |
| Used an integration (440 accounts) | 17.5% | 14.2% to 21.3% |

The small group's range is wide: its true churn could be as low as 17.4%,
barely different from the other group. The big group's range is narrow. **Wide
range = weak evidence.** This is why the project insists on reporting an
interval and not just a number.

## Sample size and power

**Power** is the chance a test will notice a real effect. Too little data and
you will miss real effects, not because they are absent but because the test
was too weak to see them ("underpowered").

The project's helper, `required_sample_size_per_group` in
[`experiments/ab_test.py`](../../experiments/ab_test.py), answers: how many per
group would you need? To reliably detect 27% versus 17.5% takes about **300
accounts per group**. The "never used an integration" group has 59. That is why
the result is flagged underpowered.

Prove that it is the data size, not the pattern: keep the exact same rates but
have three times the accounts (48 of 177 versus 231 of 1,320). The p-value
becomes about **0.002**, clearly significant. Same percentages, more evidence.

## The bigger trap: correlation is not causation

Nobody **assigned** accounts to use integrations. Accounts chose for
themselves. Maybe the healthier, more engaged accounts are the ones that bother
to connect other tools, and they would have stayed anyway. Then integrations
are a sign of health, not a cause of it.

A **randomized experiment (an A/B test)** fixes this: a coin flip decides who
gets the change, so the two groups differ only by that change. That is why the
project says "worth a real experiment, not proven", instead of "integrations
reduce churn".

## Designing an experiment before running it

Before anyone runs a test, decide:

1. **The hypothesis and one main metric.** "This onboarding change will lower
   churn."
2. **The smallest effect worth acting on.** A 5-point drop, say.
3. **How many accounts you need**, from the sample-size function.
4. **Whether you can get them.** New accounts arrive at about 3.6 a week. The
   project's design check says a 5-point churn test needs about 1,046 accounts
   per group, which at that pace takes roughly **580 weeks**. The right
   answer is to redesign the test or not run it. Finding this out **before**
   spending a quarter is the value of designing first.
5. **Guardrail metrics.** Things a "win" must not break, like support
   tickets.

## Other tests in the toolbox

`stats/tests.py` also has a **t-test** (do two groups have different
averages?) and a **chi-square test** (are two categories related?). Same idea
each time: is this gap bigger than luck would produce.

## Try it

Run the project's own examples:

```bash
python -m experiments.ab_test
```

You will see the feasibility check (about 580 weeks), the 59 versus 440
comparison, `p_value=0.0748`, and the underpowered warning.

Now play with the numbers:

```bash
python - <<'PY'
from experiments.ab_test import two_proportion_z_test
from stats.tests import proportion_confidence_interval

r = two_proportion_z_test(16, 59, 77, 440)
print("actual:", r.p_value, "underpowered:", r.underpowered)

r3 = two_proportion_z_test(48, 177, 231, 1320)   # same rates, 3x the accounts
print("3x data:", r3.p_value, "significant:", r3.significant_at_05)

print(proportion_confidence_interval(16, 59))
print(proportion_confidence_interval(77, 440))
PY
```

Expected: p 0.0748 and underpowered True, then p 0.002 and significant True,
then the two intervals from the table above.

**Your own task:** try `two_proportion_z_test(8, 30, 39, 220)`, which is
roughly the same rates at even smaller sizes. What happens to the p-value, and
what does that tell you? (It jumps to about 0.24. The gap is nearly identical,
26.7% versus 17.7%, but with so few accounts it is well within luck. Less data
means weaker evidence for the same difference.)

## Check yourself

- In one sentence, what does a p-value of 0.0748 mean?
- Why is "not significant" different from "no effect"?
- Why does a wide confidence interval matter?
- Why are the integration results correlation and not causation?
- What did designing the experiment first save?
