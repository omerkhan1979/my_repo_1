---
title: "Observability"
linkTitle: "Observability"
weight: 2
date: 2021-12-17
description: >
  Policies and recommendations for observability 
---

## Recommended logging:

[Zap](https://github.com/uber-go/zap) - provides good structured logging support with flexible configuration

Use https://github.com/takeoff-com/go-log `zapx.NewWithServiceName` to create `*zap.SugaredLogger`.

Methods `zapx.NewWithServiceName`, `zapx.NewWithConfig` don't return error and have fall back logic in case logger creation fails. If you prefer to handle error by yourself, use `zapx.New`.

Benefits of using `github.com/takeoff-com/go-log/zapx`

- logger is configured to work with Google Cloud's operations suite
- covered by tests
- easy way to update by updating shared library

### Zap best practices

#### Structured logging

Use structured logging instead of string formatting. All methods of `SugaredLogger` ending in `w` accept variadic key-value pairs.

- [SugaredLogger.Infow](https://pkg.go.dev/go.uber.org/zap#SugaredLogger.Infow)
- [SugaredLogger.Warnw](https://pkg.go.dev/go.uber.org/zap#SugaredLogger.Warnw)
- [SugaredLogger.Errorw](https://pkg.go.dev/go.uber.org/zap#SugaredLogger.Errorw)
- [SugaredLogger.With](https://pkg.go.dev/go.uber.org/zap#SugaredLogger.With)

#### Pass logger as dependency

Creators of Zap advise passing `logger` as dependency.

- https://github.com/uber-go/zap/blob/master/FAQ.md#why-include-package-global-loggers
  > Avoid < global loggers > where possible.
- https://github.com/uber-go/zap/issues/924#issuecomment-789461851
  > We recommend using dependency injection, and passing *zap.Logger explicitly as part of constructors.

#### Zap example

Below configuration uses default NoOp implementation as a fallback, if failed to create a logger (should not happen in practice).

```go
logger, err := zapx.New(zapx.Config{
  ServiceName: "your-service-name",
})
if err != nil {
  log.Printf(`{"severity": "error", "message": "failed to initialize zap logger: %v"}`, err) // print as structured message to send to Error Reporting
  logger = zap.S() // fallback to default NoOp implementation
}
```

Log error
```go
if err != nil {
  logger.Errorw("failed to initialize metrics", zap.Error(err))
}
```

### CI configuration

Go uses Git to fetch dependencies. Configure Git to authorize via shared Github Personal Access Token before running `go` commands.

Google Cloud Build (if used) isn't able to access private repositories, so dependencies should be vendored.

#### Github Actions

```shell
- name: Set up Go
  uses: actions/setup-go@v3
  with:
    go-version: 1.16

- name: Configure access to download dependencies in Go
  run: git config --global url."https://${{ secrets.TAKEOFFBOT_TOKEN }}:@github.com/takeoff-com/".insteadOf "https://github.com/takeoff-com/"
  
- name: Vendor dependencies
  run: go mod vendor
```

See example of `composite` (reusable) [Github action](https://github.com/takeoff-com/products-audit/blob/1505f12532a126e0e8caef3f17dca51ee14f8ff4/.github/actions/vendor-dependencies/action.yml)

## Recommended tracing:

[Opencensus](https://opencensus.io) - https://pkg.go.dev/go.opencensus.io

Why? 
- officially supported by google https://cloud.google.com/monitoring/custom-metrics/open-census.
- see Architecture Decision Record [Use OpenCensus for metrics and tracing](https://github.com/takeoff-com/go-ppp/blob/master/adr/0001-use-opencensus-for-metrics-and-tracing.md)

Use https://github.com/takeoff-com/go-telemetry `opencensusx.InitTelemetryWithServiceName` to start sending OpenCensus metrics and traces to Google Cloud.

Example of usage [opencensusx.InitTelemetryWithServiceName](https://github.com/takeoff-com/go-telemetry/blob/fff96c419786df708d250f0282077ade58c0c6f4/examples/cmd/cloudrun/main.go#L43)

`go-telemetry` tries to use as minimal configuration as possible suitable for reuse for most services.

Google Cloud Load Balancer starts traces by itself, however if you need more traces change default tracing config.

```go
import (
  octrace "go.opencensus.io/trace"
)

func main() {
  opencensusx.InitTelemetryWithServiceName(logger, ServiceName, MetricRequestPerRetailerView)
  octrace.ApplyConfig(octrace.Config{
    DefaultSampler: octrace.ProbabilitySampler(0.25),
  })
}
```

#### Metrics declaration

``` golang
package metrics

import (
	"go.opencensus.io/stats"
	"go.opencensus.io/stats/view"
	"go.uber.org/zap"
)

var (
	// The latency in milliseconds
	EventDeliveryLatencyMs = stats.Float64(
		"webhook/events/delivery/latency",
		"The latency in milliseconds between event creation and successful delivery",
		stats.UnitMilliseconds,
	)

	EventDeliveryDelivered = stats.Int64(
		"webhook/events/delivery/total-delivered",
		"The latency in milliseconds between event creation and successful delivery",
		stats.UnitDimensionless,
	)
)

var (
	EventsDeliveryLatencyView = &view.View{
		Measure:     EventDeliveryLatencyMs,
		Description: "The latency in milliseconds between event creation and successful delivery",

		// Latency in buckets:
		// [>=0ms, >=25ms, >=50ms, >=75ms, >=100ms, >=200ms, >=400ms, >=600ms, >=800ms, >=1s, >=2s, >=4s, >=6s]
		Aggregation: view.Distribution(25, 50, 75, 100, 200, 400, 600, 800, 1000, 2000, 4000, 6000),
	}

	EventDeliveryDeliveredView = &view.View{
		Measure:     EventDeliveryDelivered,
		Description: "The total number of successfully delivered events",
		Aggregation: view.Count(),
	}
)

func RegisterMetrics() {
	if err := view.Register(EventsDeliveryLatencyView); err != nil {
		zap.S().Fatalf("Failed to register the view: %v", err)
	}

	if err := view.Register(EventDeliveryDeliveredView); err != nil {
		zap.S().Fatalf("Failed to register the view: %v", err)
	}
}
```

#### Recording of stats

``` golang
stats.Record(ctx, metrics.EventDeliveryLatencyMs.M(float64(diff)/float64(time.Millisecond)))
stats.Record(ctx, metrics.EventDeliveryDelivered.M(1))
```

Example of custom metric view
![Screenshot 2021-12-03 at 16 13 56](https://user-images.githubusercontent.com/9500802/144616773-bd6d994b-7b85-4453-a214-989fe639e9c8.png)

#### Start tracing span

``` golang
	ctx, span := trace.StartSpan(ctx, "scope.name")
	span.AddAttributes(
		trace.Int64Attribute("page", int64(pageNumber)),
		trace.Int64Attribute("rows", int64(rowsPerPage)))

	defer span.End()
```

Trace view

![Screenshot 2021-12-03 at 16 19 48](https://user-images.githubusercontent.com/9500802/144617673-0bed3966-0367-47e9-8e94-b299b7ed8402.png)

Google Cloud Load Balancer adds header [`X-Cloud-Trace-Context`](https://cloud.google.com/trace/docs/setup#force-trace).

To have end-2-end traces including Google Cloud Load Balancer, start trace from `http.Request` using `github.com/takeoff-com/go-telemetry/sdpropagation.StartSpanWithRemoteParentFromRequest`.

```go
import (
  "github.com/takeoff-com/go-telemetry/opencensusx"
  "github.com/takeoff-com/go-telemetry/sdpropagation"
)

func(w http.ResponseWriter, r *http.Request) {
  ctx, span := sdpropagation.StartSpanWithRemoteParentFromRequest(r, SpanNamePrefix+"getProductChangesMethodGet")
  defer span.End()
}
```

## Roadmap

Approach to metrics and tracing aren't solved completely yet at Takeoff and in general.

### OpenCensus vs OpenTracing

OpenTracing library is declared to be future of metrics and tracing, however:

1. Metrics functionality of OpenTracing is still in early stages of development being basically unusable last time checked.
2. Google Cloud Go SDK uses OpenCensus for tracing, so we would lose a lot of information if instrument with OpenTracing.
3. See [Use OpenCensus for metrics and tracing](https://github.com/takeoff-com/go-ppp/blob/master/adr/0001-use-opencensus-for-metrics-and-tracing.md) for more details on this.

### Pass trace header when calling other internal services

It's possible to pass tracing data between services in Stackdriver format, however this needs further investigation.

Probably, wrapper method of [`contrib.go.opencensus.io/exporter/stackdriver/propagation.HTTPFormat.SpanContextToRequest`](https://github.com/census-ecosystem/opencensus-go-exporter-stackdriver/blob/5a007e3a208d86e384994b441f297c800c492c1e/propagation/http.go#L90) should be added to `github.com/takeoff-com/go-telemetry/sdpropagation` similar to `sdpropagation.StartSpanWithRemoteParentFromRequest`.

### Force trace to be sampled

Patterns around using `Span` and `SpanContext` need further investigation, particularly forcing trace to be sampled.

### Establishing connection between traces and logs

Logs should include `trace` field as described in [Integrating with Cloud Logging](https://cloud.google.com/trace/docs/trace-log-integration) to establish connection between traces and logs.

### Example of trace attributes

It would be good to add illustration of benefits using trace attributes.

### Example of cross project tracing

Cross GCP project traces should work out-the-box (see [Viewing traces across projects](https://cloud.google.com/trace/docs/cross-project-traces)).

It would be good to start propagating trace header in all services and get example of such cross project traces.