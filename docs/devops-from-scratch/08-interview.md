# 8. Interview cheat sheet

You are new to this, and that is fine for an entry-level role that says "0 to 2
years, including internships". Interviewers for these roles are checking three
things: do you understand the basics, are you honest about what you have done,
and will you learn fast. Pretending to have production experience fails the
second one and gets caught by the first follow-up question.

Practise these out loud. Change the words until they sound like you.

**Only say what is true for you.** Some lines below assume you have done the
"Try it" exercises in the chapters, or that you are studying for AZ-900. If you
have not yet, do them first, or change the line. An honest "I've read it but
haven't run it" beats a claim you cannot back up.

## Where you honestly stand

Match of the job posting to this project. Be precise about the last column, it
is your script for being honest.

| Job posting asks for | Where in this repo | Honest level |
|---|---|---|
| CI/CD with GitHub Actions | [`ci.yml`](../../.github/workflows/ci.yml) | Built, running, green on every push |
| Azure DevOps or Jenkins | Nowhere | Not used. Same concept, different file format |
| Docker containers | [`Dockerfile`](../../Dockerfile), [`docker-compose.yml`](../../docker-compose.yml) | Image builds and the app starts healthy in CI |
| Kubernetes concepts (AKS/EKS) | [`k8s/`](../../k8s/) | Manifests written and policy-tested. Never run on a cluster |
| Monitor availability and performance, SLIs | [`reliability/sli.py`](../../reliability/sli.py) | Built and tested, on sample data, not live traffic |
| Azure Monitor, CloudWatch | Nowhere | Not used. Understand what they do |
| Incident handling, troubleshooting | [`docs/runbooks/`](../runbooks/) | Runbooks and one postmortem of a real near miss. No on-call experience |
| Azure or AWS resources | [`infra/`](../../infra/) | Terraform written, never applied. No live cloud account used |
| IAM and RBAC | [`security-rbac.md`](../security-rbac.md), [`readonly_role.sql`](../../infra/rbac/readonly_role.sql) | Application guard built and tested. Database role and cloud IAM written, not applied |
| Git | The whole repo | Yes |
| Python scripting | The whole repo | Yes |
| Bash or PowerShell | Commands in CI and the docs | Basic. Not scripts of my own |
| Agile ceremonies | Not from this project | Say so, and mention a place you did use them if you did |
| AZ-900 | Nowhere | Not taken yet. Studying for it |

## The answers

### "Tell me about your DevOps experience."

"I'm early in it. I built a data analysis project and then added a
reliability layer to it so I could learn the practice properly: a Docker
container, a GitHub Actions pipeline that lints, tests and builds the image,
and query logging with SLIs and SLOs. I've written up Kubernetes and Terraform
too, but I haven't run those against a real cluster or account, and I'll say
that plainly. I learn fastest by building and breaking things, so I also
wrote a from-scratch guide for myself with exercises."

### "Explain CI/CD. Walk me through your pipeline."

"CI means every push is checked automatically, so problems show up in minutes.
Mine has three jobs. Lint catches code mistakes. Test runs 48 tests on a
freshly built database. The third builds the Docker image, runs a health check
inside it, then starts the app and waits for it to report healthy. That last
job only runs if the first two pass. CD is the next step, delivering a passing
build to an environment. Mine stops at proving the image starts, I haven't
wired a real deployment."

### "What's a container and why use one?"

"It packages the app with everything it needs, so it runs the same on my
laptop, in the pipeline, and on a server. I hit the reason for real: my
dashboard depended on a generated database file that only existed on my
machine, so a fresh deploy would have crashed. I caught it before deploying,
fixed it, and the container build now proves it works from a clean checkout."

### "Explain SLI, SLO and error budget."

"An SLI is a measurement, like the share of queries that succeed. An SLO is the
target for it, mine is 99.5%. The error budget is the failure that target
allows, so 1 in 200. If the budget is gone, you stop shipping features and fix
reliability. I also measure p95 latency and not the average, because an average
hides the slow requests that users actually feel. I have a test showing a case
where the average looks fine and p95 breaches."

### "The dashboard is down. What do you do?"

"First check whether it's the app or the data. The app has a liveness endpoint,
and I have a health check that tests the database, the tables and data
freshness, so I can tell which layer is broken. Then I look at the logs and
follow the runbook for that failure. Mitigate first, then fix the root cause,
then verify with the same check that caught it. After anything serious I'd
write a blameless postmortem."

### "Readiness probe versus liveness probe?"

"Readiness asks whether the pod should receive traffic. Failing it just takes
the pod out of the Service. Liveness asks whether the container is stuck.
Failing it restarts the container. Getting them confused can cause restart
loops for apps that start slowly."

### "Have you used Kubernetes or Azure in production?"

"No. I've written Kubernetes manifests and tested them with policy checks, and
I understand deployments, services, probes, resource limits and autoscaling.
I've read Terraform for AWS, Azure and GCP. I haven't run either against real
infrastructure yet, and I'd be learning that on the job with guidance, which
is what I understand this role to be."

### "What is least privilege?"

"Every person and program gets only the access it needs. In my project the
dashboard connects with a read-only database role, so even a bug can't delete
data. There's also a guard in the code that blocks writes and logs the attempt,
so a spike in blocked queries would be visible. Two layers, because any one
layer can have a bug."

### "Tell me about something that went wrong."

"Before deploying my dashboard I realised the data and model files were
gitignored, so a fresh clone wouldn't have them and the app would crash on the
first page load. I tested it by deleting them locally, added code to rebuild
them, then made the pipeline build from a clean checkout so it can't come back
unnoticed. I wrote it up as a blameless postmortem, focused on what in the
process allowed it."

### "What would you learn next?"

"Azure fundamentals first, since the role is Azure-leaning, and I'm working
toward AZ-900. Then running my Kubernetes manifests on a real cluster and
setting up real alerts in a cloud monitoring tool, since those are the two
things my project only covers on paper."

## Things not to say

- Do not say you "ran Kubernetes in production" or "managed cloud
  infrastructure". You have not.
- Do not claim on-call experience. You have read runbooks, not been paged.
- Do not say your uptime was 99.5%. That is a target, measured on sample data.
- If you do not know something, say "I haven't used that, here's how I'd
  approach it". That is a strong answer for this level.

## Resume wording

Keep resume bullets to what is true. Something like: "Containerised a Streamlit
analytics app with Docker and built a GitHub Actions pipeline (lint, 48 tests,
image build, health check); defined SLIs and SLOs from query logs and wrote
runbooks and a postmortem." Do not write "deployed to Kubernetes" or "managed
cloud infrastructure".
