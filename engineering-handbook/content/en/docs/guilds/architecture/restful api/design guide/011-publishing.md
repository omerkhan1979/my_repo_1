---
title: Publishing Public API
linkTitle: Publishing APIs
weight: 10
date: 2023-11-09
description: >
  Considerations for publishing your API for external use
---


{{% alert title="Warning: Expected to change!" %}}
The _default_ API documentation should be assumed to be private. That is not
currently the way things work with our tools. Once we add support for this the
documentation will be updated.
{{% /alert %}}

Some of our APIs are expected to be used by our customers -- for instance we
have APIs for creating and updating orders.

Some of our APIs are not intended to be exposed to retailers at all -- for
instance we might have some API for managing database backups.

In order to provide high quality documentation to our retailers we must:
- Document our public API using OpenAPI 3.0 or greater
- All endpoints that are expected to be used by customers should be added to
  https://github.com/takeoff-com/emarcotte-scratchpad/
- All endpoints AND query parameters, schema elements, headers, etc added to the
  documentation portal that are _not_ expected to be used by any customer should
  be marked as `x-internal: true`.
  - See also: https://redocly.com/docs/cli/decorators/remove-x-internal/
- All endpoints should have proper resource:verb permissions documented in
  auth-service.
- All endpoints permissions for endpoints expected to be used by customers
  should be included in the [retailer integration
  role](https://github.com/takeoff-com/tf-auth-svc-bootstrap/blob/main/src/modules/bootstrap-roles/canned-roles/multi-tenant/retailer-role.json).

All changes to the public API should be described in the "change log" section of
https://github.com/takeoff-com/emarcotte-scratchpad/blob/main/index.yaml#8 prior
to publishing. The CI pipeline in the repository can help you understand what is
changing in public, private and RINT APIs.
