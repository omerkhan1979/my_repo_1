---
title: "Versioning and Backwards Compatibility"
linkTitle: "Versioning"
weight: 6
date: 2021-09-10
description: >
  How to iterate your API request/response content.

---

{{% alert title="Warning" color="warning" %}}
This page is:
1. Still a work in progress
2. Probably full of gaps
3. Generally untested in the wild
4. A **significant deviation** from the Google AIP approach.

If you have questions or comments, please raise them.
{{% /alert %}}

### Basics

Takeoff's public API is consumed by many different parties. Maintaining a high
quality of service while also delivering new capabilities is a tricky balancing
act: existing APIs may need to be updated to enable those capabilities but those
updates may break existing usage.

The [API Review Process]({{< relref path="./002-review-policy.md" >}}) is
intended to help reduce the need for future API restructuring that could lead to
version increments. Unfortunately, there will probably be some change that
forces us into an increment.

In order to deliver breaking changes a versioning scheme is needed. Follow
these ground rules for versioning:

1. Non breaking changes **MUST NOT** introduce new API versions.
   - **Good**: Adding an optional attribute and not changing the API version where that
     attribute may be specified.

   - **Bad**: Having optional _additional_ attributes as the _only_ difference
     between a v1 and v2 API schema.

2. Teams **SHOULD** strive to reduce breaking changes.
   - **Good**: Finding ways to make something optional rather than required in
     the API payload for a v1 API.

3. Public API URLs **MUST NOT** include version strings
   - **Good** `api.takeoff.com/sites/123/customerOrders/456`
   - **Bad** `api.takeoff.com/v1/anything`
   - **Bad** `v1.api.takeoff.com/anything`

4. Internal/private APIs that sit behind some gateway that transforms requests
   **MAY** choose whatever versioning scheme needed.
   - **Acceptable** `api.takeoff.com/sites/123/customerOrders/456` proxies to
     `customer-order-svc/v1/ordersSomething`
   - **Acceptable** Gateway handles all content transformations and backend
     service does not have any knowledge of API versioning.

