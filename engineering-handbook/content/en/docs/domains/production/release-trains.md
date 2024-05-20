---
title: "Release Trains"
linkTitle: "Release Trains"
date: 2023-31-10
weight: 3
description: About Takeoff Release Trains
---

### Process Overview

Release Trains (RTs) are a set of Takeoff services that are tested and deployed as a group for the purpose of consistency and efficiency. 

At a very high level, the key parts of the Release Train process are as follows:

1. **RT Cycle Start**
   
   Release Trains run on a two-week cycle, starting on **even** Wednesdays at 12:00 PM Eastern time.

2. **Creation of Epic and Deployment Requests**
   
   For each RT cycle, a partially automated process runs that creates a new PROD Epic with a specific naming scheme (e.g., `RTww-yy:[YY-MM-DD]` for example: `RT44-23:[23-11-01]`). 
   
   For each client's deployment, a Deployment Request ticket is also created with a specific naming scheme of `[client] RTww-yy:[YY-MM-DD] - [Release Qualification]` (e.g., `[Loblaw/Lobster] RT44-23:[23-11-01] - [Release Qualification ]`). Deployment Request tickets are populated with key details such as Due Date (date of deploy), Deploy Type, and Clients Impacted.

3. **"Wednesday Deploy Process" (a.k.a. RT Cut)**
   
   At the beginning of each cycle, [@team-chamaeleon](https://takeofftech.atlassian.net/jira/people/team/bde44f31-3d2a-4dba-b037-44cd57874e0f?ref=jira) runs an automated process known as the "RT Cut." 
   
   This automated process upgrading our remaining QAI environments (Abs and Winter), creating Test Plans and Test Runs in Testrail, creating an On-Demand Environment (ODE) for each retailer, running automated tests on each retailer's ODE, and reporting the results to Testrail. 
   
   More information about this process is available in the [Release Train Management](https://github.com/takeoff-com/release-train-management#readme) and [Pytest Reporting](https://github.com/takeoff-com/pytest-reporting) repos in Github.

4. **Test and Check Results**
   
   Test results are reviewed by members of [@team-chamaeleon](https://takeofftech.atlassian.net/jira/people/team/bde44f31-3d2a-4dba-b037-44cd57874e0f?ref=jira), and any test failures are investigated and reported. If all testing is successful and there are no blocking issues, the process continues.

   Automated tests are managed in the [Release Qualification Tools repo](https://github.com/takeoff-com/release-qualification-tools) in Github. 

5. **Deployment Scheduling**
   
   A week before each RT cut occurs, calendar events are created for client deployments, and these events include links to Deployment Request Jira tickets and key stakeholders. Deployments are carried out for each retailer on a [predefined schedule](https://docs.google.com/spreadsheets/d/1FBR3cNin3fUXxM3Rrx0gqqPW0uXJGks0Gxq5sRtwwkc/edit#gid=0), which can be referenced in the [MFC Change Calendar](https://calendar.google.com/calendar/embed?src=takeoff.com_reb4devrajh8tu5ndahrpkpdk4%40group.calendar.google.com&ctz=America%2FNew_York). The MFC Change calendar is the source of truth for all Release Train deployments.

{{% alert title="Please Note" color="warning" %}} If you do not have access to the [MFC Change Calendar](https://calendar.google.com/calendar/embed?src=takeoff.com_reb4devrajh8tu5ndahrpkpdk4%40group.calendar.google.com&ctz=America%2FNew_York), please reach out to [@team-chamaeleon](https://takeofftech.atlassian.net/jira/people/team/bde44f31-3d2a-4dba-b037-44cd57874e0f?ref=jira).{{% /alert %}}

{{% alert title="Please Note" color="warning" %}} For pre-deploy activities or other discussion about Release Train deploys, use the corresponding **[retailer]-deploys** (_for example:_ #MAF-Deploys) Slack channels.{{% /alert %}}



---


### Frequently Asked Questions
    
**Which services are currently part of the RT?**

The services deployed as part of Release Trains can be referenced in the [Release Train Management Repo](https://github.com/takeoff-com/release-train-management/blob/master/RT_SERVICES.yaml). 

**What blocks the release pipeline from proceeding?**
    
Failed deployments of services.
        
**Which retailer envs are used for performing Release Qualification?**
        
All clients are tested using [On-Demand Environments](https://github.com/takeoff-com/on-demand-env), however, `winter-qai` and  `abs-qai` are still in use for certain tests that cannot yet be performed on ODEs.
        
**Do all retailer envs get updated to the latest RT?**
    
Yes - the exception would be if the deployment of the previous RT to production did not happen, causing us to keep the previous version of the RT code for a given retailer.

**How do I find the current Release Train version?**

To find the current Release Train version, navigate to the [Production Domain Releases](https://takeofftech.atlassian.net/projects/PROD?selectedItem=com.atlassian.jira.jira-projects-plugin:release-page) page in Jira. Ensure that **Unreleased** is selected in the dropdown box, and you will be provided with the RT version(s). 

Note that you may see more than one version. This is because in some cases, there is overlap because the previous RT has not yet been deployed to all the clients. Overlap can occur for multiple reasons. For example, if a client is unable to take a deploy on the planned date and the deploy needs to be moved out. 

In this situation, both RTs are in play - the previous RT from the perspective of the deployment itself and the upcoming RT from the perspective of both RQ and deployment to other retailers.

![image alt text](/images/en/docs/Engineering/prod_domain/rt-track-and-scope/3459580097.png?width=680)

**What is the Release Qualification status, and when is it planned to be deployed to Production?**
    
Navigate to the [Takeoff Deployment Dashboard](https://takeofftech.atlassian.net/jira/dashboards/10131).

1. Enter the RT version - note the naming scheme is `RT<ww>-<yy>`, where `<ww>` is the week of the cut and `<yy>` is the year.

   In this example, `RT42-23`, refers to the RT that was cut on the 42nd week of year 2023. RT versions are also followed by a date inside square brackets: `[yy-mm-dd]`. That value is not needed when filtering for deploys or scope, but it identifies the day that the release train was "cut" (the [RT Automation was run](https://github.com/takeoff-com/release-train-management)). 
   
   Note that we have RTs cut every two weeks, so the naming scheme will continue to have an even `<ww>` number.

![image alt text](/images/en/docs/Engineering/prod_domain/rt-track-and-scope/3460366388.png)

2. The status of each client's testing is displayed in the Status column.

3. The due date here refers to the planned deployment date to the given retailer's prod environment. The due dates above are matched with events on the [MFC Change Calendar](https://calendar.google.com/calendar/embed?src=takeoff.com_reb4devrajh8tu5ndahrpkpdk4%40group.calendar.google.com&ctz=America%2FNew_York) (as seen below). 

   To view this calendar, [you need to add it in Google Calendar](https://support.google.com/calendar/answer/37100?hl=en&co=GENIE.Platform%3DDesktop).

![image alt text](/images/en/docs/Engineering/prod_domain/rt-track-and-scope/3459743940.png)

### What is the scope of a given Release Train?

The scope of Release Train's contents is identified using Jira Automation rules that watch the **Development** field in Jira tickets for merges to RT repos. 

If a ticket is in one of a specific set of Jira projects and has a merge to a repo for an RT service, when the ticket moves to a Done state, the fix version for the upcoming RT is automatically applied.

To see which Jira tickets are included in the scope of the RT:

1. Navigate to the [Takeoff Deployment Dashboard](https://takeofftech.atlassian.net/jira/dashboards/10131).

2. Scroll down to the Select the version of RT from the drop-down - ensure that you have only selected one Release Train version (multi-select is not supported). 
   
   In most cases, you would want to select a single RT, but there can be times, for example, where a TAM would want to know what the scope/contents of multiple RTs were because their client skipped a previous RT and is not getting a bundled version of multiple RTs.

![image alt text](/images/en/docs/Engineering/prod_domain/rt-track-and-scope/3459612956.png)