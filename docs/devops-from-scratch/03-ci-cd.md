# 3. CI/CD

## The problem

If checking the code is a person's job, it gets skipped when they are busy or
tired. Bugs slip through. Deploys become scary events.

## The idea

- **CI, Continuous Integration:** every time someone pushes a change, a
  machine automatically checks it (style, tests, does it build). If a check
  fails, you find out in minutes, not weeks.
- **CD, Continuous Delivery or Deployment:** getting a passing change to users
  automatically, or with one click.

A **pipeline** is the list of automated steps. It runs on a fresh computer
each time, so it cannot secretly depend on something only on your laptop. That
is exactly what would have caught the fresh-deploy bug.

## GitHub Actions

GitHub can run pipelines for free on its own computers. The pipeline is a text
file in [`.github/workflows/`](../../.github/workflows/). Here are the words in
[`ci.yml`](../../.github/workflows/ci.yml):

| Word | Meaning |
|---|---|
| `on: push` | When to start. Here: whenever someone pushes to `main`, or opens a pull request |
| `jobs` | Groups of steps. This file has three: `lint`, `test`, `container` |
| `runs-on: ubuntu-latest` | Which kind of fresh computer to use |
| `steps` | The actual commands, one after another |
| `uses: actions/checkout@v4` | A ready-made step: download the repo onto that computer |
| `run:` | A command to run, exactly like in your terminal |
| `needs: [lint, test]` | This job waits, and only runs if those two passed |

### The three jobs

1. **lint** (`ruff check .`): a robot proofreader for code. It catches real
   mistakes like an unused import or an undefined name.
2. **test** (`pytest`): runs all 48 tests against a freshly built warehouse.
3. **container:** builds the Docker image, runs the health check inside it,
   then starts the dashboard and waits until it answers `/_stcore/health`.
   It uses `needs`, so it only runs once lint and test are green. Why waste
   three minutes building an image of broken code?

### Pass and fail

A command reports success by an **exit code**: `0` means fine, anything else
means failure. A pipeline step that exits non-zero turns the whole run red.
This is why the health check and the SLO report are built to exit `1` when
something is wrong. It is how a machine "reads" them.

## Environments: Dev, Test, Prod

Real teams do not deploy straight to users. They promote the **same image**
through stages:

1. **Dev:** where developers try things, breakage is fine.
2. **Test (or staging):** a copy of production for final checks.
3. **Prod:** real users.

Same image, different settings (like which database). You never rebuild between
stages, because then what you tested is not what you shipped. This project does
not deploy anywhere real, so it stops at "build and prove it starts". Know the
idea anyway, it is a standard interview topic.

## Other tools, same idea

The job posting names Azure DevOps and Jenkins. They do the same thing as
GitHub Actions with different file formats: a file that says "on this trigger,
run these steps in this order on a fresh machine". If you understand this
chapter you understand the concept. Only GitHub Actions is used in this repo.

## Try it

**See it pass.** Open the Actions tab on GitHub, click the latest CI run, click
the `container` job, and expand its steps to read the output.

**Make it fail on purpose, then fix it.**

```bash
git checkout -b ci-experiment
echo "import glob" >> reliability/sli.py      # an unused import
ruff check .                                   # fails locally (E402 and F401), the same as CI would
git add -A && git commit -m "Break lint on purpose"
git push -u origin ci-experiment
```

This workflow only starts on a push to `main` or on a pull request, so open a
pull request for `ci-experiment` on GitHub. The `lint` job turns red, the
`test` job still runs (it does not depend on lint), and `container` is skipped
because it `needs` lint. That skipping is the `needs:` line doing its job.

Then remove the line, commit, push, and watch the pull request go green. Close
the pull request and delete the branch afterwards, never merge it. You have
now seen the whole feedback loop.

## Check yourself

- What does CI catch that a person skimming code might miss?
- What does `needs:` do, and why use it?
- What does exit code `0` mean, and why do pipelines care?
- Why promote one image through Dev, Test, Prod instead of rebuilding?
