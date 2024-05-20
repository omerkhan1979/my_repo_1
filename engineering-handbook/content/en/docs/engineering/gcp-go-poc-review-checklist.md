---
title: "GCP & Go PoC Review Checklist"
linkTitle: "PoC Review Checklist"
weight: 100
---

This is a list of what should be done for successfull PoC Review.

## What is PoC Review?

In Q3 2021 the company completed a series of GCP & Go training courses to initiate technology stack upgrade. 
Proof of Concept (PoC) is a Team Project that would evaluate and stretch earned knowledge after retraining. 
Review is an important part of the process to gather feedback from the company experts and share our own experience with the Company. We are going to learn new and share our knowledge inside the company to grow as experts inside the company through Review.

## Why do we need this Checklist?

The PoC, Review Process, New Technology Stack, and Non-Functional limitations are something unknown. 
And all unknown comes with uncertainty and fear. The Checklist is the list of requirements for PoC that bring clarity to the process.

## The Checklist

* Documentation
     * [ ] Project page in Confluence on Domain Space where should be:
          * [ ] Project name
          * [ ] Link to Github repository with the POC
          * [ ] Development Team
          * [ ] Stakeholders
          * [ ] Problems statement and how the team gonna solve it
          * [ ] System Architecture Diagram. Can be done in any tool you would like, but it should be "readable". _Check PlantUML, can be easy integrated into Confluence and Github._
* PoC Github Repository
     * [ ] Readme and/or Wiki contains information:
          * [ ] What component doing
          * [ ] _Optional_ How to Run locally
          * [ ] _Optional_ How to Test locally
          * [ ] How to Test on GCP Sandbox
          * [ ] How to Deploy on GCP Sandbox
          * [ ] How to Deploy on Non Prod env
     * [ ] CI / CD Pipeline for non-prod environment
          * [ ] Github Actions for CI/CD
          * [ ] CI part should lint code
          * [ ] CI part should run tests
          * [ ] CD part should provide deployable artifact (if applicable)
          * [ ] CD part should tag the version to deploy. [calver](https://calver.org/) should be used
          * [ ] CD part should deploy POC to sandbox or non-prod environment
          * [ ] POC should be able to deploy with “one-click” (a.k.a. “can deploy anybody”) any version/tag
     * [ ] Infrastructure as a Code
          * [ ] Terraform use where it posible
          * [ ] Lives with the code
          * [ ] Provides install & remove capability
          * [ ] Provides update capability
          * [ ] Provides rolling update capability
     * [ ] Database Management
          * [ ] Schema versioning (aka DB Migrations)
               * [ ] Support previous service/application version (N & N-1 rule) in case of application code rollback
          * [ ] Schema updates must be rolled out independently of code updates
          * [ ] RDBMS is preferable
          * [ ] Storing JSON documents in columns is not OK
* Non-Functional Requirement to the PoC
     * [ ] Microservice architecture approach will be standard
     * [ ] A database per service pattern
     * [ ] Apigee for API Gateway
     * [ ] RESTful APIs _(Use of gRPC will be decided by the API Architecture Guild Initiative)_
          * [ ] Support previous API version if new version bring breaking changes to the interface (N & N-1 rule)
     * [ ] Secrets Manager required _(No hard coded secrets, even in POC code)_
     * [ ] Canary Deployment capability required
     * [ ] _Optional_ Multi-tenant. _(Think about it as you learn, but not required at this time)_
     * [ ] OpenAPI/Swagger should be presented for APIs
     * [ ] HTTPs / SSL / TLS should be used for APIs
     * [ ] Align with [“Go Patterns, Principles & Practices”](https://github.com/takeoff-com/go-ppp)
     * [ ] Align with [“API Guildelines”](https://engineering-handbook.takeofftech.org/docs/architecture/restful-api/design-guide/)
     * [ ] Monitoring via StackDriver https://sre.google/sre-book/monitoring-distributed-systems/
* Quality Gate
     * [ ] Tests are required. Standard Go & GCP tools - 80% code coverage
* UI
     * ReactJS should be used

## FAQ

### Confluence is kinda deprecated in favor of Github/ Eng Handbook?
No, it is not deprecated. Confluence would be used as Search Index for PoC projects. PoC should contain a single page with information about the PoC.

### Why run locally is optional?
When we using GCP solutions, some of them do not have emulators or integretion with them can be hard. Due to that, run localy or test localy are optional and personal sandbox should be used as dev-evironment.
