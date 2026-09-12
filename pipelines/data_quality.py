"""Reusable data-quality checks for data-platform-engineer's pipeline.

Generic, dataframe-in / report-out checks so the same functions run against raw
extracts before transform and against warehouse tables after load — a pipeline
that only validates on one side of the transform can let a bug in the transform
itself go uncaught.
"""

from dataclasses import dataclass

import pandas as pd


@dataclass
class CheckResult:
    check: str
    passed: bool
    detail: str

    def __str__(self) -> str:
        status = "PASS" if self.passed else "FAIL"
        return f"[{status}] {self.check}: {self.detail}"


def check_nulls(df: pd.DataFrame, columns: list[str], table_name: str) -> CheckResult:
    null_counts = {c: int(df[c].isna().sum()) for c in columns}
    bad = {c: n for c, n in null_counts.items() if n > 0}
    return CheckResult(
        check=f"{table_name}: null check on {columns}",
        passed=not bad,
        detail="no nulls" if not bad else f"nulls found: {bad}",
    )


def check_uniqueness(df: pd.DataFrame, key_columns: list[str], table_name: str) -> CheckResult:
    dup_count = int(df.duplicated(subset=key_columns).sum())
    return CheckResult(
        check=f"{table_name}: uniqueness on {key_columns}",
        passed=dup_count == 0,
        detail="no duplicates" if dup_count == 0 else f"{dup_count} duplicate rows found",
    )


def check_referential_integrity(
    child_df: pd.DataFrame,
    child_key: str,
    parent_df: pd.DataFrame,
    parent_key: str,
    relationship_name: str,
) -> CheckResult:
    orphans = set(child_df[child_key]) - set(parent_df[parent_key])
    return CheckResult(
        check=f"referential integrity: {relationship_name}",
        passed=not orphans,
        detail="all references resolve" if not orphans else f"{len(orphans)} orphaned references: {list(orphans)[:5]}",
    )


def run_checks_and_report(results: list[CheckResult], stage: str) -> bool:
    print(f"\n--- Data quality: {stage} ---")
    for r in results:
        print(r)
    all_passed = all(r.passed for r in results)
    print(f"{stage}: {'ALL CHECKS PASSED' if all_passed else 'CHECKS FAILED'}")
    return all_passed
