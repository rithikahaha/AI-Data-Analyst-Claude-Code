"""Service level indicators (SLIs) and objectives (SLOs) for the warehouse
connector, computed from the query log that connectors/warehouse.py writes.

Two SLIs, the two a small analytics service can measure honestly:

- Availability: share of queries that succeeded. Queries the read-only guard
  blocked are excluded, a rejected DROP is the guard working, not an outage.
- Latency: how long successful queries take, judged at the 95th percentile
  because an average hides the slow queries users actually notice.

Data in, report out (same shape as pipelines/data_quality.py), so the maths is
testable with a few synthetic records instead of a live system.
"""

import json
import math
import os
import sys
from dataclasses import dataclass
from pathlib import Path

DEFAULT_QUERY_LOG_PATH = Path(__file__).resolve().parent.parent / "logs" / "queries.jsonl"

AVAILABILITY_SLO = 0.995  # 99.5% of queries succeed
LATENCY_P95_SLO_MS = 1000.0  # 95% of successful queries finish within 1s


@dataclass
class SLIReport:
    total_requests: int
    availability: float | None
    error_budget_remaining_pct: float | None
    latency_p50_ms: float | None
    latency_p95_ms: float | None
    availability_ok: bool
    latency_ok: bool

    @property
    def healthy(self) -> bool:
        return self.availability_ok and self.latency_ok


def load_records(path: Path) -> list[dict]:
    if not path.exists():
        return []
    records = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            records.append(json.loads(line))
    return records


def percentile(values: list[float], pct: float) -> float:
    """Nearest-rank percentile, no numpy needed for a metric this small."""
    ordered = sorted(values)
    rank = max(1, math.ceil(pct / 100 * len(ordered)))
    return ordered[rank - 1]


def compute_slis(
    records: list[dict],
    availability_slo: float = AVAILABILITY_SLO,
    latency_p95_slo_ms: float = LATENCY_P95_SLO_MS,
) -> SLIReport:
    counted = [r for r in records if r["status"] in ("ok", "error")]
    if not counted:
        return SLIReport(0, None, None, None, None, availability_ok=True, latency_ok=True)

    ok = [r for r in counted if r["status"] == "ok"]
    availability = len(ok) / len(counted)

    # Error budget: the failures the SLO allows, and how much of that is left.
    allowed_failures = (1 - availability_slo) * len(counted)
    actual_failures = len(counted) - len(ok)
    if allowed_failures > 0:
        budget_remaining = max(0.0, (1 - actual_failures / allowed_failures) * 100)
    else:
        budget_remaining = 100.0 if actual_failures == 0 else 0.0

    durations = [r["duration_ms"] for r in ok]
    p50 = percentile(durations, 50) if durations else None
    p95 = percentile(durations, 95) if durations else None

    return SLIReport(
        total_requests=len(counted),
        availability=availability,
        error_budget_remaining_pct=round(budget_remaining, 1),
        latency_p50_ms=p50,
        latency_p95_ms=p95,
        availability_ok=availability >= availability_slo,
        latency_ok=p95 is None or p95 <= latency_p95_slo_ms,
    )


def report(r: SLIReport) -> None:
    print("\n--- Service level indicators ---")
    if r.total_requests == 0:
        print("No queries logged yet, nothing to measure.")
        return
    mark = lambda ok: "OK" if ok else "SLO BREACHED"  # noqa: E731
    print(f"Requests measured: {r.total_requests}")
    print(f"Availability: {r.availability:.2%} (SLO {AVAILABILITY_SLO:.1%}) [{mark(r.availability_ok)}]")
    print(f"Error budget remaining: {r.error_budget_remaining_pct}%")
    if r.latency_p95_ms is not None:
        print(f"Latency p50: {r.latency_p50_ms:.1f} ms, p95: {r.latency_p95_ms:.1f} ms (SLO {LATENCY_P95_SLO_MS:.0f} ms) [{mark(r.latency_ok)}]")


if __name__ == "__main__":
    log_path = Path(os.environ.get("QUERY_LOG_PATH", DEFAULT_QUERY_LOG_PATH))
    sli = compute_slis(load_records(log_path))
    report(sli)
    sys.exit(0 if sli.healthy else 1)
