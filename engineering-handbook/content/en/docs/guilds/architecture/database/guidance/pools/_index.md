---

# (@formatter:off)
title: "Connection Pooling"
linkTitle: "Connection Pooling"
weight: 3
description: >
    *Guidance for using database connection pools.*
# (@formatter:on)
---

{{% alert color="primary" %}}

Connection pool software manages a number of open, reusable database connections for an application.

Covered on this page:

- Why is connection pooling a good practice?
- Guidance for configuring connection pools.

{{% /alert %}}

{{% alert color="info" %}}
This chart taken from MAF shows how being mindful of pool configurations could help the system as a whole. Notice how idle (pink) and active (green/orange) connections far exceed the transactions all services actually request (blue).

![TPS vs. Connections](/images/en/docs/Guilds/Architecture/Database/Pools/tps_vs_connections.png)
{{% /alert %}}

## Benefits

Keeping a pool of pre-made, open connections for your application to use is probably always a good 
idea. It has these benefits:

- Most DBMS systems limit the number of connections available to clients at any one time.
  Applications attempting to connect to the database once the limit has been reached will receive an
  error. A connection pool can throttle application requests to reduce the chance of exceeding the
  limit.
- Establishing and terminating connections takes time and system resources. Keeping a small number
  of reusable connections alive spreads this overhead across all requests, lowering the per-request
  cost.
- Limiting the number of simultaneous jobs in the database can help overall performance (see the
  next section).

## Configuration Guidance

It's important to configure your connection pool appropriately for your application to get the
benefits listed above. This section contains guidance for determining values for the most important settings.

{{% alert title="Before you begin" color="warning" %}}

The configuration of your database pool can impact the performance and stability of your
application _and_ other applications sharing the database instance. Keep the following in mind as
you make your choices:

* Our Postgres instances limit the number of connections to 500 by default.
* All services share a single Postgres instance for a given retailer (at least for now).
* An in-process pool configuration will apply to _each instance_ of your application (e.g., if you
  set a pool size of 10 and have 2 replicas, you will actually be creating 20 connections).
* The characteristics of your application's interactions with the database may shape your decisions. Inspect the ["Cloud SQL Database - Number of transactions" GCP Metrics](https://console.cloud.google.com/monitoring/metrics-explorer?project=takeoff-maf) for the target database, which are measured in transactions per minute. (You may also want to inspect read and write statistics, existing connections, etc.)

{{% /alert %}}

### Single vs. multiple pools

* Most applications should maintain a single pool by default.
* If your application has a wide range of database interactions, create separate
  pools for them. For example, if most of your queries take milliseconds, but some jobs take seconds
  or minutes, each type should have a separate pool to avoid starving the fast transactions of
  connections. You may also bucket your pools based on time-sensitive/insensitive workflows.
  * This part is mostly "know your application," but you can gather metrics by inspecting [PostgresDB Metrics - Grafana][pggrafana] or other duration metrics specific to your services and jobs.

### Maximum number of connections

This setting limits the number of open connections held by your application at any one
time.

{{< tabpane_md >}}
  {{< tab_md header="PostgreSQL" >}}

***Guidance***
* Default to a maximum of 10 connections _total_ for all application instances.
* Reduce this number if your application does not handle many simultaneous requests for work (e.g.,
  concurrent user requests, Pub/Sub messages).
  * Utilize GCP metrics explorer (see above).
  * Keep scalability in mind - this number will increase as sites are added.
  * See [benchmarks]({{< relref "benchmarks" >}}) to guide your decisions.

***Reasoning***

Keep this number fairly low to reduce the chance of hitting the max connection limit on shared Postgres instances. Further, most of our databases record a few thousand transactions per minute at peak times; a pool of 10 connections can handle around 80,000 transactions per minute, given 80 clients attempting to concurrently perform a seven-statement transaction.

  {{< /tab_md >}}

  {{< tab_md header="Spanner" >}}
***Guidance***

