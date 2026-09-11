---
name: anomaly-detection
description: Flag outliers or unusual spikes/drops in a metric before reporting it, and investigate likely causes. Use whenever a number looks surprising, or as a standard QA pass on any trend.
---

# Anomaly Detection

## Steps

1. Compute a simple baseline for the metric — trailing 7/30-period average and
   standard deviation, or period-over-period % change.
2. Flag any point beyond ~2 standard deviations from the trailing baseline, or a
   period-over-period change beyond a business-reasonable threshold (e.g., >50% day
   over day for daily revenue).
3. For each flagged point, check for an obvious cause before calling it a real trend:
   - A single unusually large order/customer skewing an aggregate.
   - A data gap (fewer rows than expected for that period — see `qa-reviewer`).
   - A known calendar effect (holiday, month-end, promotional period) if that context
     is available.
4. Distinguish "real anomaly worth flagging to the business" from "artifact of small
   sample size or a data issue" — only the former belongs in the final answer's
   headline; the latter belongs in caveats.

## Answer format

If an anomaly is found and relevant to the question, call it out explicitly with the
date/period and magnitude, and state whether it changes the overall conclusion.
