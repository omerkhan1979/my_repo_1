---
title: Authorization
linkTitle: Authorization
weight: 10
date: 2023-11-08
description: >
  How to document and enforce resource access for API callers
---

See also: [authentication]({{< relref path="./012-authentication.md" >}})

API permissions are managed with
[`auth-svc`](https://github.com/takeoff-com/auth-svc/). Each endpoint must be
documented with which resource and permission is required.

Permissions should be managed through the [auth-svc integration terraform
module](https://github.com/takeoff-com/tf-mod-auth-mgr#service-permissions-management)

Endpoint permissions metadata should reflect the underlying resource rather than
try to leverage some other resource. For example `GET /sites/xxx/customerOrders`
should not try to say it requires `products` read access. It should require
`customerOrders` read access.

