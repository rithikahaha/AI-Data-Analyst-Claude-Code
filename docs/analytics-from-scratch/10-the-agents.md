# 10. The AI agents

## What an "agent" is here

Claude Code is an AI assistant you run in a terminal or app, inside a project
folder. It can read files, run commands and write code. You can also give it
**instructions** about how to behave in this project.

In this repo those instructions are plain text (Markdown) files, and that is
all the "agents" are:

| Where | What it is |
|---|---|
| [`CLAUDE.md`](../../CLAUDE.md) | The project guide. Claude Code reads it automatically. It states the ground rules. |
| [`.claude/agents/`](../../.claude/agents/) | One file per specialist agent: who it is, when to use it, how it works. |
| [`.claude/skills/`](../../.claude/skills/) | Reusable playbooks, like recipes for a funnel analysis. |

**No Python code starts or runs the agents.** Claude Code loads these files and
follows them. This matters, because it means the agents are only as good as
their instructions, and they can still be wrong. Which is why the project has
checks (chapter 9) and why a human reviews the output.

## The front matter

Open any file in `.claude/agents/`. It starts with a small header:

```
---
name: sql-engineer
description: Explores warehouse schema and writes correct, efficient, read-only SQL ...
tools: Read, Grep, Glob, Bash
---
```

`description` is the important line. It tells Claude Code **when to use this
agent**. `tools` limits what it may do. The rest of the file is the
instructions in plain English.

## The lead and the specialists

You only ever talk to one agent, [`analyst-lead`](../../.claude/agents/analyst-lead.md).
It works through the six phases from chapter 1 and hands each piece to the
specialist who owns it:

| Agent | Job | Chapters |
|---|---|---|
| `analyst-lead` | Understands the question, routes it, writes the final answer | 1 |
| `sql-engineer` | Finds the right tables, writes read-only SQL | 3 |
| `data-scientist` | Statistics, A/B tests, the churn model | 6, 7 |
| `data-visualizer` | Charts and the dashboard | 8 |
| `qa-reviewer` | Sanity-checks results before they are shared | 3, 9 |
| `ai-engineer` | Looks up metric definitions, checks the agents' quality | 4 |
| `data-platform-engineer` | Pipelines, data quality, deployment, reliability | 2, and the DevOps guide |

They are seven **specialties**, not seven job openings. One system covers the
range a modern analyst is expected to handle, and splitting it keeps each part
sharp instead of one instruction blob that is mediocre at everything.

## The QA agent is the one to admire

Read the "Per-query checklist" in
[`qa-reviewer.md`](../../.claude/agents/qa-reviewer.md). Every item is a
mistake from earlier chapters: wrong row counts, nulls, **join fan-out**, a
partial last period, and ambiguous definitions. The agent is told to check
these **before** an answer goes out and to never silently drop a problem it
finds. That is what makes the rest trustworthy.

## Skills: recipes for repeat work

Skills are shorter playbooks for jobs that come up again and again. Each has
when to use it, the steps, and the answer format:

| Skill | For |
|---|---|
| `schema-explorer` | Looking up table and column names before writing SQL |
| `funnel-analysis` | "Where are we losing people?" |
| `cohort-retention` | Following groups of customers over time |
| `growth-metrics-analysis` | Trends, growth rates, NRR |
| `anomaly-detection` | Spotting odd spikes and drops |
| `experiment-design` | Planning a test before running it |
| `executive-summary` | Writing the answer for a busy reader |
| `request-triage` | Ranking competing requests |
| `metric-governance` | Adding or changing a metric definition properly |

## Ground rules

The rules from `CLAUDE.md` that every agent follows, and where each comes from
in this guide:

1. **Read-only.** Never change the data. (Chapter 3.)
2. **Show the work.** Always give the SQL or test behind a number. (Chapter 3.)
3. **Sanity-check before answering.** (Chapters 3 and 5.)
4. **Cite the definition used.** (Chapter 4.)
5. **Statistical claims need a test, not a glance.** (Chapter 6.)

## What a run looks like

Question: *"Are we healthy overall, and which accounts need attention?"*

1. **Ask.** `analyst-lead` reads "healthy" as revenue health and "attention" as
   churn risk, and states that interpretation.
2. **Prepare.** `sql-engineer` finds the subscription and event tables.
3. **Process.** `qa-reviewer` checks counts and definitions.
4. **Analyze.** SQL for NRR (108.5%) and churn by plan (Starter 28.8%,
   Enterprise 6.7%). `data-scientist` tests the integration gap (p = 0.075)
   and scores accounts with the churn model.
5. **Share.** `data-visualizer` charts it if a chart helps.
6. **Act.** `analyst-lead` writes: healthy overall, risk concentrated in the
   cheapest plan, gap promising but not proven, call the top-scored accounts
   first.

The full write-up is example 3 in
[`examples/example_qna.md`](../../examples/example_qna.md).

## Where you fit

The AI can write SQL, run tests and draft charts fast. It cannot decide which
question is worth answering, notice that a result is too good to be true, or
tell a stakeholder "not proven yet". You do that. The README's table "What AI
automated versus what I decided" and the
[interview cheat sheet](../EXPLAIN_THIS_PROJECT.md) say the same thing with real
examples from this project.

## Try it

1. Read [`analyst-lead.md`](../../.claude/agents/analyst-lead.md) top to
   bottom. Find the six numbered phases and the "Output shape" section.
2. Read the `description:` line of every file in `.claude/agents/`. For each
   one, write a question you would ask that should trigger it.
3. Open this folder in Claude Code and ask the three questions from the
   README's Quickstart. Watch which parts you now recognize: the tables it
   checks, the SQL it shows, the caveats. **Verify one number yourself**: run
   the SQL it showed with `run_query` and confirm it matches. Checking is the
   whole job.
4. **Write a skill.** Create `.claude/skills/top-industries.md` following the
   shape of `funnel-analysis.md` (front matter, steps, answer format) for
   "which industries have the most accounts, and which churn most". Read it
   back. Would a stranger know exactly what to do? Delete it afterwards if
   you do not want to keep it.

## Check yourself

- What is an agent in this project, physically?
- Which line of an agent file decides when it gets used?
- Which agent checks for join fan-out, and when?
- Why can the agents still be wrong, and what stops a wrong answer getting out?
