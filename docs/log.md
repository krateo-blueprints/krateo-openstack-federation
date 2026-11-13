---
type: Log
title: krateo-openstack-federation — log
description: History of krateo-openstack-federation.
resource: oci://ghcr.io/krateo-blueprints/charts/krateo-openstack-federation
tags: [log]
timestamp: 2026-11-12T00:00:00Z
---

# Log

Curated history; release notes live in GitHub Releases.

## 2026-11-13 — 0.1.1: the mapping reads mod_auth_openidc's environment variables

`mapping.remote` now defaults to `OIDC-sub`, `OIDC-preferred_username` and `OIDC-groups`, the
environment form, instead of `HTTP_OIDC_*`. Measured on the OpenStack blueprint's S2 verification
(Keycloak 26.6.3, keystone-oidc 2026.1 with mod_auth_openidc 2.4.15): Apache drops request headers whose
name contains `_`, so `HTTP_OIDC_PREFERRED_USERNAME` was never set, the mapping's username remote
matched nothing, and every login failed with "Could not map any federated user properties". With
`OIDC-preferred_username` alone changed, the login mapped the user into the `keycloak` domain and its
tenant project. All three move to the environment form: it is set by mod_auth_openidc, cannot come
from a client header, and works for any claim name.

## 2026-11-12 — 0.1.0

First release. See [overview](overview.md). Measured on GKE (Keystone 2026.1 from the OpenStack
blueprint 0.3.47, openstack-keystone-operator-kog 0.4.0, oasgen-provider 0.60.0, Kyverno 1.19.2):

- The domain, identity provider (its `domain_id` resolved from the name `keycloak`), mapping and
  protocol reconcile Ready, and Keystone stores the mapping as rendered.
- Keystone's own mapping engine (`keystone-manage mapping_engine`) on the stored rules: a `tenants`
  member `alice` maps to user id = `sub`, name `alice`, group `tenant-alice-members`;
  `tenants;platform-admins` maps the same; `tenants,platform-admins` (mod_auth_openidc's default
  delimiter) and `platform-admins` alone are refused. Hence `OIDCClaimDelimiter ";"`.
- A tenant Namespace (`krateo.io/tenant=true`, `krateo.io/tenant-user=frank`) generates the project
  (in the `keycloak` domain), the group and the grant (Keystone answers 204). A Namespace that existed
  before the chart is covered by `generateExisting`; one with an invalid or missing username generates
  nothing; a label change on the Namespace changes nothing (same UIDs, same Keystone ids); deleting the
  Namespace removes the three resources and their Keystone objects within 6 s. Kyverno's background
  controller had no access to Secrets throughout.
- `useServerSideApply` is required: with a plain update, synchronize tries to revert the KOG
  controller's finalizer and annotations on the generated resources. With it, Kyverno and the
  controller share the objects; Kyverno logs a burst of `failed to revert downstream resource` errors
  in the seconds after a project is generated and none afterwards, and the finalizer stays.

An earlier design triggered on the user's clientconfig Secret. It needs Kyverno to read Secrets: the
background controller GETs the trigger (a forbidden GET is treated as "the trigger does not exist" and
the generation silently fails), and `generateExisting` lists Secrets cluster-wide. The Namespace
trigger needs neither.
