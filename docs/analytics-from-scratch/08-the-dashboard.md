# 8. The dashboard

## Why a dashboard

Most people who need these numbers will never run SQL. A dashboard is a web
page that shows the key numbers and charts, so a manager can check the health
of the business by opening a link.

The project's dashboard is built with **Streamlit**, a Python library that
turns a script into a web page. It is live at
`https://ai-data-analyst-claude-code.streamlit.app/`, and the code is in
[`dashboard/app.py`](../../dashboard/app.py).

## Four tabs, four questions

| Tab | The question | Chapter |
|---|---|---|
| Engagement | Are people using the product more or less? (weekly active users) | 5 |
| Revenue Health | Are existing customers paying more or less? (NRR, churn by plan) | 4 |
| Onboarding Funnel | Where do new users drop out? | 5 |
| Account Risk | Which accounts should we call first? (the model) | 7 |

The numbers on each tab come from the functions in
[`dashboard/queries.py`](../../dashboard/queries.py). The same functions feed
the exported snapshot, so the two can never drift apart. **One definition,
used everywhere** is a rule worth remembering.

## Writing for a non-technical reader

The first version of the dashboard was accurate and unreadable to anyone who
did not already know what "net revenue retention" means. The rewrite follows
three rules, and you can see them in `app.py`:

1. **Say what it means, not just the number.** Not "NRR 108.5%" alone, but a
   sentence: existing customers are paying 8.5% more than when they started.
2. **Give a verdict.** A short banner says whether the number is good or a
   concern, so the reader does not have to know the benchmark.
3. **Point at the problem.** The funnel tab automatically calls out the
   biggest drop-off instead of leaving the reader to find it.

The risk list uses plain colored labels (red High at 60% or more, yellow
Medium at 35% or more, green Low) next to the percentage, so nobody needs to
interpret a raw probability like 0.94.

## The chart that lied

A real bug, and a real lesson. The first funnel chart showed its bars in
alphabetical order: activation, then onboarding, then signup. That is the
funnel **backwards**. It looked fine at a glance. It was wrong.

It was only caught by opening the dashboard in a browser and checking every
chart, instead of reading the code and assuming. The fix was an explicit sort
order in the code. **Charts can be wrong while the numbers under them are
right.** Always look at the finished thing.

## Try it

Run the dashboard:

```bash
streamlit run dashboard/app.py
```

It opens in your browser. (The first run builds the data and trains the model
if they are missing, which takes a moment. That self-bootstrapping is what
lets it work on a fresh deploy.)

Then check the dashboard against the database, the way a careful analyst would.
For each tab, find the number on screen, run the matching function, and
confirm they agree:

```bash
python - <<'PY'
from dashboard.queries import net_revenue_retention, churn_by_plan_tier, onboarding_funnel
print(net_revenue_retention())     # should match the Revenue Health tab: 108.5
print(churn_by_plan_tier())        # Starter 28.8, Team 20.7, Enterprise 6.7
print(onboarding_funnel())         # 3206, 2295, 1421
PY
```

**Your own task:** read the Engagement tab's caption in `app.py`. In your own
words, would a manager understand it without help? If not, what would you
change?

## Check yourself

- Why does the dashboard reuse the functions in `queries.py`?
- What are the three rules for writing for a non-technical reader?
- What was wrong with the first funnel chart, and how was it caught?
