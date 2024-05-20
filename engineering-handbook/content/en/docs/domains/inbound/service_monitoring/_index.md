---
title: "Service Monitoring"
linkTitle: "Service Monitoring"
date: 2022-10-12
weight: 1
---

| Metric                                                 | Deviation Criteria                                                                                                                                                                                                                                                |
|--------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Endpoint Latency                                       | Latency got bigger.                                                                                                                                                                                                                                               |
| Endpoint Response Fails (HTTP 500)                     | Occurrences                                                                                                                                                                                                                                                       |
| Endpoint Response Fails (HTTP 400)                     | Trend Increased by %%                                                                                                                                                                                                                                             |
| GCP Pub/Sub Subscription Delivery Latency Health Score | https://cloud.google.com/pubsub/docs/monitoring#delivery_latency_health</br> Precalculated health scores for: ack_latency, expired_ack_deadlines, nack_requests, seek_requests, and utilization.                                                                  |
| GCP Pub/Sub Subscription Number of unacked messages    | If number of messages growing steep - system is under load and unable to process this number of messages                                                                                                                                                          |
| GCP Pub/Sub Subscription Oldest Unacked Messages Age   | If Age reached the retention period of Subscription - we have a data loss.</br> If the retention period is in days, and the age of the message is growing steep along with the number of unacked messages - the system is unable to process messages efficiently. |
| GCP Pub/Sub Subscription ACK Latency                   | Trend Increased by %%</br> Subscribers are slow in processing.                                                                                                                                                                                                    |

## What is SLO?
**SLO** (Service Level Objectives) is an agreement within an SLA about a specific metric like uptime or response time.
So, if the SLA is the formal agreement between you and your customer, SLOs are the individual promises you’re making 
to that customer. 
SLOs are what set customer expectations and tell engineering teams what goals they need to hit and measure 
themselves against.

	SLA = SLO + consequences (what would happen if SLO would not be met)

Existing services can produce a number of metrics, but how to choose the right one?
We should ask our clients what metrics are important for them:
upstream services that actively using HTTP interfaces, probably, would like to have a predictable latency and 
throughput metrics
when other part of the system depends on the data, probably, they would be interested in end-to-end latency

Picking right metrics for SLO is a non-pure technical task, product & business should be involved.
SLO should be easy to measure.
There is no need for a huge number of SLOs, in this case the team can lose focus on making the system better.
You probably would need 1 - 2 most important metrics per service, that could help qualify for SLO status.
It is better to have SLO objectives spelled in plain language to make sure everyone in the company knows what & why 
we are measuring, they should always account for issues such as client-side delays.
Having SLOs for those internal systems is an important piece of not only meeting business goals but enabling internal 
teams to meet their own customer-facing goals.

Start by thinking about (or finding out!) what your users care about, not what you can measure.
Often, what your users care about is difficult or impossible to measure, so you’ll end up approximating users’ needs in 
some way.
However, if you simply start with what’s easy to measure, you’ll end up with less useful SLOs.
As a result, we’ve sometimes found that working from desired objectives backward to specific indicators works better 
than choosing indicators and then coming up with targets.

## HTTP
### Endpoint Latency

Most web services have a lot of endpoints.
These endpoints are consumed by other services.
In modern microservice architecture systems, sum of latencies from all endpoints is a result of how user-facing service 
process requests.
When one endpoint of downstream services is getting degraded, this can cause side effects for upstream services that 
can affect user experience or fail.

Latency is one of the health indicators of the service.
When response latency of the endpoint is getting bigger (f.e. Response latency becomes twice as bigger then before), 
this is a marker that something went wrong and we Engineering Team should investigate the reason for such deviant 
behavior.

**SLO example:**
>99% of the <GET> request for <the endpoint> is completed below <100> milliseconds, for the last <10 minutes>
{{< imgproc http_latency Resize "500x" >}}
{{< /imgproc >}}

### Endpoint Response Fails (HTTP 5xx, 4xx)
Normally service should never fail with HTTP 500.
Normally it can fail with HTTP 4xx as a reaction to improper client request data, authentication or etc.
But when the number of HTTP 4xx errors rise in trends, probably something could go wrong with the communication 
contract.
This is a marker for the Engineering team to investigate the reason.


**SLO example:**
> 90% of request completed successfully, for the last <14 days>

