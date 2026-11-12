---
type: Example
title: krateo-openstack-federation — S2 example
description: Federation values for the OpenStack blueprint's S2 verification, with Keycloak in-cluster over private-CA HTTPS and the openstack realm.
resource: oci://ghcr.io/krateo-blueprints/charts/krateo-openstack-federation
tags: [example, s2]
timestamp: 2026-11-12T00:00:00Z
---

# S2

[values.yaml](values.yaml) sets the issuer of an in-cluster Keycloak (`keycloak-system`, port 8443,
realm `openstack`). Keystone's mod_auth_openidc must trust the private CA that signs Keycloak's
certificate, and its OIDC block must set `OIDCClaimDelimiter ";"` (see
[usage](../../docs/usage.md#keystones-apache-config)).

```console
$ helm install federation oci://ghcr.io/krateo-blueprints/charts/krateo-openstack-federation \
    --version X.Y.Z -n openstack -f examples/s2/values.yaml
```