Use the [Go library](https://pkg.go.dev/cloud.google.com/go/spanner#SessionPoolConfig) defaults unless we find a reason to change them.
  {{< /tab_md >}}
{{< /tabpane_md >}}

{{% alert title="Nested Transactions" color="warning" %}}
If your application has nested transactions, the maximum number of connections ***must*** be at least the number of concurrently running transactions (parent transaction + sub-transactions). Otherwise, your process will deadlock waiting for connections that will never come.
{{% /alert %}}

### Minimum number of idle connections

This setting determines the number of idle connections waiting to be used by the application.

{{< tabpane_md >}}
  {{< tab_md header="PostgreSQL" >}}
***Guidance***
In general, look at your transaction metrics. Is the line smooth or spikey? Are the spikes close together or quite spread out? Are the spikes modest or huge?

If your application's transaction counts are...
* fairly consistent or spike in a moderate range, set the minimum number equal to maximum connections.
  * Default when in doubt.
  * Example: Sinfonietta is generally between 1,000 and 4,000 transactions per minute for most of the day.
* usually low with infrequent, higher-volume periods, set this number to a small fraction of maximum connections.
  * Example: Fulfillment Orchestrator hovers around 100 transactions per minute, but may briefly spike to 7,000 during pick windows. It might have a max pool of 10 and a minimum pool of 2.

***Reasoning***

Idle connections can [negatively impact pool performance](https://aws.amazon.com/blogs/database/performance-impact-of-idle-postgresql-connections/) and reduce the number of available connections. Most of our internal application workflows can withstand some startup overhead entering peak times without a substantive impact on overall system performance. For applications with more consistent work patterns, frequently opening and closing connections is more likely to negatively impact both client and server.

  {{< /tab_md >}}

  {{< tab_md header="Spanner" >}}
***Guidance***

Use the [Go library](https://pkg.go.dev/cloud.google.com/go/spanner#SessionPoolConfig) defaults
unless we find a reason to change them.
    {{< /tab_md >}}
{{< /tabpane_md >}}

### Lifetime of idle connections

This setting determines how long idle connections live without activity.

{{< tabpane_md >}}
{{< tab_md header="PostgreSQL" >}}
***Guidance***

10 minutes, which is probably the default for your pool library.

***Reasoning***

This lets idle connections live long enough to ensure a spike in traffic has died down.

{{< /tab_md >}}

{{< tab_md header="Spanner" >}}
***Guidance***

Use the [Go library](https://pkg.go.dev/cloud.google.com/go/spanner#SessionPoolConfig) defaults
unless we find a reason to change them.
{{< /tab_md >}}
{{< /tabpane_md >}}

## Pool Libraries

{{< tabpane_md >}}
{{< tab_md header="PostgreSQL" >}}
* ***Clojure:*** Use [hikari-cp](https://github.com/tomekw/hikari-cp), which is based on the [popular Java library](https://github.com/brettwooldridge/HikariCP) of the same name.
* ***Go:*** Both the [standard SQL package](https://pkg.go.dev/database/sql#pkg-variables) and [pgx](https://github.com/jackc/pgx/wiki/Getting-started-with-pgx#using-a-connection-pool) have connection pool capabilities.

{{< /tab_md >}}

{{< tab_md header="Spanner" >}}
Use the [Go library](https://pkg.go.dev/cloud.google.com/go/spanner#SessionPoolConfig).
{{< /tab_md >}}
{{< /tabpane_md >}}

## Metrics

* Metrics on connections and transactions can be obtained through [GCP Metrics Explorer][gcpmetrics].
* For greater visibility into hikari performance, you should also export [Prometheus metrics](https://www.codetd.com/en/article/7669942). See service-catalog as an example of this:
  1. [Initialize and expose the prometheus registry](https://github.com/takeoff-com/service-catalog/blob/master/service/src/main/clj/service_catalog/app_info/metrics.clj)
  2. [Add prometheus registry to pool configuration](https://github.com/takeoff-com/service-catalog/blob/master/service/src/main/clj/service_catalog/db.clj)
  3. [Create dashboard to visualize](https://grafana.tom.takeoff.com/goto/V1ujXQEnk?orgId=1)

{{% alert color="info" %}}
The way we export and visualize these metrics will likely change as we move to more GCP-native metrics and dashboards, Spanner usage, and Go.
{{% /alert %}}


## References

- [About Pool Sizing (HikarCP)][poolsize]
- [Performance Impact of Idle PostgreSQL Connections][idleconnectionsaws]

[poolsize]: https://github.com/brettwooldridge/HikariCP/wiki/About-Pool-Sizing

[idleconnectionsaws]: https://aws.amazon.com/blogs/database/performance-impact-of-idle-postgresql-connections/

[gcpmetrics]: https://console.cloud.google.com/monitoring/metrics-explorer?project=takeoff-maf

[hikari-cp]: https://github.com/tomekw/hikari-cp

[benchmarks]: {{< relref "benchmarks" >}}

[pggrafana]: https://grafana.tom.takeoff.com/goto/nKBLhhy7k?orgId=1