>Less than 5% of request with status <403/401> appeared, for the last <14 days>

>Less than 5% of request with status <400> appeared, for the last <14 days>

>Less than 1% of request with status <500> appeared, for the last <14 days>

### Endpoint Request Size
Request size can be useful during investigation of high latency.
E.x.: Request size got bigger, and service responded slowly. Which can help provide fix faster.

## GCP Pub/Sub Subscription
### Delivery latency health score
{{< imgproc delivery_health_scores Resize "500x" >}}
{{< /imgproc >}}

“Delivery latency health score” is a proprietary metric introduced by Google.
The metric allows us to check how Pub/Sub consumers are efficient with processing messages.
Engineers can use these metrics to identify reasons that can affect message delivery (ack) latency.

We can define alert policies that would help us react when the system is under heavy load.

See https://cloud.google.com/pubsub/docs/monitoring#delivery_latency_health for more information

### Number unacked messages
{{< imgproc number_unacked_messages Resize "500x" >}}
{{< /imgproc >}}

metrics provided by gcp pub/sub that can help react in cases when consumer(s) for some reason are unable to process
messages efficiently and number if messages are getting much faster than expected.
can be caused by a bigger number of messages, or system performance degradation, or system down.
this is a marker to investigate system behavior.
it’s hard to use for sli, but this can be used for additional monitoring and investigation.

see https://cloud.google.com/pubsub/docs/monitoring#monitoring_the_backlog for more information

### Oldest Unacked Messages Age
{{< imgproc oldest_unacked_messages_age Resize "500x" >}}
{{< /imgproc >}}

Metrics provided by GCP Pub/Sub that can help react on cases when consumer(s) for some reason are unable to process 
messages in time.
Can be caused by system performance degradation, or system down, or messages crashing processing.
This is a marker to investigate system behavior.

**SLO example:**

Our SLA:
> System processing 100k messages less than in 1 hour

Let's try to calculate possible value for this metric.

Threshold Value depends on how fast a topic is filled with messages.

| Parameter                            | Value        |
|--------------------------------------|--------------|
| Grouping                             | `1 minute`   | 
| Push rate, avg.                      | `12,000/min` |
| Expected processing rate base on SLO | `1,667/min`  |

    12000 / 1667 =~ 8

`8 times` we need to pull data to process it. `8 times` is approximately `8 minutes` to pull the "wave"

Last items in the wave would wait the long of the wave and the time that would ne spend on processing previous items, 

    1/2 * x * (x + 1) =~ 36

So, result SLo is:
> Oldest unacked message age should be less <36 minutes>

We can say that a message waiting in the queue no longer than 36 minutes, 
is would be a marker that we would violate total processing time, because messages are stuck in queue.

See https://cloud.google.com/pubsub/docs/monitoring#monitoring_the_backlog for more information

### Subscription ACK Latency
{{< imgproc subscription_ack_latency Resize "500x" >}}
{{< /imgproc >}}

Metrics provided by GCP Pub/Sub that can help react on cases when consumer(s) for some reason are started process 
messages slow.
Can be caused by system performance degradation.
This is a maker to investigate system behavior.

**SLA example:**
System processing 100k messages less then in 1 hour

**SLO example:**
3, 600, 000 ms / 100 000 items = 36 ms per item

> Acknowledgement of an item should be less than <36ms>

If we acknowledge items one by one, if we process batches, we probably need to pick a bigger number.
e.x. system processing batches of 100.

> Acknowledgement of an item should be less than <3.6s>

See https://cloud.google.com/monitoring/api/metrics_gcp#gcp-pubsub for more information about the metric itself.

### Subscription Pull Requests
We need to measure Throughout, we can use the “Number of Ack Messages” rate, but when we receive a small number of 
messages the rate will be low, and we will receive False Alert at 3 a.m.

For cases when our workers try to consume messages from the Subscription we can monitor how efficiently our workers 
pull data from Subscription with the “Subscription Pull requests” metric, that tracks all requests that our workers 
do to pull data from Subscriptions.

When a subscription is empty, workers would pull data faster.
When messages arrive the rate will go down.
Our task here is to identify a proper Threshold Level and Time Window to trigger an alert.
To set up Threshold Level and Window we should use historical data to identify acceptable pull request rate for our 
system for our SLI/SLO.

