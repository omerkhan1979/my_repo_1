---
title: "How to Change Scheduled Maintenance in Statuspage"
linkTitle: "Update Scheduled Maintenance"
weight: 3
---
### Step 1: What is the current status of the maintenance?

Expand the relevant section:

{{%expand "Maintenance has not started yet" %}}
 - [Reschedule Maintenance](#reschedule-maintenance-not-yet-started) 
 - [Cancel Scheduled Maintenance](#cancel-scheduled-maintenance-not-yet-started)
{{% /expand%}}

{{%expand "Maintenance is currently in-progress" %}}
- [](#)
  - [Cancel Scheduled Maintenance not yet started](#cancel-scheduled-maintenance-not-yet-started)
  - [Complete maintenance early](#complete-maintenance-early)
  - [Extend a Maintenance window in progress](#extend-a-maintenance-window-in-progress)
- [](#-1)
  - [Reschedule Maintenance in progress](#reschedule-maintenance-in-progress)
- [](#-2)
  - [Cancel Maintenance in progress](#cancel-maintenance-in-progress)
- [](#-3)
  - [Reopen Completed Maintenance](#reopen-completed-maintenance)
  - [Set component status back to operational](#set-component-status-back-to-operational)
{{% /expand%}}

{{%expand "Maintenance window has completed" %}}
- [Re-open a completed Maintenance Window](#reopen-completed-maintenance)
- [Set component status back to operational](#set-component-status-back-to-operational)
{{% /expand%}}

----------
### Reschedule Maintenance not yet started

To change the **date**, **time**, or **duration** of an existing scheduled maintenance event:

1.  In [**manage.statuspage.io**](https://manage.statuspage.io/pages/qth8l8vxd7y4 "https://manage.statuspage.io/pages/qth8l8vxd7y4"), click **Incidents > Maintenances** tab > **Update** for the event you want to update. 
![Alt text](/images/en/docs/Domains/Production/statuspage/schedule_maintenance/nav_to_maint.png)
2.  On the **Schedule & Automation** tab, set the new **Date** or **Time** (**in UTC 24-hour**), or **Hours**.
3.  Click **Update**.
4.  **!!!Important!!!** Navigate to the **Status Update** tab, and click **Update** at the bottom.
![Alt text](/images/en/docs/Domains/Production/statuspage/schedule_maintenance/reschedule-datetime.png)
----------
### Cancel Scheduled Maintenance not yet started

1.  In [**manage.statuspage.io**](https://manage.statuspage.io/pages/qth8l8vxd7y4 "https://manage.statuspage.io/pages/qth8l8vxd7y4"), click **Incidents > Maintenances** tab > **Update** for the event you want to update.
![Alt text](/images/en/docs/Domains/Production/statuspage/schedule_maintenance/nav_to_maint.png)
2. Expand the **Apply Template** drop-down, and select **D. Maintenance Cancelled**.
3.  In the **Maintenance** status area, click **Completed**.  
![image alt text](/images/en/docs/Domains/Production/statuspage/schedule_maintenance/nine.png)
4.  Click **Update**.
5.  Make sure you [set the component status back to operational](#set-component-status-back-to-operational).
----------
### Complete maintenance early

Do this if a deployment completes sooner than the planned window.  
For example, the deployment window is for 2 hours, but the deployment is done in 30 mins.

1.  In [**manage.statuspage.io**](https://manage.statuspage.io/pages/qth8l8vxd7y4 "https://manage.statuspage.io/pages/qth8l8vxd7y4"), click **Incidents > Maintenances** tab > **Update** for the event you want to update.
![Alt text](/images/en/docs/Domains/Production/statuspage/schedule_maintenance/nav_to_maint.png)
2. On the **Maintenance status** slider, click **Completed**.
3. Click **Update**.
4. Make sure you [set the component status back to operational](#set-component-status-back-to-operational).
----------
### Extend a Maintenance window in progress

1.  In [**manage.statuspage.io**](https://manage.statuspage.io/pages/qth8l8vxd7y4 "https://manage.statuspage.io/pages/qth8l8vxd7y4"), click **Incidents > Maintenances** tab > **Update** for the event you want to update.
![Alt text](/images/en/docs/Domains/Production/statuspage/schedule_maintenance/nav_to_maint.png)
2. Set the additional **Hours** or **Minutes**.
3.  Click **Update**. **The client is not yet notified - complete all steps in this section to notify the client.**
4.  Go to the **Status update** tab > **Apply template** > **C. Maintenance Extended.**
5.  In the **Message** field, **enter the amount of time the window is extended (not the total time).**
6.  Click **Update**.
![Alt text](/images/en/docs/Domains/Production/statuspage/schedule_maintenance/extend_maint.png)
----------

### Reschedule Maintenance in progress

_**This edge case should be avoided whenever possible**_ **-** _**it is much easier to reschedule maintenance BEFORE it is in progress.**_
1.  In [**manage.statuspage.io**](https://manage.statuspage.io/pages/qth8l8vxd7y4 "https://manage.statuspage.io/pages/qth8l8vxd7y4"), navigate to **Components** > **Client’s site name** > **Edit**.
2.  Expand the **Status** > select **Operational**, and click **Save Component**.  
    **Note**: Repeat this for **each** site if the deployment applies to multiple sites.
![Alt text](/images/en/docs/Domains/Production/statuspage/schedule_maintenance/reschedule_maint.png)
3. Navigate to **Incidents > Maintenances** tab > **Update** for the event you want to update.
![Alt text](/images/en/docs/Domains/Production/statuspage/schedule_maintenance/reschedule_maint_nav.png)
4. On the **Status Update** tab, click **Scheduled**, set all relevant component(s) to **Operational**, make sure **Notifications is deselected**, and click **Update**.
![Alt text](/images/en/docs/Domains/Production/statuspage/schedule_maintenance/reschedule_nav_update.png)
5. Navigate to the scheduled Maintenance > **Schedule and Automation** tab > set the new **Scheduled** date.
6. Click **Update**.
![Alt text](/images/en/docs/Domains/Production/statuspage/schedule_maintenance/reschedule_maint_datetime.png)
7. Navigate to the scheduled Maintenance, and on the **Status Update** tab, select **Apply Template** > **Maintenance Rescheduled** > **Update**.
![Alt text](/images/en/docs/Domains/Production/statuspage/schedule_maintenance/reschedule_maint_send.png)
----------
### Cancel Maintenance in progress 

1.  In [**manage.statuspage.io**](https://manage.statuspage.io/pages/qth8l8vxd7y4 "https://manage.statuspage.io/pages/qth8l8vxd7y4"), click **Incidents > Maintenances** tab > **Update** for the event you want to update.
![Alt text](/images/en/docs/Domains/Production/statuspage/schedule_maintenance/nav_to_maint.png)
2. Expand the **Apply Template** drop-down, and select **D. Maintenance Cancelled**.   
3.  Make sure **Maintenance Status** is **Completed**.
4.  Make sure you [set the component status back to operational](#set-component-status-back-to-operational).
5.  Click **Update**.
![Alt text](/images/en/docs/Domains/Production/statuspage/schedule_maintenance/cancel_maint_in_progress.png)
----------
### Reopen Completed Maintenance

_**This edge case should be avoided whenever possible**_ **-** _**it is better to extend maintenance while it is in progress.**_

In this scenario, a maintenance event auto-completes (the end of the window is reached), but the maintenance needs to be extended.

_**Note: In this workflow, you are creating a NEW maintenance event. From the client’s perspective, it looks like the old one.**_

1.  Follow the steps to [create a new scheduled maintenance](https://engineering-handbook.takeofftech.org/docs/domains/production/statuspage/schedule_maint/ "https://engineering-handbook.takeofftech.org/docs/domains/production/statuspage/schedule_maint.md").
2.  Set the **date** as today’s date, and **Start time** about 5 minutes from now, and set the window duration according to the length you want to extend (e.g., 30 mins, 1 hour, etc).
3.  Select the template **C. Maintenance Extended**.
4.  Click **Schedule Now**.

### Set component status back to operational

After scheduled maintenance has been completed, always check that the component **Status** is set back to **Operational**. 
If it is still **Under Maintenance** you need to manually set it back to **Operational**:

1.  Navigate to the **Components** tab.
2.  Locate the component and click **Edit**.
3.  Set the **Status** to **Operational**.   
4.  Click **Save component**. 
5.  If necessary, repeat steps 2-4 for all sites with an incorrect status.
![Alt text](/images/en/docs/Domains/Production/statuspage/schedule_maintenance/set_comp_to_operational.png)
