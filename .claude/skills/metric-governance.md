---
name: metric-governance
description: Add, change, or resolve a conflict in a metric's definition in the glossary, with a dated reason logged. Use whenever a stakeholder proposes a new metric, disputes an existing definition, or two people are computing the "same" number two different ways.
---

# Metric Governance

`rag/retrieve.py` grounds a *single question's* answer in an existing
definition. This is the separate, ongoing job of deciding what that
definition should be in the first place, and making sure it doesn't quietly
drift when someone edits it.

## When this applies

- A stakeholder asks for a metric that isn't in `knowledge/metrics_glossary.md`
  yet.
- Two people are reporting different numbers for something that should be one
  metric (a classic sign a definition was never pinned down, or drifted).
- Someone proposes changing an existing definition (e.g., redefining "active
  user" to a different event or window).

## Steps

1. **Check whether it's really a new metric or a variant of an existing one.**
   "Active user" and "active account" sound similar and mean different things
   in this schema (see the glossary), collapsing them into one definition is
   how a churn model ends up trained on the wrong thing.
2. **Write the definition the same way every existing entry is written:** the
   exact column/table/condition it resolves to, not a prose description
   someone could implement two different ways. If it can't be written as an
   exact query condition, it's not ready to be a governed metric yet.
3. **State what it's NOT**, the way the glossary already distinguishes
   "active user" from "active account", or "churn" from "contraction". Most
   metric confusion is at exactly this kind of boundary.
4. **Log the change** in the glossary's `## Changelog` section: date, what
   changed, and why (a stakeholder ask, a bug where two dashboards disagreed,
   a definition that was ambiguous in practice). Never silently edit a
   definition, if a downstream chart or model relied on the old one, the
   changelog is how anyone traces why a number moved.
5. **Flag every known consumer of a changed definition** (a dashboard tile, a
   model's feature, an existing skill's worked example) so whoever owns that
   consumer knows to re-check it, don't assume a definition change is
   self-contained.

## Output shape

- **Definition:** the exact glossary-entry text, same shape as existing
  entries.
- **What it's not:** the nearest-neighbor term it could be confused with.
- **Changelog line:** dated, one sentence, states the reason.
- **Consumers to re-check:** anything that used the old definition, if this
  is a change rather than a new addition.
