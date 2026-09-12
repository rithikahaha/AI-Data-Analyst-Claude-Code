import json

from ml.features import FEATURE_COLUMNS, TARGET_COLUMN, build_feature_frame


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


def test_train_churn_model_saves_model_and_metrics():
    from ml.train_churn_model import METADATA_PATH, MODEL_PATH
    from ml.train_churn_model import main as train_main

    train_main()

    assert MODEL_PATH.exists()
    metadata = json.loads(METADATA_PATH.read_text())
    assert set(FEATURE_COLUMNS) <= set(metadata["feature_columns"])
    assert 0.0 <= metadata["metrics"]["auc"] <= 1.0
