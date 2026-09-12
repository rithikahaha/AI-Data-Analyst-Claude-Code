"""Ensures the sample warehouse exists before any test needs it, regenerating
it via the real pipeline (not a shortcut) so tests exercise the same path
production data takes.
"""

import pytest

from connectors.warehouse import DEFAULT_SQLITE_PATH


@pytest.fixture(scope="session", autouse=True)
def sample_warehouse():
    if not DEFAULT_SQLITE_PATH.exists():
        from scripts import export_raw_sources
        from pipelines import etl

        export_raw_sources.main()
        etl.main()
    yield DEFAULT_SQLITE_PATH
