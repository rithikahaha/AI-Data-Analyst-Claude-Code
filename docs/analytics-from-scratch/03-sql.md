# 3. SQL

## What SQL is

SQL is the language for asking a database questions. Every analyst uses it
daily. You write a sentence-like request, the database returns a table.

A query reads almost like English:

```sql
SELECT plan_tier, COUNT(*) AS accounts
FROM subscriptions
GROUP BY plan_tier
```

"From the subscriptions table, group the rows by plan, and count how many are
in each group."

## The building blocks

| Piece | Means | Example |
|---|---|---|
| `SELECT` | Which columns to show | `SELECT name, region` |
| `FROM` | Which table | `FROM organizations` |
| `WHERE` | Keep only rows that match | `WHERE region = 'Europe'` |
| `GROUP BY` | Make one row per group | `GROUP BY plan_tier` |
| `COUNT`, `SUM`, `AVG` | Summarize a group | `COUNT(*)` counts rows |
| `COUNT(DISTINCT x)` | Count unique values of x | unique users |
| `ORDER BY` | Sort the result | `ORDER BY 2 DESC` |
| `JOIN` | Combine two tables using a shared column | see below |
| `WITH name AS (...)` | A named step, called a CTE | see below |

## JOIN: combining tables

`product_events` says which organization did something (`org_id`) but not the
organization's name. To get both, join on the shared column:

```sql
SELECT o.name, COUNT(*) AS events
FROM organizations o
JOIN product_events e ON e.org_id = o.id
GROUP BY o.name
```

The `o` and `e` are short nicknames for the tables. Always write the nickname
before a column (`o.name`) when more than one table is involved. It prevents
mix-ups and makes the query readable.

## CTEs: build the answer in steps

A **CTE** (common table expression) is a named intermediate result. It beats
nesting queries inside queries, which becomes unreadable fast:

```sql
WITH weekly AS (
    SELECT strftime('%Y-%W', event_date) AS week, COUNT(DISTINCT user_id) AS wau
    FROM product_events
    WHERE event_type = 'login'
    GROUP BY 1
)
SELECT * FROM weekly ORDER BY week DESC LIMIT 3
```

Read it top to bottom: first work out weekly active users, then show the last
three. The agents are told to prefer this style in
[`sql-engineer.md`](../../.claude/agents/sql-engineer.md).

## The trap: fan-out

The most common way an analyst gets a wrong number without any error message.

One organization has many events. When you join organizations to events, each
organization's row is **repeated once per event**. Then counting rows counts
events, not organizations.

The real numbers:

- 500 organizations.
- After joining to events, the result has **50,207 rows**.
- `COUNT(DISTINCT o.id)` on that same join is still **500**.

So `COUNT(*)` after a join would say 50,207 "organizations". The fix is to
count distinct IDs, or to summarize each table **before** joining. The agents'
QA step checks for exactly this.

## The read-only guard

Analysts should read data, not change it. The project enforces that in
[`connectors/warehouse.py`](../../connectors/warehouse.py). Every query goes
through one function, `run_query`, which only accepts statements starting with
`SELECT`, `WITH` or `EXPLAIN`. Anything else, like `DROP TABLE`, is rejected
and logged. (For why two layers guard this, see
[access control](../security-rbac.md).)

## Try it

Run queries from Python through the same function the agents use:

```bash
python - <<'PY'
from connectors.warehouse import run_query

print(run_query("SELECT plan_tier, COUNT(*) AS accounts FROM subscriptions GROUP BY plan_tier ORDER BY 2 DESC"))
print(run_query("SELECT event_type, COUNT(*) AS n FROM product_events GROUP BY event_type ORDER BY n DESC"))
PY
```

You should see 174 Team, 165 Enterprise and 160 Starter accounts, and
`login` as the most common event (21,677).

Now see the fan-out trap yourself:

```bash
python - <<'PY'
from connectors.warehouse import run_query
print(run_query("SELECT COUNT(*) AS n FROM organizations o JOIN product_events e ON e.org_id = o.id"))
print(run_query("SELECT COUNT(DISTINCT o.id) AS n FROM organizations o JOIN product_events e ON e.org_id = o.id"))
PY
```

50,207 versus 500, same join, different answer. Only one of them answers "how
many organizations have any events?".

Prove the guard works:

```bash
python -c "from connectors.warehouse import run_query; run_query('DROP TABLE users')"
```

You get an error about read-only statements. **Your own task:** write a query
for "how many users does each plan tier have?" (You will need to join
`users` to `subscriptions` through `org_id`, and count distinct users.) Try it
before reading on.

One answer:

```sql
SELECT s.plan_tier, COUNT(DISTINCT u.id) AS users
FROM users u
JOIN subscriptions s ON s.org_id = u.org_id
GROUP BY s.plan_tier
ORDER BY users DESC
```

It returns Team 1,108, Enterprise 1,052, Starter 1,044. Add them up and you
get 3,204, not the 3,206 users in the table. Why? Two users belong to the one
organization that has no subscription, so the join drops them. A total that
does not match is a clue, not an annoyance, and chasing it down is exactly the
habit this project is trying to teach.

## Check yourself

- What does `GROUP BY` do?
- What is a CTE, and why use one?
- Why did the join give 50,207 rows from a 500-row table?
- Why does the project block `DROP TABLE` in code as well as in the database?
