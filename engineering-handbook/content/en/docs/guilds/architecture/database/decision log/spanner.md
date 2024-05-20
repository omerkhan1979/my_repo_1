---
title: "Using Google Cloud Spanner"
linkTitle: "Cloud Spanner"
weight: 1
date: 2021-11-01
description: >
    *Decision to use Google Cloud Spanner*
---

{{% alert color="primary" %}}
[Google Cloud Spanner](https://cloud.google.com/spanner) is Google's fully-managed relational DBMS
and the relational database of choice at Takeoff. This section provides reasonsing on this decision.
{{% /alert %}}

## Why Spanner?

The Architecture Guild decided on Spanner based on this hypothesis: we will spend less time
maintaining databases and _more time developing valuable new features for our clients_. We weighed
Spanner against our current paradigm of running [PostgreSQL][pgsql] in [CloudSQL][cloudsql] and 
determined that the benefits outweigh the drawbacks, particularly as the organization scales. We
believe that Spanner offers the lowest long-term labor costs to achieving multi-tenant solutions,
high availability, and scalable global offerings. Here are a few key benefits:

* Automatic data sharding
  * performs automatic optimization by sharding data based on usage (provided schemas are designed
  correctly)
* Global, external, strong consistency
  * manages read and write replicas on a global scale with external, strong consistency
* Cross-regional high availability and disaster recovery
  * automatic disaster recovery fail-over across regions
* Automatic retention policy
  * rows can be logically discarded automatically to reduce storage costs and avoid performance 
  degradation

While it is certainly true that we could achieve these benefits with Postgres/CloudSQL, we would
likely spend a good deal of developer time to implement, debug, and maintain them. There are of
course drawbacks to using a new system, but we believe these costs will diminish over time:

* Learning curve
  * Spanner is SQL-compliant, but there are patterns and features that developers will need to be
  aware of in order to use it appropriately. Spanner's [PostgreSQL interface][pg-interface] will
  likely help with this transition.
* Development tooling
  * The ecosystem for tools (e.g., schema management, code generators) is not as large as for more
    established DBMS. That is not to say that tools don't exist however, and this gap will likely
    narrow over time with Google's resources behind it.
* Monetary cost
  * Spanner is marginally more expensive than CloudSQL, and developers have often cited this as a
    point of contention. We must, however, account for total cost when making this decision: the
    cost of developers to maintain similar functionality and the opportunity cost of developing the
    features that generate revenue. If our aim is to reduce cost, our efforts would be better spent
    eliminating waste from expensive practices that produce less value (e.g., indiscriminate
    logging).
  * If you're still curious, see the [Spanner Pricing Sheet][spanner-pricing] or play around with
    the [Pricing Calculator][price-calc].

[spanner]: https://cloud.google.com/spanner

[cloudsql]: https://cloud.google.com/sql

[pgsql]: https://www.postgresql.org/

[pg-interface]: https://cloud.google.com/blog/topics/developers-practitioners/postgresql-interface-adds-familiarity-and-portability-cloud-spanner

[spanner-pricing]: https://cloud.google.com/spanner/pricing

[price-calc]: https://cloud.google.com/products/calculator
