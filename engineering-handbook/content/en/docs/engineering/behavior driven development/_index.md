---
title: "Behavior-Driven Development"
linkTitle: "BDD Guidance"
weight: 20
description: >
  Takeoff BDD process guidance
---

## Introduction

[Behavior-Driven Development (BDD)](https://en.wikipedia.org/wiki/Behavior-driven_development) is a collaborative software development approach that emphasizes clear communication between developers, testers, and business stakeholders. It focuses on creating human-readable scenarios that serve as both requirements and definitions for features, facilitating a shared understanding and alignment on project goals. 

At a very high level, BDD uses descriptions of features written in Gherkin syntax and stored in **Feature Files** (`.feature` filetype) to convert structured natural language statements into executable software tests using **Step Definitions**. At Takeoff, we use [Pytest BDD](https://pytest-bdd.readthedocs.io/en/stable/#bdd-library-for-the-pytest-runner) to accomplish this. For more information about our implementation of Pytest BDD, see the [Pytest BDD Testing Framework readme](https://github.com/takeoff-com/release-qualification-tools/tree/master/pytest_BDD/docs). 

If you are new to BDD, we also recommend reading [Behavior-Driven Development (BDD)](https://en.wikipedia.org/wiki/Behavior-driven_development) on Wikipedia first, and [Best Practices for writing Feature Files](feature-files.md).

This article provides an overview of Roles and Responsibilities, Jira ticketing, and other guidelines for managing the BDD development workflow. 

### Roles and Responsibilities
- **Product Owners (POs)** are responsible for creating Given-When-Then (GWT) feature scenarios in Gherkin syntax. They are also responsible for reviewing and approving Pull Requests for the resulting Feature Files to ensure that the Feature File accurately represents the feature.   
- **Developers** are responsible for implementing features, and for crafting the Feature File using the GWT feature scenarios created by Proudct Owners. 
- **Software Development Engineers in Test (SDETs)** are responsible for reviewing the Feature File to make sure it aligns with the current library of statements, as well as for creating Step Definitions based on Feature Files. 
In the future, Developers will be responsible for creating Step Definitions, but for the short term SDETs will help facilitate this.  

### Feature File Tickets
  - There must always be a clear and logical link between tickets for Feature File creation work and the corresponding GWT scenarios, whether the GWT scenarios are within the AC of the Feature File ticket itself, a separate ticket, a Google doc, etc. 
  - Any tickets used for Feature File creation must have the `BDD-feature-file` label.
 
### Step Definition Tickets
  - In the short term, tickets created for Step Definitions should be receieve the `BDD-step-definition` label, and must be **Dev-tasks** in the [Production project](https://takeofftech.atlassian.net/jira/software/c/projects/PROD/boards/327). 
{{% alert color="warning" %}}**Dev-task** is being used for now because [Team Chamaeleon](https://takeofftech.atlassian.net/people/team/bde44f31-3d2a-4dba-b037-44cd57874e0f) will create Step Definitions in the short term to facilitate adoption. Once Dev teams start creating their own Step Definitions, these will be **Story** tickets in Dev team projects.{{% /alert %}}
  - Step Definition tickets must be linked to the corresponding Feature File ticket.
 
### Development Guidelines
-  Step Definitions can sometimes be written without needing a fully completed feature. For example, just an API spec may be sufficient for a Step Definition to be created. However, development of Feature Files should be completed before the development of the Step Definition begins.
- Engineers must request review and approval of Pull Requests for Feature Files from Product Owners so that we are ensuring that Feature Files meet business requirements. This also supports the Agile Development concept of [Three Amigos](https://www.agilealliance.org/glossary/three-amigos/). 
