---
name: executive-summary
description: Format a finished numeric finding into a plain-English executive summary for a non-technical stakeholder. Use as the final step before presenting any analysis result.
---

# Executive Summary Formatting

Turn a query result into something a business stakeholder can act on in 10 seconds.

## Structure

1. **Headline** — one sentence, the finding itself, with the number: "Grade D loans
   default at 3x the portfolio average." Not "Here is an analysis of loan grades."
2. **So what** — one sentence on business implication or a recommended action:
   "Tightening underwriting on Grade D would reduce expected losses by roughly $X."
3. **Evidence** — the supporting table or chart, kept small (top 5-10 rows, not a
   full dump).
4. **How this was calculated** — the SQL and table/column definitions used, for
   anyone who wants to verify or extend it.
5. **Caveats** — anything QA flagged (small sample, ambiguous definition, data gap).
   Never omit this section to make the finding look more certain than it is.

## Style rules

- No jargon a business stakeholder wouldn't use themselves ("MoM", "cohort", "p95")
  without a one-clause explanation the first time it's used.
- Prefer "3x higher" over "300% higher" or raw ratios when it reads more naturally.
- Numbers should carry units and context (currency, %, "out of N loans") — a bare
  number is not an answer.
