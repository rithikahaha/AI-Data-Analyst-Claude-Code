import pytest

from ml.features import CATEGORICAL_FEATURES, FEATURE_COLUMNS, NUMERIC_FEATURES, TARGET_COLUMN, build_feature_frame


def test_feature_frame_has_expected_columns():
    df = build_feature_frame()
    for col in FEATURE_COLUMNS + [TARGET_COLUMN]:
        assert col in df.columns


def test_feature_frame_target_is_binary():
    df = build_feature_frame()
    assert set(df[TARGET_COLUMN].unique()) <= {0, 1}


def test_feature_frame_not_empty():
    df = build_feature_frame()
    assert len(df) > 0


@pytest.fixture(scope="module")
def trained_model():
    from ml.train_churn_model import main as train_main

    train_main()


def test_train_and_check_drift_end_to_end(trained_model):
    from ml.check_drift import check_drift

    report = check_drift()
    assert "any_drift" in report
    # A freshly-trained model checked against the same data it trained on
    # should not report drift.
    assert report["any_drift"] is False


def test_registry_has_active_model_after_training(trained_model):
    from ml.registry import get_active_model

    active = get_active_model()
    assert active is not None
    assert set(FEATURE_COLUMNS) <= set(active["feature_columns"])
    assert 0.0 <= active["metrics"]["auc"] <= 1.0
