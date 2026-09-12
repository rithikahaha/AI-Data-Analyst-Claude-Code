# Metrics glossary

Source-of-truth definitions for terms that could otherwise mean more than one thing
in this schema. `ai-engineer`'s `rag/retrieve.py` retrieves entries from this file
so an agent grounds an answer in a citable definition instead of guessing when a
question uses one of these terms. Each entry is written as its own retrievable
chunk — keep new entries in this same one-paragraph-per-term shape.

## Active user

A user is **active** in a given week if they logged a `login` event in
`product_events` during that week (weekly active users / WAU). This is distinct
from an **active account**, which means the organization's `subscriptions.status
= 'active'` — an account can be active (still paying) while zero of its users
have logged in recently, which is exactly the kind of account
`ml/train_churn_model.py` is trying to flag.

## MRR (monthly recurring revenue)

**MRR** for an account means `subscriptions.current_seat_count *
subscriptions.price_per_seat`, computed during the ETL transform
(`pipelines/etl.py`) — it is 0 for any subscription with `status = 'churned'`.
`subscriptions.initial_mrr` is the MRR at the start of that subscription's
current contract, used to measure expansion/contraction.

## Expansion / contraction

An account has **expanded** if `current_seat_count > initial_seat_count` on its
subscription row, and **contracted** if `current_seat_count < initial_seat_count`
while still active. These are different from churn — a contracting account is
still paying, just less.

## Net revenue retention (NRR)

**NRR** is `SUM(mrr) / SUM(initial_mrr)` across a cohort of established accounts
(this repo uses accounts whose subscription started at least 90 days before the
most recent observed activity, to exclude accounts too new to have expanded or
contracted yet). NRR above 100% means expansion from existing accounts is
outpacing churn and contraction combined — it is the single most-watched
revenue-quality metric at a B2B SaaS company, and is a different question from
"is revenue growing," which counts new-account revenue too.

## Churn (account)

**Churn**, for an account, means `subscriptions.status = 'churned'` — an account
that canceled its subscription, with `end_date` set. Churn rate for a group is
`churned / total` within that group, not a time-windowed rate (e.g., "churned in
the last 30 days") unless the question asks for that explicitly.

## Activation

**Activation** means a user logged a `created_project` event in
`product_events` — the point at which they've gone beyond onboarding and
actually used the product's core feature. See
`.claude/skills/funnel-analysis.md` for the full onboarding funnel definition
(`signup` → `completed_onboarding` → `created_project`).
