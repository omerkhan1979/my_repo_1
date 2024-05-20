---
title: Proxy Design
linkTitle: Proxy Design
weight: 11
date: 2022-12-28
description: >
  How to design Apigee Proxies
---

{{% alert title="Warning" color="warning" %}}

The API Guild really wishes we had a "Just Copy This Repo" approach for how to
design your proxies but we're still learning. If you have a question, concern,
or find issues please come chat in
[#project-api-ppp](https://takeofftech.slack.com/archives/C03QPBL4R9S) and lets
figure out how we can improve this for everyone.

{{% /alert %}}

[API
proxies](https://cloud.google.com/apigee/docs/api-platform/fundamentals/understanding-apis-and-api-proxies)
are a way to route requests to backend services. At runtime, HTTP requests are
parsed and rules within an Apigee Organization and Environment are used to make sure
those requests make it to the correct backend services. During this flow the
rules can also mutate the request or response to reshape it however that backend
expects.

In general, proxying allows us to decouple a service provider from its consumers
which increases our flexibility, though it also increases complexity. This page
proposes a series of design choices to help manage the complexity of our API
Proxies.

## Concepts

There are a few concepts to keep in your mind as you design your API proxies.

### Fewer ingresses, more paths

All APIs get traffic from somewhere. There are a handful of different ways we
generate API traffic today:

1. Mobile, TOM UI, Decanting UI, and other user-facing front-ends.
2. Service-to-service requests (internal or retailer-facing)

These systems make requests by connecting to an ingress of some sort. In
Kubernetes, we use a public IP bound to nginx-ingress. In Apigee a public IP is
bound to a Google load balancer system, ultimately bound to Apigee environments
and proxies.

In Kubernetes, we leaked implementation details everywhere. Inside the cluster, if
you wanted to get an order the only "abstraction" we had available to us was the
Kubernetes service object that helped us find Pod IP addresses. Consumers still
had to know that there was an `oms`, what port (and protocol!) it used as well
as the API schema. Any time you wanted to refactor which service owned a
resource you had to touch every other service. Outside the cluster was only a
marginally better experience: nginx ingress normalized ports for us, so you
never had to know that OMS used port 8000.

As we remodel with Apigee we want to use _fewer_ ingresses and leverage a
consistent API service discovery method for consumers.

We're still evolving this guide but the basic intention is that every resource
will be available under `https://api.takeoff.com:443`. There may be different
domain names in use in the ecosystem, but they will be mostly hidden from
consumers and managed via redirects or proxying.

The only additions we have considered adding are:

1. mobile.takeoff.com - backend-for-frontend for takeoff mobile
2. app.takeoff.com - backend-for-frontend for web apps (TOMUI)
3. api.takeoff.internal - an internal DNS name if we find the need to route traffic
   across private networks instead of public DNS.

We are still trying to figure out if we can bring any of the
existing Kubernetes domain names into Apigee or not (e.g.
oms-winter-dev.tom.takeoff.com pointing to Apigee).

Following are the currently supported endpoints for APIGee which up and running would be eventually migrated to `https://api.takeoff.com` : 
- `uat.uat-api.tom.takeoff.com`
- `prod.prod-api.tom.takeoff.com`
- `dev.nonprod-api.tom.takeoff.com`


### API Proxies are not necessarily the same as a standalone API.

You may choose to take some larger API offering and carve it up into many
sub-proxies. For example, the backend-for-frontend API to manage our mobile
experiences may be composed of a handful of internal proxies: one to do
inventory actions, one to interact with orders, one to get picking tasks, one to
get label data and so forth.

As you model the API for your domain you will find you naturally have several
different resources and will have several different proxies as well.

The current best starting place is that each resource is best modeled as a proxy
as it likely shares a backend service, or at least similar processes to get to
backend services. More concretely if you had these endpoints for an order
resource

- `GET /sites/xxx/orders`
- `POST /sites/xxx/orders:search`
- `POST /sites/xxx/orders/yyy`

You would start modeling this as a single proxy. If you had siblings or
sub-resources they would be different proxies.

### Shared Flows can help reduce duplication

As we add more and more API proxies we'll find places where we're repeating
ourselves. For any scenario like this, we should refactor reusable chunks into
[shared flows](https://cloud.google.com/apigee/docs/api-platform/fundamentals/shared-flows).

Shared flows need to be managed "across" all users - it is not possible to refer
to a specific revision of a shared flow in different proxies. As a result, we
recommend developing those shared flows in the central
[Apigee-APIs](https://github.com/TakeoffTech/apigee-apis/) repo. If we can come
up with a safe way to manage different repos access to Apigee without conflicts
we may change this recommendation.

### API Proxies can talk to other API Proxies.

As you design your API you may find that one part of it just needs to
forward traffic to some other system. This might be most common in a "Backend
for frontend" area where we have a "pass-through" for various resources. The
pass-through may even include transformations. For instance, if we used a
special form of access token in the mobile application APIs, we could
exchange it for some different backend token before using the existing proxy.

## High-level design considerations

### Base Paths

The base path for your proxy is _extremely_ important. It needs to be unique across the Takeoff multi-tenant eco-system.
Each base path uniquely represents a micro-service and any resources/operations hosted by the same should be relative to the base path.

For example ,the site infromation micro-service may have the base path as `site-info` and may be hosting the following APIs

 - /sites/{site_id}/spokes/{spoke_id}:attach
 - /sites/{site_id}/spokes
 - /spokes
 - /retailers/{retailer_id}
 
With facade proxy setup on apigee ( explained in the subsequent sections ) every microservice needs to host the resources under its service-specific base path. The facade proxy would take care of identifying the microservice which owns the resource and redirect the call to the same for processing.

### Domains VS paths

Traffic from apps should use consistent ingresses.

We **CURRENTLY** only have one DNS naming pattern for all of our Apigee environments and
consuming apps to use. In the near term teams can either work with the API Guild
to figure out how to get additional names configured as they bootstrap these new
ingresses OR model the ingress under a base path. Once we have figured out the
DNS side of things we will necessarily need to update clients and could use that
time to re-bind away the top-level base path.

In your proxy endpoint XML, this will look something like:

```
  <HTTPProxyConnection>
    <BasePath>/mobile/sites/*/dogs</BasePath>
  </HTTPProxyConnection>
```

For non-user-facing APIs (e.g. our public API or backend API) we recommend not having any base prefix (e.g. just /sites...).

Your backend service does not need a human-readable DNS name, and it may not even need to be public. You can use the various [Shared VPC
Networks](https://github.com/TakeoffTech/tf-tg-live/tree/master/org-gcp/nonprod/shared-services/prj-vpc-host-nonprod/apigee-service-project)
to route traffic from API proxies to backend servers. For serverless endpoints, this is a little bit more tricky due to limitations around [Internal HTTPS load balancer "global
access"](https://cloud.google.com/load-balancing/docs/negs/hybrid-neg-concepts#regional_vs_global).

### Proxy Naming

The proxy name can be fairly simple you can define your base path simply based on the name of your microservice.
for example if you are creating a microservice for managing `dispatches` you can name you proxy as `dispatch-service`
and the base path as `dispatch-service`.

### Deployment

At this time we only have one "Officially managed" Apigee API and Shared Flow
deployment pipeline via the
[apigee-apis](https://github.com/TakeoffTech/apigee-apis/) repo. We recognize
this is a bottleneck. We are open to ideas for how this can be improved (for
instance it might not be hard to update our terraform recipe to add additional
repos with permissions).

We are hoping we can avoid a scenario where various repos all have complete control over
Apigee as it makes it very hard for us to orchestrate whole releases of our
software.

In some sense, the gateway, perhaps at the level of "ingresses" should
be treated as a single entity and theoretically configured in one place for
each.

Within our Github organization, we use
https://github.com/emarcotte/typescript-apigee-deploy-action to execute API and
Shared Flow deployments. It has some useful features like diffing that we were
hoping could help us form a "terraform-like" experience without having to
implement terraform modules that Google seems to have ignored.

We plan to add support for:
- Converting OpenAPI specs to "Takeoff Flavored" apigee proxies
- Terraform workflows to generate environment-specific API proxy artifacts with updated KVM entires 
- Updating API portals, if the APIs even exist.
- Build a new Apigee proxy deployment repo that sources various proxies as versioned artifacts and uses a terraform based deployment module


If you have ideas or want to contribute one of these things, please reach out to
the slack channel.


### Facade Proxy

As mentioned in the document earlier the underlying microservices should never leak their details to other microservices/external world
( i.e. which service is implementing what API). Also, some of the cross-cutting concerns like Authentication and Authorization need to be taken care of in a single consistent way. 
To achieve the same a *facade proxy* has been set up on apigee. The facade proxy works in the following way.
The facade proxy hosts the root base paths like:

    - /sites
    - /retailers
    - /spokes
    - /auth 

To begin with, a large number of APIs are going to fall under one of the above base paths. */sites* is likely to be the root for a large number of APIs in the takeoff eco-system
Following are some of examples : 
 
 - /sites/{site_id}/spokes/{spoke_id}:attach
 - /sites/{site_id}/customerOrders/{customer_order_id}
 - /sites/{site_id}/zoneProfiles/active
 - /sites/{site_id}/zoneProfiles/{zoneProfileId}:activate
 - /sites/{site_id}/orderTotes/{order_tote_id}
 - /sites/{site_id}/pickingResults:batchCreate

Each of the above API's are served by different microservices in the backend 

| Path     | Owning Microservice      | Path exposed by Owning Microservice     |
| ------------- | ------------- | -------- |
| /sites/{site_id}/spokes/{spoke_id}:attach          | Site Info          | /site-info/sites/{site_id}/spokes/{spoke_id}:attach   |
| /sites/{site_id}/customerOrders/{customer_order_id}          | Orders API          | /order-mgmt/sites/{site_id}/customerOrders/{customer_order_id}   |
| /sites/{site_id}/zoneProfiles/active | Zones API | /zone-mgmt/sites/{site_id}/zoneProfiles/active |
| /sites/{site_id}/orderTotes/{order_tote_id} | Tote Manager | /tote-mgmt/sites/{site_id}/orderTotes/{order_tote_id} |



The facade proxy accepts requests from retailers, other internal multi-tenant microservices, and retailer sites. The facade delegates the call to the authentication service for validation. 
The Authentication service authenticates and authorizes the requests. If the request is authorized it returns the following details based on who is calling the API.
There is the following variety of users: 

- TMA/TomUI User - retailer-specific users accessing user interface and making calls to API's in the multi-tenant platform
- Multi-tenant Microservice User- All internal services which are going to talk to each other
- Retailer User - A client credentials-based user configured to be used on any of the customer-specific service setup in its bespoke environment
- Site User  - A client credentials-based user configured to be used to integrate retailers services set up for a particular site. for example: any retailer portal setup to receive orders ( this infra would require creating orders in the Takeoff eco-system)

The following set of headers would be additionally relayed to the microservice owning a particular path if the request is authenticated. 
The headers would be dependent on who the calling user is and what details are available in the path. The table below explains the same. 


Takeoff Headers    | Description   | TMA/TomUI  User |Multi-tenant Microservice User| Retailer User | Site User
|---| ----| --- |---| ---| ---|
X-Takeoff-Location-ID | Legacy Site attribute | Yes (If Present) | Yes ( if  site_id present in path ) | Yes ( if  site_id present in path ) | Yes
X-Takeoff-Location-Code-Gold | Legacy Site attribute | Yes (If Present) | Yes | ( if  site_id present in path ) | Yes ( if  site_id present in path ) | Yes
X-Takeoff-Location-Code-Tom | Legacy Site attribute | Yes (If Present) | Yes ( if  site_id present in path ) | Yes ( if  site_id present in path ) | Yes
X-Takeoff-Retailer-ID | New Site Info attribute | Yes | Yes ( if site_id or retailer_id present in path ) | Yes | Yes
X-Takeoff-Retailer-Code | Unique code defined for every retailer | Yes | Yes ( if site_id or retailer_id present in path ) | Yes | Yes
X-Takeoff-Site-ID | New Site Info attribute | Yes | Yes | Yes ( if  site_id present in path ) | Yes
X-Takeoff-Retailer-Site-ID | Unique code defined by every retailer for a site | Yes | Yes | Yes ( if  site_id present in path ) | Yes
X-Takeoff-Retailer-Deployed-Region | Deployed GCP region for a retailer | Yes | Yes | Yes | Yes
X-Takeoff-User-Name | name of the calling identity | Yes | Yes | Yes | Yes
X-Takeoff-User-Email | email of the calling identity | Yes | Yes | Yes | Yes
X-Token | Bearer Token passed as part of authorization | Yes | Yes | Yes | Yes
X-Correlation-ID | Unique ID passed to every request | Yes ( added if not passed) | Yes ( added if not passed) | Yes ( added if not passed) | Yes ( added if not passed)

# How to Integrate with a Facade Proxy? 

To integrate with the Facade Proxy and Authentication you need to enroll your service with the [authentication service](https://github.com/takeoff-com/auth-svc).
Following page details out how you can use a shared module created for [Onboarding with Authentication Service](https://takeofftech.atlassian.net/wiki/spaces/FUL/pages/4070342659/Shared+module+for+onboarding+with+Authentication+Service) 

As a part of registration with the Authentication service, each microservice will need to provide the details of what
permissions are needed on what resource for a user/service to be able to access the APIs. 
This is required to identify the resource being accessed as a part of the API call thus disambiguating what
resource should the user/service have permissions  for in order to access an API. 

The other minor change that would be required is to ensure the APIs hosted by the microservices cannot be called 
externally and that the facade proxy should be able to call the APIs internally  

Add a new shared flow callout policy in your proxy as below : 
```
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<FlowCallout continueOnError="false" enabled="true" name="FC-restrictExternal">
  <DisplayName>FC-restrictExternal</DisplayName>
  <Parameters/>
  <SharedFlowBundle>restrict-external</SharedFlowBundle>
</FlowCallout>
```

The step needs to be added into the `preflow` proxy-endpoint for the proxy hosted into the Apigee.

```
<Step>
   <Name>FC-restrictExternal</Name>
</Step>
````

Please refer [site-info proxy](https://github.com/takeoff-com/apigee-apis/blob/master/apigee-workspace/src/main/apigee/apiproxies/siteinfo-svc/apiproxy/proxies/default.xml) for the same.
