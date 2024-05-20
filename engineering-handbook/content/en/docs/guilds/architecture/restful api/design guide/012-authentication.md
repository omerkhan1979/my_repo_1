---
title: Authenication
linkTitle: Authentication
weight: 10
date: 2021-09-10
description: >
  How to authenticate services and users in your APIs
---

See also: [authorization]({{< relref path="./013-authorization.md" >}})

# api.takeoff.com authentication

The new API platform is intended to prioritize multi-tenant concepts, including
API token management and user management. It does continue to allow some legacy,
single-tenant access.

We have introduced a new [authentication and authorization
system](https://github.com/takeoff-com/auth-svc/) that is intended to be part of
our Apigee proxy ecosystem.

To authenticate with Takeoff's API, users must either:

1. Generate an access token using `api.takeoff.com/auth/token`
2. Generate an id token from the relevant single-tenant firebase project, using
   [`signInWithPassword`](https://firebase.google.com/docs/reference/rest/auth#section-sign-in-email-password)

To make API requests, these tokens _must_ be sent in the `Authorization` header, for instance:

```
Authorization: Bearer myGeneratedTokenHere
```

`X-Token`'s for legacy retailer-integration users (e.g. `wings-prod@takeoff.com`) which are
marked as `admin` in the legacy ecosystem _must not have access to
`api.takeoff.com` endpoints. This is a not a technical limitation. We're trying
to encourage adoption of the new token provider.

# Legacy authentication

APIs in the legacy ecosystem (TOM UI, RINT, Kubernetes services, etc) are expected to continue
to use the existing `X-Token` Firebase ID token scheme.

These tokens should come from
[`signInWithPassword`](https://firebase.google.com/docs/reference/rest/auth#section-sign-in-email-password)
or from the shared "service worker token".


{{% alert title="NOTE: Beware service worker token" %}}
It is discouraged to introduce new usage of the service-worker-token in new code
run outside of existing kubernetes applications.
{{% /alert %}}

# "Multi-tenant to legacy" authentication

Headless multi-tenant processes that need to reach out to legacy services that
use `X-Token` should look into the [auth-service GCP token middleware](https://github.com/takeoff-com/auth-service/pull/312/files).

You can find more details in [this article about the
dispatch->bifrost](https://takeofftech.atlassian.net/wiki/spaces/TOE/pages/4117364737/How+to+authenticate+a+single-tenant+service+from+a+multi-tenant+service?atlOrigin=eyJpIjoiOWQ3ZTdhNzUyMmJmNDBlMGIxNDFiNDZmM2U3OWVmNDQiLCJwIjoiY29uZmx1ZW5jZS1jaGF0cy1pbnQifQ)
project.

The high-level summary is that you will generate an ID token for the
service-account your Cloud Run/Cloud function runs as. You need to teach the
legacy service about the projects that have trusted service accounts. 

Once the configuration is in place, your cloud run/function can make requests
with the `X-Token` header value to be an ID token for that service
account with the audience of the service you're invoking.

Once authenticated, the middleware then acts as though the user is the
equivalent of the `service worker` account (e.g. tom.system@takeoff.com).

