# Postmortem: dashboard would have crashed on a fresh deploy

**Date:** 2026-09-12
**Status:** resolved, no user impact (caught before the first hosted deploy)
**Severity:** would have been high, the whole dashboard down on first load
**Fix:** commit `e457a03`

Blameless format: this describes how the system allowed the problem, not who
caused it.

## Summary

The Streamlit dashboard read a SQLite database and a trained churn model from
disk. Both are generated files and are gitignored, so they exist on a
developer's machine but not in a fresh clone. A hosted deploy clones the repo,
so the dashboard would have started with no data and raised an error on the
first page load.

## Timeline

- The dashboard worked locally, every tab rendered, tests passed.
- Before deploying to Streamlit Community Cloud, I checked what a fresh clone
  contains rather than what my working directory contains.
- Found that `data/` and `ml/models/` are in `.gitignore`, so neither would be
  there.
- Added `ensure_sample_data()` to `dashboard/app.py`, which runs the export,
  ETL and model training if the files are missing.
- Verified by deleting `data/` and `ml/models/` locally and confirming the app
  rebuilt them and rendered every tab.

## Root cause

"Works on my machine." Local state (generated files) hid a missing dependency
on the deploy path. Tests and manual checks both ran in the working
directory, so neither could see the gap.

## What went well

- The gap was caught by reasoning about the deploy environment before any
  user hit it.
- The fix was verified the way the failure would actually occur (delete the
  files), not just by re-reading the code.

## What went badly, and what changed

| Problem | Action |
|---|---|
| Nothing in CI ran from a clean checkout with no generated files | The `container` job in CI now builds the image from the repo alone and starts it, so a missing file fails the build |
| First page load did slow one-off work (rebuilt the data and trained the model) | The Dockerfile bakes the data and model into the image, so containers start fast |
| No definition of "healthy" | Added `reliability/healthcheck.py` and the Streamlit liveness probe, used by Docker, Kubernetes and CI |

## Lessons

1. Test the deploy path, not just the code. A clean environment is the only
   honest test of what a deploy contains.
2. Anything gitignored is a dependency someone has to create. Either generate
   it at build time or fail loudly when it is missing.
