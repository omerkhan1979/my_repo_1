---
title: "How to Schedule Maintenance in Statuspage"
linkTitle: "How to Schedule Maintenance in Statuspage"
weight: 2
---

## Before you begin

Start by adding the maintenance to the [deployment calendar](https://calendar.google.com/calendar/embed?src=takeoff.com_reb4devrajh8tu5ndahrpkpdk4%40group.calendar.google.com&ctz=America%2FNew_York).


### How to Schedule Maintenance:

Log in to [Statuspage management interface](https://manage.statuspage.io/pages/qth8l8vxd7y4/incidents).

1.  Navigate to the **Incidents** screen.
    
2.  Click **Maintenances**.

    **Note**: **This step is important because it is possible to accidentally create an _incident_. The two screens are easily confused, and it is possible to send a false alert for a service incident/outage.**
![image alt text](/images/en/docs/Domains/Production/statuspage/schedule_maintenance/1nav_to_maint.png) 
    
1.  Click **Schedule maintenance**.  
![image alt text](/images/en/docs/Domains/Production/statuspage/schedule_maintenance/2click-sched.png) 
    
4.  Expand **Apply template** (_DO NOT start filling out the form_).
5.  Select **0. Maintenance-scheduled**.
![image alt text](/images/en/docs/Domains/Production/statuspage/schedule_maintenance/3apply-template.png)   
    
6.  In the **Scheduled Time** fields, complete the date, time, and duration fields.    
7.  In the **Components affected** area, select all client site(s) that apply.
![image alt text](/images/en/docs/Domains/Production/statuspage/schedule_maintenance/4config-time.png)  

8.  At the bottom of the page, make sure **Send notifications** is selected.
9.  Click **Shedule now**.  
![image alt text](/images/en/docs/Domains/Production/statuspage/schedule_maintenance/5notifications.png) 

## Notifications

Notifications are immediately be sent to subscribers when **Schedule now** is clicked, as well as a 1-hour reminder, maintenance start, and maintenance complete as shown in the screenshot above.
