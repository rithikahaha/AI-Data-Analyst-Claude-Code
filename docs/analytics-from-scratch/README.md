# The analytics side, from scratch

The full explanation of what this project does, written so you can understand
it, run it, and defend it. It assumes you know a little Python and nothing
else. Every chapter uses real files from this repo and real numbers from the
sample data, so the ideas and the proof are in the same place.

The other half of the project (containers, pipelines, monitoring) has its own
guide: [DevOps and SRE from scratch](../devops-from-scratch/README.md).

## How to use this

For each chapter, in order:

1. **Read it.** Short on purpose.
2. **Run the "Try it" part.** Every command and number here was run against the
   real repo. If your output differs, something is different on your machine,
   and finding out why is part of learning.
3. **Say it out loud** in your own words, as if to a friend.

## The path

| # | Chapter | The question it answers | Time |
|---|---|---|---|
| 1 | [The big picture](01-the-big-picture.md) | What is this project, and what does an analyst actually do? | 30 min |
| 2 | [The data](02-the-data.md) | Where do the numbers come from, and how are they cleaned? | 1 to 2 hours |
| 3 | [SQL](03-sql.md) | How do I ask the database a question? | 2 hours |
| 4 | [Metrics](04-metrics.md) | What do "active user", "MRR" and "NRR" mean, exactly? | 1 to 2 hours |
| 5 | [Trends and funnels](05-trends-and-funnels.md) | Is it growing? Where do we lose people? | 1 hour |
| 6 | [Statistics](06-statistics.md) | Is that difference real, or just noise? | 2 hours |
| 7 | [Machine learning](07-machine-learning.md) | Can we predict which accounts will leave? | 2 hours |
| 8 | [The dashboard](08-the-dashboard.md) | How do I show this to someone who is not technical? | 1 hour |
| 9 | [dbt and tests](09-dbt-and-tests.md) | How do I know the numbers are right? | 1 to 2 hours |
| 10 | [The AI agents](10-the-agents.md) | What do the agents actually do, and what do I do? | 1 hour |
| 11 | [Limits and honesty](11-limits-and-honesty.md) | What is this project not, and how do I say so? | 30 min |
| | [Glossary](glossary.md) | What does this word mean? | look up as needed |

Chapters 3 to 7 are the heart of it. If you are short on time, do those.

## Before you start

```bash
pip install -r requirements.txt
python -m scripts.export_raw_sources
python -m pipelines.etl
python -m pytest -q
```

The commands are written for **Git Bash** (it comes with Git for Windows).
In PowerShell, lines like `NAME=value command` do not work. Chapter 2 explains
what those first three commands do.

## One thing to keep in mind

All the data is **made up**. A script generates a fake software company with
500 customers. That is deliberate and it is stated everywhere. What is real is
the method: the SQL, the statistics and the model are the same ones you would
use on real data. Chapter 11 covers how to say this honestly in an interview.
