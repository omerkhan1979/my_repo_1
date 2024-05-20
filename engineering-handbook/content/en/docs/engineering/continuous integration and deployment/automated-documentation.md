---
title: "Automated Documentation"
linkTitle: "Automated Documentation"
weight: 7
date: 2022-06-17
description: >
---

## Overview

**Automated Documentation** is the process of adding metadata to or specifically formatting code so that a tool can be run against the codebase in order to generate documentation for the application. This is extremely valuable for a number of reasons.

1. When documentation and code live together, it is easy to find documentation both to utilize and update it.
2. It becomes more obvious when code changes require documentation updates with documentation intrinsic to the codebase.
3. Documentation review can be included with code review when changes are made.

## Purpose

Documentation is critical for software applications, especially for systems that use a RESTful API model. Without good documentation, there will be serious negative impacts not just to our end user customers, but amongst engineering teams that are attempting to interact with services developed by other groups (and even their own services given sufficient time to forget how they work). Automated documentation generation helps us to keep our documentation accessible, readable, and correct.

## Tools

**OpenAPI** is an open standard that we use to describe our RESTful API's in order to help us organize and manage our interactions with them.

**SwaggerUI** is a tool that helps manage, document and use RESTful API's based on the OpenAPI standard.

## Usage and Enforcement

Since our services will already be utilizing the OpenAPI Standard, generating docuemntation for them is trivial. We will be using the various [Swagger](https://swagger.io/resources/articles/documenting-apis-with-swagger) tools created by SmartBear to create our RESTful API's.

There are [GitHub Actions](https://github.com/marketplace/actions/swagger-ui-action) that can generate the static documentation and host it in a [GitHub Pages](https://github.com/peter-evans/swagger-github-pages) site. As this solution utilizes tools that we already use on a daily basis, it is probably the best fit for our company.

