---
title: "GitHub Actions Requirements"
linkTitle: "GitHub Actions Requirements"
weight: 5
date: 2022-07-08
description: >  
---

## Basics

Automate, customize, and execute your software development workflows right in your repository with GitHub Actions. You can discover, create, and share actions to perform any job you'd like, including CI/CD, and combine actions in a completely customized workflow.
To organize a CI/CD pipeline for your application you only need a GitHub repository to create and run GitHub Actions workflow.

- GitHub Action [examples](https://docs.github.com/en/actions/examples)
- Worflow [syntax](https://docs.github.com/en/actions/learn-github-actions/workflow-syntax-for-github-actions)
- [Triggering workflow](https://docs.github.com/en/actions/learn-github-actions/events-that-trigger-workflows)
- [Contexts](https://docs.github.com/en/actions/learn-github-actions/contexts)
- [Expressions](https://docs.github.com/en/actions/learn-github-actions/expressions)
- [Variables](https://docs.github.com/en/actions/learn-github-actions/environment-variables) and [Secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [CI workflows](https://docs.github.com/en/actions/automating-builds-and-tests/about-continuous-integration) with GitHub Actions
- [CD workflows](https://docs.github.com/en/actions/deployment/about-deployments/about-continuous-deployment) with GitHub Actions
- [Packaging](https://docs.github.com/en/actions/publishing-packages/about-packaging-with-github-actions)
- [Monitoring and troubleshooting](https://docs.github.com/en/actions/monitoring-and-troubleshooting-workflows/about-monitoring-and-troubleshooting)

## GH Action repository naming convention

> **Note**   
> In relation to the Takeoff standards GitHub Action repository name should contain suffix `...-action` at the end of the name, during GitHub Action repository creation under [takeoff-com](https://github.com/takeoff-com) organization.   

## Workflows and Action location
We wouldn't open a new continent if we'll say that all workflows and actions and other scripts related to the CI/CD should be located under `../.github` folder in the root of your project.
All workflows and actions could be separated to respectively folders as it showed in the [PoC CI/CD](https://github.com/takeoff-com/poc-templated-cicd-python/tree/master/.github).  

```
├── .github
│   ├── CODEOWNERS
│   ├── ISSUE_TEMPLATE
│   │   ├── bug_report.md
│   │   ├── bug_report.yml
│   │   ├── config.yml
│   │   ├── documentation.yml
│   │   ├── feature_request.md
│   │   ├── feature_request.yml
│   │   └── question.yml
│   ├── README.md
│   ├── actions
│   │   └── slack_notification
│   │       └── action.yml
│   └── workflows
│       ├── black.yaml
│       ├── build_and_test.yaml
│       └── ci.yaml
```

## ReadMe as hub for documentation

Creating a **README** file for your action is strongly recommended, means it is the first place where your mates will get up to 90% of needed information. 
We recommend creating a **README** file to help people learn how to use your action. You can include this information in your `README.md` file:   

- A detailed description of what the action does
- Required input and output arguments
- Optional input and output arguments
- Secrets the action uses
- Environment variables the action uses

## Ownership

> **Note**   
> We recommend adding a `CODEOWNERS` [file](https://github.com/takeoff-com/poc-templated-cicd-python/blob/master/.github/CODEOWNERS) with the list of responsible persons for contribution and codeowning of the GitHub Action.   
> If you want to share your GitHub Action across the [takeoff-com](https://github.com/takeoff-com) organization, please, add the Production domain team **Hydra** to the `CODEOWNERS` list.


## Feedback & bugfixing

To provide a good tone of feedback and made the quality of your application transparent and bug free 😂  please, add [`ISSUE_TEMPLATES`](https://github.com/takeoff-com/poc-templated-cicd-python/issues/new/choose) form for the GitHub Action repository as it showed in [PoC CI/CD](https://github.com/takeoff-com/poc-templated-cicd-python/tree/master/.github/ISSUE_TEMPLATE).   


## CI/CD GitHub Action repository template
Navigate to the [cicd-actions-template](https://github.com/takeoff-com/cicd-actions-template) to use it as an initial step to create a shared GitHub Action repository under the [takeoff-com](https://github.com/takeoff-com) organization.  
Click on the **Use this template** button to create a new repository from `cicd-actions-template`.  

![create repo button](/images/en/docs/Engineering/cicd/actions_template_button.png)