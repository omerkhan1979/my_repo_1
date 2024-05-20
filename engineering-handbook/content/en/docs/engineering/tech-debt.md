---
title: "Engineering Backlog and Technical Debt"
linkTitle: "Engineering Backlog and Technical Debt"
weight: 3
date: 2022-05-17
description: >
  Engineering backlog classification and JIRA Hygiene
---

## What is Technical Debt?
In software development, technical debt is the implied cost of additional rework caused by choosing an easy solution now instead of using a better approach that would take longer. Analogous with monetary debt, if technical debt is not repaid, it can accumulate "interest", making it harder to implement changes ([Wikipedia](https://en.wikipedia.org/wiki/Technical_debt))

**JIRA Label:** `tech-debt`

### Tech Debt Classification

Why would we need proper labeling/good JIRA Hygiene? It would provide us with better insights into where we are accumulating tech debt.

|**Class**|**JIRA Label**|
|--|--|
| Customer Impacting | `customer-impacting` |
| Update of outdated / unsupported software | `obsolete-software` |
| Impacting velocity of future development  | `velocity-constraint` |
| Incident creator | `incidents-source` |
| Feature Flags (Launch Darkly) Deprecation Initiative | `feature-flag-deprecation` |

Tech debt that has no impact **we won’t do.**

#### Example

Labels for Tech Debt JIRA issue wich cause regular Sev-X issues: `tech-debt, customer-impacting`



## What is Engineering Initiative?
Engineering Initiative is a technical debt when a team decides to address accumulated technical debt by rewriting the entire service or services.

There are other reasons to make investments in engineering initiatives which are not a tech debt:

1. When it allows team or teams to free up their capacity in the future e.g., Tests Automation will enable teams to get feedback from the system faster, so they might focus their time on true value creation and reduce Work in Progress/IDLE-time

1. When it significantly simplifies our solution, that might reduce the Total Cost of Ownership (ToC)

1. When it might reduce dependencies from another business domain, which leads to reduced cost of coordination between two or more business domains

1. When it drives down the number of support requests or any other downtime

**JIRA Labels:** `engineering-backlog`