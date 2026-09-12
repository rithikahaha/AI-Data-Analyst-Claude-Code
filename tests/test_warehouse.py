import pytest

from connectors.warehouse import list_tables, run_query


def test_read_only_guard_blocks_writes():
    for statement in ["DELETE FROM orders", "DROP TABLE customers", "UPDATE customers SET name='x'"]:
        with pytest.raises(ValueError):
            run_query(statement)


def test_read_only_guard_allows_select():
    df = run_query("SELECT 1 AS one")
    assert df["one"].iloc[0] == 1


def test_list_tables_matches_seeded_schema():
    tables = set(list_tables())
    assert {"customers", "products", "orders", "order_items", "subscriptions", "events"} <= tables


def test_customers_table_has_no_duplicate_ids():
    df = run_query("SELECT id, COUNT(*) AS n FROM customers GROUP BY id HAVING n > 1")
    assert df.empty, "ETL should have deduped the raw customer extract's overlap rows"


def test_orders_total_amount_matches_line_items():
    mismatches = run_query(
        """
        SELECT o.id
        FROM orders o
        JOIN (SELECT order_id, SUM(quantity * unit_price) AS computed_total FROM order_items GROUP BY order_id) li
          ON li.order_id = o.id
        WHERE ABS(o.total_amount - li.computed_total) > 0.01
        """
    )
    assert mismatches.empty
