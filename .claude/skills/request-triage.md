---
name: request-triage
description: Rank a backlog of competing business questions when there's more asked than can be answered right now. Use whenever multiple stakeholders have open requests and someone needs to know what to work on first, not how to answer any one of them.
---

# Request Triage

Every phase in `analyst-lead`'s process assumes you already know which
question to work on. This is the step before that: deciding which of several
competing requests actually gets worked first, an ongoing part of the job that
answering any single question well doesn't cover.

## Steps

1. **List every open request as a one-line question**, not a vague area
   ("look into churn" isn't triageable, "which plan tier is driving the churn
   increase this quarter" is).
2. **Score each on three axes, 1-5:**
   - **Impact.** Does the answer change a real decision (pricing, roadmap,
     an at-risk renewal), or is it "nice to know"?
   - **Confidence.** How sure are you the data actually exists and is clean
     enough to answer this without a data-quality detour first (see
     `data-platform-engineer`)?
   - **Ease.** Roughly how much work: one query, or a full
     `data-scientist` stats/ML pass?
3. **Score = Impact x Confidence x Ease** (a simple ICE score). This is a
   forcing function for an explicit conversation, not a precise formula, two
   requests that score the same still need a human tiebreaker on which
   decision is more time-sensitive.
4. **Flag anything time-boxed separately from the score**, a lower-scoring
   question tied to a decision happening this week outranks a higher-scoring
   one with no deadline, ICE alone doesn't know about calendars.
5. **Say what's NOT getting worked on, and why**, a prioritized list that
   silently drops three requests is worse than one that names them as
   deprioritized and states the reason, the stakeholder who asked can then
   push back if the call is wrong instead of just wondering why they never
   heard back.

## Output shape

A ranked table: Question | Impact | Confidence | Ease | Score | Note
(deadline, dependency, or why it's deprioritized). State the top pick's
question explicitly before starting on it, don't just start querying.
