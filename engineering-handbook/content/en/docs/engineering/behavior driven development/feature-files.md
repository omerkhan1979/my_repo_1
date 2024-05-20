---
title: "Feature Files"
linkTitle: "Feature Files"
weight: 2
description: >
  Takeoff BDD Feature File Best Practices
---

## Best Practices for writing Feature Files

Use these best practices as guidelines for creating Files Files (`.feature` file extension).

- [Best Practices for writing Feature Files](#best-practices-for-writing-feature-files)
  - [Sample Feature File](#sample-feature-file)
    - [Feature](#feature)
    - [Background](#background)
    - [TestRail Test Case Marker](#testrail-test-case-marker)
    - [Scenario Outlines](#scenario-outlines)
      - [Steps](#steps)
      - [Examples](#examples)
    - [Reuse Steps](#reuse-steps)
    - [Tags and Markers](#tags-and-markers)
    - [Comments](#comments)
    - [Regularly Review and Refactor](#regularly-review-and-refactor)


### Sample Feature File

The following Order Processing Feature File example will be referenced throughout the Best Practices below.

```
@orderflow @bdd_rq
Feature: Order Processing
  As an MFC Operational staff member, I want to process an OSR and a manual order.

Background:
  Given "osr" configuration is set in env

  @bdd_testrail=791582
  Scenario Outline: Validate the order flow process with OSR and Manual
    Given products from "<osr>" "<manual>" "<in-store>" "<variable_weight>" are available in the environment

    When order is created with type "<service_type>"
    And order is consolidated and staged
    Then order status matches ORDER_STATUS_AFTER_PICKING config in TSC

       Examples:
        | osr | in-store | manual | variable_weight | service_type|
        | 1   | 0   | 0      | 0               | DELIVERY |
        | 0   | 0   | 1      | 0               | DELIVERY |
        | 0   | 1   | 0      | 0               | DELIVERY |

```


#### Feature

Feature Files (.feature file extension) start with a **Feature** section and a description. The description is optional, and it may have as many or as few lines as desired. The description will not affect automation at all – think of it as a comment. Another optional Agile best practice is to include a brief User Story for the features on a separate line immediately below the Feature statement. 

```
@orderflow @bdd_rq
Feature: Order Processing
  As an MFC Operational staff member, I want to process an OSR and a manual order.

```

Use a **Feature** title that is clear, simple, and universally understandable. In this case, the title is "Order Processing" shows that the test is about verifying that an order is processed.

#### Background

Sometimes scenarios in a Feature File may share common setup steps or preconditions that need to be satisfied to test the feature. Rather than duplicate these steps, they can be put into a Background section. 

```
Background:
  Given "osr" configuration is set in env
```

Since each scenario is independent, the steps in the Background section will run before each scenario is run. The Background section does not have a title. It can have any type or number of steps, but as a best practice, it should be limited to Given steps.

#### TestRail Test Case Marker
In order to link your Scenario to your TestRail test case, you must provide the `@bdd_testrail` marker with your TestRail Case ID.
```
@bdd_testrail=791582
```
This will allow the pytest bdd test results to be reported to your TestRail test run as outlined in [Testrail Reporting](https://github.com/takeoff-com/release-qualification-tools/blob/master/docs/reporting/01-testrail-reporting.md).

#### Scenario Outlines 

The Scenario Outline section defines the goal of a given test scenario. Scenario Outlines are only required if an [Examples](#Examples) section is used. Each test scenario is comprised of the **Outline**, **Steps**, and optionally **Step** or **Examples** tables to parameterize the test.

```
  Scenario Outline: Validate the order flow process with OSR and Manual
```

A Feature File can have multiple **Scenario Outline** sections, but make sure to write them briefly to avoid making the Feature File too large. Design statements for reuse whenever possible. Scenarios are run independently; the output of one scenario has no bearing on the next.

##### Steps

This Feature File then has one Scenario section and a series of **Given–When–Then** steps in order. It could have more scenarios, and more steps, but for simplicity this example has only one. 

```
   Given products from "<osr>" "<manual>" "<in-store>" "<variable_weight>" are available in the environment

    When order is created with type "<service_type>"
    And order is consolidated and staged
    Then order status matches ORDER_STATUS_AFTER_PICKING config in TSC
```
Another thing to notice is that you can and should parameterize steps where possible. **Steps should also be written for reusability.**

##### Examples

Scenario outlines are parameterized using **Examples** tables. Each **Examples** table has a title, and in Gherkin, a table is passed as an input for the test. Each row in the table represents one test instance for that particular combination of parameters.

All rows in the table must be for tests of the same TestRail test case (you CANNOT mix tests belonging to different TestRail Case IDs)

In the example Feature File above, there would be two tests for this **Scenario Outline**. The table values are substituted into the steps above wherever the column name is surrounded by the “<” “>” symbols.

Each row represents a unique set of order attributes, covering multiple order fulfillment combinations. 
```
       Examples:
        | osr | in-store | manual | variable_weight | service_type|
        | 1   | 0        | 0      | 0               | DELIVERY |
        | 0   | 0        | 1      | 0               | DELIVERY |
        | 0   | 1        | 0      | 0               | DELIVERY |
```

Be careful not to confuse step tables with Examples tables! This is a common mistake for Gherkin beginners. Step tables provide input data structures, whereas Examples tables provide input parameterization.

#### Reuse Steps

Steps should be written for reusability as much as possible. A step hard-coded to search for a **banana** is not very reusable, but a step parameterized to search for **any product** is.

Reusing steps across scenarios brings enormous benefits in the form of stability, consistency, clarity, and time savings.  

#### Tags and Markers

**Tags** are a great way to classify scenarios. They can be used to selectively run tests based on tag name (`@orderflow`), and they can be used to apply before-and-after wrappers around scenarios.

Tags start with the “@” symbol. Tag names are case-sensitive and whitespace-separated. As a best practice, they should be lowercase and use hyphens (“-“) between separate words. Tags must be put on the line before a Scenario or Scenario Outline section begins. Any number of tags may be used.

```
@orderflow

```

**Markers** 
[Pytest-bdd](https://pytest-bdd.readthedocs.io/en/stable/#organizing-your-scenarios) uses [pytest markers](https://pytest.org/en/7.4.x/how-to/mark.html) as a storage of the tags for the given scenario test, which allows us to use standard Pytest test selection. For example, the example test at the top of this page can be run using `pytest -v -s -m orderflow`.

#### Comments

**Comments** allow the author to add additional information to a feature file. In Gherkin, comments must use a whole line, and each line must start with a hashtag “#”. Comment lines may appear anywhere and are ignored by the automation framework.

Since Gherkin is very self-documenting, it is a best practice to limit the use of comments in favor of more descriptive steps and titles.

#### Regularly Review and Refactor

As with any testing software testing method, regularly reviewing and refactoring your tests is strongly encouraged. Using this Feature File as an example, it helps to align with the evolving needs of 
ISPS testing and ensures the test remains accurate to the feature's current purpose and functionality.
