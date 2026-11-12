---
type: Component
title: krateo-openstack-federation — index
description: The map of the krateo-openstack-federation doc bundle: Keystone federation with a Krateo Keycloak realm, and a Keystone project per Krateo tenant user.
resource: oci://ghcr.io/krateo-blueprints/charts/krateo-openstack-federation
tags: [openstack, keystone, federation, keycloak]
timestamp: 2026-11-12T00:00:00Z
---

# krateo-openstack-federation

Keystone trusts a Krateo Keycloak realm over OpenID Connect, and every Krateo tenant user gets their
own Keystone project, all declared as openstack-keystone-operator-kog custom resources.

- [overview](overview.md): what is declared, and how a user's project comes and goes
- [usage](usage.md): prerequisites, install, what Keystone's Apache config must provide, verifying
- [configuration](configuration.md): the values surface
- [api](api.md): the resources rendered and generated
- [examples](examples.md): index of examples
- [release](release.md): how a release ships
- [log](log.md): history
