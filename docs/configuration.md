---
type: Configuration
title: krateo-openstack-federation — configuration
description: The values surface: deletion policies, the KOG Configuration, the federation domain, identity provider issuer, protocol, mapping claim names and the per-user tenant policy.
resource: oci://ghcr.io/krateo-blueprints/charts/krateo-openstack-federation
tags: [configuration]
timestamp: 2026-11-12T00:00:00Z
---

# Configuration

| value | default | meaning |
|---|---|---|
| `resourceGroup` | `identity.openstack.krateo.io` | the KOG's API group |
| `resourceVersion` | see values.yaml | the version the KOG serves its resource kinds at (each RestDefinition's API VERSION column) |
| `deletionPolicy` | `orphan` | for the domain, provider, mapping and protocol: `orphan` leaves the Keystone object on delete, `delete` removes it |
| `configuration.name` | `keystone-config` | name of the per-kind Configurations |
| `configuration.tokenSecret.{name,key}` | `keystone-token` / `token` | the bearer Secret; the chart creates it with a placeholder because the KOG's auth-bridge injects the real token |
| `domain.{name,description}` | `keycloak` | the federation domain |
| `identityProvider.id` | `keycloak` | Keystone's IdP id (in the WebSSO URL) |
| `identityProvider.issuer` | `""` | **required**, `https://`: the realm's issuer exactly as in tokens, e.g. `https://keycloak.example.com/realms/krateo` |
| `protocol.id` | `openid` | must match Keystone's mod_auth_openidc Location and its `[openid]` config group |
| `mapping.id` | `keycloak_mapping` | |
| `mapping.remote.{subject,username,groups}` | `HTTP_OIDC_SUB`, `HTTP_OIDC_PREFERRED_USERNAME`, `HTTP_OIDC_GROUPS` | the names Keystone sees the claims under (see [usage](usage.md#keystones-apache-config)) |
| `mapping.requiredGroup` | `tenants` | only users in this Keycloak group are mapped |
| `tenants.enabled` | `true` | generate a project, group and grant per tenant user |
| `tenants.trigger.{label,userLabel}` | `krateo.io/tenant` / `krateo.io/tenant-user` | a tenant Namespace carries `<label>=true` and `<userLabel>=<username>` |
| `tenants.projectPrefix` | `tenant-` | project `<prefix><username>`, group `<prefix><username>-members` |
| `tenants.role` | `member` | the role the group holds on the project |
| `tenants.deletionPolicy` | `delete` | what deprovisioning does in Keystone: `delete` removes the project and group, `orphan` leaves them |
