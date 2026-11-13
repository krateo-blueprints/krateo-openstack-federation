---
type: Usage
title: krateo-openstack-federation — usage
description: Prerequisites, install, what Keystone's Apache (mod_auth_openidc) config must provide for the mapping, and how to verify the federation and a tenant user's project.
resource: oci://ghcr.io/krateo-blueprints/charts/krateo-openstack-federation
tags: [usage, keystone, mod_auth_openidc]
timestamp: 2026-11-12T00:00:00Z
---

# Usage

## Prerequisites

- openstack-keystone-operator-kog >= 0.4.0 (domains by name), with its RestDefinitions Ready, in the
  namespace you install this chart into.
- Kyverno >= 1.19 (`policies.kyverno.io/v1` GeneratingPolicy).
- Tenant Namespaces labelled `krateo.io/tenant=true` and `krateo.io/tenant-user=<username>` (the
  platform creates one at each user's first sign-in).
- Keystone with OpenID Connect enabled (mod_auth_openidc in front of keystone-api), the Keycloak realm
  as its provider, and `[openid] remote_id_attribute` set (e.g. `HTTP_OIDC_ISS`).
- A Keycloak realm whose tokens carry `sub`, `preferred_username` and a `groups` claim with bare group
  names (the krateo-keycloak-realm chart's portal client does).

## Install

```console
$ helm install federation oci://ghcr.io/krateo-blueprints/charts/krateo-openstack-federation \
    --version X.Y.Z -n openstack \
    --set identityProvider.issuer=https://keycloak.example.com/realms/krateo
```

`identityProvider.issuer` must be the realm's issuer exactly as Keycloak writes it into tokens, port
included when there is one. Keystone compares it with the remote id mod_auth_openidc reports.

## Keystone's Apache config

The mapping reads three claims under the names in `mapping.remote`: by default mod_auth_openidc's
environment variables `OIDC-sub`, `OIDC-preferred_username` and `OIDC-groups` (`OIDCClaimPrefix
"OIDC-"`, the claim's case kept). Use the environment form, not the header form `HTTP_OIDC_*`:

- Apache drops request headers whose name contains `_`, so `HTTP_OIDC_PREFERRED_USERNAME` never
  reaches Keystone; with the header form the mapping matched nothing and every login was refused
  ("Could not map any federated user properties", measured on the S2 verification).
- Environment variables are set by mod_auth_openidc itself; a client cannot supply them.
- **`OIDCClaimDelimiter ";"` is required.** Keystone splits a multi-valued assertion on `;` only.
  With mod_auth_openidc's default `,`, a user in two groups arrives as one value
  (`tenants,platform-admins`), the mapping's `tenants` condition does not match, and the user is
  refused.

## Verify

- The four one-per-cloud resources report `Ready=True`; in Keystone the `keycloak` IdP's `domain_id` is
  the `keycloak` domain's id.
- For a tenant user `alice`: `IdentityProject tenant-alice`, `IdentityGroup tenant-alice-members` and
  their role assignment exist and are Ready, and Keystone answers 204 to
  `HEAD /v3/projects/<project>/groups/<group>/roles/<member>`.
- Signing in through Horizon's Keycloak choice: the user lands in the `keycloak` domain and can switch
  to `tenant-alice`.
