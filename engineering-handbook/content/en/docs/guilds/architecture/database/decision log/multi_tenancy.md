---
title: "Multi-Tenant Isolation with Cloud Spanner"
linkTitle: "Spanner Multi-Tenant Isolation"
weight: 1
date: 2021-11-19
description: >
    *Isolation level when using Google Cloud Spanner to store the data of multiple clients*
---

{{% alert color="primary" %}}
[Google Cloud Spanner](https://cloud.google.com/spanner) offers [four patterns for storing data for mutliple customers](https://cloud.google.com/solutions/implementing-multi-tenancy-cloud-spanner) This section provides an explanation for the decision to use table-based isolation.
{{% /alert %}}

## Decision Criteria

### Cost

In general, Spanner cost is determined by your usage of an instance (amount of storage, number of operations) multiplied by the number of regions an instance spans. This is the lowest cost option, as instance and database-level isolation may result in requiring more instances. Further, no development costs are incurred during on-boarding of new clients, as no schema or infrastructure changes are needed (new clients are seamlessly added as new rows with a unique identifier).

_Verdict_: No associated cost.

### Isolation - Access

According to our contract analysis, there is no legal need for us to separate customer data in a certain way.

Since multi-tenant databases should be accessed from multi-tenant services, the problem of authorization will be present regardless of our data separation, and we must make sure to write our code so that customers are only given the appropriate data. Some separation models may make this easier with proper tools, but none give it to your for free.

_Verdict_: Not really a factor.

### Isolation - Performance

We're optimistic that performance issues can be avoided with [proper schema design](https://cloud.google.com/spanner/docs/whitepapers/optimizing-schema-design) due to Spanner being able to [adapt to the load](https://cloud.google.com/spanner/docs/schema-and-data-model#load-based_splitting). Further, Spanner can scale a table to any number of rows, provided the instance is configured with enough space (and even this can be automatically scaled).

_Verdict_: Performance should not be impacted.

### Agility

With no extra tools, Table-level separation makes migrating schemas, adding new customers, and handling connections much easier than any other level. (However, it would require every developer to write queries with the appropriate filters to get only the data they need.)

_Verdict_: Provides the most seamless on-boarding experience.

### Operations

Benefits:
* There are fewer instances and databases to deploy and manage.

Drawbacks:
* Some consideration needs to be made for the fact that we currently deploy in a staggered fashion, effectively using some retailers as "canaries" for the others. In this sense, schema changes will impact all retailers served by a single instance.
* Some additional logging and metric filtering may need to be created to adequately debug database operations for specific clients.

_Verdict_: Table-level isolation should not burden operations once we learn how to deal with the drawbacks.

[spanner]: https://cloud.google.com/spanner
[multi-tenancy]: https://cloud.google.com/solutions/implementing-multi-tenancy-cloud-spanner