---
title: "Deployment SOP"
linkTitle: "Deployment SOP"
date: 2023-10-27
weight: 5
description: >
  SOP for Takeoff deployments
---
 <img src="/images/en/docs/Engineering/prod_domain/deploy process/rocket.jpg" alt = "rocket" width="300" height="350" style="float:right" /> 

## Purpose

This page provides a standardized process for deploying Takeoff services to retailer production environments.

## Prerequisites
1. Read and follow the [Change Control Process](https://takeofftech.atlassian.net/wiki/spaces/APCOE/pages/3874488436/Change+Control+Process#5.-Rollout-change).
1. Understand the risk-level of your change, and make sure you are [communicating the risk level to appropriate stakeholders](https://takeofftech.atlassian.net/wiki/spaces/APCOE/pages/3858235586/Change+Control+Process+Communication) and TAMs at minimum. 
1. Review the [Release Communication Best Practices deck](https://docs.google.com/presentation/d/1IxrKhZv_jre5S4hcBLBWOQ5ifp_qR12Xmz6ENMWUYqw/edit#slide=id.p).
1. Make sure you have access to the [MFC Change Calendar](https://calendar.google.com/calendar/embed?src=takeoff.com_reb4devrajh8tu5ndahrpkpdk4%40group.calendar.google.com&ctz=America%2FNew_York)
1. Make sure you have access to [Takeoff's Statuspage](https://engineering-handbook.takeofftech.org/docs/domains/production/statuspage/).<br>
1. Determine if the change can go out as part of a Release Train Scheduled Maintenance window.
            {{%expand "**Expand for more details about deploying in Release Train Maintenance windows**" %}}
<p>

Release Trains are managed by [Team Chamaeleon](https://takeofftech.atlassian.net/jira/people/team/bde44f31-3d2a-4dba-b037-44cd57874e0f?ref=jira), are pre-scheduled, and are mostly automated. See the [Release Trains](https://engineering-handbook.takeofftech.org/docs/domains/production/release-train.md) article for more details about the Release Train process.

Release Train deployment windows are typically planned as 2-hour time blocks, but rarely require more than 15 minutes to complete. As a result, these windows are a good opportunity to deploy other non-RT changes as part of the same Scheduled Maintenance window. 

Deploying during a Release Train Scheduled Maintenance Window does not exempt you from following the [Change Control Process](https://takeofftech.atlassian.net/wiki/spaces/APCOE/pages/3874488436/Change+Control+Process#5.-Rollout-change), [Deployment Planning](#deployment-planning) or the [Deployment Steps](#deployment-steps), however the MFC Change Calendar event and Scheduled Maintenance in Statuspage will already be created. 

To plan a deploy during a Release Train Scheduled Maintenance window, reach out to [Team Chamaeleon](https://takeofftech.atlassian.net/jira/people/team/bde44f31-3d2a-4dba-b037-44cd57874e0f?ref=jira) with your request and details about your planned deployment.  

{{% /expand%}}   
<p>

#### Planning a stand-alone Deployment

1. Follow the guidance in the [Change Control Process](https://takeofftech.atlassian.net/wiki/spaces/APCOE/pages/3874488436/Change+Control+Process#1.-Create%2FIdentify-Appropriate-Change-Ticket-(Jira)) for planning and communicating the change (i.e., Jira ticket, Slack Channel, etc).
   
   1. If site downtime is required for the change, and/or the change is high-risk, create an event on the [MFC Change Calendar](https://calendar.google.com/calendar/embed?src=takeoff.com_reb4devrajh8tu5ndahrpkpdk4%40group.calendar.google.com&ctz=America%2FNew_York), again, following the guidance in the [Change Control Process](https://takeofftech.atlassian.net/wiki/spaces/APCOE/pages/3874488436/Change+Control+Process#Roles-of-Key-Players-Involved-in-Change-Control-Process). 
   
        Invite relevant internal stakeholders (Technical Account Manager, SRE team, engineering team members, etc). 

    2. If the change does not require site downtime, and is a low-risk change, then it can likely be deployed without a Scheduled Maintenance window.
2. Create the [Scheduled Maintenance](https://engineering-handbook.takeofftech.org/docs/domains/production/statuspage/schedule_maint/) in Statuspage. 
3. Communicate your deployment plans and any needed pre-deploy activities in the appropriate **#\[retailer\]-deploys** and/or Change Control Slack channels following the timelines in the Change Control process. 
4. At the time of deployment, follow the remaining steps described below in [Deployment Steps](#deployment-steps).

#### Deployment Steps
   
1.  (*Optional*) Join the meeting for the deployment in the [MFC Change Calendar](https://calendar.google.com/calendar/embed?src=takeoff.com_reb4devrajh8tu5ndahrpkpdk4%40group.calendar.google.com&ctz=America%2FNew_York) invite. If possible, wait a few minutes to allow other stakeholders to join. 
<br>If a specific stakeholder is required, but does not join, message them in Slack. If they do not respond, escalate accordingly so that we are not keeping the Scheduled Maintenance window open unnecessarily.
        
1.  Log in to [Statuspage](https://engineering-handbook.takeofftech.org/docs/domains/production/statuspage/) and navigate to the Scheduled Maintenance. The Scheduled Maintenance will auto-trainsition to in-progress if you [followed the guidance correctly](https://engineering-handbook.takeofftech.org/docs/domains/production/statuspage/schedule_maint/).    
   
2.  Use [Grafana to confirm that all services are up and running and show no errors in logs](https://grafana.tom.takeoff.com/d/se-service-health/system-health?orgId=1). 

3.  If you are deploying during a Release Train Scheduled Maintenance window, confirm that the Release Train deployment has completed by checking in the appropriate **#\[retailer\]-deploys** channel.

4.  In your associated Change Control Slack channel, post a “deploy is starting” message.

5.  Proceed with the deployment steps required by your service and domain.

6.  If the deployment completed successfully, verify **System health** [on Grafana](https://grafana.tom.takeoff.com/d/se-service-health/system-health?orgId=1) (use the drop-down at the top to navigate to the specific retailers).

7.  Verify that any affected Kubernetes (k8s) pods are up and running with the expected versions.
   If you have set up [Kubernetes](https://takeofftech.atlassian.net/wiki/spaces/~812792799/pages/1450082489/Kubernetes+at+Takeoff+101.0+GCloud+and+Kubernetes+Quickstart), the following commands are helpful for verifying deployments:

```
    kubectx <context> (for ex: kubectx gke\_takeoff-tangerine\_us-central1-a\_prod)    
    kubens <namespace> (for ex: kubens prod)
    helm list (lists versions of all the helm releases, done with Jenkins/Deploy.sh script)
    kubectl get pods 
    kubectl get deployments
    kubectl get pods -o jsonpath="{.items[*].spec.containers[*].image}" | tr -s '[[:space:]]' '\n' | sort | uniq -c | grep takeoff (lists ALL the versions of ALL the services deployed)
```

11.  Only after you have verified that system health looks good and all pods are up, follow the steps to [Complete the Scheduled Maintenance in Statuspage](https://engineering-handbook.takeofftech.org/docs/domains/production/statuspage/change_schedule/#complete-maintenance-early) event.

        {{% alert title="Confirm that the Statuspage Component is set to Operational" color="warning" %}}**Please Confirm** that you have set the [Component Status back to Operational](https://engineering-handbook.takeofftech.org/docs/domains/production/statuspage/change_schedule/#set-component-status-back-to-operational).{{% /alert %}}



12.  Post a “deploy is complete” message in the appropriate Change Control and (if part of an RT window) **#\[retailer\]-deploys** Slack channels.

13.  Be sure to complete any remaining steps to wrap up the change according to the [Change Control Process](https://takeofftech.atlassian.net/wiki/spaces/APCOE/pages/3874488436/Change+Control+Process#5.-Rollout-change).

    
#### If something goes wrong during the deploy

If issue(s) are encountered during a deploy, Takeoff teams **must** assess the issue(s) and determine the appropriate course of action (rollback, patch forward, etc.). _Area Subject Matter Experts must be looped in to ensure that all involved teams have the opportunity to provide insight_. 

Immediately reach out to the site's Technical Account Manager and post a message on the appropriate Change Control and Prod-Support Slack Channels.

Do not close out the the Scheduled Maintenance window if it is ongoing. With permission from the client and/or TAM, Maintenance Windows can be [extended in Statuspage](https://engineering-handbook.takeofftech.org/docs/domains/production/statuspage/change_schedule/#extend-a-maintenance-window-in-progress). 

Opsgenie can also be used to request assistance. Additional guidance is available in the [Incident Management Handbook](https://engineering-handbook.takeofftech.org/docs/domains/production/incidentmgmt/).

If you need to find the team that owns a specific service, see the [Component Ownership Mapping](https://docs.google.com/spreadsheets/d/1Vr_CVMoz5rLPmyZczx8DF5yQ7HDveoY2OQyb9piebRQ/edit#gid=877683636) sheet.

Rollbacks should be a last resort and can take a considerable amount of time depending on DB schema changes, and decisions on rollback are time-sensitive. Again, please follow the guidance in the [Change Control Process](https://takeofftech.atlassian.net/wiki/spaces/APCOE/pages/3874488436/Change+Control+Process#5.-Rollout-change) if a problem is encountered during the deployment. 
