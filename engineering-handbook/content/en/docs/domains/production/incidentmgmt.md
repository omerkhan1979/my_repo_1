---
title: "Incident Management Handbook"
linkTitle: "Incident Management"
date: 2021-07-14
weight: 1
description: >
  Our in-depth Incident Management handbook. 
---
{{% alert title="Note" color="warning" %}}This content was originally based on Atlassian’s excellent [document](https://takeofftech.atlassian.net/wiki/download/attachments/1302757582/Atlassian-incident-management-handbook-(1).pdf?api=v2) on their Incident Management process, which I had the pleasure of hearing them discuss at a past AWS re:Invent conference.

This is a long document as it covers both Incident Management process and application of different tools across that process. A shortened runbook for use by the Incident Manager during an Incident can be found in the [incident manager runbook](https://cartfresh.atlassian.net/wiki/spaces/~406080379/pages/1360626431/Incident+Manager+Run-book?atlOrigin=eyJpIjoiZjc3M2RmYWQ1OGQ2NGIzNDlmZTJkOWVlMzJjODZjYmUiLCJwIjoiYyJ9). {{% /alert %}}

Incident Values
---------------

A process for managing Incidents can't cover all possible situations, so we should empower our teams with general guidance in the form of values. Incident values are designed to:

- Guide autonomous decision-making by people and teams in Incidents and postmortems. 
- Build a consistent culture between teams of how we identify, manage, and learn from Incidents.
- Align teams as to what attitude they should be bringing to each part of Incident identification, resolution, and reflection.

| **Stage** | **Incident Value** | **Related Takeoff Value** | **Rationale** |
| --- | --- | --- | --- |
| Detect | Know about issue before our Clients do | Commit to Service completeness, building monitoring and alerting into all Services | A balanced service includes enough monitoring and alerting to detect Incidents before our customers do. <br><br>The best monitoring alerts us to problems before they even become Incidents. |
| Respond | Escalate, escalate, escalate | Work as a Team | Nobody likes being woken up and we should not take the responsibility lightly. But people understand that occasionally they will be woken for an Incident where it turns out they aren't needed. What’s usually harder is waking up to a major Incident and playing catch up when you should have been alerted earlier.<br><br>We won't always have all the answers, so "don't hesitate to escalate." |
| Recover | Issues will happen, clean it up quickly | Maintain empathy for our Clients | Our Clients don't care why their service is down, only that we restore service as quickly as possible.<br><br>Never hesitate in getting an Incident resolved quickly so that we can minimize impact to our Clients. |
| Learn | Always Blameless Postmortem | Assure openness and honesty in our communications | Incidents are part of running services. We improve services by holding teams accountable, not by apportioning blame. |
| Improve | Never have the same Incident twice | Be the change we seek | Identify the root causes and the changes that will prevent the whole **class** of Incident from occurring again.<br><br>**Commit** to delivering specific changes by specific dates. |

Tooling Requirements
--------------------

- **Fire Hydrant**
  - Incident Process Orchestration tool, which performs many actions for us during an Incident including:
    -   Initiation the Incident workflow
    -   Creation of various Incident process related artifacts such as Incident Slack Channel and Meets Channel
    -   Updating of Statuspage based on Incident status changes
    -   Invoking Opsgenie to pull in Incident Responders as needed
    -   and more

- **Incident Tracking**
  - Every Incident should be tracked as a Zendesk Issue with a mirrored Jira Issue automatically created to track the completion of postmortems and mitigation efforts.

- **Chat**
  - Using Slack as a real-time text communication channel is fundamental to diagnosing and resolving the Incident as a team.
  - We utilize the following channels and formats for Incident channels
    - `#incidents` - this channel records all Slack channels which are created for Incidents (Note: this channel name will change in the near future to remove the reference to “Severity”)
    - `#incident-{site ID}-{location}-{zendesk ticket #}` - this is the format of the Incident Slack channels which will be created, e.g. `#incident-wf0001-clifton-nj-87046`
  - Reacting to a slack message within the incident channel with a **&#58;star:** emoji will track that comment, which can then be used in RCA and post-mortem activities

- **Video/Voice Conferencing**
  - For Incidents, team video/voice conferencing via Google Meet can help us discuss, present, and agree on solution approaches. It is also useful to engaging partners like Knapp to speed understanding of the nature of the problem which is causing the Incident.

- **Alerting**
  - Firehydrant will page different teams that have been configured based on incident role and expectations. FireHydrant integrates with Opsgenie. It does not generate alerts at all, rather invokes Opsgenie to generate alerts for Incident team members as needed based on the FireHydrant Incident runbook or as deemed necessary by the Incident Manager.

- **Documentation**
  - Utilize Jira [Incident Board](https://takeofftech.atlassian.net/secure/RapidBoard.jspa?rapidView=256) for Incident state documents sharing postmortem
  - TAMS will be utilizing FireHydrants built in Post-mortem tool as part of the RCA process.

- **Service Status**
  - Communicating status with both internal stakeholders and Clients through email templates or Service Status Pages helps keep everyone in the loop about the nature of and progress on resolving the Incident.
    - We utilize Zendesk triggers to automatically update from the Zendesk Incident issue
    - We generate emails manually from a basic template and send to defined Distribution Lists to target Internal or Client facing personnel
    - We utilize a Service Status Page solution via Statuspage. Updates to the status page and Zendesk ticket will be made every 30 minutes during a severity 1 incident.

Role Requirements & Expectations
-----------------


<table>
<thead>
<tr><th>
Role
</th><th>
Expectations
</th>
</thead>
<tbody>
<tr>
<td>Software Incident Manager</td>
<td>
Respond to Takeoff software incidents and take any necessary steps to restore service and return to normal operations as quickly as possible

Asking the following questions and documenting in slack:

-   What is the client impact?
-   What is known about the problem?
-   What has been attempted?
-   What are the next steps?

Documenting updates and progress in slack for viewers approximately every 30 minutes
</td>
</tr>
<tr>
<td>Hardware incident manager (Technician On-call) - NEW</td>
<td>
Respond to hardware-related incidents and lead efforts at diagnosing and resolving the issue. This may be through working directly with the site team or working through a Takeoff tech on-site. Work with Knapp to drive forward progress for hardware or Knapp software troubleshooting. Escalating to maintenance leadership as needed.

Ask the following questions

-   What is the client impact?
-   What is known about the problem?
-   What has been attempted?
-   What are the next steps?

Documenting updates and progress in slack for viewers approximately every 30 minutes.
</td>
</tr>
<tr>
<td>On-site Technician - NEW</td>
<td>
Takeoff Technician on-site point of contact. This role is focused on hands-on troubleshooting and electro-mechanical issue resolution - taking necessary actions and delivering updates to/through the remote tech on-call. Provide additional information about client impact and on-site communication.
</td>
</tr>
<tr>
<td>Domain Expert (Outbound engineer, or SRE engineer)</td>
<td>
Point of contact and SME for software-related incidents. This role is added on-demand depending on the software issue
</td>
</tr>
<tr>
<td>Account team - NEW</td>
<td>
Communicates with the site team and/or retailer leadership. Assess and understand client impact, and share details with the incident manager or tech on-call. Understanding operational impact, helping to make strategic decisions (decisions to cancel orders, business level decisions, etc)
</td>
</tr>
<tr>
<td>Support team</td>
<td>
Communicate with the ticket creator, provide updates on the status and next steps in the ticket

Assist in troubleshooting, paging additional responders as needed, and monitor the background 
</td>
</tr>
<tr>
<td>TAMs</td>
<td>
Responsible for the customer-facing retrospective after the incident is resolved. With a focus on learning how to prevent incidents of this nature. Scheduling and coordinating the RCA, compiling the artifacts of the incidents, and assigning any action items from the incidents. 
</td>
</tr>
</tbody>
</table>

Incident Stages
---------------

### **Every incident has 4 stages in FireHydrant:**

1.  Acknowledged - Incident Started
2.  Investigating - the team is looking for the cause of the issue
3.  Identified - the team identified the cause of the issue and is on a fix
4.  Mitigated - the issue has been resolved

## Acknowledged

However an Incident occurs, the first step the team takes is logging an issue ticket in Zendesk. Takeoff staff should be able to check if there is an Incident already in progress by looking at the Slack [`#incidents`](https://takeofftech.slack.com/archives/CSEJZS7P1) channel. Dashboards should be active around office space with the Incident Dashboards and/or Service Status page so affected teams can easily monitor Incidents in progress.  
  
The following attributes of an Incident should be captured and flow through the various systems involved in resolving and documenting the Incident:

| **Ticket Field** | **Type** | **Help Text** |
| --- | --- | --- |
| Summary | Text | Brief description of issue. |
| Description | Text | Longer description of the issue. |
| Client Impact | Text | How is the Incident impacting the Client’s business processes? [Refreshed Incident Ranking Workflow](https://takeofftech.atlassian.net/wiki/spaces/ST/pages/2934505833/Refreshed+Incident+Ranking+Workflow) |
| Client Urgency | Text | How long until the Incident will impact the Client’s business processes? [Refreshed Incident Ranking Workflow](https://takeofftech.atlassian.net/wiki/spaces/ST/pages/2934505833/Refreshed+Incident+Ranking+Workflow) |
| Incident Priority | Single-select | A derived value based on Client Impact and Urgency:  <br>[Refreshed Incident Ranking Workflow](https://takeofftech.atlassian.net/wiki/spaces/ST/pages/2934505833/Refreshed+Incident+Ranking+Workflow) |
| Faulty Service | Single-select | The service or component that has the fault that’s causing the Incident. Take your best guess if unsure. Select “Unknown” if you have no idea. |
| Affected Clients | Multi-select | Which Clients are affected by this Incident? Select any that apply. |
| Affected MFCs | Multi-select | Which MFCs are affected by this Incident? Select any that apply. |

Once the Incident issue is created, an Incident Key, e.g. “albertsons-incident-42675” is generated for a variety of purposes:

* Slack Incident channel naming
    
* Opsgenie Alert description (or tagging) for any Alerts to the on-call Incident Manager and necessary Engineering teams (Note: Incident Flow is not yet functioning in this way but will be)
    
* Jira Incident Issue description (or tagging) for Issue which is used for documenting the Incident (Note: Incident Flow is not yet functioning in this way but will be)
    
Once an incident is declared, FireHydrant will automatically create the communication channels in slack and google meet, and page the relevant on call responders. The goal at this point is to establish and focus all Incident team communications in well-known places.

We use four team communication methods for every Incident:

* Zendesk: This acts as the external entry point for Clients or Partners to report Incidents. It is also used for communicating with Clients, Partners, and internal teams around the nature and state of the Incident.
    
* Slack: The Incident Slack Channel allows the Incident team to communicate, share observations, links, and screenshots in a way that is timestamped and preserved. Automatically assign the channel the same name as the Incident issue key (e.g., [#wakefern-incident-40206](https://takeofftech.slack.com/archives/C021S13CW9H)), which makes it easier for Incident Responders to find.
    
* Google Meet: The Incident Meets Conference Bridge allows face-to-face synchronous video & audio communication, which helps teams build a shared understanding of the situation and make decisions faster.
    
* Jira: The Incident Issue is where we track Incident actions (for example, who changed what, when, why, how to revert, during the Incident, etc) and a timeline of events. An Incident Issue is extremely useful as the source of truth during complex or extended Incidents and for generating action items and learning from the Incident
    

Using both video conference and text chat room synchronously works best during most Incidents, because they are optimized for different things. Video chat excels at creating a shared mental picture of the Incident quickly through group discussion, while text chat is great for keeping a timestamped record of the Incident, shared links to dashboards, screenshots, and other URLs. In this way, video and text chat are complementary rather than one or the other.

The Incident Slack Channel should also be used to record important observations, changes, and decisions that happen in unrecorded conversations. The Incident Manager (or anyone on the Incident team) does this by simply noting observations, changes, and decisions as they happen in real-time. It’s okay if it looks like people are talking to themselves. These notes are incredibly valuable during the Incident postmortem when teams need to reconstruct the Incident timeline and figure out the thing that caused it. Reacting to a slack message within the incident channel with a star emoji will track that comment, which can then be used in RCA and post-mortem activities.

Communications automation sets the Slack Channel topic with information about the Incident and useful links, including:

- The Incident Summary and Priority
- Who is acting in what role, starting with the Incident Manager
- Links to the Incident Zendesk issue, the Meet video/phone conference room, and the Jira Incident Issue (Note: automation does not currently document the Jira Incident Issue in the Slack channel, but this capability should be added)

Remember that we automatically named the Slack Channel based on the Incident’s issue key (e.g., [#wakefern-incident-40206](https://takeofftech.slack.com/archives/C021S13CW9H)), and our page alerting automation includes this issue key in page alerts, and all of our internal communication about the Incident (covered later) includes the same issue key. This consistency means that anyone with that issue key can easily find the Incident’s chat room and come up to speed on the Incident.

### Assess

{{< alert title="Note" >}}Takeoff has historically utilized the concept of Issue Severity which flows from Zendesk and related [definition](https://takeofftech.atlassian.net/wiki/spaces/EN/pages/1090093101/Severity+definition+and+SLAs) to determine whether an Issue warrants invoking [Incident Flow](https://takeofftech.atlassian.net/wiki/spaces/~406080379/pages/2840200201/Proposed+Incident+Management+Process+Changes#Separation-of-Severity-from-Incident-Flow). We are retiring usage of Severity as the determiner of whether an Issue warrants handling as an Incident and will be removing all references to Severity from Incident Management processes.  
The concepts of Client Impact, Client Urgency, and Issue Priority as described below are new and will be utilized going forward for determining if an Issue warrants invoking Incident Flow.{{< /alert >}}

After the Incident team has their communication channels set up, the next step is to assess and verify the Incident’s Priority so the team can decide what level of response is appropriate.

To help determine whether an Issue warrants Incident Flow and whether changes in circumstances might warrant changes in Issue Priority, we leverage an _Incident Priority Matrix_ which measures the cross product of the issue’s Client Impact and Urgency to determine Priority.

#### Incident Priority Matrix

Incident priority levels and client impact definitions an be referenced [here](/wiki/spaces/EN/pages/3753050461).

## Investigating

### Communicate

Once we are confident that the Incident is real, the incident manager is responsible for working with the support team via slack to provide additional information or context related to the incident that the support team can use for their regular 30-minute updates. Communicating quickly about new Incidents helps to build trust with our staff and Clients.

#### Status Pages

We are currently working on tying site status into our incident flow. This section is kept for future usage.

#### Escalate

As Incident Manager, you have taken command of the Incident, established team communications, assessed the situation, and informed Staff and Clients that an Incident is in progress. What’s next?

Sometimes the first responders to the Incident may be all who are needed in order to resolve the Incident, but more often than not, you need to bring other Teams into the Incident by paging them. This is called _escalation_.

The key system in this step is Opsgenie. Opsgenie allows us to define on-call rosters so that any given Team has a rotation of staff who are expected to be contactable to respond in an Incident. This is superior to needing a specific individual all the time (“get Andrew again”) because individuals won’t always be available (they tend to go on vacation from time to time, change jobs, or burn out when you call them too much). It is also superior to “best efforts” on-call because with defined rotations it’s clear which individuals are responsible for responding.

When escalating to Teams, we should always include the Incident’s Issue Key on the Alert about the Incident. This is the key that the person receiving the Alert uses to join the Incident’s Slack channel.

During an incident, if the incident manager or Technical Support team needs to pull in domain experts into the incidents, then FireHydrant should be used using the ‘incident update’ command.

Handover for Long Running Incidents:

-   If incident manager is needing a break after 4 hours pull in the next incident manager who is next on the rotation or another incident manager in your timezone.

### Delegate

The Incident Manager can also devise and delegate roles as required by the Incident, for example, multiple tech leads if more than one stream of work is underway, or separate internal and external communications managers.

After escalating to someone and they join the Incident response, the Incident Manager delegates a role to them. As long as they understand what’s required of their role then they will be able to work quickly and effectively as part of the Incident team. We should train our responders on what the Incident roles are and what they do using a combination of documentation and hands-on “shadowing” experience.

In complicated or large Incidents such as a multiple Client impacting outage of our Cloud Provider's infrastructure, it is advisable to bring on another qualified Incident Manager as a backup “sanity check” for the Incident Manager.

The Slack Channel’s topic should be used to show who is currently in which role, and this must be kept up-to-date if roles change during an Incident. (Note: this has historically not been done due to lack of Roles usage.)

#### Send follow-up communications

Internal stakeholders who want to know the current status of the incident and stay updated throughout should join the incident channel.

### Mitigated

An Incident is resolved when the current or imminent business impact has ended. At that point, the emergency response ends and the team transitions onto any cleanup tasks and the postmortem

Cleanup tasks should be linked and tracked as issue links from the Incident’s Jira Issue.

We should utilize Zendesk and Slacks start-of-impact time, detection time, and end-of-impact time as part of its RCA/postmortem process. This information is used to calculate time-to-recovery (TTR) which is the interval between start and end, and time-to-detect (TTD) which is the interval between the start and detect. The distribution of our the Incident TTD and TTR is often an important business metric.

We send final internal and external communications when the Incident is resolved. The internal communications have a recap of the Incident’s impact and duration, including how many support cases were raised and other important Incident dimensions, and clearly state that the Incident is resolved and there will be no further communications about it. The external communications are usually brief, telling Client(s) that service has been restored and we will follow up with a postmortem.


Summary of Tools and Usage
--------------------------

### FireHydrant

-   Primary tool used to orchestrate communication, create collateral, and organization during an incident.
-   Used to declare incidents, track important developments (starring messages), and then utilized as a guide during RCAs

### Zendesk

- Client and Partner ticket creation to inform Technical Support of an issue
- Communication updates with ticket creator, internal Takeoff teams, and Client & Partners

### Slack

- Creation of an Incident specific channel
  - Attributes
    - Channel naming convention
      - Incident Key
    - Indicates who has major Incident Roles including Incident Commander
    - Indicates Confluence page with Incident details
- Slack Bot in Client Prod channel that an Incident is in progress for the Client and how to join

### Google Meet

* Incident Command Center
  - Opened to facilitate
    - Video/Audio Conference Bridge
    - Alerting and Escalation
    - Automatic Incident Data Gathering

### Opsgenie

- Alerting
    - Ability to examine at alert streams from outside sources such as Prometheus
    - Ability to assign, acknowledge, and escalate Alerts

- Services/Teams/On-Call Rotations
    - Tying Services to associated Teams
    - Tying On-Call Rotations to Teams
    - Facilitating escalating to on-call engineers as needed


### Jira

- Creation of the Incident Issue used to document the Incident ([RCA board](https://takeofftech.atlassian.net/jira/software/c/projects/RCA/boards/256?selectedIssue=RCA-466))
- Creation of an Incident tag (use “issue key” as described above)
- Creation of Incident remediation artifacts, e.g. stories for work on mitigations

### Service Status Page

{{< alert color="warning" title="Please Note" >}}NOT CURRENTLY UTILIZED BUT PLANNED FOR USE IN NEAR FUTURE{{< /alert >}}
