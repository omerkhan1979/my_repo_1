
---
title: "Test summary reports"
linkTitle: "Test summary reports"
weight: 3
description: >
    Test summary report/metrics 
---


## Engineering Domain Review (technical)

<span style="color: red"> **Mandatory:** </span>

- Present testing results:
    - Test Pass rate trends (unit, manual, automated tests, etc)
    - Size metric (number of story points, or ticket counts, other measure that gives context to amount of effort)


<span style="color: green"> **Suggested:** </span>

- Regression defects found VS fixed during the sprint
    - Defects found at or after “Test” status

*Regression defects found VS fixed during the sprint example (JQL):*

Jira | Priority | Severity | Status 
------------ | ------------- | ------------ | ------------ 
Project: INC | *All | *All | *All

- Found issues that blocked Deployment

- Risk mitigation of new features
    - Coverage 
    - Test Pass rate trends
- Full Functionality Coverage (Traceability Matrix)
- % of Manual Tests Cases that have been Automated
- \# Manual Test Cases that were executed in a sprint
- Manual Test Cases pass rate
- \# Automated Test Cases that were executed in a sprint 
- Automated Test Cases pass rate 
- \% of Unit Test Coverage with the Latest Application build


## Sprint Review (high level metrics)

<span style="color: red"> **Mandatory:** </span>

- New Feature scenario coverage 
    - List of acceptance Criteria
    - How it was covered (Nothing, Manual, Automated, Part of CI)
    
New Feature scenario coverage ***example***:
    
Feature | Acceptance Criteria | # P0 Test Cases | Test Coverage
------------ | ------------- | ------------ | ------------ 
Feature A | AC1; AC2 | 2 | CI: 2; Automated: 8; Manual: 4
Feature B | AC1; AC2; AC3; AC4 | 4 | CI: 0; Automated: 0; Manual: 4

<span style="color: green"> **Suggested:** </span>

- Escapes (production issues)

Escapes (production issues) ***example***:

Issue | JIRA ID | Test Case ID | Test Type
------------ | ------------- | ------------ | ------------ 
OSR orders not dropping to Pickerman | OUTBND-#### | 12345 | Auto
Pickerman app fails during launch | OUTBND-#### | - | Manual


- Quality & Stability risks
    - Example: No rollback possible; 1 hour downtime needed; Major refactor to other areas
- Time to Resolution 
    - Example: Monitoring added for feature
    - Alerts when response time > 1s 
    
{{% alert title="Additional information" %}} Link to QG metrics board: [Metrics](/docs/guilds/quality/metrics/metrics/) {{% /alert %}}
