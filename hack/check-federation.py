#!/usr/bin/env python3
"""CI gate for the chart's invariants, on rendered output.

- The issuer is required and must be https (Keystone trusts that issuer's claims).
- One-per-cloud resources default to krateo.io/deletion-policy: orphan (an uninstall must never cut
  every federated user off); Configurations and the token Secret carry helm.sh/resource-policy: keep.
- The mapping maps sub -> user id, the username -> user name and the tenant group, gated on the required
  Keycloak group; the group name it builds equals the one the policy generates.
- The GeneratingPolicy synchronizes, triggers only on Namespaces labelled krateo.io/tenant=true with a
  valid krateo.io/tenant-user, takes the user from that label, and generates a project, group and grant whose names line up, with tenants.deletionPolicy.
- Kyverno's background controller gets exactly the three generated kinds.
SELF-TEST: a render with deletionPolicy=delete must fail the orphan check.
"""
import shutil, subprocess, sys, tempfile
from pathlib import Path
import yaml

CHART = Path("helm/krateo-openstack-federation")
ISSUER = ["--set", "identityProvider.issuer=https://kc.example/realms/krateo"]


def render(extra=(), expect_fail=False):
    work = Path(tempfile.mkdtemp(prefix="fed-"))
    try:
        dst = work / "c"
        shutil.copytree(CHART, dst)
        cy = dst / "Chart.yaml"
        cy.write_text(cy.read_text().replace("CHART_VERSION", "0.0.0-ci"))
        p = subprocess.run(["helm", "template", "r", str(dst), "-n", "openstack", *extra], capture_output=True, text=True)
        if expect_fail:
            return p.returncode != 0, p.stderr
        if p.returncode != 0:
            sys.exit(f"::error::render failed: {p.stderr.strip()[:400]}")
        return [d for d in yaml.safe_load_all(p.stdout) if d]
    finally:
        shutil.rmtree(work, ignore_errors=True)


def orphan_errors(docs):
    once = [d for d in docs if d["kind"] in ("IdentityDomain", "IdentityFederationProvider", "IdentityMapping", "IdentityFederationProtocol")]
    errs = [] if len(once) == 4 else [f"expected 4 one-per-cloud resources, rendered {len(once)}"]
    return errs + [f"{d['kind']}/{d['metadata']['name']}: deletion-policy is not orphan"
                   for d in once if d["metadata"].get("annotations", {}).get("krateo.io/deletion-policy") != "orphan"]


errors = []
failed, err = render(expect_fail=True)
if not failed or "issuer is required" not in err:
    errors.append("a render without identityProvider.issuer must fail")
failed, err = render(["--set", "identityProvider.issuer=http://kc.example/realms/krateo"], expect_fail=True)
if not failed or "https" not in err:
    errors.append("a render with an http issuer must fail")

if not orphan_errors(render(ISSUER + ["--set", "deletionPolicy=delete"])):
    sys.exit("::error::self-test: deletionPolicy=delete passed the orphan check; the gate is broken")

docs = render(ISSUER)
errors += orphan_errors(docs)
by = lambda k: [d for d in docs if d["kind"] == k]
for d in by("Secret") + [d for d in docs if d["kind"].endswith("Configuration")]:
    if d["metadata"].get("annotations", {}).get("helm.sh/resource-policy") != "keep":
        errors.append(f"{d['kind']}/{d['metadata']['name']}: not helm.sh/resource-policy: keep")
if len([d for d in docs if d["kind"].endswith("Configuration")]) != 7:
    errors.append("expected 7 Configurations (4 one-per-cloud kinds + 3 tenant kinds)")

idp = by("IdentityFederationProvider")[0]["spec"]["identity_provider"]
if idp.get("domain") != "keycloak" or idp.get("remote_ids") != ["https://kc.example/realms/krateo"]:
    errors.append(f"identity provider: domain/remote_ids wrong: {idp}")

rule = by("IdentityMapping")[0]["spec"]["mapping"]["rules"][0]
local = {list(x)[0]: x[list(x)[0]] for x in rule["local"]}
remote = rule["remote"]
if local["user"].get("id") != "{0}" or local["user"].get("name") != "{1}":
    errors.append(f"mapping user must be id={{0}} (sub), name={{1}} (username): {local['user']}")
if local["group"].get("name") != "tenant-{1}-members":
    errors.append(f"mapping group name must be tenant-{{1}}-members: {local['group']}")
if len(remote) != 3 or remote[2].get("any_one_of") != ["tenants"]:
    errors.append(f"mapping remote must be sub, username, groups gated on [tenants]: {remote}")
# mod_auth_openidc's environment form: Apache drops request headers whose name contains "_", so the
# header form HTTP_OIDC_PREFERRED_USERNAME never exists (measured on S2: every login refused).
if [r.get("type") for r in remote] != ["OIDC-sub", "OIDC-preferred_username", "OIDC-groups"]:
    errors.append(f"mapping remote types must default to the environment form OIDC-<claim>: {[r.get('type') for r in remote]}")

gp = by("GeneratingPolicy")[0]["spec"]
if not gp["evaluation"]["synchronize"]["enabled"] or not gp["evaluation"]["generateExisting"]["enabled"]:
    errors.append("policy must synchronize and generateExisting")
rr = gp["matchConstraints"]["resourceRules"][0]
if rr["resources"] != ["namespaces"] or gp["matchConstraints"]["objectSelector"]["matchLabels"] != {"krateo.io/tenant": "true"}:
    errors.append(f"policy must trigger on Namespaces labelled krateo.io/tenant=true: {gp['matchConstraints']}")
cond = gp["matchConditions"][0]["expression"]
if '"krateo.io/tenant-user" in object.metadata.labels' not in cond or ".matches(" not in cond:
    errors.append(f"policy must require a valid krateo.io/tenant-user label: {cond}")
user = [v for v in gp["variables"] if v["name"] == "user"][0]["expression"]
if user.strip() != 'object.metadata.labels["krateo.io/tenant-user"]':
    errors.append(f"user must come from the krateo.io/tenant-user label: {user}")
gen = list(yaml.safe_load_all(gp["generate"][0]["template"]["value"]))
kinds = [g["kind"] for g in gen]
if kinds != ["IdentityProject", "IdentityGroup", "IdentityGroupRoleAssignment"]:
    errors.append(f"policy must generate project, group, grant: {kinds}")
else:
    grant = gen[2]["spec"]
    if grant["project"] != gen[0]["spec"]["project"]["name"] or grant["group"] != gen[1]["spec"]["name"]:
        errors.append("the grant must name the generated project and group")
    for g in gen:
        if g["metadata"]["annotations"].get("krateo.io/deletion-policy") != "delete":
            errors.append(f"generated {g['kind']}: deletion-policy must follow tenants.deletionPolicy (delete)")

cr = by("ClusterRole")[0]
if cr["metadata"]["labels"].get("rbac.kyverno.io/aggregate-to-background-controller") != "true":
    errors.append("ClusterRole must aggregate to Kyverno's background controller")
if sorted(cr["rules"][0]["resources"]) != ["identitygrouproleassignments", "identitygroups", "identityprojects"] or len(cr["rules"]) != 1:
    errors.append(f"ClusterRole must grant exactly the 3 generated kinds: {cr['rules']}")

for e in errors:
    print(f"::error::{e}")
if errors:
    sys.exit(1)
print("Checked issuer validation, deletion policies, keep, the mapping, the tenant policy and Kyverno RBAC.")
