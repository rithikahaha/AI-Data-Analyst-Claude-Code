# Explaining and defending this project

A cheat sheet for talking about this project out loud, in the same format as
a good interview-prep guide: what they're really asking, and a script built
only from things that actually happened in this repo. Check the git history
if you want to re-verify any of it before an interview.

Read this once before any interview where this project might come up.
Practice the answers out loud, not just in your head.

## 1. "Walk me through this project in 30 seconds."

**What they're really asking:** Can you explain your own work simply, or do
you hide behind jargon?

**Your answer:**
"It's an AI analyst built on Claude Code. Instead of me running SQL queries
and building dashboards by hand, I built a small team of AI agents (one for
SQL, one for statistics and machine learning, one for data pipelines, one for
dashboards) that route a plain-English business question to whichever one
actually owns it, and answer with real numbers and honest caveats. I built the
whole system: the agents, the data pipeline, the model, the dashboard, and the
tests."

Keep it to those 3-4 sentences. If they want more, they'll ask.

## 1b. "Walk me through the actual steps it takes to answer a question."

**What they're really asking:** Did you just wire up a chatbot, or do you
actually understand the analyst workflow you're automating?

**Your answer:**
"I structured it around six phases: Ask, Prepare, Process, Analyze, Share, Act.
Ask means understanding the real business problem, not just the literal
question, and grounding any ambiguous term against a glossary instead of
guessing. Prepare means confirming the right data actually exists before
analyzing it. Process is data-quality checks, nulls, duplicate joins,
referential integrity, before trusting any number. Analyze is the SQL,
statistics, or ML. Share is the chart, when one actually helps. Act is closing
with the business implication, not just restating a stat. Each phase routes to
whichever agent owns it, that's literally how `analyst-lead` is written."

This is a strong answer specifically because it shows you didn't skip the
"boring" phases (Prepare, Process) that people forget when they're excited
about the AI part.

## 1c. "That's how you'd answer one question. What about the rest of the job?"

**What they're really asking:** Do you understand that being a data analyst
is more than running queries when someone asks, or do you think the job ends
at "here's your number."

**Your answer:**
"Answering one question well is maybe half of it. I also built the parts
around that: `pipelines/monitor.py` runs on a schedule and checks whether the
pipeline's quietly stalled or a metric has drifted, so a problem gets caught
before a stakeholder asks and gets a wrong answer from it. Before I'd let
anyone run an experiment, there's a feasibility check, required sample size
against actual signup volume, that already caught one experiment idea in this
project that would've taken over 500 weeks to reach significance on the
traffic available, which is a decision to redesign it, not run it and hope.
There's a changelog on the metrics glossary so a definition change is
traceable instead of silent, a triage method for when more questions come in
than I can answer at once, and a decision log that tracks whether a past
recommendation actually got acted on. None of that shows up in a single
query, but it's most of what the job actually is day to day."

## 2. "AI can write SQL and build dashboards. Why does this need you?"

**What they're really asking:** This is the defining 2026 question. Do you
understand what you bring that AI doesn't. A vague answer about "creativity"
fails this immediately.

**Your answer:**
"Honestly, AI wrote most of the code in this project: the SQL, the Python,
the dbt models. What it didn't do is decide what was worth building, or catch
it when it was wrong. Two concrete examples. The dashboard's charts initially
rendered in alphabetical order instead of the actual sequence they were
supposed to show. It looked fine until I actually opened it in a browser and
checked. And a churn comparison that looked like a real 35% difference came
back not statistically significant when I had it properly tested. The honest
answer was 'promising, not proven,' and I made sure that's what got reported,
not the exciting-sounding number. AI is fast at producing things that look
right. My job was making sure they actually were."

If they push for more: "I also rejected the first version of the agent
design. It had 11 narrow agents, one per skill, which isn't how a real team
is structured. I had it rebuilt around 7 roles that map to actual job
titles."

## 3. "How are you actually using AI in your work? Be specific."

**What they're really asking:** Are you AI-literate or just AI-aware.

