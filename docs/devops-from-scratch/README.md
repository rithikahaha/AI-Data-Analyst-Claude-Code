# DevOps and SRE from scratch

Written for someone who has never touched any of this. No jargon without an
explanation first. Every chapter uses a real file from this repo, so you learn
the idea and see it working in the same place.

The analytics half of the project has its own guide: [The analytics side, from scratch](../analytics-from-scratch/README.md).

## How to use this

For each chapter, do three things in order:

1. **Read it.** Short on purpose.
2. **Run the "Try it" part.** Reading is not learning, breaking things and
   fixing them is.
3. **Say it out loud** in your own words, as if to a friend. If you get stuck,
   re-read that part.

## The path

| # | Chapter | The question it answers | Time |
|---|---|---|---|
| 1 | [The big picture](01-the-big-picture.md) | What are DevOps and SRE, and how does one code change reach users? | 30 min |
| 2 | [Containers](02-containers.md) | How do I make it run the same everywhere? | 1 to 2 hours |
| 3 | [CI/CD](03-ci-cd.md) | How do checks and delivery happen automatically? | 1 to 2 hours |
| 4 | [Monitoring](04-monitoring.md) | How do I know it is healthy, with numbers? | 1 to 2 hours |
| 5 | [Incidents](05-incidents.md) | What do I do when it breaks? | 1 hour |
| 6 | [Kubernetes](06-kubernetes.md) | How do I run many containers reliably? | 2 hours |
| 7 | [Cloud and access](07-cloud-and-access.md) | Where does it run, and who is allowed to touch it? | 2 hours |
| 8 | [Interview cheat sheet](08-interview.md) | How do I talk about this honestly? | 1 hour |
| | [Glossary](glossary.md) | What does this word mean? | look up as needed |

Do them in order. Each one builds on the last.

## Before you start

You need Python and this repo already working:

```bash
pip install -r requirements.txt
python -m scripts.export_raw_sources
python -m pipelines.etl
python -m pytest -q
```

The commands in these chapters are written for **Git Bash**, which comes with
Git for Windows (right-click a folder, "Show more options", "Git Bash Here").
Plain PowerShell does not understand lines like `NAME=value command`. If you
must use PowerShell, set the variable first with `$env:NAME = "value"`, run the
command, then `Remove-Item Env:NAME`.

Chapters 2 and 6 use Docker Desktop. Install it, open it, and wait until it
says the engine is running. If it is not running, the `docker` commands fail
with a "cannot connect" error. That is not a bug in the project.

## An honest note on where you stand

You are new to this, and this guide and the project's DevOps layer were built
with AI while you learn. That is fine, and it is the same story as the rest of
this project. What makes it real is that you can run it, break it on purpose,
and explain it. The interview chapter shows how to say exactly that, and
which parts are built and tested versus only illustrative.
