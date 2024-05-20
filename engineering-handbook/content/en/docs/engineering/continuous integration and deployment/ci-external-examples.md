---
title: "CI/CD External Examples"
linkTitle: "CI/CD External Examples"
weight: 7
date: 2022-05-27
description: >
---
## CI/CD External Examples

### What is CI/CD? at Google[^1]
**Continuous Integration (CI)**, at its core, is about getting feedback early and often, which makes it possible to identify and correct problems early in the development process. With CI, you integrate your work frequently, often multiple times a day, instead of waiting for one large integration later on. Each integration is verified with an automated build, which enables you to detect integration issues as quickly as possible and reduce problems downstream.

**Continuous Delivery (CD)** extends CI. CD is about packaging and preparing the software with the goal of delivering incremental changes to users.  Deployment strategies such as red/black and canary deployments can help reduce release risk and increase confidence in releases. CD makes the release process safer, lower risk, faster, and, when done well, boring. Once  deployments are made painless with CD, developers can focus on writing code, not tweaking deployment scripts. <br>
![DevOps and Google Cloud CI/CD Sketchnote](/images/en/docs/Engineering/cicd/gcp_ci.png)

### Most spread elements of a CI/CD pipeline at Semaphore[^2]
Pipelines reflect the complexity of a project. Configuring even the simplest pipeline with one job that runs on every code change will save a team many headaches in the future.

On Semaphore, pipelines can easily be extended with multiple sequential or parallel blocks of jobs. Pipelines can also be extended using promotions that are triggered manually or automatically, based on custom conditions. <br>
![cicd-pipeline](/images/en/docs/Engineering/cicd/cicd-pipeline.jpeg)

**A pipeline for a simple Go program** <br>
![go simple pipeline](/images/en/docs/Engineering/cicd/golang-ci-pipeline.jpeg)

**CI/CD pipeline for a monorepo** <br>
![cicd monorepo](/images/en/docs/Engineering/cicd/ci-monorepo.jpeg)

### Netflix global CI/CD with Spinnaker[^3]
Spinnaker is an open source multi-cloud CI/CD platform for releasing software changes with high velocity and confidence use at Netfllix. <br>
![Netflix CI/CD with Spinnaker](/images/en/docs/Engineering/cicd/netflix-cicd-spinnaker.png)

![Spinnaker pipeline](/images/en/docs/Engineering/cicd/nf-cicd-spinnaker.png)

[^1]: [DevOps and CI/CD on Google Cloud explained](https://cloud.google.com/blog/topics/developers-practitioners/devops-and-cicd-google-cloud-explained)

[^2]: [CI/CD Pipeline at Semaphore](https://semaphoreci.com/blog/cicd-pipeline)

[^3]: [How They Build Code at Netflix](https://netflixtechblog.com/how-we-build-code-at-netflix-c5d9bd727f15)