
---
title: "Quality and Testing Guidelines"
linkTitle: "Quality and Testing Guidelines"
weight: 3
description: >
  This document is intended to summarize the various tools, testing strategies, and practices applied in Takeoff
---
## Goal and Motivation  
As Takeoff’s technology stack moves away from a monolith to microservices that leverage Google’s cloud offerings, we face 
challenges in communication.  This document is intended to summarize the various tools, testing strategies, and practices  
used at Takeoff to produce a quality product. It outlines recommended and deprecated items as well as suggestions and 
pitfalls. It also serves as a quick general-purpose overview to working with the quality guild.

---

> ℹ️ 
> This document is “living” and will be updated to reflect our evolving patterns, principles, and practices.  To introduce new strategies or technologies,
communicate with the [Quality Guild](https://takeofftech.slack.com/archives/C027H3P4KKQ).

---

## Document Ownership
[Quality Guild](https://takeofftech.slack.com/archives/C027H3P4KKQ)

## TL;DR (Executive Summary)
In brief, the guild suggests
* Use Gherkin syntax for describing tests where possible. 
  * Only describe key, user-facing behaviors in clear language and involve the Three Amigos (Quality Perspective, Development/Engineering, and Product) in creating the scenarios
  * For everything else, xUnit style tests are completely valid and cost less to develop
* Try to keep the testing language aligned with the service language
* Test as part of the CI workflow, block merging to main and require “clean green” tests to proceed
* CI Workflows should live in Github actions
* Focus testing on the integration points of micro-services
* Consumer driven contract tests should be in our shared future plans
* Mocks bring additional complexity and risk (which contract tests help reduce)
* Don’t forget our legacy services
* We have a traditional test pyramid (or in some cases an hourglass)
* Keep the tests green to maximize signal to noise
* There are many testing strategies, above all, shoot for reasonable scenario coverage however is efficient and reasonable

## A Note on Terminology
---
> Unit, Integration, Regression, Functional, Integrated, Smoke, Scenario, …
---
Overall, we’re going to not worry about naming specifics and focus on when is the right time to run broad classes of tests. Hint: early, often, and require intervention on test failures.
It is occasionally helpful to group tests into categories, such as “unit” tests, describing when, how, and where they run. For the sake of this discussion, we will split our language into
tests that run with Continuous Integration (CI) as part of the pull request (PR) workflow and those that don’t due to time, complexity, etc.

## Quality Radar
Our goal here is to encourage common tool usage and support evolving broadly.  This document summarizes the current status of evaluated tools and tech within Takeoff.

[![Quality Radar](/images/en/docs/Guilds/Quality/Quality-and-Testing-Guidelines/quality_radar.png)](https://radar.thoughtworks.com/?sheetId=https%3A%2F%2Fdocs.google.com%2Fspreadsheets%2Fd%2F1XlSSZxMuC1bN7Mit0iklCrqojQMfyM95idqLqtoN6uQ%2Fedit%23gid%3D0)
- Hold - No new deployment of the technology, only fitting where in use, but finding migration paths out is recommended.
- Assess - Consider if this could be useful in the future. There’s promise here, and a PoC shared with the guilds is requested before moving forward.
- Trial - Already established outside of Takeoff as standard technology. If using this, share feedback with the group.
- Adopt - Broadly in use at Takeoff and trusted or otherwise a clear choice. All teams should consider using this where relevant.
    - [Sheet used to generate artifacts](https://docs.google.com/spreadsheets/d/1XlSSZxMuC1bN7Mit0iklCrqojQMfyM95idqLqtoN6uQ/edit?usp=sharing)
    - Resulting static [pdf file](/images/en/docs/Guilds/Quality/Quality-and-Testing-Guidelines/TestingQualityRadar-2022.pdf)
    - See the interactive version [here](https://radar.thoughtworks.com/?sheetId=https%3A%2F%2Fdocs.google.com%2Fspreadsheets%2Fd%2F1XlSSZxMuC1bN7Mit0iklCrqojQMfyM95idqLqtoN6uQ%2Fedit%23gid%3D0).

## Development and Testing Strategies

##### End to End Testing (E2E)
Generally, End to End tests requires a service or collection of services to be running. They help get large, feature or behavior-focused test coverage across a group of functions or services
in a “realistic” manner (that is, not involving mocks or other runtime modifications). The general guideline is to limit the amount of E2E testing to the minimum amount needed for comfort.

##### Integrated
Integrated E2E tests run across a collection of services.  These are what projects such as On-Demand Environments are enabling. An extreme version of this is testing in production.  
The existing java integration tests framework uses this approach.

##### Integration
Integration tests focus on checking the integration points between subsystems, systems, or any nontrivial client/supplier relationship. An example here is to test the integration 
between service_a and service_b, there is no need to have any other services up and running. Whereas the E2E testing requires the running of all the services to test full user journeys.

##### Isolated
Isolated or “service level” E2E tests focus on the integration of features within a service and seek to mock or otherwise exclude or resolve external dependencies. One such approach is to
associate a service under test into a well-formed test environment but only focus on features and behaviors of the service. This style of testing is a better fit for CI-based testing.

#### Behavioral Driven Design (BDD)
BDD is a development method that has been abused as a testing tool at Takeoff in the past.  We support BDD when it is recognized that BDD is a development method with critical features
exercised with automated tests.  Writing too many cases in BDD often results in exceedingly complex and fragile code.

[Gherkin](https://cucumber.io/docs/gherkin/) syntax is the standard way to define the feature files.  [Karate](https://github.com/karatelabs/karate) is a popular framework that allows for BDD. 
[Pytest](https://github.com/pytest-dev/pytest-bdd) also has a bdd plugin.

---

ℹ️ 
From the docs:
- "BDD aims to narrow the communication gaps between team members, foster better understanding of the customer and promote continuous communication with real-world examples".
- Who write the specs: [the three amigos](https://www.agilealliance.org/glossary/three-amigos/).
- BDD adds complexity   

BDD Framework -> Feature File <- Step Definitions <- Supporting libraries, page objects, models, etc. ***VS*** Framework -> Test Files <- Supporting libraries, page objects, models, etc.

  Remember to write ***“correct”*** Gherkin syntax:   
  - Write all steps in third-person point of view
  - Write steps as a subject-predicate action phrase
  - Given-When-Then steps ***must*** appear in order and cannot repeat

---
   
Overall, using BDD is excellent when it is used correctly. **It is not a testing tool.** If used wrong, it only adds complexity and fragility. Generally, only **critical use case scenarios are a fit** for BDD. 
See this [post at cucumber’s site](https://cucumber.io/blog/bdd/bdd-is-not-test-automation) for further reading.  

TDD and BDD are techniques for designing and developing software. They produce tests as a by-product, but they are not testing activities. This notion is lost on the large majority of people who claim to be doing BDD.
If you write your tests after you've written the code you're not doing BDD no matter what tool you're using.

##### General Guidance
The quality guild strongly recommends the usage of Gherkin/Cucumber in the true sense of BDD; However, if teams want to PoC Cucumber in a non-BDD sense, then we strongly suggest that a couple of things be followed:   
1. The Gherkin syntax **MUST** in in plain English (non-technical)  
2. Product/Business stakeholders **MUST** take part in adding to and reviewing the defined scenarios
3. The step definition code **SHOULD** be written in the same language as the service code itself (Go or Python).  For Legacy services, existing tests should not be re-written just to meet the goal of using a recommended language. 
   
#### Test Driven Development (TDD)
A method of ensuring new functionality is testable and the behaviors are covered by one or more tests.

1. Add a test
2. Run all tests. The new test should fail for expected reasons
3. Write the simplest code that passes the new test
4. All tests should now pass
5. Refactor as needed, using tests after each refactor to ensure that functionality is preserved

---  
 
ℹ️ NOTE: We’re not going to cover the universe of testing strategies, only those we’re focusing in on as a guild for now.  Over time, we will adapt this document to address the focus as needed.

---   

## High-Level Guidelines for Services
Consider [adopting TDD](https://takeofftech.atlassian.net/wiki/spaces/QG/pages/3428876289/Quality+and+Testing+Guidelines#) and always keep [testability](https://takeofftech.atlassian.net/wiki/spaces/EN/blog/2020/04/16/1611006054) in mind.  
Remember, our goal is to release software that meets the needs of our users.

#### Legacy Services
The goal with our legacy code is to detect and prevent errors the best we can with what we have.
- [Release train / Regression testing](https://takeofftech.atlassian.net/wiki/spaces/QG/pages/3275522132) (Functional testing)
- [Python guided release qualification tool](https://takeofftech.atlassian.net/wiki/spaces/PD/pages/3399254183/Release+qualification+python+tools+description?search_id=90d8460e-f6f5-4b7a-8b00-07b3b502fa0c)

You may be surprised to see *“Integrated tests”* in the *“adopt”* category of the radar. These tests, often implemented as end-to-end tests, are fragile and require diligent maintenance. Our advice here is to use this style of testing sparingly, 
but we do advocate for their continued use. Choose only the critical flows, run these tests often, and fix them **immediately** if they are broken for any reason. This is aligned with the traditional testing pyramid as shown to the right.  

*Integrated tests* are helpful in providing confidence in the other layers of testing. Testing done in isolation supported by mocks, stubs, etc. risks missing real world details. Any accidental “coding to the mock” will hopefully be caught by this
layer of testing. Most relevant to Takeoff, we have plenty of legacy services that need that additional sanity checking provided by a focused set of integrated integration tests. 

#### New Services
New services should be held to a higher standard. Coverage is expected earlier and should be more effective
- Test implementation language should match the primary service language where possible
- Test implementation should live with the implementation under test, ideally in the same repo
- Service should be tested primarily as part of CI/CD flow
- Implementations should merge to main production-ready
  
For new services, focus on the interaction points and make them very explicit. Microservices are all about their interactions, and we’ll need to be careful that the behaviors and boundaries are explicit and well-enough covered by tests. [Spotify 
describes a “testing honeycomb”](https://engineering.atspotify.com/2018/01/11/testing-of-microservices/) that is more aligned with testing microservices; See the image to the right. 

Traditional Testing Pyramid ***(Legacy Services)*** | Testing Honeycomb ***(New Services)*** |
------------ | ------------- |
![Test Pyramid](/images/en/docs/Guilds/Quality/Quality-and-Testing-Guidelines/test_pyramid.png) | ![Test Honeycomb](/images/en/docs/Guilds/Quality/Quality-and-Testing-Guidelines/test_honeycomb.png)

### Stress / Load / Scale / Performance Testing side note
We’re not quite to a point to make strong guidance on tooling or patterns for these types of tests. What we do recommend is that GCP monitoring, tracing, and alerting in Production are utilized. Many performance issues are detectable through tracing and attention early.

#### Anti-Patterns
##### *Heavy Reliance on Mocks/Fakes*
Mocks enable us to decouple our service from others, enabling fast, stable, CI/PR-time tests. That's great, but we must always be mindful that mocks are additional code to maintain and may not always perfectly match the production environment. Even worse, as the “3rd party” service changes, often the mock goes un-updated.
![Mock only](/images/en/docs/Guilds/Quality/Quality-and-Testing-Guidelines/mock1.jpeg)  

Consumer Driven Contract tests provide a safer approach. On the consumer side, they provide a validated mock that has been tested against the real and published implementation. On the provider side, they supply behavior and semantic checks. 
![Mock + contract](/images/en/docs/Guilds/Quality/Quality-and-Testing-Guidelines/mock2.png)

##### *Heavy Reliance on End to End (Integrated) tests*
End to end tests are brittle, expensive to maintain, and hard to execute.  They can be part of validating a deployment, but should be used sparingly and with great care.  Focus only on critical behaviors and customer-focused scenarios.  
Remember an End to End or integrated test is A test that will pass or fail based on the correctness of another system.

##### *Regression/Functional Tests Not Automated*
Failing to automate as part of the development of a feature dramatically reduces the chance the feature will ever be tested automatically. 

##### *Automating Too Much*
Too many tests covering a small patch of code, or re-covering the same code leads to too much maintenance later on.  Understand the coverage and actively manage it. Prune low value tests.

##### *Ignoring Failures*
If the tests were high value to begin with, treat every failure like a production bug and address it before merging to main. Dealing with test flakiness is a critical skill in testing because automated tests that do not provide a consistent signal will slow down the entire development process.

##### *Flaky or Slow Tests*
A failing test should be a cause of concern and the person(s) that triggered the respective build should investigate why the test failed right away.  
A test that sometimes fails and sometimes passes (without any code changes in between) is unreliable and undermines the whole testing suite. The negative effects are two fold:
- Developers do not trust tests anymore and soon ignore them
- Even when non-flaky tests actually fail, it is hard to detect them in a sea of flaky tests

##### *Not converting production bugs to tests*
One of the goals of testing is to catch regressions. Most applications have a “critical” code part where the majority of bugs appear. When a test escape bug is fixed it’s important to ensure that it doesn’t regress. One of the best ways to enforce this is to write a test for the fix (either unit or integration or both).

## Measurement and Reporting
For our legacy implementations and [release qualification](https://takeofftech.atlassian.net/wiki/spaces/QG/pages/3275522132) we use TestRail and have a [service for collecting automated results](https://takeofftech.atlassian.net/wiki/spaces/QUAL/pages/1502216595)
for the Java framework. We also use [SonarQube](https://sonarqube.tom.takeoff.com/projects) to collect CI-based test code coverage statistics. For new projects, the key metrics are around outcomes; things like escaped bugs.

A dashboard for monitoring metrics will be produced that should highlight where each domain is succeeding and where help is needed. The quality guild will focus on offering assistance to teams that are lagging in the metrics as well as any team that asks for help.

## Proposing New Strategies or Technologies
To add new items to our tracked list and push them from  “Assess” or “Trial” to “Adopt”, the quality guild would like to follow a simple PoC, Demonstration, and Review process. Work with the @guild-quality-leadership to plan a presentation time, likely during a regular quality guild meeting.

## Key Initiatives “In Flight”
- [Automated Release Trains](https://takeofftech.slack.com/archives/C02GKHW2Z55)
- [On-Demand Environments](https://takeofftech.slack.com/archives/C02A38MNU76)

## Selected Examples
![Loader](/images/en/docs/Guilds/Quality/Quality-and-Testing-Guidelines/loader.gif)

## Final Notes
In a perfect world, the risk of an escape would be minimized. Using sane rollback strategies, canary deployments, and proactive monitoring allows teams to recover faster from mistakes. Contract testing would be baked in to everyone’s workflow. Requirements would be clear and well designed.
We’d have the ability to stream real customer workflows against production copies to validate assumptions. These are all good long term goals, but for today we have to work with what we’ve got. With the [Strangler Fig Pattern](https://shopify.engineering/refactoring-legacy-code-strangler-fig-pattern), 
we can move forward incrementally.   

The Quality Guild is focusing on ***helping teams improve on their outcomes.***   

Just because ‘distributed’ and ‘decoupled’ both start with D, they're not the same thing.*

## QA related courses we recommend everyone:
- [Introduction to Software Testing (basic course but still very useful for developers)](https://www.coursera.org/programs/engineers-huaef?authProvider=takeoff&collectionId=&productId=vS3glRiaEeeAuQ5XyvTfVA&productType=course&showMiniModal=true)  
- [Google IT Automation with Python](https://www.coursera.org/programs/engineers-huaef?authProvider=takeoff&collectionId=&productId=7_nEU3iaEeiVXgoT1iWlYg&productType=s12n&showMiniModal=true)  
- [ Introduction to Automated Analysis](https://www.coursera.org/programs/engineers-huaef?authProvider=takeoff&collectionId=&productId=rlXxHh-8Eee-XAo4YcylNA&productType=course&showMiniModal=true)  

## Further Reading
- [How much testing is enough](https://testing.googleblog.com/2021/06/how-much-testing-is-enough.html)  
- [Fixing a test hourglass](https://testing.googleblog.com/2021/06/how-much-testing-is-enough.html)   
- [The ultimate microservices testing reading list](https://techbeacon.com/app-dev-testing/ultimate-microservices-testing-reading-list)  
- [Cleaning up the integrated tests scam](https://blog.thecodewhisperer.com/permalink/clearing-up-the-integrated-tests-scam)  
- [Testing of microservices](https://engineering.atspotify.com/2018/01/11/testing-of-microservices/)  
- [Microservices Test Strategies, types & tools: a comlete guide](https://www.simform.com/blog/microservice-testing-strategies/)
    
   
  
