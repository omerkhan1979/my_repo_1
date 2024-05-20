---
title: "Unit Tests"
linkTitle: "Unit Tests"
weight: 7
date: 2022-05-31
description: >  
---
## Unit Tests
![Unit Tests](/images/en/docs/Engineering/cicd/unit-tests.png) ![unit tests lifecycle](/images/en/docs/Engineering/cicd/unit-tlifecycle.jpeg)

### Purpose 

**Unit testing** - is a type of testing in which individual units or functions of software testing. Its primary purpose is to test each unit or function. A unit is the smallest testable part of an application. It mainly has one or a few inputs and produces a single output. In procedural programming, a unit referred to as an individual program.  
**Unit Test framework** - a tool that provides an environment for unit or component testing in which a component can be tested in isolation or with suitable stubs and drivers. It also provides other support for the developer, such as debugging capabilities.   

Unit testing is the process of testing discrete functions at the source code level. A developer will write a test that exercises a function. As the function is exercised, the test makes assertions against the results that the function returns. Functions that do not return a result are not good subjects for unit tests. Such functions alter the state of the system beyond the scope of the given function. Thus, the function needs to be tested at the integration or system level. Unit testing is about exercising discrete functions, that are well encapsulated and return a result upon execution.   

Unit Testing is important because software developers sometimes try saving time doing minimal unit testing and this is myth because inappropriate unit testing leads to high cost Defect fixing during System Testing, Integration Testing and even Beta Testing after application is built. If proper unit testing is done in early development, then it saves time and money in the end.   

Automated testing is the bedrock of the CI/CD pipeline. The Development Phase is the first step in the CI/CD deployment process. However, it is not the only step. The next phase of testing in the Development Phase of CI/CD process.
Unit testing is the place to start when implementing testing in the Development Phase of the CI/CD pipeline.

### What principles/properties makes good Unit Tests?  
![Test Pyramid](/images/en/docs/Engineering/cicd/test-pyramid.jpeg)  

* **Easy to write.** Developers typically write lots of unit tests to cover different cases and aspects of the application’s behavior, so it should be easy to code all of those test routines without enormous effort.

* **Readable.** The intent of a unit test should be clear. A good unit test tells a story about some behavioral aspect of our application, so it should be easy to understand which scenario is being tested and — if the test fails — easy to detect how to address the problem. With a good unit test, we can fix a bug without actually debugging the code!

* **Reliable.** Unit tests should fail only if there’s a bug in the system under test. That seems pretty obvious, but programmers often run into an issue when their tests fail even when no bugs were introduced. For example, tests may pass when running one-by-one, but fail when running the whole test suite, or pass on our development machine and fail on the continuous integration server. These situations are indicative of a design flaw. Good unit tests should be reproducible and independent from external factors such as the environment or running order.

* **Fast.** Developers write unit tests so they can repeatedly run them and check that no bugs have been introduced. If unit tests are slow, developers are more likely to skip running them on their own machines. One slow test won’t make a significant difference; add one thousand more and we’re surely stuck waiting for a while. Slow unit tests may also indicate that either the system under test, or the test itself, interacts with external systems, making it environment-dependent.

* **Truly unit, not integration.** As we already discussed, unit and integration tests have different purposes. Both the unit test and the system under test should not access the network resources, databases, file system, etc., to eliminate the influence of external factors.

### Tools and frameworks
#### Commonly used[^1]  
* JUnit / TestNG / AssertJ / Mockito / JMockit  
* Mocha
* PHPUnit / SimpleTest  

#### Python[^2] 
* Pytest / PyUnit / Nose  

#### Clojure[^3]
* clojure.test / Expectations / Speclj

#### Go[^4]  
* Go test / go2xunit / GoConvey[^5] / testify[^6]  

[^1]: [Unit testing tools](https://www.javatpoint.com/unit-testing-tools)  
[^2]: [List of unit testing frameworks](https://en.wikipedia.org/wiki/List_of_unit_testing_frameworks)  
[^3]: [Clojure test](https://clojure.github.io/clojure/clojure.test-api.html)  
[^4]: [Go test](https://go.dev/doc/tutorial/add-a-test)  
[^5]: [GoConvey ](https://github.com/smartystreets/goconvey)  
[^6]: [Testify ](https://github.com/stretchr/testify)
