---
title: "go-telemetry"
linkTitle: "go-telemetry"
weight: 1
date: 2022-08-21
description: (**internal**) Metrics and tracing

---

https://github.com/takeoff-com/go-telemetry

Methods to start reporting [OpenCensus](https://opencensus.io) metrics and traces to Google Cloud.

Usage:
```shell
go get github.com/takeoff-com/go-telemetry
```

See [Recommended tracing](/docs/guilds/architecture/go/guidelines/observability/#recommended-tracing)

Examples:
- https://github.com/takeoff-com/go-telemetry/blob/fff96c419786df708d250f0282077ade58c0c6f4/examples/cmd/cloudrun/main.go
- https://github.com/takeoff-com/products-audit/blob/13f30227e3da89feeee9e96be8592078a9809dc6/cloud-functions/get-product-changes/entrypoint.go#L43

Metrics based alerts and SLO (terraform)
- https://github.com/takeoff-com/products-audit/blob/13f30227e3da89feeee9e96be8592078a9809dc6/terraform/modules/observability/observability.tf
