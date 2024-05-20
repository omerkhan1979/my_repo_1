---
title: "Linting"
linkTitle: "Linting"
weight: 3
date: 2021-12-17
description: >
  Policies and recommendations for linting 
---

# Recommended linting tool & configuration

[golangci-lint](https://github.com/golangci/golangci-lint) - defacto standard linting tool 

Sample linting configuration.

{{% alert %}}
Feel free to enable/disable linters you think fit best in your specific project with provided explanation 
{{% /alert %}}

``` yaml
modules-download-mode: readonly

linters:
  enable-all: true
  disable:
    - varnamelen
    - nilnil
    - gochecknoglobals
    - funlen
    - goerr113
    - gci
    - paralleltest
    - forbidigo
    - gofumpt
    - exhaustivestruct
    - nolintlint
    - tagliatelle
    - wrapcheck
    - scopelint
    - gochecknoinits
    - goimports
    - maligned
    - godot
    - prealloc
    - gocritic
    - interfacer
    - golint
    - godox

linters-settings:
  gomnd:
    settings:
      mnd:
        checks: case,condition,return

issues:
  exclude-rules:
    - path: _test\.go
      linters:
        - testpackage
        - maligned
        - dupl
    - linters:
        - gosec
      text: "G401: "
    - linters:
        - gosec
      text: "G505: "

```

How to run - execute following command in the root of your module

``` bash
golangci-lint run
```

## Static checks

[static-check](https://staticcheck.io) - tool for static check for golang  

How to run - execute following command in the root of your module

``` bash
staticcheck -checks=all ./...
```

## Style

[Effective Go](https://golang.org/doc/effective_go) is an obvious starting point

And [Google](https://github.com/golang/go/wiki/CodeReviewComments) & [Uber](https://github.com/uber-go/guide/blob/master/style.md) style guides are good extensions.


##### Gofmt

From [Google Code Review Comments](https://github.com/golang/go/wiki/CodeReviewComments#gofmt):

> Run [gofmt](https://golang.org/cmd/gofmt/) on your code to automatically fix the majority of mechanical style issues. Almost all Go code in the wild uses gofmt. The rest of this document addresses non-mechanical style points.

> An alternative is to use [goimports](https://godoc.org/golang.org/x/tools/cmd/goimports), a superset of gofmt which additionally adds (and removes) import lines as necessary.

How to run - execute following command in the root of your module

``` bash
gofmt -s -w .
```
