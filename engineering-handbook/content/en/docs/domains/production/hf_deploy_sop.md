---
title: "Hotfix Deployment SOP"
linkTitle: "Hotfix Deployment SOP"
date: 2024-02-20
weight: 6
description: >
  SOP for Hotfix deployments of Release Train services
---

## Purpose

This page provides a standardized process for conducting Hotfix deployments of Release Train services to retailer environments.

Hotfixes can be fast-paced, and the steps required to plan and deploy a hotfix are complex. **We strongly recommend reading through this page in advance** so that you are prepared when one occurs.

## Prerequisites
This process closely parallels the [Deployment SOP](/docs/domains/production/deploy_sop/), so many of the prerequisites and steps listed here overlap with a standard deployment. 

1. Read and follow the [Change Control Process](https://takeofftech.atlassian.net/wiki/spaces/APCOE/pages/3874488436/Change+Control+Process#5.-Rollout-change).
1. Understand the risk-level of your change, and make sure you are [communicating the risk level to appropriate stakeholders](https://takeofftech.atlassian.net/wiki/spaces/APCOE/pages/3858235586/Change+Control+Process+Communication) and TAMs at minimum. 
1. Review the [Release Communication Best Practices deck](https://docs.google.com/presentation/d/1IxrKhZv_jre5S4hcBLBWOQ5ifp_qR12Xmz6ENMWUYqw/edit#slide=id.p).
1. Make sure you have access to:
   - The [MFC Change Calendar](https://calendar.google.com/calendar/embed?src=takeoff.com_reb4devrajh8tu5ndahrpkpdk4%40group.calendar.google.com&ctz=America%2FNew_York)
   - [Takeoff's Statuspage](https://engineering-handbook.takeofftech.org/docs/domains/production/statuspage/).
   - [Jenkins](https://jenkins.tom.takeoff.com/) - See [here](https://takeofftech.atlassian.net/wiki/spaces/SE/pages/1893433671/Jenkins) for more information.  

<p>

#### Hotfix Deployment Planning
Please keep the following in mind when planning a hotfix deployment:  
<ul>
   <ul>
      <li>Focus on clear, swift communication across all channels and reducing Mean Time to Repair (MTTR). Seek ways to accelerate the process and avoid bottlenecks.</li>
      <li>If planning a hotfix is near the end of work week, keep staffing and coverage in mind. For example, if a fix can feasibly be deployed on a Thursday, rather than EOD on a Friday, that   is likely better for both Takeoff and the client.</li>
      <li>If a fix is in-progress, remember that automated checks and build processes also need to run (CI, etc.) before the fix can be deployed. Remember to factor that in When scheduling a window for deployment so that we dont risk needing to re-schedule at the last minute.</li>
      <li>If a member of the Production Domain has not been looped in to the planning, reach out on [Slack](https://takeofftech.slack.com/archives/C027W27MHEY), and ideally the appropriate on-call person as defined in [Opsgenie](https://takeoff.app.opsgenie.com/). </li></ul></ul>

1. Follow the guidance in the [Change Control Process](https://takeofftech.atlassian.net/wiki/spaces/APCOE/pages/3874488436/Change+Control+Process#1.-Create%2FIdentify-Appropriate-Change-Ticket-(Jira)) for planning and communicating the change (i.e., Jira ticket, Slack Channel, etc). 
Note that *"Sev 1 hot fixes do NOT require a new change slack channel but the change should still be notified in #announcements-change-control within 24 hours of the incident."*
   
   i. Create an event on the [MFC Change Calendar](https://calendar.google.com/calendar/embed?src=takeoff.com_reb4devrajh8tu5ndahrpkpdk4%40group.calendar.google.com&ctz=America%2FNew_York), again, following the guidance in the [Change Control Process](https://takeofftech.atlassian.net/wiki/spaces/APCOE/pages/3874488436/Change+Control+Process#Roles-of-Key-Players-Involved-in-Change-Control-Process). 
   <br>Invite relevant internal stakeholders (Technical Account Manager, SRE team, engineering team members, etc). 

1. If there is enough time to do so prior to the planned deploy time for the hotfix (e.g., several hours or more), create a [Scheduled Maintenance](https://engineering-handbook.takeofftech.org/docs/domains/production/statuspage/schedule_maint/) event in Statuspage. 
2. Communicate your deployment plans and any needed pre-deploy activities in Slack (Change control, **#Incident**, and/or **#prod-support-\[retailer\]**) following the timelines in the Change Control process.
3. At the time of deployment, follow the remaining steps described below in [Deployment Steps](#deployment-steps---jenkins).

**Note**: Also make sure to contact [Team Chamaeleon](https://takeofftech.atlassian.net/jira/people/team/bde44f31-3d2a-4dba-b037-44cd57874e0f?ref=jira) and/or the appropriate Domain to follow through with planning the rollout of the fix to any remaining clients that may need it. Often, this involves rolling the fix into deployments for the remaining clients as part of Release Trains.  

#### Deployment Steps - Jenkins

Manually deploying an RT service requires access to [Jenkins](https://jenkins.tom.takeoff.com/).
    
1.  Depending on the requirements of the situation, you may need to join the Incident bridge or the meeting for the deployment in the [MFC Change Calendar](https://calendar.google.com/calendar/embed?src=takeoff.com_reb4devrajh8tu5ndahrpkpdk4%40group.calendar.google.com&ctz=America%2FNew_York) invite. If other stakeholders do not join immediately, reach out in Slack so that you are not waiting too long.
**Note**: For some deployments, you may not need to join any meetings or calls. For Hotfixes it is always good pactice to check if any stakeholders have joined the associated meeting.   

2. Log in to [Jenkins](https://jenkins.tom.takeoff.com/) and navigate to the [multi-deploy pipeline](https://jenkins.tom.takeoff.com/job/multi_deploy_pipeline/). 
<ol type="a">
   <ol type="a">
      <li>Select the appropriate <strong>Client</strong> and <strong>Env</strong>.</li>
      <li>Enter the appropriate build tag for the service(s) you want to deploy (e.g., decanting-service <a href="https://github.com/takeoff-com/decanting-service/releases/tag/24-02-05.619-hotfix.627">24-02-05.619-hotfix.627</a>).</li>
      <li>Click <strong>Build</strong>. The Stage View screen appears and the deployment begins.</li>
      <li>Communicate that the deployment is starting in the associated Slack channels.</li>
      <li>Monitor the deployment progress.</li>
   </ol>
</li>
</ol>

**Note**: You may need to hover over the in-progress service deployment and click **Proceed**.


<img src="/images/en/docs/Engineering/prod_domain/deploy process/Jenkins-deploy.png" alt = "jenkins" width="auto" height="auto" style="float:center" /> 

3.  If the deployment completed successfully, verify **System health** [on Grafana](https://grafana.tom.takeoff.com/d/se-service-health/system-health?orgId=1). If it did not succeed, review the logs and reach out to the [Production Domain](https://takeofftech.slack.com/archives/C027W27MHEY) for help if necessary. 

4. Verify that any affected Kubernetes (k8s) pods are up and running with the expected versions.
   If you have set up [Kubernetes](https://takeofftech.atlassian.net/wiki/spaces/~812792799/pages/1450082489/Kubernetes+at+Takeoff+101.0+GCloud+and+Kubernetes+Quickstart), the following commands are helpful for verifying deployments:

```
    kubectx <context> (for ex: kubectx gke\_takeoff-tangerine\_us-central1-a\_prod)    
    kubens <namespace> (for ex: kubens prod)
    helm list (lists versions of all the helm releases, done with Jenkins/Deploy.sh script)
    kubectl get pods 
    kubectl get deployments
    kubectl get pods -o jsonpath="{.items[*].spec.containers[*].image}" | tr -s '[[:space:]]' '\n' | sort | uniq -c | grep takeoff (lists ALL the versions of ALL the services deployed)
```
5.  Only after you have verified that system health looks good and all pods are up, follow the steps to [Complete the Scheduled Maintenance in Statuspage](https://engineering-handbook.takeofftech.org/docs/domains/production/statuspage/change_schedule/#complete-maintenance-early) event.

        {{% alert title="Confirm that the Statuspage Component is set to Operational" color="warning" %}}**Please Confirm** that you have set the [Component Status back to Operational](https://engineering-handbook.takeofftech.org/docs/domains/production/statuspage/change_schedule/#set-component-status-back-to-operational).{{% /alert %}}

6.  Post a “deploy is complete” message in the appropriate Slack channels.

7.  Be sure to complete any remaining steps to wrap up the change according to the [Change Control Process](https://takeofftech.atlassian.net/wiki/spaces/APCOE/pages/3874488436/Change+Control+Process#5.-Rollout-change).
    
#### If something goes wrong during the deploy

If issue(s) are encountered during a deploy, Takeoff teams **must** assess the issue(s) and determine the appropriate course of action (rollback, patch forward, etc.). 

Immediately reach out to the site's Technical Account Manager and post a message on the appropriate Change Control and Prod-Support Slack Channels.

Do not close out the Scheduled Maintenance window if it is ongoing. With permission from the client and/or TAM, Maintenance Windows can be [extended in Statuspage](https://engineering-handbook.takeofftech.org/docs/domains/production/statuspage/change_schedule/#extend-a-maintenance-window-in-progress). 

Opsgenie can also be used to request assistance. Additional guidance is available in the [Incident Management Handbook](https://engineering-handbook.takeofftech.org/docs/domains/production/incidentmgmt/).

If you need to find the team that owns a specific service, see the [Component Ownership Mapping](https://docs.google.com/spreadsheets/d/1Vr_CVMoz5rLPmyZczx8DF5yQ7HDveoY2OQyb9piebRQ/edit#gid=877683636) sheet.

Rollbacks should be a last resort and can take a considerable amount of time depending on DB schema changes, and decisions on rollback are time-sensitive. Again, please follow the guidance in the [Change Control Process](https://takeofftech.atlassian.net/wiki/spaces/APCOE/pages/3874488436/Change+Control+Process#5.-Rollout-change) if a problem is encountered during the deployment. 
