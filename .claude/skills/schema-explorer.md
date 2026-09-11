---
name: schema-explorer
description: Discover the warehouse's tables, columns, and relationships before writing a query. Use this first whenever you're not already certain of exact table/column names.
---

# Schema Explorer

Never guess a table or column name — the sample warehouse and real warehouses will
both differ from what you might assume.

## Steps

1. Import the connector and list tables:
   ```python
   from connectors.warehouse import get_engine
   import pandas as pd
   engine = get_engine()
   print(pd.read_sql("SELECT name FROM sqlite_master WHERE type='table'", engine))
   ```
   (On a non-SQLite warehouse, use `information_schema.tables` instead.)
2. For each relevant table, inspect columns and types:
   ```python
   print(pd.read_sql("PRAGMA table_info(orders)", engine))
   ```
3. Note primary/foreign key relationships (e.g., `orders.customer_id` →
   `customers.id`) so joins are correct on the first try.
4. Spot-check a few rows (`SELECT * FROM orders LIMIT 5`) to see real data shapes —
   date formats, whether amounts are cents or dollars, whether a "status" column uses
   strings or codes.

Only after this should you hand off to writing the actual analysis query.
