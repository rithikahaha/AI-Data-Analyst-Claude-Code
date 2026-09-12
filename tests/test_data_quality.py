import pandas as pd

from pipelines.data_quality import check_nulls, check_referential_integrity, check_uniqueness


def test_check_nulls_fails_on_nulls():
    df = pd.DataFrame({"a": [1, None, 3]})
    result = check_nulls(df, ["a"], "t")
    assert not result.passed


def test_check_nulls_passes_when_clean():
    df = pd.DataFrame({"a": [1, 2, 3]})
    result = check_nulls(df, ["a"], "t")
    assert result.passed


def test_check_uniqueness_fails_on_duplicates():
    df = pd.DataFrame({"id": [1, 1, 2]})
    result = check_uniqueness(df, ["id"], "t")
    assert not result.passed


def test_referential_integrity_fails_on_orphan():
    child = pd.DataFrame({"parent_id": [1, 2, 99]})
    parent = pd.DataFrame({"id": [1, 2]})
    result = check_referential_integrity(child, "parent_id", parent, "id", "child->parent")
    assert not result.passed


def test_referential_integrity_passes_when_resolved():
    child = pd.DataFrame({"parent_id": [1, 2]})
    parent = pd.DataFrame({"id": [1, 2]})
    result = check_referential_integrity(child, "parent_id", parent, "id", "child->parent")
    assert result.passed
