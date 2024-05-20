---
title: "Contract Tests"
linkTitle: "Contract Tests"
weight: 7
date: 2022-06-14
description: >  
---

## Overview

**Contract testing** is a technique for testing an integration point by checking each application in isolation to ensure the `messages` it sends or receives conform to a shared understanding that is documented in a _`"contract"`_.   

For applications that communicate via HTTP, these `messages` would be the HTTP _request_ and _response_, and for an application that used _queues_, this would be the `message` that goes on the _queue_.

In practice, a common way of implementing contract tests is to check that all the calls to your test doubles return the same results as a call to the real application would.   

Contract testing is immediately applicable anywhere where you have two services that need to communicate - such as an API client and a web front-end. Although a single client and a single service is a common use case, contract testing really shines in an environment with many services (as is common for a microservice architecture). Having well-formed contract tests makes it easy for developers to avoid version hell. Contract testing is the killer app for microservice development and deployment.

## Terminology

In general, a `contract` is between a `consumer` (for example, a client that wants to receive some data) and a `provider` (for example, an API on a server that provides the data the client needs). In microservice architectures, the traditional terms client and server are not always appropriate -- for example, when communication is achieved through message queues. For this reason, we stick to consumer and provider in this documentation. 

**Consumer** an application that makes use of the functionality or data from another application to do its job. For applications that use HTTP, the consumer is always the application that initiates the HTTP request (eg. the web front end), regardless of the direction of data flow. For applications that use queues, the consumer is the application that reads the message from the queue. 

**Provider** an application (often called a service) that provides functionality or data for other applications to use, often via an API. For applications that use HTTP, the provider is the application that returns the response. For applications that use queues, the provider (also called producer) is the application that writes the messages to the queue.

**Pact** is a code-first tool for testing HTTP and message integrations using contract tests.   