5. External/public APIs should utilize [Content Negotiation](https://developer.mozilla.org/en-US/docs/Web/HTTP/Content_negotiation) to specify versions (see also [Adidas](https://adidas.gitbook.io/api-guidelines/rest-api-guidelines/message/content-negotiation) and [Githubs Media Type notes](https://docs.github.com/en/rest/overview/media-types?apiVersion=2022-11-28))
   - NOTE:
      - Github _no longer_ uses content-type, opting instead for a custom
        header, but they still use a vendored JSON mime type.
      - Content negotiation is supported by OpenAPI schema specifications and
        allows us to document multiple API versions in the same schema just as
        well as paths do, if not better.
   - **Good**: `curl -X POST -H "Accept: application/json; version=1" api.takeoff.com/something`
   - **Bad**: `curl -X POST -H "X-Takeoff-Version=1" api.takeoff.com/something`
     - You **MAY** choose to do something like this in your backend service, but **MUST NOT** expose it to consumers.

6. APIs should use a MIME-Type parameter to specify the version, named
   `version`, rather than a vendored mime-type string.
   - **Good**: `Accept: application/json; version=1`
   - **Bad**: `Accept: application/vnd.takeoff+json`

7. Our public API is consumed in its totality, all resources **MUST** be accessible
   under the same version number.

   - **Good** v2 supports /orders, /inventorySnapshots, /products, etc.
   - **Bad** v2 only supports /inventorySnapshots and v1 supports everything else.

   Consider this a **STRONG** incentive to find backwards compatiable API
   updates and extensible initial structures.

   As a reminder: backend services may not need to know the API schema version
   if the gateway can "upgrade" old requests and "downgrade" to old response
   formats. With enough tooling it should be possible for us to increment
   the API version without needing to have every team collaborate on updating
   their backends.

8. Public API versions will need extremely long support timelines. You'll likely
   need to build adapters to convert between API versions, probably in Apigee.

9. An API's input data schemas **MUST** also be versioned. The data clients
    provide must have a documented format that is evolved the same as our
    response formats.

10. Input schemas **MUST** be versioned with the same content negotation
    approach. Clients **MUST** send `Content-Type: application/json; version=1`
    to document which version of the input schema they're using.

   - **Good** client sends `curl -H "Content-Type: application/json; version=1"
     --data '{"my_data": 1}' some-api-here`.
   - **Bad** clients only send `application/json`, for example: `curl -H "Content-Type: application/json" --data '{"my_data": 1}' some-api-here`.
     
     These requests should return a `4xx` class error.

   - **Worse** clients send no content type data `curl --data '{"my_data": 1}'
     some-api-here` and leave it to the server to guess on the data format and
     schema version.

### Additional reading

1. [Google’s Backwards Compatibility Reference.](https://google.aip.dev/180)
2. [Microsoft's REST Versioning docs](https://docs.microsoft.com/en-us/azure/architecture/best-practices/api-design#versioning-a-restful-web-api).
3. [REST implies content negotiation](https://blog.ploeh.dk/2015/06/22/rest-implies-content-negotiation/)
4. https://apisyouwonthate.com/blog/api-versioning-has-no-right-way
5. https://stripe.com/blog/api-versioning

### Versioning limitations

Resources _must not_ change their names, even in major versions. Pick names
wisely.
- Example: You must not decide to rename `/orders/xxx` to `/customerOrders/xxx` in a version
increment. This will break references to resources stored in other systems.

Resource name restrictions should not change in version increments either as
clients may or may not support those resource name specifications.
- Example: You should not decide that orders can be `[0-9]+` in v1 and
  `[0-9A-Z]+` in v2. It would mean that v1 clients could no longer interoperate
  with v2.

### Version support life-cycle

Follow these constraints when updating your APIs:

- Minor version increments must not break existing usage by internal or external
  clients
- Clients should not have any influence over the minor version used when making
  requests. There should not be any `.X` version information in the API
  specification.
  - **Good**: Client can request `Accept: application/json; version=2`
  - **Bad**: Client can request `Accept: application/json; version=1.2`

- Major version increments must come with support for at least one previous
  version.
  - Example: If you plan to release API `v3` of something when API `v2` is in
    use, `v2` must still be supported for at least 90 days.

- Public API used by our clients should have a longer
retention period and use adapters.
  - **TODO: What is that policy?**

- Teams must work with consumers of old API versions to migrate them to newer
  versions. This might mean analyzing who is using the old version and asking
  them to upgrade, providing Pull Requests to update clients, or anything in
  between.

### What are breaking changes?

Both [Google](https://google.aip.dev/180) and
[Microsoft](https://docs.microsoft.com/en-us/aspnet/core/grpc/versioning?view=aspnetcore-5.0)
have comprehensive notes on classifying breaking changes. The common theme for
all of those classifications is that a breaking change is something that causes
your API users to see side effects that were not expected.

The unexpected side effects could be hard errors (e.g. rejecting requests after
the introduction of required fields), things happening that did not happen
before (e.g. objects changing state unexpectedly) or things not happening when
they should. Regardless, these kinds of changes should be reserved to major
version increments and should be minimized in general.

Especially, in the case of RESTful APIs, where you do not control client code,
even the addition of new fields can be a breaking change if a client is coded in
a particularly unfriendly way. Clients should not assert on the structure of
attributes they do not consume.

There are a few classes of breaking changes to consider:

- Format: For instance, you converted from JSON to YAML response payloads. A
  client expecting JSON would be broken by this change. In general, we should
  not encounter this often as we should use JSON in most places.

- Structure: For instance, you change a field from an array to an object. A
  client trying to convert a JSON structure into a native type in their
  application would likely fail the conversion. This type of change requires
  either additional fields or version increments.

- Semantic: For instance, you change a field called `product_weight` to
  represent grams instead of kilograms. These can be trickier to manage, even if
  you include an adjacent fields like `product_weight_unit` because a client may
  not know about grams if it suddenly were to start showing up in
  `product_weight_unit`. For this reason consider naming attributes like
  `product_weight_kilograms` so you could evolve the API by adding _another_
  field `product_weight_grams`.

Consider tools like [https://pactflow.io/](https://pactflow.io/) to help manage
inter-service contracts in API structure. These can help [test/validate
changes]({{< relref path="./008-testing.md" >}})
between components in their CI processes.

Alternative protocols like gRPC help with some of these concerns, but not all.
For instance, you could still change the structure or semantic meaning of an
existing attribute. It only really helps with the wire format.

