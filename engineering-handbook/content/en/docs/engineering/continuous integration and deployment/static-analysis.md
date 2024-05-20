---
title: "Static Analysis"
linkTitle: "Static Analysis"
weight: 7
date: 2022-05-31
description: >  
---

## Static Analysis

### Definition

**Static Analysis** - Static analysis is the process of analyzing code directly without compiling and running it. This includes things like [linting]({{< relref path="./automated-linting.md" >}}), coding style and automated documentation, code complexity, metrics and other more in depth procedures.

### Purpose

Static analysis allows us to find potential problems in code, enforce coding standards, run some basic tests and generate documentation. This can be done automatically and very quickly.

### Tools

#### SonarQube

We currently use [SonarQube](https://sonarqube.tom.takeoff.com/) for collecting results of static analysis of our codebase. Please check [our writeup](https://takeofftech.atlassian.net/wiki/spaces/DEVENA/pages/1902936308/SonarQube) for straightforward examples or refer to [the docs](https://docs.sonarqube.org/) if you can't find what you need. Remember to update our documentation with poigant examples when necessary!

### Enforcement

We recommend that SonarQube be integrated into all existing projects. It provides support for all languages that we use here at Takeoff, and is not difficult to add CI support via a GitHub Action. We currently require Unit Test coverage to be >=80% and build will fail if this is not met.
