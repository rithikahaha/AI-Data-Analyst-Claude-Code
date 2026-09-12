# Metrics glossary

Source-of-truth definitions for terms that could otherwise mean more than one thing
in this schema. `ai-engineer`'s `rag/retrieve.py` retrieves entries from this file
so an agent grounds an answer in a citable definition instead of guessing when a
question uses one of these terms. Each entry is written as its own retrievable
chunk — keep new entries in this same one-paragraph-per-term shape.

## Active customer

A customer is **active** if they have a subscription with `status = 'active'` in
the `subscriptions` table. This is distinct from having ever placed an order —
a customer can have purchased once, never subscribed, and therefore not count as
"active" by this definition. If a question means "purchased recently" instead,
say so explicitly rather than reusing this term.

## Revenue

**Revenue** means the gross value of orders with `status = 'completed'`
(`SUM(orders.total_amount)`), excluding `refunded` and `cancelled` orders. This
repo does not track subscription MRR/ARR as a separate figure — subscription
revenue would need to be derived from `subscriptions.monthly_price` × active
months, which is a different calculation from order revenue and should not be
added to it without saying so.

## Churn

**Churn**, for a subscription, means `subscriptions.status = 'churned'` —
a subscription that has ended with `end_date` set. Churn *rate* for a group is
`churned / (churned + active)` within that group, not a time-windowed rate
(e.g., "churned in the last 30 days") unless the question asks for that
explicitly, since `end_date` would need an additional date filter to compute it.

## Conversion (funnel)

**Conversion** at a funnel stage means the count of distinct customers who
reached that `event_type` in the `events` table, divided by the count who
reached the previous stage in the same funnel. Overall conversion is
`first_purchase` customers divided by `signup` customers. See
`.claude/skills/funnel-analysis.md` for the full method.

## Customer segment

**Segment** refers to `customers.segment` (`SMB` / `Mid-Market` / `Enterprise`),
assigned once at signup in this dataset. It is not the same as `region`
(geography) — a question about "segment" should not be answered with a
region breakdown or vice versa.