**Pact broker** _(PACTFLOW)_ is an application for storing and sharing of consumer driven contracts and verification results. It is optimised for use with "pacts" (contracts created by the Pact framework, but can be used for any type of contract that can be serialized to JSON. After consumer test session all requests going to go up and record into broker where it going to share version and collaborate on contracts.   

**Bi-Directional Contract Testing** _(BDCT)_ is a type of static contract testing where two contracts - one representing the consumer expectations, and another representing the provider capability - are compared to ensure they are compatible. 

## Pact Contract Testing[^1] [^3]
![contracts summary](/images/en/docs/Engineering/cicd/contract_summary.png)   
Contract tests assert that inter-application messages conform to a shared understanding that is documented in a contract. Without contract testing, the only way to ensure that applications will work correctly together is by using expensive and brittle integration tests.

### Types

#### Consumer-driven   
![multiple consumer driven contracts](/images/en/docs/Engineering/cicd/pact-consumer-driven.png)   
Pact is a code-first consumer-driven contract testing tool, and is generally used by developers and testers who code. The contract is generated during the execution of the automated consumer tests. A major advantage of this pattern is that only parts of the communication that are actually used by the consumer(s) get tested. This in turn means that any provider behaviour not used by current consumers is free to change without breaking tests.

Unlike a schema or specification (eg. OAS), which is a static artefact that describes all possible states of a resource, a Pact contract is enforced by executing a collection of test cases, each of which describes a single concrete request/response pair - Pact is, in effect, "contract by example".   

- In consumer-driven contract testing, the consumer oversees contract creation. You might wonder why would a consumer take in charge of contract creation?   
- To understand that, let us assume there is a producer with many open service ports. A consumer wants to interact with this producer to access e.g. service port `A`.   
- Here consumer needs to let the producer know about their needs. Hence the consumer creates a contract based on their requirements. All the system producers can access this contract.   
- In this scenario for a successful interaction between the two parties, we follow the following steps:   
  - Producers test the consumer's requirements and produce a test response.   
  - Then the producer compares its response with the consumer's response.   
  - In case of a match between the responses, the two parties start to interact.   

#### Producer-driven   
![specification first](/images/en/docs/Engineering/cicd/pact-provider-driven.png)   
The term "contract testing", or "provider contract testing", is sometimes used in other literature and documentation in the context of a standalone provider application (rather than in the context of an integration). When used in this context, "contract testing" means: a technique for ensuring a provider's actual behaviour conforms to its documented contract (for example, an OpenAPI document). This type of contract testing helps avoid integration failures by ensuring the provider code and documentation are in sync with each other. On its own, however, it does not provide any test based assurance that the consumers are calling the provider in the correct manner, or that the provider can meet all its consumers' expectations, and hence, it is not as effective in preventing integration bugs.   

- As compared to the consumer driven-contract testing a producer-driven contract testing is rarely used.
- In this testing, a producer takes charge of creating a contract between them and the consumer. Then the producer runs several build tests to meet the contract.
- If the producer passes all the test cases, then the results get stored in a common repository.
- The consumer then runs the build and test cases. Both parties interact only after passing all the test cases.

#### Non-HTTP testing (Message Pact)   
In this type of contract tests recommended to split the code that is responsible for handling the protocol specific things - for example an AWS lambda handler and the AWS SNS input body - and the piece of code that actually handles the payload.

You're probably familiar with layered architectures such as Ports and Adaptors (also referred to as a Hexagonal architecture).

### Pact Steps
1. Test the consumer(contract capture)
   - Consumer makes the correct call to API
   - Consumer codecan handle the response
2. Share the contract with the Pact Broker (Pactflow)
3. Test the provider (contract validation)
   - All known consumers of the provider
   - Provider can respond to all requests for each consumer
   - For each request, the response (headers, status, body etc.) matches rules in the contract   

![pact workflow](/images/en/docs/Engineering/cicd/pact-workflow.png)

## Bi-Directional Contract Testing[^2]
![bi-directional contract testing](/images/en/docs/Engineering/cicd/bi-directional-ct.png)   
Teams generate a consumer contract from a mocking tool (such as Pact or Wiremock) and API providers verify a provider contract (such as an OAS) using a functional API testing tool (such as Postman). Pactflow then statically compares the contracts down to the field level to ensure that they remain compatible.   
**Bi-Directional Contract Testing (BDCT)** provides the ability to _"upgrade"_ your existing tools into a powerful contract-testing solution, simplifying adoption and reducing the time to implement contract testing across your architecture.   
BDCT is a feature exclusive to Pactflow and is not available in the Pact OSS project.

### Bi-Directional Steps

**Provider**  

1. Provider starts with its specification (e.g. an OpenAPI specification) referred to as the `Provider Contract`. This may be created by hand or generated by code (e.g. swagger codegen)
2. The `Provider Contract` is tested against the provider, using a functional API testing tool (such as RestAssured, Dredd, or Postman) or generated by code (such as via Swashbuckle, Spring Docs)
3. The `Provider Contract` is uploaded to Pactflow
4. When we call `can-i-deploy` the cross-contract validation process in Pactflow generates a `Verification Result` ensuring the provider doesn't break any of its consumers
5. If that passes, we deploy the provider and record the deployment via the `pact-broker record-deployment` command.

**Consumer**   

1. Consumer tests its behaviour against a mock (such as Pact or Wiremock)
2. The `Consumer Contract` is produced, in the form of a pact file, that captures only the actual interactions generated by the consumer code
3. The `Consumer Contract` is uploaded to Pactflow
4. When we call `can-i-deploy` the cross-contract validation process in Pactflow generates a `Verification Result` determining if the consumer consumes a valid subset of the provider contract.
5. If that passes, we deploy the consumer and record the deployment via the `pact-broker record-deployment` command.   

Want more? Look in [pactflow.io](https://docs.pactflow.io/) content and instructional videos[^4] and their repos[^5].

[^1]: [Exploring HTTP Pact contracts](https://takeofftech.atlassian.net/wiki/x/fwPws)   
[^2]: [Bi-Directional Contract Testing Guide](https://docs.pactflow.io/docs/bi-directional-contract-testing)   
[^3]: [Introduction to Pact](https://docs.pact.io/)   
[^4]: [Pactflow YouTube playlists](https://www.youtube.com/c/Pactflow/playlists)
[^5]: [Pact Foundation repos](https://github.com/pact-foundation)