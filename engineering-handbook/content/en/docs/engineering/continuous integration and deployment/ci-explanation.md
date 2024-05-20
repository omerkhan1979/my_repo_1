---
title: "CI Explanation"
linkTitle: "CI Explanation"
weight: 7
date: 2022-05-27
description: >  
---
## Continuous Integration Explanation
![CI](/images/en/docs/Engineering/cicd/ci.png)

**Continuous Integration (CI)[^1]** - An automated software development procedure that merges, integrates and tests all changes as soon as they are committed. This practice of having everyone working on the same software project and communicating their modifications to the codebase on a regular basis and then testing that the code still works as it should after each change is known as continuous integration, or CI. Continuous integration is an important aspect of the DevOps method to software development and release, which emphasizes collaboration, automation, and quick feedback cycles

Continuous integration begins with routinely committing changes to a source/version control system so that everyone is working from the same blueprint. Each commit starts a build and a series of automated tests to ensure that the behavior is correct and that the change hasn’t broken anything. Continuous integration is not only advantageous in and of itself, but it is also the initial step in establishing a CI/CD pipeline.

### Why a robust CI pipeline matters in microservice architecture

In a traditional monolithic application, there is a single build pipeline whose output is the application executable. All development work feeds into this pipeline. If a high-priority bug is found, a fix must be integrated, tested, and published, which can delay the release of new features. As the application grows more complex, and more features are added, the release process for a monolith tends to become more brittle and likely to break.

Following the microservices philosophy, there should never be a long **release train** where every team has to get in line. The team that builds service `A` can release an update at any time, without waiting for changes in service `B` to be merged, tested, and deployed.

![cicd monolith vs. ms](/images/en/docs/Engineering/cicd/cicd-monolith-ms.png)

To achieve a high release velocity, your release pipeline must be automated and highly reliable to minimize risk. If you release to production one or more times daily , regressions or service disruptions must be rare. At the same time, if a bad update does get deployed, you must have a reliable way to quickly roll back or roll forward to a previous version of a service.

### Challenges

- **Triggering** - possibility to configure your CI/CD tool to poll for changes to a Git repository, or you can set up a Webhook to notify your CI/CD tool whenever a developer makes a push. The main reason for doing this is to make running the pipeline automatic, and friction-free.
If you leave the pipeline to be run manually, people will sometimes forget to run it, or choose not to. It’s far better to just make this an automated step.
- **Сheckout** - one of the first stages, the CI server will check out the code from the source code repository, such as GitHub. The CI/CD tool usually receives information from a poll, or a webhook, which says which specific commit triggered the pipeline. The pipeline then checks out the source code at a given commit point, and starts the process.
- **Linting** - the automated checking of your source code for programmatic and stylistic errors. This is done by using a lint tool (otherwise known as linter). A lint tool is a basic static code analyzer. e.g. Pylint, Flake8, Black, golint, gofmt. 
- **Static Code Analysis** - also known as Source Code Analysis is usually performed as part of a Code Review and is carried out at the Implementation phase of a Security Development Lifecycle. Static Code Analysis commonly refers to the running of tools that attempt to highlight possible vulnerabilities within `static` (non-running) source code by using techniques such as Taint Analysis and Data Flow Analysis. e.g. SonarQube, lizard, staticcheck.
- **Compile the code** - if you’re developing in a compiled language like Java (automation in our case), the first thing you’ll probably need to do is compile your program. This means that your CI tool needs to have access to whatever build tools you need to compile your app. For example, if it’s `Java`, you’ll use something like `Maven` or `Gradle`. Ideally this stage should run in a clean, fresh environment. This is one of the great use cases for `GCP`, `Kubernetes` and `Docker containers` – being able to create fresh build environments easily and repeatably.
- **Run unit tests** - this is the stage where you configure your CI/CD tool to execute the tests that are in your codebase. The aim at this point is not only to verify that all the unit tests pass, but that the tests are being maintained and enhanced as the code base grows. They are easy to write, cheap to run and have the lowest cost to maintain.
- **Tests coverage metrics** - needs to track if the application is growing rapidly, but the number of tests stays the same, this isn’t great, because it could mean that there are large parts of the code base which are untested. Here to help us we can use different tools to track coverage or to create coverage matrix. e.g. pytest-cov, cover.
- **Package the code** - when all of the tests are passing, it can move on to packaging the code. Exactly how you package your application depends on your programming language and target environment. Whatever packaging format that was chosen, a good practice is that you should build the binary only once. Don’t build a different binary for each environment, because this will cause a pipeline to become very complex.
- **Run acceptance or contract tests** - these kind of tests are a way of ensuring that your software does what it is meant to do, and that it meets the original requirements. But manual acceptance testing is very tedious and time-consuming. So there are a growing number of ways that you can perform automated acceptance and contract testing.
- **Continuous Delivery or Deployment** - when the application has been tested, it can move into the delivery or deployment stage. At this stage, you have an artifact ready to be deployed (continuous delivery). Or, you can continue to CI/CD heaven and automatically deploy your software (continuous deployment). Most pipelines don’t make it to this final stage, and that’s a shame 😄. There is enormous value in being able to automatically deploy your software into production. To achieve continuous deployment, you need a production environment to deploy into. If you’re deploying to a public cloud, you can use the cloud provider’s API to deploy your application. Or if you’re using `Kubernetes`, you might use a `Helm` chart to deploy your app.

[^1]: [Glossary] (content/en/docs/Engineering/Continuous integration and Deployment/cicd-glossary.md)