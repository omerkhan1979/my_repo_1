---
title: "Project structure"
linkTitle: "Project structure"
weight: 7
date: 2021-12-17
description: >
  Policies and recommendations for project structure 
---

### Project structure

The project structure chosen is a slight variation of the structure of [ardanlabs/service](https://github.com/ardanlabs/service)
```
.
├── app
│   └── services
├── business
│   ├── core
│   └── sys
├── foundation
│   ├── docker
│   ├── logger
│   ├── secret
│   └── web
├── ops
│   ├── db
│   │   └── migrations
│   ├── docker
│   ├── gcp
│   ├── local
│   └── terraform
```

#### *app*

**app** folder should contain code related for specific application. For example:

* Http handlers
* Start up configuration
* e2e tests
* Deployment configuration in case of App engine (app.yaml)
* Cloud function main entry point

**app** folder should not contain **business** logic or **DAL**(Data access layer) code

#### *business*

**business** is place for all business related logic:

* validations
* business flows
* computation rules
* entities
* logging

Also, **business** folder should contain **DAL**. Note that it's highly discouraged to use **DAL** code directly in **
app** layer

#### *foundation*

**foundation** folder contains application and business agnostic code that can be reused between project and subject for
future extraction into separate library if required. Logging should not be used here

#### *ops*

**ops** folder contains infrastructure as a code e.g.

* Terraform
* docker-compose for local development
* Dockerfile's of applications
