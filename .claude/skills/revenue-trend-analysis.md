---
name: revenue-trend-analysis
description: Standard playbook for "how is revenue trending" questions — MoM/YoY growth, seasonality, and segment breakdowns. Use for any question about revenue, sales, or GMV over time.
---

# Revenue Trend Analysis

## Steps

1. Confirm the revenue definition: gross order value, net of refunds, or recognized
   revenue? Default to gross order value (`orders.total_amount` where
   `status = 'completed'`) unless the question specifies otherwise, and say so.
2. Aggregate by the right grain for the question — daily for a "last 2 weeks"
   question, monthly for anything spanning multiple quarters:
   ```sql
   SELECT strftime('%Y-%m', order_date) AS month, SUM(total_amount) AS revenue
   FROM orders
   WHERE status = 'completed'
   GROUP BY 1
   ORDER BY 1;
   ```
3. Compute growth rates alongside the raw trend:
   - MoM: `(this_month - last_month) / last_month`
   - YoY: compare the same month a year prior (only if data history is long enough —
     check with `schema-explorer` first).
4. If the question mentions a segment (customer tier, region, product category),
   add it as a `GROUP BY` dimension and consider a stacked or small-multiples chart
   via `data-visualizer` instead of one aggregate line.
5. Call out seasonality or one-off spikes (e.g., a single large order skewing a
   month) rather than reading them as trend.

## Answer format

Lead with the direction and magnitude ("Revenue grew 12% MoM in [month], driven
mostly by X"), then show the trend chart, then the query.
