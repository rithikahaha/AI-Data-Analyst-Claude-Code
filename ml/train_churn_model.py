"""Train a churn-risk classifier on the sample warehouse.

Reference pipeline for the data-scientist agent: build features via SQL, hold out
a test set, evaluate on AUC/precision/recall (not accuracy, churn is imbalanced),
and save the fitted pipeline + metrics.
"""

import json
from datetime import datetime, timezone
from pathlib import Path

import joblib
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import (
    average_precision_score,
    precision_recall_fscore_support,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

from ml.features import CATEGORICAL_FEATURES, FEATURE_COLUMNS, NUMERIC_FEATURES, TARGET_COLUMN, build_feature_frame

MODELS_DIR = Path(__file__).resolve().parent / "models"
MODEL_PATH = MODELS_DIR / "churn_model.joblib"
METADATA_PATH = MODELS_DIR / "churn_model_metadata.json"


def build_pipeline() -> Pipeline:
    preprocessor = ColumnTransformer(
        transformers=[
            ("categorical", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL_FEATURES),
        ],
        remainder="passthrough",
    )
    classifier = GradientBoostingClassifier(random_state=42)
    return Pipeline(steps=[("preprocess", preprocessor), ("classify", classifier)])


def main() -> None:
    df = build_feature_frame()
    X = df[FEATURE_COLUMNS]
    y = df[TARGET_COLUMN]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y
    )

    pipeline = build_pipeline()
    pipeline.fit(X_train, y_train)

    y_pred = pipeline.predict(X_test)
    y_proba = pipeline.predict_proba(X_test)[:, 1]

    precision, recall, f1, _ = precision_recall_fscore_support(
        y_test, y_pred, average="binary", zero_division=0
    )
    auc = roc_auc_score(y_test, y_proba)
    avg_precision = average_precision_score(y_test, y_proba)

    metrics = {
        "auc": round(float(auc), 4),
        "average_precision": round(float(avg_precision), 4),
        "precision": round(float(precision), 4),
        "recall": round(float(recall), 4),
        "f1": round(float(f1), 4),
        "n_train": len(X_train),
        "n_test": len(X_test),
        "churn_rate_train": round(float(y_train.mean()), 4),
        "churn_rate_test": round(float(y_test.mean()), 4),
    }

    MODELS_DIR.mkdir(exist_ok=True)
    joblib.dump(pipeline, MODEL_PATH)

    metadata = {
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "feature_columns": FEATURE_COLUMNS,
        "numeric_features": NUMERIC_FEATURES,
        "categorical_features": CATEGORICAL_FEATURES,
        "target": TARGET_COLUMN,
        "model_type": "GradientBoostingClassifier",
        "metrics": metrics,
    }
    METADATA_PATH.write_text(json.dumps(metadata, indent=2))

    print(f"Trained churn model on {len(X_train)} rows, tested on {len(X_test)}.")
    print(json.dumps(metrics, indent=2))
    print(f"\nSaved model to {MODEL_PATH}")
    print(f"Saved metadata to {METADATA_PATH}")


if __name__ == "__main__":
    main()