**Your answer:**
"I used Claude Code to build this entire project. Not just to draft text, but
to write and run actual code: SQL, Python, dbt models, a Streamlit dashboard.
My job in that process was direction and verification. I decided the business
questions worth answering, I reviewed every piece of output before accepting
it, and I caught real mistakes: a chart rendering in the wrong order, an
agent architecture that didn't reflect how real teams are staffed. I didn't
just prompt and accept. I ran the tests, opened the dashboard in a browser,
and cross-checked the dbt output against the Python pipeline's numbers before
trusting either one."

## 4. "What would you automate, and what would you never automate?"

**What they're really asking:** Do you understand your own work well enough
to know which parts are mechanical.

**Your answer:**
"Using this exact project: I'd automate writing the first draft of any SQL
query, building a chart once the data's ready, and running a standard
significance test. All of that AI did well here. I would never automate
deciding whether a 'finding' is actually worth reporting. The integration and
churn comparison in this project looked like a strong pattern, but the honest
statistical read was 'not significant yet.' An automated pipeline reports the
percentage. A person decides whether that percentage means anything."

## 5. "Isn't 'not statistically significant' just a failed result?"

**What they're really asking:** Do you understand statistics, or do you just
run tests and report whatever comes out.

**Your answer:**
"No. It's the correct result, and reporting it honestly instead of burying it
is the point. In this project, accounts that adopted an integration churned
at 17.5%, versus 27.1% for accounts that didn't. That's a 35% relative
difference, tempting to present as a finding. But the group that didn't
adopt the integration was only 59 accounts, and a proper significance test
came back p=0.075, just above the standard 0.05 cutoff. So the honest answer
is 'worth testing with a real experiment, not proven yet.' Reporting a
number as confirmed when it isn't is how teams end up chasing patterns that
were just noise."

## 6. "This uses fake or synthetic data. Doesn't that make it less impressive?"

**What they're really asking:** Are you going to misrepresent this as real
business impact.

**Your answer, said plainly:**
"It's a generated sample dataset, and I say that upfront. This isn't a claim
about a real company's numbers. What it demonstrates isn't 'I found a $100k
insight,' it's 'I can build the system that would find it': the agents, the
pipeline, the tests, the model, the dashboard, all real and all running end
to end. For the roles I'm applying to, that's a more relevant claim than a
one-off analysis on a real dataset would be."

Never imply the numbers (75.6% WAU growth, 108.5% NRR, and so on) are real
business results. They're real outputs of a real, working system, on data
built to exercise it.

## 7. "How do you make sure this stays relevant as tools change?"

**What they're really asking:** Do you have a learning system, or just a
skillset that will expire.

**Your answer:**
"The specific tools here (Claude Code, dbt, Streamlit) might not be what I'm
using in two years. What doesn't expire is the underlying discipline: verify
before you trust, know what a statistical result actually means before you
report it, and understand the business question well enough to know if the
AI-generated answer is actually answering it. I added a dbt semantic layer to
this project specifically because I didn't have analytics-engineering
experience and wanted to build it deliberately rather than wait for a job to
require it."

## Numbers you can quote

All verified, re-checked before quoting.

- 34 tests passing (`pytest`), CI on every push
- 40/40 dbt checks passing, and its output matches the Python pipeline exactly
- Churn model AUC: **0.6675**, exactly reproducible (fixed random seeds in
  both the data generation and the model). If asked "does it change when you
  retrain," the honest answer is no, and that's deliberate. Reproducibility
  is worth more here than pretending each run is a fresh discovery.
- WAU: 234 to 411 over 26 weeks (up 75.6%)
- Net revenue retention: 108.5%
- Starter churn 28.8% versus Enterprise 6.7%
- Integration-adoption churn comparison: 17.5% versus 27.1%, p=0.075 (not significant)
- Onboarding funnel: 71.6% of signups complete onboarding, 61.9% of those activate
- A proposed onboarding-flow experiment would need ~580 weeks to reach a
  conclusive sample size on this account base's signup volume, the feasibility
  check that says "redesign this, don't run it," before any data is collected

If asked for a number not on this list, say "let me check the repo and get
back to you" rather than guessing. That's a stronger answer than a wrong
number said confidently.
