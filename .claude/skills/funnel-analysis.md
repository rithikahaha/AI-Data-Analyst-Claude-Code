---
name: funnel-analysis
description: Standard playbook for sequential conversion questions — signup to activation to purchase, or cart to checkout to payment. Use for "where are we losing customers/users" questions.
---

# Funnel Analysis

## Steps

1. Define the funnel stages in order and the table/event each maps to (e.g.,
   `customers.created_at` → signup, `orders` with `status='completed'` → purchase).
   State the mapping explicitly — funnel definitions are a common source of
   disagreement between teams.
2. For each stage, count distinct entities that reached it, filtered to the same
   cohort/time window as the previous stage — a funnel mixing different populations
   per stage gives a meaningless conversion rate.
3. Compute stage-to-stage conversion (`stage_n / stage_(n-1)`) and overall conversion
   (`final_stage / first_stage`).
4. Identify the single largest drop-off point — that's usually the actionable
   finding, more so than the overall conversion rate.
5. If the question implies a segment comparison (e.g., "does the funnel differ by
   acquisition channel"), break out the same funnel per segment rather than just
   reporting an aggregate.

## Answer format

Lead with where the biggest drop-off is and its size, then the full funnel numbers
(as a funnel chart via `data-visualizer`), then the query and stage definitions used.
