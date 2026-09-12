import pytest

from connectors.warehouse import list_tables, run_query


def test_read_only_guard_blocks_writes():
    for statement in ["DELETE FROM subscriptions", "DROP TABLE organizations", "UPDATE organizations SET name='x'"]:
        with pytest.raises(ValueError):
            run_query(statement)


def test_read_only_guard_allows_select():
    df = run_query("SELECT 1 AS one")
    assert df["one"].iloc[0] == 1


def test_list_tables_matches_seeded_schema():
    tables = set(list_tables())
    assert {"organizations", "users", "subscriptions", "product_events"} <= tables


def test_organizations_table_has_no_duplicate_ids():
    df = run_query("SELECT id, COUNT(*) AS n FROM organizations GROUP BY id HAVING n > 1")
    assert df.empty, "ETL should have deduped the raw organization extract's overlap rows"


def test_subscriptions_mrr_matches_seats_times_price():
    mismatches = run_query(
        """
        SELECT id
        FROM subscriptions
        WHERE status != 'churned'
          AND ABS(mrr - current_seat_count * price_per_seat) > 0.01
        """
    )
    assert mismatches.empty


def test_churned_subscriptions_have_zero_mrr():
    df = run_query("SELECT COUNT(*) AS n FROM subscriptions WHERE status = 'churned' AND mrr != 0")
    assert df["n"].iloc[0] == 0