Let’s check some examples.

**Example 1. Healthy system. Autoscaling.**

Every morning the system receives data to process.
System has auto-scaling configuration and adding workers to process incoming data more efficiently.
{{< imgproc pull_requests_example1 Resize "900x" >}}
{{< /imgproc >}}

**Example 2. Unhealthy system. Workers reduce pull request rate.**

After September 8, something went wrong and the system stopped working efficiently.
Pull Request rate dropper at least twice.
{{< imgproc pull_requests_example2 Resize "900x" >}}
{{< /imgproc >}}

**Example 3. System unable to process pull of data.**

Workers got stacked or down on August 24 and 26.
System was fixed only on August 31, because the team had not configured the monitoring system.
{{< imgproc pull_requests_example3 Resize "900x" >}}
{{< /imgproc >}}

## Metrics Reading Materials
- https://www.atlassian.com/incident-management/kpis/sla-vs-slo-vs-sli
- https://sre.google/sre-book/service-level-objectives/
- https://cloud.google.com/pubsub/docs/monitoring#maintain_a_healthy_subscription
- https://cloud.google.com/apigee/docs/api-monitoring
- https://sre.google/sre-book/monitoring-distributed-systems/#xref_monitoring_golden-signals
- https://cloud.google.com/monitoring/api/metrics_gcp#gcp-loadbalancing
- https://cloud.google.com/monitoring/api/metrics_gcp#gcp-pubsub
- https://cloud.google.com/monitoring/api/metrics_gcp#gcp-run
- https://cloud.google.com/stackdriver/docs/solutions/slo-monitoring
- https://static.googleusercontent.com/media/sre.google/en//static/pdf/art-of-slos-handbook-letter.pdf

## Dashboards
### GCP Dashboards
How to create a custom dashboard - https://cloud.google.com/monitoring/charts/dashboards

Create Dashboard for every client staging, UAT, prod via terraform.  https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/monitoring_dashboard
It’s better to create Dashboard via UI (Console), get JSON layout there and use it in terraform.

#### Pub/Sub Charts
Not so long ago GCP started adding more charts for PubSub Subscription & Topic.
{{< imgproc subscription_default_metrics Resize "500x" >}}
{{< /imgproc >}}

So it would be easier to grab some charts from there for your Dashboard.

Charts that can be useful:
 - Delivery latency health score (For more info https://cloud.google.com/pubsub/docs/monitoring#delivery_latency_health)
 - Oldest unacked message - can help monitor how well your service with processing the queue, and it there any message got stack because of some unhandled error on the worker (For more info https://cloud.google.com/pubsub/docs/monitoring#monitoring_the_backlog)
 - Ack latencies - help you monitor how your workers are fast with processing messages.
 - Number undelivered (unacked) messages would help you monitor the queue size 

#### HTTP Charts 
##### Load Balancer https://cloud.google.com/monitoring/api/metrics_gcp#gcp-loadbalancing
Metrics that would be useful:
 - https/total_latencies
 - Can use to track latencies
 - Can filter by response_code_class to minotaur 4xx, 5xx, 2xx, etc. responses
 - Can use matched_url_path_rule to filter by URL Path to create alerts/SLO for different URLs
 - https/request_bytes_count
 - It good to know how requests are heavy
 - https/response_bytes_count
 - It good to know how responses are heavy, in case of high latency

Example:
 - https://github.com/takeoff-com/products-audit/blob/13f30227e3da89feeee9e96be8592078a9809dc6/terraform/modules/observability/observability.tf#L13
{{< imgproc cloud_function_load_balancer_example_dashboard Resize "900x" >}}
{{< /imgproc >}}

### Grafana Dashboards
Manual from SRE Team how to use Grafana in Takeoff https://takeofftech.atlassian.net/wiki/spaces/SE/pages/1425703538/Grafana

#### HTTP endpoints dashboard - Grafana
Example:
 - https://github.com/takeoff-com/grafana/blob/master/dashboards/asmt/distiller-api.yaml
 - https://grafana.tom.takeoff.com/d/distiller-api/distiller-api?orgId=1&refresh=1m&var-datasource=Prom%20Abs%20Prod&var-env=prod&var-client=abs
{{< imgproc grafana_dashboard_example Resize "900x" >}}
{{< /imgproc >}}





