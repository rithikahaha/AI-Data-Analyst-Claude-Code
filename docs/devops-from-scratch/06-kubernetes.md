# 6. Kubernetes

## The problem

One container on one computer is easy. Real services need more:

- Run **several copies** so one crash does not take everything down.
- **Restart** a copy automatically if it dies or hangs.
- **Update** to a new version without any downtime.
- **Add copies** when traffic spikes, remove them when it calms down.
- Spread all of this across **many computers**.

Doing that by hand is a full-time job. **Kubernetes** (often "K8s") does it for
you. You describe what you want, and it keeps reality matching.

## The core idea: desired state

You do not say "start a container". You say "I want 2 copies of this running,
always". Kubernetes keeps comparing what you asked for with what exists. A copy
dies, it notices the gap and starts another. That loop is the whole product.

Think of a manager who is told "always keep two cashiers on shift" and
simply makes it true, whoever calls in sick.

## The words

| Word | Plain meaning |
|---|---|
| **Cluster** | The group of computers Kubernetes controls |
| **Node** | One computer in the cluster |
| **Pod** | The smallest unit: one running container (sometimes a few that work together) |
| **Deployment** | "Keep N copies of this pod running, and update them safely" |
| **Service** | A stable address in front of the pods. Pods come and go, the Service address stays the same and shares traffic between them |
| **Probe** | A health question Kubernetes asks a container (see below) |
| **HPA** | Horizontal Pod Autoscaler: adds or removes pods based on load |
| **Secret** | A place for passwords and connection strings, kept out of your code |
| **Manifest** | A YAML file describing what you want |

**AKS and EKS** are just Kubernetes run for you by Azure and AWS, so you do not
manage the computers yourself. The job posting says "exposure preferred", which
means knowing these words and ideas is enough.

## Reading [`k8s/deployment.yaml`](../../k8s/deployment.yaml)

| Setting | What it means | Why |
|---|---|---|
| `replicas: 2` | Keep two copies running | One can die and the app stays up |
| `maxUnavailable: 0`, `maxSurge: 1` | During an update, start one new pod before removing an old one | No dip in capacity while deploying |
| `readinessProbe` | "Are you ready to receive traffic?" | Until it says yes, no user is sent to it |
| `livenessProbe` | "Are you still alive?" | If it fails 3 times, Kubernetes restarts the container |
| `resources.requests` | The minimum the pod needs | Used to decide which node it fits on |
| `resources.limits` | The most it may use | A runaway pod cannot starve its neighbours |
| `runAsNonRoot`, `capabilities: drop: ALL` | No admin powers | Least privilege |
| `readOnlyRootFilesystem: true` | The container cannot write to its own files | Malware cannot plant anything |
| `emptyDir` volumes | Small scratch folders that are writable | The few places the app really must write |
| `secretKeyRef` | Read the database URL from a Secret | No password in the file or the image |

### Readiness vs liveness, the classic interview question

They sound alike and do different jobs.

- **Readiness** asks "should I send you traffic?" A pod that is still starting
  up is alive but not ready. Failing readiness only removes it from the
  Service. It is not restarted.
- **Liveness** asks "are you stuck?" Failing liveness restarts the container.

Mixing them up causes real outages. Example: if the liveness check is too
strict, a slow-starting app gets restarted forever before it ever finishes
starting.

## The honest part

The manifests in `k8s/` have **never been run on a cluster**. What is tested is
[`tests/test_k8s_manifests.py`](../../tests/test_k8s_manifests.py), which reads the
YAML and checks that probes exist, limits are set, the container is not
privileged, and secrets are referenced and not written in. That is a
pre-flight checklist, not proof it runs. Say exactly that in an interview.

## Try it

**Step 1: read and check without a cluster.**

```bash
python -m pytest tests/test_k8s_manifests.py -v
```

Break it on purpose. Open `k8s/deployment.yaml`, delete the whole
`readinessProbe:` block, and re-run. The test
`test_container_has_readiness_and_liveness_probes` fails.
Undo with `git checkout k8s/deployment.yaml`.

**Step 2 (optional, you will learn the most here): run it for real.**

Docker Desktop can run a small one-node Kubernetes cluster on your laptop. In
Docker Desktop, open Settings, then Kubernetes, and enable it. Wait until it
shows running. Then:

```bash
docker build -t ai-data-analyst:local .
kubectl get nodes                          # one node, status Ready
kubectl apply -f k8s/deployment.yaml -f k8s/service.yaml
kubectl get pods                           # wait until READY shows 1/1, twice
kubectl describe pod <pod name>            # read the Events at the bottom
kubectl logs <pod name>
kubectl port-forward service/ai-data-analyst-dashboard 8501:80
```

Open `http://localhost:8501`. I have not run these steps against a live
cluster, so if something fails, that is a genuine learning moment: read the
`describe` output, the Events section usually names the cause. A likely
snag is that the cluster cannot find the locally built image.

Now watch the "desired state" loop:

```bash
kubectl delete pod <one pod name>          # kill a pod on purpose
kubectl get pods                           # a replacement appears within seconds
```

That is Kubernetes doing its job. Clean up with
`kubectl delete -f k8s/deployment.yaml -f k8s/service.yaml`.

The autoscaler file (`hpa.yaml`) needs a metrics server that Docker Desktop does
not include by default, so skip applying it locally. Reading it is enough.

## Check yourself

- What does "desired state" mean?
- Deployment vs Service: what does each one do?
- Readiness vs liveness: what happens on failure for each?
- Why `maxUnavailable: 0`?
- What have you actually verified about these manifests, and what not?
