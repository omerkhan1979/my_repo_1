---
title: "Integration Tests"
linkTitle: "Integration Tests"
weight: 7 
date: 2022-06-07 
description: >
---

## Integration Tests

### Purpose

Integration tests verify that different modules or services used by your application work well together. Therefore, for
integration tests to be practical, they should cover as many integration points as possible. For example, it can be
testing the interaction with the database or making sure that microservices work together as expected. Once all the
individual units are created and tested, we start combining those tested modules and start performing the integrated
testing.

### Pre-requisites

Before an integration test can be executed, the external systems that the test will be touching must be properly
configured. If not, the test results will not be valid or reliable. For example, a database needs to be loaded with
well-defined data that is correct for the behavior being tested. Data updated during a test needs to be validated,
especially if that updated data is required to be accurate for a subsequent test.

### When to run

While integration tests can be run at the times you need them, they shouldn’t be run at the same time as unit tests.
Keeping your test suites separate allows developers to run fast unit tests and saves longer integration testing process
for the build server in another test suite.

### Types of Integration tests

Integration Testing is approached by combining different functional units and testing them to examine the results.
Integration testing types fall under two categories as in the image.
![integration-testing-types](/images/en/docs/Engineering/cicd/Integration-testing-types.png)

More details about Integration types can be found [here](https://techaffinity.com/blog/what-is-integration-testing/)

### Frameworks

It is not necessary to have a separate framework to run integration tests. Though it might have additional features for
readability

#### Go

Though integration tests in GO can be written the same way as unit tests, one can found it helpful to use additional
frameworks, one of examples is [Venom](https://github.com/ovh/venom)

### Final thoughts

- Integration test give the second level of feedback to developers after unit tests
- Many times the face or the structure of data changes when it travels from one module to another. Some values are
  appended or removed, which causes issues in the later modules. Such changes can only be verified by Integration
  testing
- This test runs faster than the end to end tests. With integration testing, you can find and fix the bugs at the very
  start of the development.
- Integration testing is crucial part of CI and must continiously extended and improved 

