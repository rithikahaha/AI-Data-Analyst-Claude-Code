"""Feature drift check for ml-platform-engineer.

Compares the current warehouse's feature distributions against the snapshot taken
at training time (saved in churn_model_metadata.json). Uses a simple standardized-
mean-shift check per numeric feature — simple on purpose: the point is to have an
automated tripwire an agent can run before trusting a model's predictions, not to
build a full statistical monitoring platform.
"""

import json
from pathlib import Path

from ml.features import NUMERIC_FEATURES, build_feature_frame

METADATA_PATH = Path(__file__).resolve().parent / "models" / "churn_model_metadata.json"

DRIFT_THRESHOLD_STD = 0.5  # flag if current mean has shifted more than this many training-std-devs


def check_drift() -> dict:
    if not METADATA_PATH.exists():
        raise FileNotFoundError(
            "No trained model metadata found — run `python -m ml.train_churn_model` first."
        )
    metadata = json.loads(METADATA_PATH.read_text())
    training_snapshot = metadata["training_feature_snapshot"]

    current_df = build_feature_frame()

    report = {"trained_at": metadata["trained_at"], "features": {}, "any_drift": False}
    for feature in NUMERIC_FEATURES:
        train_mean = training_snapshot[feature]["mean"]
        train_std = training_snapshot[feature]["std"] or 1e-9
        current_mean = float(current_df[feature].mean())

        shift_in_std_devs = abs(current_mean - train_mean) / train_std
        drifted = shift_in_std_devs > DRIFT_THRESHOLD_STD

        report["features"][feature] = {
            "training_mean": round(train_mean, 3),
            "current_mean": round(current_mean, 3),
            "shift_in_std_devs": round(shift_in_std_devs, 3),
            "drifted": drifted,
        }
        report["any_drift"] = report["any_drift"] or drifted

    return report


if __name__ == "__main__":
    result = check_drift()
    print(json.dumps(result, indent=2))
    if result["any_drift"]:
        print(
            "\nDrift detected on at least one feature — consider retraining "
            "(data-scientist) before continuing to trust this model's scores."
        )
    else:
        print("\nNo drift detected past threshold.")
