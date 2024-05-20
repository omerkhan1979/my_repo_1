
---
title: "Quality"
linkTitle: "Quality"
weight: 3
description: >
  Quality Guild
---
## One-Pager / Quick Information
![8e2daa74-293e-4e0d-9be5-49f677334ea8](https://user-images.githubusercontent.com/6999695/160448317-658f3c31-091a-4286-ba3a-9a5bc636f932.png)

## Quality and Testing Guidelines
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

See [Quality and Testing Guidelines](/docs/guilds/quality/quality-and-testing-guidelines/qual_n_test_guidelines/) on Eng Handbook for further details and updates.

## Eng Handbook Space and Confluence (for "living" info) - More Information
- For the main documents please go through all the child pages in this section 
- Also the guild regularly updates "living" information on the [Quality Guild Confluence space](https://takeofftech.atlassian.net/wiki/spaces/QG/overview?homepageId=3204808938).

