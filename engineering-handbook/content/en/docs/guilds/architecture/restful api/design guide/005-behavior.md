---
title: "Resource Behavior (Verbs)"
linkTitle: "Resource Behavior"
weight: 4
date: 2021-11-01

description: >
  How to add behavior to resources

---

The resources that exist in an API are only useful if they can be interacted
with. Users will expect to be able to create, read, list, update and delete most
resources as well as execute domain-specific custom operations.

These interactions must be modeled using the standard HTTP verbs: PUT, POST,
GET, PATCH and DELETE.

It is not required that every resource supports all methods. For example, in
some book-scanning application you might have a resource modeling chapters that
were automatically created by parsing the text. In this case you might not want
to have create and delete operations for chapters. Instead you would have them
only on books, but could then "list" and "read" the chapters as sub-resources.

Throughout this page we make reference to [Google's
AIP](https://google.aip.dev/) guidance for defining behaviors. Pay special
attention to the concepts and not the specifics. They heavily emphasize gRPC
tooling aspects that are not necessarily applicable to a REST API. In some cases
we will also refer to [Google's PubSub REST API](
https://cloud.google.com/pubsub/docs/reference/rest/v1/projects.subscriptions/create)
for concrete examples.

This page includes status codes for many common success and error cases. If you
find yourself needing to represent something more complex, consider using the
status codes from [W3C's status code
reference](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html) or [Google's
standard HTTP/gRPC error
mappings](https://cloud.google.com/apis/design/errors#error_model) and letting
the API guild know of this gap.


## Create

See also: [Google’s Create reference](https://google.aip.dev/133). See [Subscription
create](https://cloud.google.com/pubsub/docs/reference/rest/v1/projects.subscriptions/create) for a concrete example.

Constraints:

- The request must be an HTTP POST

- The request body must be an object structure containing the resource body.

  - **Good**: `POST /orders` with data:
    ```
    { order data here }
    ```

  - **Bad**: `POST /orders` with data:
    ```
    {"order": {order data here} }
    ```

    Though previous versions of this guide did accept this.

  - **Bad**: `POST /orders` with array data:
    ```
    [{order data here}]
    ```

    Batch create should be done via separate endpoints.

- A successful response body must be the fully populated resource, including its
  name. The attributes should be at the top level of the response

  - **Good**: Response for `POST /orders/123`:
    ```
    {"name": "123", "lines": [...], etc...}
    ```
  - **Bad**: Response for `POST /orders/123`:
    ```
    {"order": {"name": "123", ...}}
    ```

- Idempotency is optional

### User Controlled Naming

Sometimes the API user may be allowed to provide the name of a resource. For
instance, you might have an API for managing articles they are writing, so the
resource hierarchy might have resources like `/articles/userProvidedNameHere`

- The create request URL should be `/{collection name here}/{resource name here}`
- The API must provide user facing document around the constraints of the
  resource name.
  - Example: “Order IDs Must be lowercase ASCII characters `0-9a-z`”.

### Response Codes

- `201` - When the request was successfully processed.
- `403` - When the user does not have permissions to create the resource.
  - NOTE: This should be validated _prior_ to validating for conflicts (e.g.
    `409` responses)
- `409` - When the resource already exists

See also [Error Responses]({{< relref path="./004-payloads.md#errors" >}}) for
other other common response codes.

## Read

See also: [Google’s Get reference](https://google.aip.dev/131). See
[Subscription
get](https://cloud.google.com/pubsub/docs/reference/rest/v1/projects.subscriptions/get)
for a concrete example.

APIs must support handling the HTTP GET verb in the context of a resource’s URL.

Constraints:

- The full resource should be returned in the response body by default.
  - **Good** `/resource` returns full entity
  - **Bad** `resource?fields=all-fields` as the only way to get all fields.

- The response body should be an object, with no wrapping.
  - **Good:** `GET /books/123` returns
    ```
    {"title": "War and Peace", ...}
    ```
  - **Bad:** `GET /books/123` returns
    ```
    {"book": {"title": "War and Peace", ...}}
    ```
- Query-string parameters *may* reduce fields included
  - See also [Google's partial responses document](https://google.aip.dev/157).
  As use cases come up for this we will document the standard please [let us
  know]({{< relref path="./001-policy-updates.md" >}}).

- The request is idempotent

### Response Codes

- `200` - The request was successfully processed.

See also [Error Responses]({{< relref path="./004-payloads.md#errors" >}}) for
other other common response codes.

## List

See also: [Google’s List
reference](https://github.com/aip-dev/google.aip.dev/blob/master/aip/general/0132.md).
See [Subscription
list](https://cloud.google.com/pubsub/docs/reference/rest/v1/projects.subscriptions/list)
for a concrete example.

To enumerate a collection of resources a “list” request may be defined by an
API. List operations are performed on a collection URL rather than a specific
resource.

In general the list operation is fairly restricted in what it supports. As a
result an API might choose to implement a [custom search method](#custom-methods) that
affords more flexibility.

Constraints:

- The request must include the collection name, and parent if the collection
  belongs to a parent.
  - **Good:** `GET /books`
  - **Good:** `GET /clients/123/orders`

- The request may include [`filter` and `order_by`]({{< relref
  path="./004-payloads.md#common-attributes" >}}) fields as strings to do simple
  user-driven changes to the which resources are returned in the list. These
  should be included as query parameters (e.g. `/myThing?filter=xxxx)`).  If
  more complex interactions are needed than the query string affords, consider a
  [custom search method](#custom-methods)
  - **Good:** `GET /books?order_by=author_email`
  - **Bad:** `GET /books:sortedByEmail`

- The list response should not be relative to the current user. Any user who has
  access to the collection should get the same result.

- The request is idempotent

- The response must not be top-level array. The response must have a top level
  attribute that is the collection name which contains the enumerated resources.
  See [payloads]({{< relref path="./004-payloads.md" >}}) for more details on
  payload structure.

  - **Good:** `GET /books` with response:

    ```
    {"books": [{book 1 here}, {book 2 here}...], }
    ```
  - **Bad:** `GET /books` with response:

    ```
    [{book 1}, {book 2}]
    ```

- The response should contain the resource bodies in their entirety.

- The response should not include [soft deleted]({{< relref
  path="./005-behavior.md#soft-delete" >}}) resources. The request may include a
  `show_deleted` parameter to include those soft-deleted resources in the
  response. It is not require to support soft-deletion, or to support listing
  soft-deleted resources.

### Pagination

[Google's Pagination document](https://google.aip.dev/158) includes many details
on the challenges for being able to return subsets of a list request. Use
[PubSub subscription
list](https://cloud.google.com/pubsub/docs/reference/rest/v1/projects.subscriptions/list)
as an example of how pagination should work.


As Google emphasizes in their pagination reference, adding pagination is a
breaking change. Introducing the concept of partial results where it was not
previously means a client may not see all the data they expect to see.

It is **not** required to support pagination in list requests, for instance you
might have a collection that is maybe static or has a relatively small number of
resources over time. An example of this could be a bookstore with collections
for point of sales machines (e.g.  `/stores/123/pointOfSaleMachines/aisle-1`)).
Other than initial setup, this collection is unlikely to see significant growth
over time.  Collections that grow over time should include pagination (e.g. the
list of orders will keep growing over time).

To support pagination consider these constraints:

- The request payload should include a `page_size` attribute to set how big the
  response will be. The attribute may be optional provided that the API
  documents the default value clearly for users.

- The request payload should allow an optional `page_token` to allow retrieving
  the next set of results.
  - Requests without `page_token` must return the first page of results.
  - Requests with invalid or unknown `page_token` should reply with a `400` and
    indicate that the page token was invalid in the response body.
    - Example from PubSub API:
      ```
      {
          "error": {
              "code": 400,
              "message": "Invalid page token given (token=DBsEUg8Ye3VnfG1eG).",
              "status": "INVALID_ARGUMENT"
          }
      }
      ```

- The response payload should include a `next_page_token` that the user passes
  as `page_token` to fetch the next set of results. The response should exclude
  this field to indicate that there are no more pages.

- The `page_token` should be a value users cannot decode. One strategy for
  enabling this is to store the tokens in a database. Another could be to encode
  some pagination data in a way that only the API's backend knows how to decode.

  There is no official encoding scheme for page tokens. It is not required to
  use a sophisticated cryptography system, but it is strongly encouraged that
  you avoid schemes that are trivially decoded (e.g.  base64). Clients who
  discover the encoding scheme will expect us to support it going forward.

- The response payload may include a `total_size` attribute to include the
  number of resources to be paged through.

- API's must document document how long page tokens are valid for.

- Even though `page_token` should be opaque, it is still subject to version
  compatibility constraints. API's should avoid releasing changes that would
  break existing tokens (e.g. changing the encoding/decoding keys, or changing the
  storage format before previously issued tokens have expired).

An example cycle of requests might look like:

```
GET /books?page_size=2

{"books": [{book1}, {book2}], "next_page_token": "asdf1234", "total_size": 5}

GET /books?page_size=2&page_token=asdf1234

{"books": [{book3}, {book4}], "next_page_token": "qazwert789", "total_size": 5}

GET /books?page_size=2&page_token=qazwert789

{"books": [{book5}], "total_size": 5}
```

### Response Codes

- `200` - The request was successfully processed.

See also [Error Responses]({{< relref path="./004-payloads.md#errors" >}}) for
other other common response codes.

## Update

{{% alert title="Warning" color="warning" %}}
This section deviates substantially from the [Google update
AIP](https://google.aip.dev/) reference material. We _do not_ recommend use of
`field_mask` and we _do not_ recommend the use of an outer wrapper on your
resource's payload.
{{% /alert %}}

See also: [Google’s Update Reference](https://google.aip.dev/134).

The update method allows users to change a resource that has already been
created.

Constraints:

- The API schema should document which attributes of the resource can be
  updated.

- Update methods are not intended to have side effects. Use [custom
  methods](#custom-methods) to trigger side effects. Similarly, any "state"
  attributes should not be updatable via `update`.

- The update must respond with the full resource itself, as it does with
  [create](#create)

- The update method if supported by a resource it should be implemented using
  the `PATCH` request. `PATCH` requests are considered to be "partial" updates. This
  is important as the addition of new fields to resources makes a PUT/full
  update hard for old clients to transparently accept.

  Basically: A full `PATCH` update today might be a partial one tomorrow.

- The request **MAY** utilize [`etag`s]({{< relref path="./004-payloads.md#etag" >}})
  to require users to have up-to-date data prior to deletion.

- The request payload must be an object. The object **SHOULD NOT** contain a top level wrapping field.

  - **Bad:** `PATCH /books/123` with data:
    ```
    {"book": { attributes of book to update }}

    ```
  - **Good:** `PATCH /books/123` with data:
    ```
    { attributes of book to update }
    ```

- The schema **MAY** require certain subsets of patches be done individually.
  For instance if books have "authors" and "publishers" it may require that only
  one is updated at a time.

  This may be useful if you're wrapping a legacy service that does not allow for
  more complex "partial" updates to be merged together or has bespoke update
  endpoints for each attribute.

- The schema **MAY** evolve to add additional supported `PATCH` structures within an API version.
  For instance if you were to add an "authors" attribute to a book resource, it is
  reasonable to add it as an optional `PATCH` structure on its own or with other
  attributes.

- The schema **MAY** evolve to add additional supported `PATCH` structures
  within an API version.

- The schema **SHOULD** avoid evolutions that remove supported `PATCH`
  structures OR add required fields to existing `PATCH` structures within an
  API version.

- Schemas will likely need to leverage OpenAPI's [`oneOf` or
  `anyOf`](https://swagger.io/docs/specification/data-models/oneof-anyof-allof-not/)
  to document the various acceptable forms of updates that are available for
  each resource.
  - See [this example golang
    API](https://github.com/takeoff-com/emarcotte-scratchpad/tree/c78be7b13947eda6432e53490e2cca8d538f4b25/partial-test)
    that implements various forms of "partial" `PATCH` support.

### Response Codes

- `200` - The request was successfully processed.

See also [Error Responses]({{< relref path="./004-payloads.md#errors" >}}) for
other other common response codes.

## Delete

See also: [Google’s Delete reference](https://google.aip.dev/135). See
[Subscription
delete](https://cloud.google.com/pubsub/docs/reference/rest/v1/projects.subscriptions/delete)
for a concrete example.

APIs that support deleting a resource must support handling the HTTP DELETE verb
in the context of a resource’s URL. This may be treated in two ways:
- A "hard delete" where the resource is permanently removed
- a [soft delete](#soft-delete) where the resource is scheduled for removal, and
  may be restored.

Constraints:

- The response body may be empty.
- The response body may contain the resource itself.
- The request may utilize [`etag`s]({{< relref path="./004-payloads.md#etag"
  >}}) to require users to have up-to-date data prior to deletion.

### Soft-Delete

See also: [Google’s Soft Delete reference](https://google.aip.dev/164).

Resources that support soft deletion have special considerations:

- The resource must not actually be removed from underlying storage when
  deleted.
  - The resource must store state indicating that the resource is marked for
    deletion.
- The request should include an `expire_time` after which the resource will be
  "hard" deleted
- APIs must not remove the resource before the `expire_time`
- APIs that do not provide an `expire_time` must document what the
  retention policy is.
  - It is preferable to let users define `expire_time` as a reduction in this
    time could be considered a breaking change.
- APIs should document the limits for `expire_time`, for example "Must be
  no more than 30 days from the current date."

## Custom Methods

See also: [Google’s AIP Custom Method reference](https://google.aip.dev/136) as
well as the [Google Cloud Custom Methods
reference](https://cloud.google.com/apis/design/custom_methods). For a concrete
example, look at [Subscription's
ack](https://cloud.google.com/pubsub/docs/reference/rest/v1/projects.subscriptions/acknowledge)
method.

The standard methods exist to do simple data manipulations. An APIs surface
should be majority standard methods and should fall back to custom methods when
those standard methods are insufficient.

One major case to consider standard methods is for [triggering status
changes](https://github.com/aip-dev/google.aip.dev/blob/master/aip/general/0216.md)
on your resources. By separating the data management and status management it
can be clearer which actions will have side effects.

Custom methods must use the `POST` verb.

Custom methods should be constructed as `/collectionOrResource:methodNameHere`.

Custom methods must be named using an American English verb phrase in `camelCase`
- **Good:** `/orders/123:reserve`, `/orders:batchCreate`
- **Bad:** `/orders/123/reserve`, `/orders/batchCreate`, `/orders/batch-create`.

Here's a non exhaustive list of custom methods you might consider for your API:

- State transitions

  In an Order API you might see custom methods like: `split`, `cancel`,
  `enqueue` to transition the order from one lifecycle state to another. These
  would be referenced like: `/orders/123:cancel` for example.

- Undelete

  An `undelete` request, such as `POST /orders/123:undelete` should be considered
  the opposite of a [soft-delete](#soft-delete) request.

  An undelete request should return the full resource body.

- Search

  A search custom method is the more complex version of the [list request](#list).
  It might be useful to consider a simple list interface separately from a search
  interface to avoid some heavy-weight operations or span collections.

  Search requests have the same [pagination](#pagination) constraints as list
  requests.

  We have not documented the payload structure for a search request yet. If you
  need this please [let us know]({{< relref path="./001-policy-updates.md" >}}).
  We've been looking at [Google's filtering doc](https://google.aip.dev/160) but
  it might be overkill.

- Bulk operations

  Custom methods can sometimes be used to provide bulk create/update/delete
  operations. If you find yourself needing this capability [let us know]({{<
  relref path="./001-policy-updates.md" >}}).

### Response Codes

- `200` - The request was successfully processed.

See also [Error Responses]({{< relref path="./004-payloads.md#errors" >}}) for
other other common response codes.

## Long Running Operations

When to use long running operation? Recommended by Google threshold > 10 sec.

See also: [Google’s Delete reference](https://google.aip.dev/151) as well as
[Google Cloud Long Running Operations reference](https://cloud.google.com/apis/design/design_patterns#long_running_operations).

Constraints:

- The api must support 3 methods:
  - Read operation by operation ID, see [Read](#read)
  - List of operations, see [List](#list)
  - Create operation, see [Create](#create)

- Operation ID must be of type UUID V4

- The request is not idempotent

- `Create` method must return response shape:
  ```
  {
    "name": "e6e38ae2-4af8-44c9-ba8a-3b2dc3d0fe28"
  }
  ```

- `Read` method must return response shape:
  ```
  {
    "name": "e6e38ae2-4af8-44c9-ba8a-3b2dc3d0fe28",
    "metadata": Any // TODO google recommends any, however, we might want to omit Any usage at all ,
    "done": boolean,
    "result(optional)": string,
    "error(optional)": string,
    "started_at": ISO date string
    "finished_at(optional)": ISO date string,
  }
  ```

- `List` method must return response shape:
  ```
  {"operations": [{operation1 here}, {operation2 here}]}
  ```
