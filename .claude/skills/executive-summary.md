---
name: executive-summary
description: Format a finished numeric finding into a plain-English executive summary for a non-technical stakeholder. Use as the final step before presenting any analysis result.
---

# Executive Summary Formatting

Turn a query result into something a business stakeholder can act on in 10 seconds.

## Structure

1. **Headline** — one sentence, the finding itself, with the number: "Starter-plan
   accounts churn at 4x the rate of Enterprise accounts." Not "Here is an analysis
   of churn by plan tier."
2. **So what** — one sentence on business implication or a recommended action:
   "Targeting the highest-risk Starter accounts with proactive outreach could
   protect roughly $X in at-risk MRR."
3. **Evidence** — the supporting table or chart, kept small (top 5-10 rows, not a
   full dump).
4. **How this was calculated** — the SQL and table/column definitions used, for
   anyone who wants to verify or extend it.
5. **Caveats** — anything QA flagged (small sample, ambiguous definition, data gap).
   Never omit this section to make the finding look more certain than it is.

## Style rules

- No jargon a business stakeholder wouldn't use themselves ("WoW", "cohort", "p95")
  without a one-clause explanation the first time it's used.
- Prefer "4x higher" over "300% higher" or raw ratios when it reads more naturally.
- Numbers should carry units and context (currency, %, "out of N accounts") — a
  bare number is not an answer.
