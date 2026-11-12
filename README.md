# krateo-openstack-federation

## What is this

A Helm chart that federates OpenStack Keystone with a Krateo Keycloak realm over OpenID Connect, and
gives every Krateo tenant user their own Keystone project. Everything is declared as
[openstack-keystone-operator-kog](https://github.com/krateo-blueprints/openstack-keystone-operator-kog)
custom resources: a `keycloak` domain, the identity provider, the `openid` protocol and its mapping,
plus a Kyverno GeneratingPolicy that creates a project, group and `member` grant for each user when
their Krateo tenant Namespace appears, and removes them when it goes.

## Install

```console
$ helm install federation oci://ghcr.io/krateo-blueprints/charts/krateo-openstack-federation \
    --version X.Y.Z -n openstack \
    --set identityProvider.issuer=https://keycloak.example.com/realms/krateo
```

Requires openstack-keystone-operator-kog >= 0.4.0 in the same namespace and Kyverno >= 1.19. Keystone's
mod_auth_openidc must set `OIDCClaimDelimiter ";"`: see [docs/usage.md](docs/usage.md).

## Configure

The values are in [docs/configuration.md](docs/configuration.md). The only required one is
`identityProvider.issuer`.

## Examples

- [examples/s2](examples/s2/README.md): in-cluster Keycloak over private-CA HTTPS.

## Docs

- [docs/index.md](docs/index.md): the doc map.
- [docs/llms.txt](docs/llms.txt): the LLM doc index.

## Develop & release

CI ([`lint.yaml`](.github/workflows/lint.yaml)) runs on every PR and push to `main`: the chart gates
(`hack/check-schema-required.py`, `hack/check-federation.py`), helm lint and template, and the shared
docs linter. A SemVer tag on a `main` commit whose lint passed publishes the chart to
`oci://ghcr.io/krateo-blueprints/charts/krateo-openstack-federation` and the Marketplace blueprints
index; see [docs/release.md](docs/release.md).
