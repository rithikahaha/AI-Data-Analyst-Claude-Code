# 2. The data

## Where the numbers come from

Real companies have data scattered across different systems: a CRM for
customers, a billing system for money, a product database for usage. This
project imitates that with one script that generates four "exports" as CSV
files, in [`scripts/export_raw_sources.py`](../../scripts/export_raw_sources.py):

| Source system | File it writes | Becomes the table |
|---|---|---|
| CRM | `organizations.csv` | `organizations` |
| Identity provider | `users.csv` | `users` |
| Billing system | `subscriptions.csv` | `subscriptions` |
| Product analytics | `product_events.csv` | `product_events` |

The script uses fixed random seeds (`random.seed(42)`), so it produces
**exactly the same data every time**. That is why the numbers in this guide
never change.

## The four tables

Think of each table as a spreadsheet. A row is one thing, a column is one fact
about it.

**`organizations`** has one row per customer company (500 rows).
Columns: `id`, `name`, `industry`, `region`, `signed_up_date`.

**`users`** has one row per person (3,206 rows).
Columns: `id`, `org_id` (which company they belong to), `name`, `email`,
`role`, `joined_date`.

**`subscriptions`** has one row per paid plan (499 rows).
Columns: `id`, `org_id`, `plan_tier`, `price_per_seat`, `initial_seat_count`,
`current_seat_count`, `start_date`, `end_date`, `status` (`active` or
`churned`), `mrr`, `initial_mrr`.

**`product_events`** has one row per action (50,207 rows).
Columns: `id`, `user_id`, `org_id`, `event_type`, `event_date`.

The link between tables is the `org_id` and `user_id` columns. They point at
the `id` of another table. These links are called **foreign keys**, and they
are how you combine tables (chapter 3).

Notice there are 500 organizations but 499 subscriptions. One organization
has no subscription. That is normal in real data and a good reminder never to
assume the tables line up perfectly.

## ETL: extract, transform, load

The raw CSV files are deliberately a bit messy, the way real exports are.
[`pipelines/etl.py`](../../pipelines/etl.py) cleans them in three steps:

1. **Extract:** read the CSV files.
2. **Transform:** fix them. It removes duplicate organizations and works out
   revenue.
3. **Load:** write the clean tables into a database file,
   `data/sample_warehouse.db`. (This kind of database is called SQLite. It is
   just a file, so no server is needed.)

Two specific messes the pipeline fixes:

- **Duplicates.** The generator adds 9 duplicate organization rows on purpose,
  imitating a CRM that exported the same customers twice. If you did not
  remove them, every customer count would be slightly wrong.
- **Missing revenue column.** The billing system stores seats and price, not
  revenue. The pipeline computes **MRR** (monthly recurring revenue) as
  `current_seat_count x price_per_seat`, and sets it to 0 for churned
  accounts.

## Data quality checks

A number built on bad data is worse than no number, because people trust it.
So the pipeline **checks the data before and after cleaning**, in
[`pipelines/data_quality.py`](../../pipelines/data_quality.py). Three kinds of
check:

| Check | Question it asks |
|---|---|
| **Nulls** | Is anything important blank? |
| **Uniqueness** | Does any ID appear twice? |
| **Referential integrity** | Does every `org_id` in `users` point at a real organization? |

If a check fails after cleaning, the pipeline **stops** instead of loading bad
data. Failing loudly is the point.

## Try it

Run the pipeline and read the output:

```bash
python -m scripts.export_raw_sources
python -m pipelines.etl
```

Look for the "raw extracts (pre-transform)" section. You should see a
`[FAIL]` on uniqueness for `raw.organizations`, with a note about duplicate
rows. That failure is **expected**: it is the planted mess. The later sections
should all say `PASS`.

Now look at the data yourself:

```bash
python - <<'PY'
import pandas as pd
from connectors.warehouse import run_query
raw = pd.read_csv("data/raw/organizations.csv")
print("rows in raw CSV:", len(raw), "| unique ids:", raw["id"].nunique())
print("rows in warehouse:", run_query("SELECT COUNT(*) AS n FROM organizations")["n"][0])
print(run_query("SELECT * FROM organizations LIMIT 3"))
PY
```

You should see 509 rows in the raw file but 500 unique ids, and 500 in the
warehouse. That difference of 9 is the duplicates being removed.

**Break it on purpose.** In `pipelines/etl.py`, in the `transform` function,
find the line that starts `organizations = raw["organizations"].drop_duplicates(...`
and change it to just `organizations = raw["organizations"]`. Re-run the
pipeline. The "transformed tables" section now shows
`[FAIL] transformed.organizations: uniqueness on ['id']: 9 duplicate rows found`
and it refuses to load. That is the pipeline protecting you from bad data.
Undo it with `git checkout pipelines/etl.py`, then re-run the pipeline once so
the warehouse is rebuilt correctly.

## Check yourself

- What does ETL stand for, and what does each step do?
- Why does the generator plant duplicate rows on purpose?
- Why does the pipeline stop instead of loading data that fails a check?
- How is MRR calculated, and why is it 0 for churned accounts?
