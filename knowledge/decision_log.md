# Decision log

Every answer in `examples/example_qna.md` closed with a recommendation. This
logs what happened after: was it acted on, and did it work? Closing this loop
is a separate, ongoing part of the job from answering the question in the
first place, an analyst who never checks back is just producing numbers, not
outcomes.

Log a new entry any time `analyst-lead`'s Act step makes a real recommendation
someone could act on. Fill in the outcome fields later, when there's an
answer, don't block on it up front.

Columns: **Date** | **Question** | **Recommendation** | **Decision made** |
**Outcome (filled in later)**

| Date | Question | Recommendation | Decision made | Outcome |
|---|---|---|---|---|
| 2026-09-13 | "Are we healthy overall, and which accounts need attention this quarter?" | Prioritize customer-success outreach on Starter-plan accounts scoring highest on the churn model, and treat the integration-adoption/churn link as worth a real experiment, not yet a rollout. | Not yet made, this is sample data illustrating the log's shape, not a real decision. | Pending |

## Why the integration-adoption experiment specifically needs this

The p=0.075 result in example 3 is exactly the kind of finding that quietly
turns into "we rolled it out anyway" without anyone tracking whether it
actually helped. If that experiment gets run, its result belongs as a new row
here, referencing back to this one, not as a one-off Slack message that
nobody can find in six months.
