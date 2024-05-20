---
title: "General"
linkTitle: "General"
weight: 1
date: 2021-09-10
description: >

---

## Go Programming Language

Official [Go site](https://go.dev) states:
> The Go programming language is an open source project to make programmers more productive.

> Go is expressive, concise, clean, and efficient. Its concurrency mechanisms make it easy to write programs that get the most out of multicore and networked machines, while its novel type system enables flexible and modular program construction. Go compiles quickly to machine code yet has the convenience of garbage collection and the power of run-time reflection. It's a fast, statically typed, compiled language that feels like a dynamically typed, interpreted language.

## Style

We strive to write idiomatic Go. You should be familiar with [Effective Go](https://go.dev/doc/effective_go) and it's prerequisite reading.

[Google](https://github.com/golang/go/wiki/CodeReviewComments) & [Uber](https://github.com/uber-go/guide/blob/master/style.md) style guides provide useful additional content.

##### Gofmt

From [Google Code Review Comments](https://github.com/golang/go/wiki/CodeReviewComments#gofmt):

> Run [gofmt](https://golang.org/cmd/gofmt/) on your code to automatically fix the majority of mechanical style issues. Almost all Go code in the wild uses gofmt. The rest of this document addresses non-mechanical style points.

> An alternative is to use [goimports](https://godoc.org/golang.org/x/tools/cmd/goimports), a superset of gofmt which additionally adds (and removes) import lines as necessary.
