
---
title: "Functional Testing Process"
linkTitle: "Functional Testing Process"
weight: 3
description: >
    A detailed description of the system, system integration testing process that has to be performed by the scrum teams

---

## WHAT?
{{% alert title="NOTE" %}} Functional testing has also been called “Regression” testing, we’ll likely see those two terms interchangeably in some documents. 
The goal is to ensure that there are no regressions in known functionality.  {{% /alert %}}

#### Each scrum team has to execute a functional testing cycle at the end of every sprint

- **Tests that are included in a functional test suite have to be marked with label in Test Rail: “Regression-<domain name>”**
    - Labels already created in test rail, as an example label for Outbound domain will be: *Regression-Outbound*
        - We need these labels to be able to:
            - Generate test runs (set of tests selected for execution) based on domain
            - Automation framework to pull needed tests from Test Rail for execution and push result into test runs after
            - For fast and easy test report generation in Test Rail
- **Every domain has to treat functional tests failures as internal Sev1 issue**
    - Create new bugs in Jira to track the issues and add the following labels so the success of this process can be measured/tracked
        - *autotest-failure* ([for any auto test failures, but NOT product bugs](https://takeofftech.atlassian.net/wiki/spaces/QUAL/pages/1665075696))
        - *regression_bug* (for product bugs)
- Production domain will run acceptance tests only after domain functional tests were passed 
    - Failure results for a domain component(s) will remove the component from the release until functional tests pass
    - No matter when occurs failure - during functional testing by scrum teams → component(s) will be blocked for deployment and will be punted until the next RT (e.g. next sprint)

## WHEN?

#### Functional testing has to begin on Thursday - Friday of every 2nd week in the sprint 
- At the beginning of Thursday and Friday 2nd week of the sprint **(at 5:30 AM UTC)** **team-chamaeleon will deploy to all environments latest master.**

{{% alert title="NOTE" %}} please make master branch contains everything that was done during the sprint before this time  {{% /alert %}}
  
## HOW?

#### The team will be able to reserve time-slots for every client functional testing on QAI env on both days (Thu and Fri) using this doc [Functional Testing "Windows" per client](https://takeofftech.atlassian.net/wiki/spaces/QG/pages/3275915334) 

{{% alert title="NOTE" %}} please choose wisely as it will be up to you and another team after, if you’ll want to change the slot → only option is to get with a team that has it and swap with them {{% /alert %}}

##### On Thursday (or even before the end of the sprint) create a functional test runs (manual AND / OR automated that will be executed/created by itself in TR) for each day in Test Rail
- Please use next naming template: **“<team-name>-<date>-regression”**
- Fill in all needed information in Test Runs:
  - Mark tests with an actual execution result (Passed / Failed / Blocked / etc)
  - Add defects into the defect field of the failed test
  - Add additional comment if needed into the failed test(s)
  
---  

Let's take a look at the diagram of how the process will work: 
![regression diagram](/images/en/docs/Guilds/Quality/Functional-testing-process/functional_testing_process.png) 

---

Let's chunk into pieces this process again:
1. Start sprint
2. Sprint deliverables
3. On **Thursday** of the 2nd-week sprint (means Wed night everything has to be merged to master branch by scrum teams)
    - Team chameleon deploy master builds to QAI envs (Ukraine timezone morning)
4. Test execution preparation process (test suite creation, tests refinement, etc)
5. Scrum teams starting their functional testing based on the schedule they selected, no one else will touch these envs during your testing sessions
   - If this happened, please ping immediately Erik Schweller and/or Oleksii Zaichenko and/or Omer Khan and/or Richard Cole 
6. Scrum teams fixing the issues found during the functional testing cycle 
7. Push build with the fixed issue to the master
8. On **Friday** of the 2nd-week sprint (means Thu night every fix should be merged to master branch by scrum teams)
    - Team chameleon deploy master to QAI envs (Ukraine timezone morning)
9. Scrum teams starting their functional testing and defects re-test (has to be done on latest master beforehand) based on the schedule they selected
10. Last functional testing cycle and verification of fixed bugs passed?
    - IF <span style="color: green">**“YES”**</span> - release process continues
    - IF <span style="color: red">**“NO”**</span> - release process for the affected component(s)/service(s) could possibly be <span style="color: red">**punted**</span>
        - Deployment of components would get **postponed until the next RT** if the issue(s) is/are considered to be blocking - in this case QAI env will have to be **rolled back** to the previous RT version to keep in sync with what is running on prod). The only exception to this would be if the issue(s) are fixed  and merged to master before RT cut or cherry-picked to the RT branch post cut.
