# 4. Metrics

## Why definitions matter

Ask three people "how many active users do we have?" and you can get three
answers. One counts anyone with an account. One counts anyone who logged in
this month. One counts anyone who did something this week. All three are
"correct". Only one is what the question meant.

This is the most common way a correct query gives a misleading answer. So the
project pins down each important metric in one file,
[`knowledge/metrics_glossary.md`](../../knowledge/metrics_glossary.md), and
every agent is told to check it instead of guessing.

## The metrics in this project

**Active user (WAU).** A user is active in a week if they logged a `login`
event that week. WAU is weekly active users, the count of such users.

This is different from an **active account**: an organization whose
subscription status is `active`. An account can be paying while none of its
users has logged in for months. Those are exactly the accounts most likely to
cancel.

**MRR (monthly recurring revenue).** Seats times price per seat, for each
subscription. A 12-seat Starter account pays 12 x $15 = $180 a month. Churned
accounts count as 0.

**Expansion and contraction.** An account **expanded** if its current seat
count is higher than when it started, and **contracted** if lower while still
active. In the data, 138 subscriptions expanded and 16 contracted.

**Churn.** An account that cancelled (`status = 'churned'`). Churn rate for a
group is churned accounts divided by total accounts in that group. Overall it
is 93 of 499, about 18.6%.

**Activation.** A user has activated once they create a project, the moment
they have used the product's main feature, not just signed up.

**NRR (net revenue retention).** The most watched number in subscription
businesses. It answers: "Take the customers we already had. Are they paying us
more or less than when they started?"

```
NRR = current MRR of those accounts / their starting MRR
```

Above 100% means expansion is outpacing losses from cancellations and
downgrades. In this data:

```
117,525 / 108,275 = 108.5%
```

The existing customers collectively pay 8.5% more than when they began. That
is healthy, and it is a very different question from "is total revenue
growing?", which also counts brand-new customers.

**A simplification to know about:** the project computes NRR over accounts that
started at least 90 days before the last activity in the data (so brand-new
accounts do not distort it), comparing current to starting MRR. A textbook NRR
usually compares a fixed 12-month window. The idea is the same. Say
"simplified" if asked.

## How the agents look definitions up

When a question uses a fuzzy term, an agent searches the glossary with
[`rag/retrieve.py`](../../rag/retrieve.py). It uses a classic technique called
**TF-IDF**: it scores how much each glossary entry shares distinctive words
with the question, and returns the best match. No AI model or API key is
needed for this step, on purpose. If nothing scores high enough, it returns
nothing, and the agent must say the term is not defined instead of inventing a
definition.

("RAG" means retrieval-augmented generation: look up relevant text, then use it
to ground an answer. This is the simple version of that idea.)

## Try it

Look up definitions the way an agent does:

```bash
python -m rag.retrieve
```

It runs three sample questions and prints the best glossary entry for each,
with a relevance score.

Compute NRR yourself:

```bash
python - <<'PY'
from dashboard.queries import net_revenue_retention
print(net_revenue_retention())
PY
```

You should get current MRR 117,525, initial MRR 108,275 and 108.5%. Check the
division by hand.

Count the two kinds of "active" and see how they differ:

```bash
python - <<'PY'
from connectors.warehouse import run_query
print(run_query("SELECT COUNT(*) AS active_accounts FROM subscriptions WHERE status = 'active'"))
print(run_query("SELECT COUNT(DISTINCT user_id) AS users_who_ever_logged_in FROM product_events WHERE event_type = 'login'"))
PY
```

These count different things (accounts versus users, paying versus using). That
is the whole point of a glossary.

## Check yourself

- What is the difference between an active user and an active account?
- If NRR is 95%, what does that tell you?
- Why is NRR a different question from "is revenue growing?"
- What should an agent do if a term is not in the glossary?
