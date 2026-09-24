# 5. Trends and funnels

Two of the most common analyst questions: "is it going up or down?" and "where
are we losing people?". Both look simple. Both have a trap.

## Trends: weekly active users

The query behind the engagement chart, in
[`dashboard/queries.py`](../../dashboard/queries.py):

```sql
SELECT strftime('%Y-%W', event_date) AS week, COUNT(DISTINCT user_id) AS wau
FROM product_events
WHERE event_type = 'login'
GROUP BY 1
ORDER BY 1
```

`strftime('%Y-%W', ...)` turns a date into a year and week number, like
`2026-34`. Then it counts unique users who logged in during each week.

The answer the project reports: **weekly active users grew from 234 to 411
over 26 weeks, up 75.6%.** Check the arithmetic: (411 - 234) / 234 = 75.6%.

### Trap 1: the partial week

The data ends partway through a week (week 35 has only 169 users because the
week is not over). Including it makes it look like engagement collapsed. The
code drops the last week before charting. **Always check whether the most
recent period is complete.**

### Trap 2: counting the interval

234 was the count in week 8 and 411 in week 34. That is 26 weeks apart, but it
is 27 data points. "Over 26 weeks" is correct. Mixing up the number of points
and the number of gaps between them is a classic off-by-one mistake, and it
changes the growth percentage: measured from the point 26 places back instead
(week 9, 208 users), you would get 97.6% growth. Small choices move the
headline, so say exactly what you compared.

### Trap 3: the starting point

The first weeks of data in 2024 have 1 or 5 users. Growth from 1 to 411 is
41,000%, and it is meaningless. Pick a window that answers the question. A
startup's first weeks are not a fair baseline.

### Trap 4: growing because there are more accounts

If the company signed many new customers, WAU rises even if each customer uses
the product less. A good analyst asks whether it is growth in usage per
account or just more accounts, and does not stop at the first chart.

## Funnels: where do we lose people?

A **funnel** is a sequence of steps people must pass through. Here:

1. **Signed up**
2. **Completed onboarding** (the guided setup)
3. **Created a project** (activation, the point they use the real product)

Counting distinct users who reached each step:

| Step | Users | Of previous step | Lost |
|---|---|---|---|
| Signed up | 3,206 | | |
| Completed onboarding | 2,295 | 71.6% | 911 |
| Created a project | 1,421 | 61.9% | 874 |

Overall, 1,421 / 3,206 = **44.3%** activate.

The **biggest leak** is a matter of what you measure. The first step loses more
people (911), but the second step loses a bigger share of the people who
reached it (38.1%, versus 28.4%). The project reports the second, because those
are people who finished the guided setup and still never used the product. A
person who bails during setup and one who finishes and still walks away are
different problems with different fixes.

### Trap: not a true cohort

This funnel counts everyone who **ever** reached each step. A user who signed
up last week has had almost no time to activate yet, so recent signups drag the
conversion rate down. A stricter method follows a **cohort** (everyone who
signed up in a given month) for a fixed period, say 30 days each. The funnel
skill says to do that, and the simple query here does not, which is why the
example write-up lists it as a caveat. Say so if asked.

## Try it

```bash
python - <<'PY'
from dashboard.queries import weekly_active_users, onboarding_funnel
w = weekly_active_users()
print(w.tail(3))                      # note the last full week is 2026-34
first, last = w.iloc[-27]["wau"], w.iloc[-1]["wau"]
print(first, last, round((last - first) / first * 100, 1))   # 234 411 75.6
print(onboarding_funnel())
PY
```

Then experiment. Change `-27` to `-26` and see the growth jump to 97.6%. Same
data, different headline. That is why the window must be stated.

**Your own task:** activation rate by plan tier, meaning of the users who signed
up, what share created a project. Start from this:

```sql
SELECT s.plan_tier,
       COUNT(DISTINCT CASE WHEN e.event_type = 'signup' THEN e.user_id END) AS signed_up,
       COUNT(DISTINCT CASE WHEN e.event_type = 'created_project' THEN e.user_id END) AS activated
FROM product_events e
JOIN subscriptions s ON s.org_id = e.org_id
GROUP BY s.plan_tier
```

Run it with `run_query` and divide. You should find Starter about 46.6%, and
Enterprise and Team about 43%. The plans barely differ, which is itself a
finding: activation is not what separates Starter's high churn from
Enterprise's low churn.

## Check yourself

- Why does the code drop the last week?
- What is the difference between "26 weeks" and "27 data points"?
- Why is the second funnel step the bigger problem even though it loses fewer people?
- What is a cohort and why is it a fairer comparison?
