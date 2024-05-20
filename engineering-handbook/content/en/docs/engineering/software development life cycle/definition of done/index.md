
---
title: "Definition of Done"
linkTitle: "Definition of Done"
weight: 3
description: >
  Definition of Done (DoD) is crucial for every Takeoff domain and scrum team inside the domains. As an Engineering department, we have to meet company core values and principles and have a common understanding of quality and completeness.
---

## Owner(s)
Quality and Agile Guilds

## Why?
Definition of Done (DoD) is crucial for every Takeoff domain and scrum team inside the domains. As an Engineering department, we have to meet company core values and principles and have a common understanding of quality and completeness.

We value high-quality engineering and look for ways to hold ourselves accountable for producing high-quality software. However, we recognize that we are humans and will forget engineering fundamentals and make mistakes from time to time. To that end, we will adhere to this baseline definition of done and ask everyone involved in our software to remind us of our commitment and hold us accountable.
We also recognize that our team may expand upon this baseline definition of done but may not lower this bar or subterfuge its intentions.

## DoD vs. Acceptance Criteria
For those new to Agile, it's not uncommon to wonder what the difference is between 'Acceptance Criteria' and 'Definition of Done'. A quick search on the web yields many results, but generally speaking, the primary difference between the two is in their scope. DoD tends to be a general set of criteria applicable to most, if not all, items in a backlog 
(e.g. Docs updated, code written/reviewed, tests written/reviewed based on acceptance criteria) while Acceptance Criteria is a more specific set of criteria applicable to a specific item in the backlog (e.g. defines the functionality and expected outcome of the functionality).

For more related information please visit: [Agile Dictionary](https://takeofftech.atlassian.net/wiki/spaces/AG/pages/1277001729/Agile+Dictionary)

## DoD
- Change is developed according to the Acceptance Criteria defined within it
- User Scenarios are covered based on the acceptance criteria
- Project builds without errors
- Unit tests are written and passed
- Refactoring completed (when applicable)
- The feature is tested against acceptance criteria
- Test execution phase completed & identified high priority defects resolved → ref. [Quality testing guidelines](https://engineering-handbook.takeofftech.org/docs/guilds/quality/quality-and-testing-guidelines/qual_n_test_guidelines/)
    - Each [P1 or P2](https://takeofftech.atlassian.net/wiki/spaces/~406080379/pages/2840200201/Proposed+Incident+Management+Process+Changes) defect should be covered by a dedicated test case and automated (if applicable)
    - Root Cause field defined
- All applicable Test Cases, both manual and automated, have been executed and recorded as Test Runs with Results
    - Test Cases and Runs are associated/linked back to the appropriate Jira ticket for visibility
    - Test Results are recorded for each Test Run
    - A risk assessment for every story is discussed by the team to identify and include applicable tests required for execution to ensure no regressions have been introduced
- Any configuration or build changes documented and shared across all affected parties (scrum teams, domains)
    - Channels/sources for sharing information:
        - Sprint Review
        - Github
        - Eng handbook
        - Confluence
        - Zendesk
- Project deployed on the test environment identical to production platform (QAI env)
- Regression test cases exist (manual or automated) according to the defined acceptance criteria (e.g. added new tests to the regression suite where applicable)→ ref.[Functional Testing](https://engineering-handbook.takeofftech.org/docs/guilds/quality/functional-testing-process-/functional_testing_process/)
    - Test cases must be reviewed by scrum team member(s) to ensure appropriateness
    - The creation of new automated tests is considered, discussed, and applied where deemed valuable
    - Existing automated tests are updated where necessary and removed if obsolete/redundant → ref: [link](https://www.ontestautomation.com/on-including-automation-in-your-definition-of-done/);
- All needed documentation updated
    - If applicable, user-facing documentation has been written and reviewed
    - If it is a complex or new piece of technology that all of the findings are documented in Confluence AND/OR Eng handbook and shared with all engineers during Sprint Review or specifically requested demo session
- Release notes completed
- All code must pass code review prior to merging to Master