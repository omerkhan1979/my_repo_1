---
title: "Release Train Deployment SOP"
linkTitle: "RT Deployment SOP"
date: 2023-10-27
weight: 6
description: >
  SOP for Takeoff Release Train deployments
---
 <img src="/images/en/docs/Engineering/prod_domain/deploy process/rocket.jpg" alt = "rocket" width="300" height="350" style="float:right" /> 

## Purpose

This page describes the processes for deploying services that are part of Release Trains. For a high-level overview of Release Trains, see [Release Trains](https://engineering-handbook.takeofftech.org/docs/domains/production/release_trains.md).

## Prerequisites
1. With some exceptions, Release Train deployments follow the [Change Control Process](https://takeofftech.atlassian.net/wiki/spaces/APCOE/pages/3874488436/Change+Control+Process#5.-Rollout-change).
1. Release Trains use the [MFC Change Calendar](https://calendar.google.com/calendar/embed?src=takeoff.com_reb4devrajh8tu5ndahrpkpdk4%40group.calendar.google.com&ctz=America%2FNew_York) as a Source of Truth for scheduling.
1. If you are conducting an RT deployment, you need access to: 
   1. [Takeoff's Statuspage](https://engineering-handbook.takeofftech.org/docs/domains/production/statuspage/).
   2. The following repos:[Release Train Management](https://github.com/takeoff-com/release-train-management) and [Release Notes](https://github.com/takeoff-com/release-notes)


#### Deployment Planning

1. Release Trains are pre-planned and run on a two-week cycle. 

2. Release Train deployments are communicated to clients using an [Automated Process](https://github.com/takeoff-com/release-notes/blob/master/src/schedule/README.md) that creates and manages Scheduled Maintenance in [Takeoff's Statuspage](https://engineering-handbook.takeofftech.org/docs/domains/production/statuspage/).

If you need to have a Release Train service deployed outside of the normal Scheduled Maintenance window, or you need to have an updated build deployed to a Release Train that is currently being tested, see [Updating a Service version in an existing Release Train](#updating-a-service-version-in-an-existing-release-train).


#### Automated Deployments 

Release Train deployments are fully automated, however there are a few steps Team Chamaeleon members take to monitor deploys:
    
1.  (*Optional*) join the meeting for the deployment in the [MFC Change Calendar](https://calendar.google.com/calendar/embed?src=takeoff.com_reb4devrajh8tu5ndahrpkpdk4%40group.calendar.google.com&ctz=America%2FNew_York) invite.Wait a few minutes to allow other stakeholders to join. 

2.  In the Release-Train-Management repo, watch for the [Client-Env Specific Deploys](https://github.com/takeoff-com/release-train-management/actions/workflows/deploy-to.yaml) workflow to start. 
        
3. In Slack, watch the appropriate *"#prod-support-[retailer]"* channel to ensure that a message is posted from Echobot stating that the Scheduled Maintenance is closed. 

    If the Scheduled Maintenance does not close, follow the steps to [Complete the Scheduled Maintenance in Statuspage](https://engineering-handbook.takeofftech.org/docs/domains/production/statuspage/change_schedule/#complete-maintenance-early) event, and make sure to set the [Component Status back to Operational](https://engineering-handbook.takeofftech.org/docs/domains/production/statuspage/change_schedule/#set-component-status-back-to-operational).
   

#### Manually Triggered Deploys
Individual services on Release Trains can also be deployed through an automated process. 

#### Updating a Service version in an existing Release Train
If a new version of a service needs to be deployed to an existing release train, please reach out to Team Chamaeleon as soon as possible. 

    
#### If something goes wrong during the deploy

If issue(s) are encountered during a deploy, Takeoff teams **must** assess the issue(s) and determine the appropriate course of action (rollback, patch forward, etc.). _Area Subject Matter Experts must be looped in to ensure that all involved teams have the opportunity to provide insight_. 

Immediately reach out to the site's Technical Account Manager and post a message on the appropriate Change Control and Prod-Support Slack Channels.

Do not close out the Scheduled Maintenance window if it is ongoing. With permission from the client and/or TAM, Maintenance Windows can be [extended in Statuspage](https://engineering-handbook.takeofftech.org/docs/domains/production/statuspage/change_schedule/#extend-a-maintenance-window-in-progress). 

Opsgenie can also be used to request assistance. Additional guidance is available in the [Incident Management Handbook](https://engineering-handbook.takeofftech.org/docs/domains/production/incidentmgmt/).

If you need to find the team that owns a specific service, see the [Component Ownership Mapping](https://docs.google.com/spreadsheets/d/1Vr_CVMoz5rLPmyZczx8DF5yQ7HDveoY2OQyb9piebRQ/edit#gid=877683636) sheet.

Rollbacks should be a last resort and can take a considerable amount of time depending on DB schema changes, and decisions on rollback are time-sensitive. Again, please follow the guidance in the [Change Control Process](https://takeofftech.atlassian.net/wiki/spaces/APCOE/pages/3874488436/Change+Control+Process#5.-Rollout-change) if a problem is encountered during the deployment. 



5. Determine if the change can go out as part of a Release Train Scheduled Maintenance window.
            {{%expand "Expand for more details about deploying in Release Train Maintenance windows" %}}
<p>

Release Trains are managed by [Team Chamaeleon](https://takeofftech.atlassian.net/jira/people/team/bde44f31-3d2a-4dba-b037-44cd57874e0f?ref=jira), are pre-scheduled, and are mostly automated. See the [Release Trains](https://engineering-handbook.takeofftech.org/docs/domains/production/release-train.md) article for more details about the Release Train process.

Release Train deployment windows are typically planned as 2-hour time blocks, but rarely require more than 15 minutes to complete. As a result, these windows are a good opportunity to deploy other non-RT changes as part of the same Scheduled Maintenance window. 

Deploying during a Release Train Scheduled Maintenance Window does not exempt you from following the [Change Control Process](https://takeofftech.atlassian.net/wiki/spaces/APCOE/pages/3874488436/Change+Control+Process#5.-Rollout-change), [Deployment Planning](#deployment-planning) or the [Deployment Steps](#deployment-steps), however the MFC Change Calendar event and Scheduled Maintenance in Statuspage will already be created. 

To plan a deploy during a Release Train Scheduled Maintenance window, reach out to [Team Chamaeleon](https://takeofftech.atlassian.net/jira/people/team/bde44f31-3d2a-4dba-b037-44cd57874e0f?ref=jira) with your request and details about your planned deployment.  

{{% /expand%}}   
<p>