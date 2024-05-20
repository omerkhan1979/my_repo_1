---
title: "Takeoff's Statuspage"
linkTitle: "Takeoff Statuspage"
weight: 6
description: >-
     About Takeoff's instance of Atlassian Statuspage.
---
# About Statuspage

[Statuspage](https://www.atlassian.com/software/statuspage) is an Atlassian tool that we use to communicate [Scheduled Maintenance](https://support.atlassian.com/statuspage/docs/schedule-maintenance/) (production deploys, etc) and [Service Incidents](https://support.atlassian.com/statuspage/docs/what-is-an-incident/) to our clients.

The two urls for the site are used as follows: 
- Client Facing Site: [status.takeoff.com](https://status.takeoff.com/access/login) - This is where clients log in to see scheduled maintenance and real-time updates about incidents.
- Internal Site: [https://manage.statuspage.io/pages/qth8l8vxd7y4](https://manage.statuspage.io/pages/qth8l8vxd7y4) - This is our management UI where Takeoff employees can create and manage scheduled maintenance. 

See the following articles for more information: 
- [Statuspage Overview](#client-facing-page-and-notifications)
- [How to Schedule Maintenance in Statuspage](https://engineering-handbook.takeofftech.org/docs/domains/production/statuspage/schedule_maint/)
- [How to Update Scheduled Maintenance in Statuspage](https://engineering-handbook.takeofftech.org/docs/domains/production/statuspage/change_schedule/)
- [How to create and manage users in Statuspage](https://engineering-handbook.takeofftech.org/docs/domains/production/statuspage/manage_users/)

## Client-facing Page

Each of our customers has a client-specific view of ([status.takeoff.com)](https://status.takeoff.com). For example, Sedano's would see the following:
 
![image alt text](/images/en/docs/Domains/Production/statuspage/schedule_maintenance/client-page.png)

## Subscriber Notifications
Anyone who subscribes via email or text message will receive notifications from Statuspage about Incidents and Scheduled Maintenance.

#### Emails 
Are sent from from noreply.statuspage@takeoff.com and contain basic details about Scheduled Maintenance:
![image alt text](/images/en/docs/Domains/Production/statuspage/schedule_maintenance/email_overview.png) 

#### Text Messages (SMS)
![image alt text](/images/en/docs/Domains/Production/statuspage/schedule_maintenance/sms_overview.png)  

## Statuspage and Release Train Management

To support the regularly-scheduled deployments that take place for [Release Trains](https://engineering-handbook.takeofftech.org/docs/domains/production/rt-track-and-scope/), [@team-chamaeleon](https://github.com/orgs/takeoff-com/teams/team-chamaeleon) has created an automated process that creates, updates, and closes Scheduled Maintenance in Statuspage for each client's Release Train deployment. 

More details about how Scheduled Maintenance is automatically created is available in the [release-notes repo readme](https://github.com/takeoff-com/release-notes/blob/master/README.md). Similarly, information about how Scheduled Maintenance is automatically closed is available in the [release-train-management repo readme](https://github.com/takeoff-com/release-train-management/blob/master/README.md). 

## Important details about Statuspage

<style type="text/css">
.tg  {border-collapse:collapse;border-spacing:0;}
.tg td{border-color:black;border-style:solid;border-width:1px;font-family:Arial, sans-serif;font-size:14px;
  overflow:hidden;padding:10px 5px;word-break:normal;}
.tg th{border-color:black;border-style:solid;border-width:1px;font-family:Arial, sans-serif;font-size:14px;
  font-weight:normal;overflow:hidden;padding:10px 5px;word-break:normal;}
.tg .tg-1wig{font-weight:bold;text-align:left;vertical-align:top}
.tg .tg-0lax{text-align:left;vertical-align:top}
</style>
<table class="tg">
<thead>
  <tr>
    <th class="tg-1wig">Client-specific views</th>
    <th class="tg-0lax"><span style="font-weight:normal">In Statuspage, each MFC site corresponds with a "component." Clients can only view and receive notifications for their own MFC sites. </span></th>
  </tr>
</thead>
<tbody>
  <tr>
    <td class="tg-1wig">Time Zones</td>
    <td class="tg-0lax"><span style="font-weight:normal"> UTC is used for all incidents and scheduled maintenance in Statuspage.</span></td>
  </tr>
  <tr>
    <td class="tg-1wig">Notifications</td>
    <td class="tg-0lax"><span style="font-weight:normal">By default, Statuspage sends notifications to subscribers at the time that maintenance is scheduled, 1 hour before maintenance begins, at maintenance start, and at completion. Notifications are configurable within Statuspage, see [How to Change Scheduled Maintenance in Statuspage](https://engineering-handbook.takeofftech.org/docs/domains/production/statuspage/change_schedule/) for more information.</span></td>
  </tr>
  <tr>
    <td class="tg-1wig">Notification Templates</td>
    <td class="tg-0lax"><span style="font-weight:normal">Templates are available and should be used for Maintenance Scheduled<span style="font-weight:normal">, </span>Maintenance Starting<span style="font-weight:normal">, and </span>Maintenance Complete<span style="font-weight:normal">. </span>
         There are no templates for "Maintenance Updated" or "Maintenance Cancelled" because Statuspage has built-in messaging for this. See [How to Change Scheduled Maintenance in Statuspage](https://engineering-handbook.takeofftech.org/docs/domains/production/statuspage/change_schedule/) for more information.</span></td>
  </tr>
  <tr>
    <td class="tg-1wig">Status</td>
    <td class="tg-0lax"><span style="font-weight:normal">Each Maintenance workflow has four status values - Scheduled, Started, Verifying, Complete. </span><br><span style="font-weight:normal">These are </span>different<span style="font-weight:normal"> from Incident status values. Do not use “verifying” status (we cannot remove it) </span></td>
  </tr>
  <tr>
    <td class="tg-1wig">Jira integration</td>
    <td class="tg-0lax"><span style="font-weight:normal">Takeoff has an active [Jira integration](https://support.atlassian.com/statuspage/docs/set-up-the-jira-software-integration/) in some projects. This is for incidents-only, and should **not** be used. Instead, reach out to the Support team if an incident must be created.</span></td>
  </tr>
</tbody>
</table>
