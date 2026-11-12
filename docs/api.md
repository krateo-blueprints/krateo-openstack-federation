---
type: API
title: krateo-openstack-federation — api
description: The custom resources the chart renders (domain, identity provider, mapping, protocol and their Configurations) and generates per tenant user (project, group, grant), with the annotations each carries.
resource: oci://ghcr.io/krateo-blueprints/charts/krateo-openstack-federation
tags: [api, crd, kyverno]
timestamp: 2026-11-12T00:00:00Z
---

# API

Rendered once, in the release namespace (the KOG's):

| kind | name | annotations |
|---|---|---|
| `Secret` | `keystone-token` | `helm.sh/resource-policy: keep` |
| `<Kind>Configuration` (7) | `keystone-config` | `helm.sh/resource-policy: keep`: the resources' finalizers call Keystone through it |
| `IdentityDomain` | `keycloak` | `krateo.io/deletion-policy: <deletionPolicy>` |
| `IdentityFederationProvider` | `keycloak` | same |
| `IdentityMapping` | `keycloak-mapping` | same |
| `IdentityFederationProtocol` | `keycloak-openid` | same |
| `GeneratingPolicy` (policies.kyverno.io/v1) | `<release>-tenants` | |
| `ClusterRole` | `<release>-kyverno-tenants` | label `rbac.kyverno.io/aggregate-to-background-controller: "true"` |

Generated per tenant user by the policy, in the release namespace:

| kind | name | annotations |
|---|---|---|
| `IdentityProject` | `tenant-<username>` | `krateo.io/deletion-policy: <tenants.deletionPolicy>` |
| `IdentityGroup` | `tenant-<username>-members` | same |
| `IdentityGroupRoleAssignment` | `tenant-<username>-members-<role>` | same |

The ClusterRole lets Kyverno's background controller get, list, watch, create, update, patch and
delete those three kinds, and nothing else.
