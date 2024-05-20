---
title: Precedent
linkTitle: Precedent
weight: 2
date: 2021-09-10

description: When & how to decide to adopt API policy with legacy systems

---

We maintain many systems that do not comply with the current policy. There are a
few reasons this can happen which aren't critical to discuss here. If the API is
live and not using best practice, you have to figure out how and when to use
best practice as you make changes to that API.

Google describes this well in [their own document on Precedent](https://google.aip.dev/200).

When intentionally going against policy, the API specifications should include
documentation indicating what the more "correct" choice would have been and why
it was chosen to be different.

Example: documenting divergent `itemId` schema.
```
components:
  schemas:
    Line:
      type: object
      # The item is itemId here but should be `item_id`. This was done to be
      # consistent with ExternalSpec#123 which sends us itemId instead.
      properties:
        itemId:
          type: string
        requested_quantity:
          type: integer
          minimum: 1
```

As increments are made to an API it should try to maintain consistency across
resources and payloads, even if it would violate the policy. Similarly, in order
to refactor an API into a new implementation, it may also be necessary to wrap
or emulate non compliant APIs so that clients will not have to change.  These
decisions should be documented in the API specification.

Example: [Policy dictates
`create_time`](http://engineering-handbook.takeofftech.org/docs/guilds/architecture/restful-api/design-guide/004-payloads/#common-attributes)
for when a resource was created, but an API already used `created_datetime` for
  one resource, resources in the same API should use `created_datetime` to be
  internally consistent.

In cases where an API must comply with some external standards (e.g. to
integrate with another system we do not control) the API should document what
that external standard is and why it is chosen.

To break the cycle of non-compliance it is likely that you will have to create a
new [API version]({{< relref path="006-versioning.md" >}})

