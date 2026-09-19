# 1. The big picture

## The problem

Someone writes code. That code has to run somewhere, for real users, without
falling over. Those are two different jobs:

- **Development:** write the software.
- **Operations:** keep it running.

For a long time these were separate teams. Developers threw code over the wall,
operations caught it, and when something broke each side blamed the other.

## DevOps

**DevOps** is the idea of one team owning both, and automating the path from
"I wrote code" to "users are running it". Less waiting, fewer surprises.

## SRE

**SRE** (Site Reliability Engineering) started at Google. The idea: treat
reliability as an engineering problem with numbers, not a feeling. Instead of
"the site should be pretty reliable", you say "99.5% of requests must succeed",
then measure it. Chapter 4 covers this.

A short way to hold it: **DevOps is the automated path. SRE is keeping the
result reliable and proving it with numbers.** The job you are looking at
(Analyst, SRE/DevOps) mixes both.

## A restaurant, to make it stick

| Restaurant | This world | Chapter |
|---|---|---|
| A recipe | Source code | |
| Tasting every dish before it leaves the kitchen | Automated tests and checks (CI) | 3 |
| A sealed meal kit that tastes the same anywhere | A container | 2 |
| Delivering it to the customer | Deployment (CD) | 3 |
| A manager keeping enough staff on shift | Kubernetes | 6 |
| Watching queue times and complaints | Monitoring | 4 |
| A written plan for "the fryer caught fire" | Runbooks and postmortems | 5 |
| Who has the key to the cash register | Access control (IAM, RBAC) | 7 |

## The journey of one change

Say you fix a typo in the dashboard. Here is what happens to it in a
well-run setup, and where it lives in this repo:

1. You **push** the change to GitHub.
2. **CI** wakes up on its own and runs checks: lint, tests.
   ([`.github/workflows/ci.yml`](../../.github/workflows/ci.yml))
3. CI **builds a container image** of the app and starts it to prove it works.
   ([`Dockerfile`](../../Dockerfile))
4. If everything is green, the change is safe to **deploy**. A deploy puts the
   new image in front of users, often a few copies at a time.
   ([`k8s/deployment.yaml`](../../k8s/deployment.yaml))
5. Once running, it is **monitored**: is it up, how fast is it, how many
   requests fail? ([`reliability/`](../../reliability/))
6. If it breaks, a **runbook** tells whoever is on call what to do, and a
   **postmortem** records how to stop it happening again.
   ([`docs/runbooks/`](../runbooks/))

Every chapter after this one is one step of that journey.

## Try it

Look at the journey in real life. Open the **Actions** tab of the repo on
GitHub, click the latest run of "CI", and find the three jobs: `lint`, `test`,
`container`. That is step 2 and 3 happening automatically. You did not click
anything to start it.

## Check yourself

- In one sentence, what is the difference between development and operations?
- What does SRE add that plain DevOps does not emphasize?
- Which step of the journey is the "tasting every dish" step?
