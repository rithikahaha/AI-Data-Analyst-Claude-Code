"""Append-only model registry for ml-platform-engineer.

Every training run gets logged here — version, when it was trained, its metrics,
and the feature schema it expects — so a production model's provenance is never
just "a file that appeared on disk." Deliberately file-based (JSON) rather than a
database: this is meant to be inspectable in a git diff, not a service to run.
"""

import json
from pathlib import Path
from typing import Any

REGISTRY_PATH = Path(__file__).resolve().parent / "models" / "registry.json"


def _load_registry() -> list[dict]:
    if not REGISTRY_PATH.exists():
        return []
    return json.loads(REGISTRY_PATH.read_text())


def _save_registry(entries: list[dict]) -> None:
    REGISTRY_PATH.parent.mkdir(exist_ok=True)
    REGISTRY_PATH.write_text(json.dumps(entries, indent=2))


def register_model(model_path: Path, metadata: dict[str, Any]) -> dict:
    """Append a new registry entry for a freshly trained model. Versions are
    1-indexed and monotonically increasing — never overwritten, so history is
    always available for rollback.
    """
    entries = _load_registry()
    version = len(entries) + 1
    entry = {
        "version": version,
        "model_path": str(model_path),
        "trained_at": metadata["trained_at"],
        "model_type": metadata["model_type"],
        "metrics": metadata["metrics"],
        "feature_columns": metadata["feature_columns"],
        "status": "active",
    }
    for e in entries:
        if e["status"] == "active":
            e["status"] = "superseded"
    entries.append(entry)
    _save_registry(entries)
    print(f"Registered model version {version} (status=active, previous versions marked superseded).")
    return entry


def get_active_model() -> dict | None:
    entries = _load_registry()
    active = [e for e in entries if e["status"] == "active"]
    return active[-1] if active else None


def get_previous_model() -> dict | None:
    """The last superseded version — what rollback would restore."""
    entries = _load_registry()
    superseded = [e for e in entries if e["status"] == "superseded"]
    return superseded[-1] if superseded else None


def rollback() -> dict | None:
    """Mark the current active model superseded and reactivate the previous one.
    Does not delete or retrain anything — just changes which version is
    considered current.
    """
    entries = _load_registry()
    active_entries = [e for e in entries if e["status"] == "active"]
    superseded_entries = [e for e in entries if e["status"] == "superseded"]
    if not active_entries or not superseded_entries:
        print("Nothing to roll back to.")
        return None

    active_entries[-1]["status"] = "rolled_back"
    restored = superseded_entries[-1]
    restored["status"] = "active"
    _save_registry(entries)
    print(f"Rolled back to version {restored['version']}.")
    return restored


if __name__ == "__main__":
    active = get_active_model()
    if active:
        print(f"Active model: version {active['version']}, trained {active['trained_at']}")
        print(json.dumps(active["metrics"], indent=2))
    else:
        print("No model registered yet — run `python -m ml.train_churn_model` first.")
