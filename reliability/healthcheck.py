"""One-command health check: is the warehouse reachable, are the expected
tables there, and is the data still fresh.

Exit code 0 means healthy, 1 means not. That contract is what CI, a container
orchestrator, or a cron job needs, they act on the exit code, not on prose.

    python -m reliability.healthcheck
"""

import json
import sys

from connectors.warehouse import list_tables, run_query
from pipelines.monitor import run_all_checks

EXPECTED_TABLES = {"organizations", "users", "subscriptions", "product_events"}


def check_reachable() -> dict:
    try:
        run_query("SELECT 1 AS ok")
        return {"check": "warehouse reachable", "ok": True, "detail": "SELECT 1 succeeded"}
    except Exception as exc:  # any failure here is the answer, not a crash
        return {"check": "warehouse reachable", "ok": False, "detail": str(exc)[:200]}


def check_tables() -> dict:
    try:
        missing = EXPECTED_TABLES - set(list_tables())
    except Exception as exc:
        return {"check": "expected tables present", "ok": False, "detail": str(exc)[:200]}
    return {
        "check": "expected tables present",
        "ok": not missing,
        "detail": "all present" if not missing else f"missing: {sorted(missing)}",
    }


def check_freshness() -> list[dict]:
    try:
        alerts = run_all_checks()
    except Exception as exc:
        return [{"check": "data freshness", "ok": False, "detail": str(exc)[:200]}]
    return [{"check": a.check, "ok": a.severity == "ok", "detail": a.detail} for a in alerts]


def run() -> dict:
    results = [check_reachable()]
    # Later checks need a reachable warehouse, so skip them rather than
    # piling identical errors on top of the real cause.
    if results[0]["ok"]:
        results.append(check_tables())
        if results[-1]["ok"]:
            results.extend(check_freshness())
    return {"healthy": all(r["ok"] for r in results), "checks": results}


if __name__ == "__main__":
    result = run()
    print(json.dumps(result, indent=2))
    sys.exit(0 if result["healthy"] else 1)
