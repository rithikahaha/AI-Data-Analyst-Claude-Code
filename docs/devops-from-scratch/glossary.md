# Glossary

Plain meanings. Sorted alphabetically.

| Word | Meaning |
|---|---|
| **Alert** | An automatic message when a number goes bad, so a person is told instead of having to look |
| **Alert fatigue** | People ignoring alerts because too many were noisy. Page only for real harm |
| **AKS** | Azure Kubernetes Service. Kubernetes run for you by Azure |
| **Auto-scaling** | Adding or removing copies or machines automatically as load changes |
| **AWS** | Amazon's cloud |
| **Azure** | Microsoft's cloud |
| **Blameless postmortem** | A written review of an incident that asks how the system allowed it, not whose fault it was |
| **CD** | Continuous Delivery or Deployment. Getting passing changes to users automatically or with one click |
| **CI** | Continuous Integration. Every change is checked automatically |
| **CloudWatch** | AWS's monitoring service |
| **Cluster** | The group of computers Kubernetes manages |
| **Container** | A sealed, running box holding an app and everything it needs |
| **Deployment (Kubernetes)** | "Keep N copies of this running and update them safely" |
| **Deploy** | Putting a new version in front of users |
| **DevOps** | One team owning both building and running software, with the path between them automated |
| **Docker** | The most common tool for building and running containers |
| **Dockerfile** | The recipe for building an image |
| **EKS** | Amazon Elastic Kubernetes Service. Kubernetes run for you by AWS |
| **Environment** | A place the app runs: Dev, Test or Prod |
| **Error budget** | How much failure the SLO allows. 99.5% target means 0.5% |
| **Exit code** | The number a command returns. 0 is success, anything else is failure |
| **Health check** | A test a machine can run to answer "is it working?" |
| **HPA** | Horizontal Pod Autoscaler. Kubernetes adding or removing pods based on load |
| **IAM** | Identity and Access Management. AWS's system for who may do what |
| **Image** | A saved blueprint of a container. Built once, run many times |
| **Incident** | Something is broken or about to be, and users are affected |
| **Infrastructure as code** | Writing your servers, networks and databases in files instead of clicking around |
| **kubectl** | The command line tool for talking to Kubernetes |
| **Kubernetes (K8s)** | A system that keeps the right number of containers running across many computers |
| **Latency** | How long something takes |
| **Least privilege** | Give every identity only the access it needs |
| **Linting** | An automatic proofreader for code |
| **Liveness probe** | Kubernetes asking "are you stuck?". Failing it restarts the container |
| **Logs** | A diary of what happened, one line per event |
| **Manifest** | A YAML file describing what you want Kubernetes to run |
| **Metric** | A number tracked over time |
| **Mitigate** | Reduce the harm quickly, before finding the root cause |
| **Namespace** | A folder inside a Kubernetes cluster that separates things |
| **Node** | One computer in a Kubernetes cluster |
| **p95** | The value 95% of requests were faster than. Shows the slow tail |
| **Pipeline** | The list of automated steps a change goes through |
| **Pod** | The smallest Kubernetes unit, usually one running container |
| **Port** | A numbered door a program listens on, like 8501 |
| **Prod** | Production. The real thing, with real users |
| **RBAC** | Role-Based Access Control. Permissions given through named roles. Azure uses this term |
| **Readiness probe** | Kubernetes asking "ready for traffic?". Failing it stops traffic, no restart |
| **Runbook** | Step-by-step instructions for handling one specific problem |
| **Secret** | A password or key kept out of code, in a vault or a Kubernetes Secret |
| **Service (Kubernetes)** | A stable address in front of pods that shares traffic between them |
| **SLI** | Service Level Indicator. A measurement, like success rate |
| **SLO** | Service Level Objective. The target for an SLI |
| **SRE** | Site Reliability Engineering. Reliability treated as engineering, with numbers |
| **Subnet** | A slice of a private network |
| **Terraform** | The most common infrastructure as code tool |
| **Triage** | Deciding how bad it is and what to do first |
| **VM** | Virtual machine. A rented computer you can log in to |
| **YAML** | A plain text format for configuration, used by Kubernetes and GitHub Actions |
