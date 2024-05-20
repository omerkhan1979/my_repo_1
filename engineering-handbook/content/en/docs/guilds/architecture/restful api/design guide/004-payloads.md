---
title: Payload content structure
linkTitle: Payloads
weight: 5
date: 2021-09-10

description: How to structure payloads

---

HTTP requests and responses are composed of headers and bodies. This document
describes some of the considerations for documenting the format of the body at
runtime and for API user reference.

## Content-Type Header

The [`Content-Type`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Content-Type)  header helps clients and
servers tell each other what "media-type" the data they're sending the other is in. See also:
[RFC-7231](https://www.rfc-editor.org/rfc/rfc7231#section-3.1.1.1).

The `Content-Type` of request payloads should be be [JSON](https://datatracker.ietf.org/doc/html/rfc7159). Clients should
set the `Content-Type` header to `application/json` if there is a payload being sent with the request.

Clients should send [`Accept`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Accept) set to
`application/json`.

Servers should reply to all requests with the `Content-Type` header set to `application/json`.

Clients and servers may add additional information to the `Content-Type` for the purposes of [versioning]({{< relref
path="./006-versioning.md" >}}). For example: `Content-Type: application/json;
version=1`.

APIs must specify the Media Type's they will respond to.

## Payload Schemas

As mentioned in the [Content-Type](#content-type) section: payloads should be JSON, and may use any of the structure
elements (array, objects, strings, null, numbers). The schema of both request
and response payloads must be documented using [OpenAPI schema
structures](https://swagger.io/docs/specification/data-models/).  The
documentation may be generated.

The types defined in an API schema should not refer to external types (e.g.
pulling in some other APIs components). Google refers to this as ["one team owns
each
type"](https://github.com/aip-dev/google.aip.dev/blob/master/aip/apps/2713.md).
If the API "owns" a copy of data that exists in another API, it should
_duplicate_ the schema to allow the two systems to evolve independently. If the
API is referring to another APIs resource, it should do it by name, and require
the API user to fetch the resource from its proper location.

The schema documentation should be complete.
- **Good**: Describe the structure of your resource:
  ```
  components:
    schemas:
      Line:
        type: object
        properties:
          item_id:
            type: string
          requested_quantity:
            type: integer
            minimum: 1
      Order:
        description: The order payload
        type: object
        properties:
          name:
            type: string
          lines:
            type: array
            items:
              $ref: '#/components/schemas/Line'
  ```
- **Bad**: Providing incomplete specification
  ```
   components:
    schemas:
      Order:
        description: The order payload
        # no type, etc...
  ```

Naming attributes is somewhat tricky. Google [provides a large
list](https://google.aip.dev/140) of constraints, many of which we have
replicated into this document.

The schema should prefer attributes names in `lower_snake_case` to make it
easier interoperate with different programming environments, and to be distinct
from resource naming which is `camelCase`.

- **Good**: `{ "my_cool_attribute": 1 }`
- **Bad**: `{ "my-cool-attribute": 1 }`
- **Bad**: `{ "myCoolAttribute": 1 }`

Attributes should avoid words that would conflict with common programming
language keywords, such as `class`, `function`, or `import`.

Attributes that refer to a URI or URL should use `xxx_uri` as their name.

The schema should prefer arrays of objects over arrays of simple values to better enable
evolution and provide additional context.
- **Good**: A book might have publication info about when it was published:
  ```
  {"book": {
    "published": [{"publish_date": "2021-10-11"}]
  }}
  ```
- **Bad**: Same example but only using the date string rather than object:
  ```
  {"book": {
    "published": ["2021-10-11"]
  }}
  ```
  the `published` field will be very hard to evolve if we wanted to later add in
  `publisher` as an additional attribute for each publication entry.

The schema should prefer documenting attributes as objects so that additional
context can be added more easily as the API evolves.
- **Good**:
  ```
  {"barcode": {
    "value_upc": "xxx",
    "source": "bluetooth"
  }}
  ```
- **Bad**:
  ```
  {"barcode_upc": "xxx"}
  ```

Attributes that have some sort of type or unit (counts, weights, distances, volumes, etc)
should include that information in their name to keep the type information tied
to the value and avoid introducing new types that clients might not understand.
- **Good**: `{ "weight_kg": 5 }`
- **Bad**: `{ "weight": 5, "units": "kg" }`
- **Worse**: `{ "weight": 5 }` (e.g. implied units)

The API schema should document attribute relationships structurally.
- **Good**: An ordering system might have `lines` that will have been picked
  potentially in multiple ways.
  ```
  "lines": [{
    "item_d": "123",
    "requested_quantity": 4,
    "picking_records": [
      {"item_id": "123", "picked_quantity": 1, "picker_id": "joe@example.com"},
      {"item_id": "123", "picked_quantity": 3, "picker_id": "sam@example.com"}
    ]
  }]
  ```
  The relationship between the line and how it was picked is represented in the
  structure.
- **Bad**: The same system could require the API user to "join" information
  together across the payload:
  ```
  "lines": [{
    "item_id": "123",
    "requested_quantity": 4
  }],
  "picking_records": [
    {"item_id": "123", "picked_quantity": 1, "picker_id": "joe@example.com"},
    {"item_id": "123", "picked_quantity": 3, "picker_id": "sam@example.com"}
  ]
  ```
  This reduces complexity for clients to understand the relationship between
  data attributes.

Attributes refering to other resources in the API by URL should do so without including
version information.
- **Good**: `{"target_mfc": "/retailers/ABC/mfcs/123"}`
- **Bad**: `{"target_mfc": "/v1/retailers/ABC/mfcs/123"}`

Attributes that represent specific dates, times, or date-times should utilize
[ISO-8601](https://en.wikipedia.org/wiki/ISO_8601) format.
- **Good:** `{"date_of_something": "2021-11-22"}`
- **Bad:** `{"date_of_something": "2021/11/22"}` and many more.

Attributes referring to times must use the `extended` ISO format which separates
components with `:` rather than `basic` which omits it.
- **Good:** `{"date_of_something": "2021-11-22T12:12:12Z"}`
- **Bad:** `{"date_of_something": "2021-11-22T121212Z"}`


## Attribute behavior

Google [outlines](https://google.aip.dev/203) many different things that should
be documented in your API schema. Following their guidance, we should document:

- required: if the attribute is required to make a request. For instance
  creating a `tote` without a `tote_id` might not be allowed.

- Input only: if the attribute is used only to create/update a resource, but
  does not actually get echoed back. For instance, `expire_time` might be such
  an attribute on a delete request.

  It should be relatively rare that you need an input only attribute.

- Output only: if the attribute is not available to be set but will appear in
  the output. For instance the system may automatically assign IDs that cannot
  be changed.

- Immutable: if the attribute may only be set during creation and not updated
  later.

- Ordering: array attributes should document their ordering semantics, that is, will the
  array keep its order across requests or will it get sorted somehow, or is it
  not garunteed in any way?

## Common Attributes

Many resources will share common attributes. [Google defines a nice
list](https://cloud.google.com/apis/design/standard_fields) which we've used to
build our own table from.

When choosing names for attributes on your own resources for these concepts,
you should prefer these names.

| Attribute         | Type                                                      | Notes                                                                                                                                                                            |
| :---------------- | :-------------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `name`            | string                                                    | This is the name of the resource (e.g. the "123" in "/orders/123")                                                                                                               |
| `create_time`     | [ISO date string](https://en.wikipedia.org/wiki/ISO_8601) | A timestamp representing when something was created.                                                                                                                             |
| `update_time`     | [ISO date string](https://en.wikipedia.org/wiki/ISO_8601) | A timestamp representing when something was updated.                                                                                                                             |
| `delete_time`     | [ISO date string](https://en.wikipedia.org/wiki/ISO_8601) | A timestamp representing when a resource was [soft deleted]({{< relref path="./005-behavior.md#soft-delete">}})                                                                  |
| `expire_time`     | [ISO date string](https://en.wikipedia.org/wiki/ISO_8601) | The time when the resource should be considered for [deferred deletion]({{< relref path="./005-behavior.md#soft-delete">}})                                                      |
| `start_time`      | [ISO date string](https://en.wikipedia.org/wiki/ISO_8601) | For resources that track a period of time, `start_time` represents the earlier side of the range.                                                                                 |
| `end_time`        | [ISO date string](https://en.wikipedia.org/wiki/ISO_8601) | For resources that track a period of time, `end_time` represents the later side of the range.                                                                                     |
| `create_by`      | string                                                    | The user who created the resource.                                                                                                                                              |
| `update_by`      | string                                                    | The user who last updated the resource.                                                                                                                                         |
| `delete_by`      | string                                                    | The user who deleted the resource. If applicable.                                                                                                                                |
| `time_zone`       | string                                                    | If the resource includes a free-standing time-zone reference, use the [IANA timezone](http://www.iana.org/time-zones).                                                           |
| `region_code`     | string                                                    | A [unicode region code](http://www.unicode.org/reports/tr35/#unicode_region_subtag).                                                                                             |
| `language_code`   | string                                                    | The [BCP-47 language code](http://www.unicode.org/reports/tr35/#Unicode_locale_identifier).                                                                                      |
| `display_name`    | string                                                    | A human readable name for the resource. Should not have uniqueness constraints                                                                                                    |
| `title`           | string                                                    | An official name for the resource, similar to `display_name`. For instance, a user might name a bank: `{"title": "Bank Of America", "display_name": "My checking account bank"}` |
| `description`     | string                                                    | A free text description for the resource. Should not require uniqueness, and should allow for at least a couple of sentences worth of text.                                      |
| `filter`          | string                                                    | When [listing]({{< relref path="./005-behavior.md#list" >}}) indicates which resources should be included or excluded from the results.                                          |
| `query`           | string                                                    | Similar to `filter` but possibly including more complex logic when used for [searching]({{< relref path="./005-behavior.md#search" >}}).                                         |
| `page_token`      | string                                                    | When [paginating responses]({{< relref path="./005-behavior.md#pagination" >}}) marks the current "page" of results being returned.                                              |
| `page_size`       | integer                                                   | When [paginating responses]({{< relref path="./005-behavior.md#pagination" >}}) indicates how many results to include per page.                                                  |
| `total_size`      | integer                                                   | When [paginating responses]({{< relref path="./005-behavior.md#pagination" >}}) indicates how many total results are included.                                                   |
| `next_page_token` | string                                                    | When [paginating responses]({{< relref path="./005-behavior.md#pagination" >}}) marks the next "page" of results being returned.                                                 |
| `order_by`        | string                                                    | When [listing]({{< relref path="./005-behavior.md#list" >}}) or [searching]({{< relref path="./005-behavior.md#search" >}}) controls how the results are sorted.                 |
| `request_id`      | string                                                    | A token to make a request unique between multiple attempts.                                                                                                                      |
| `show_deleted`    | boolean                                                   | Allow a [list request]({{< relref path="./005-behavior.md#list" >}}) to show [soft-deleted]({{< relref path="./005-behavior.md#soft-delete" >}}) resources.                      |
| `validate_only`   | boolean                                                   | A signal that the request should only be validated, not actually processed.                                                                                                      |

## Errors & Response Codes

When requests cannot be processed the reply should be JSON payload.

The response structure should follow existing conventions for payload formatting.

The response structure must at least include:

```
{
    "message": "Some stringy message to help the user understand what went wrong without leaking any internal details about the system."
}
```

The response may include additional details about the failure.

The response's HTTP status code must follow HTTP conventions. To learn more
about the conventions read:
- Google's own [gRPC status
  codes](https://cloud.google.com/apis/design/errors#error_model) which include
  corresponding HTTP codes.
- [MDN status codes
  documentation](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status)
- [W3C's status codes](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html)

NOTE: These resources may have conflicting advice. We are defaulting to Google in
most cases. Reach out to the API guild if you need advice.

APIs should utilize the following mapping for status codes, and fall-back to the
Google MDN approaches if the exception case is not covered here.

- `400` When the request cannot be processed due to request data or system
  state being in an unacceptable state.
  - Example: Missing a required field
  - Example: Trying to remove some resource that doesn't allow removal if it
    still has child-resources that are not deleted.
- `401` - When no user credentials were provided or they could not be
  validated.
- `403` - When the user does not have permission to look at the given
  resource. Should be evaluated prior to checking if the resource exists.
- `404` - When requesting a resource that does not exist.
- `409` - When the system cannot process the request due to conflicting
  state in the system (e.g. out-of-sequence updates when using [`ETag`](#etag) or
  resource already existing, etc)
- `500` - When some general fault occurs while processing the request

## ETag

APIs may require users to have the latest version of a resource before invoking
behaviors on that resource. Google refers to this as a [Resource freshness
validation](https://google.aip.dev/154).

A common way to implement freshness validation is through an
[ETag](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/ETag).  APIs
that need to support freshness validation should include an `etag`
attribute response payloads.

Any subsequent updates being done to the payloads using PATCH/POST/PUT calls should include the `etag` as a part of the
payload. 

NOTE: We are intentionally _not_ using the HTTP header `ETag`.

Clients should propagate the `etag` they previously received in subsequent
requests.

APIs must document the semantics of the `etag`. As documented in
[RFC-7232](https://tools.ietf.org/html/rfc7232#section-2.3) they may be strong
or weak.

## Nulls

Sometimes your API doesn't need a value to exist. For example, you may be
modeling some sort of optional data or some data that will be filled in later.

Optional input data from API callers should not be added to the `required`
section of an object AND the type should also be marked as nullable. This allows
users to use a variety of tools that may or may not omit nullable data in their
serialization.

Optional data in responses should be marked as required but nullable. This will
allow users to not have to worry that an attirbute is `undefined`. Optional,
unset data _must_ appear in responses as `null`.

OpenAPI 3.1 introduced support for defining nullable types using this syntax:

```
  MyThing:
    type: ['null', string]
```

The API guilds current recommendation is **NOT** to use this construction as
many tools do not currently understand it. Instead, we recommend something like:

```
  MyThing:
    type: string
    nullable: true
```

As a reminder, nullable enumeration types **MUST** [include null in the valid
list](https://swagger.io/docs/specification/data-models/enums/) as well as mark the schema as nullable:

```
  MyThing:
    type: string
    nullable: true
    enum:
      - a
      - b
      - null
```
