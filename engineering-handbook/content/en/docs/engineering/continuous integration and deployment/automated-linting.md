---
title: "Automated Linting"
linkTitle: "Automated Linting"
weight: 7
date: 2022-05-26
description: >  
---

## Automated Linting

### Purpose

**Linting** - Code linting is an important part of catching problems with code early, and keeping it readable and supportable as time goes on.
**Automated Linting** - When used as a gate for Pull Requests, we can ensure that our code standards for linting are followed.

### Tools

#### GOLANG

**golangci-lint** - GO seems to follow the unix mentality and has a plethora of different tools that each do a single thing. The golangci-lint project has gathered a good suite of popular tools together to be used specifically in continuous integration.

For documentation and examples, please see [the repository](https://github.com/golangci/golangci-lint-action)!

#### Python

**black** - Python black is a very opinionated and heavy handed tool that covers linting as well as code style and formatting. This removes the thinking part from our hands, which is nice.

For documentation and examples, please see [here](https://black.readthedocs.io/en/stable/integrations/github_actions.html)! Code can be found in [the repository](https://github.com/psf/black)!

### Enforcement

We recommend that these tools be used in a GitHub Action to hard gate pull requests in repositories that utilize Go or Python. Linting code is very fast and there really is no excuse for not fixing the problems that they find.
