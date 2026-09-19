"""Policy checks on the illustrative Kubernetes manifests in k8s/.

There is no cluster in CI, so these assert the properties a reviewer would
otherwise check by eye before approving a deploy: probes exist, resources are
bounded, and the container is not privileged.
"""

from pathlib import Path

import yaml

K8S_DIR = Path(__file__).resolve().parent.parent / "k8s"


def _load(name):
    return yaml.safe_load((K8S_DIR / name).read_text(encoding="utf-8"))


def _container():
    return _load("deployment.yaml")["spec"]["template"]["spec"]["containers"][0]


def test_all_manifests_are_valid_yaml_with_kind_and_name():
    for path in K8S_DIR.glob("*.yaml"):
        doc = yaml.safe_load(path.read_text(encoding="utf-8"))
        assert doc["kind"] and doc["metadata"]["name"], path.name


def test_container_has_readiness_and_liveness_probes():
    c = _container()
    assert "readinessProbe" in c and "livenessProbe" in c


def test_container_resources_are_bounded():
    resources = _container()["resources"]
    assert "cpu" in resources["limits"] and "memory" in resources["limits"]
    assert "cpu" in resources["requests"] and "memory" in resources["requests"]


def test_container_is_not_privileged():
    deployment = _load("deployment.yaml")["spec"]["template"]["spec"]
    assert deployment["securityContext"]["runAsNonRoot"] is True
    sc = _container()["securityContext"]
    assert sc["allowPrivilegeEscalation"] is False
    assert sc["readOnlyRootFilesystem"] is True
    assert sc["capabilities"]["drop"] == ["ALL"]


def test_rolling_update_never_drops_below_desired_replicas():
    strategy = _load("deployment.yaml")["spec"]["strategy"]["rollingUpdate"]
    assert strategy["maxUnavailable"] == 0


def test_service_targets_the_container_port():
    assert _load("service.yaml")["spec"]["ports"][0]["targetPort"] == _container()["ports"][0]["containerPort"]


def test_secrets_are_referenced_never_inlined():
    env = {e["name"]: e for e in _container()["env"]}
    assert "secretKeyRef" in env["DATABASE_URL"]["valueFrom"]
