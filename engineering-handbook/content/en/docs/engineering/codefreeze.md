---
title: "Code Freeze Policy"
linkTitle: "Code Freeze Policy"
weight: 7
date: 2022-03-16
description: >  
---
 ![freeze header](/images/en/docs/Engineering/codefreeze/freeze.png)

This page outlines guidance around changes to our production systems during periods of Code Freeze; please review it carefully and raise any concerns or questions as soon as possible.

**Retailer Code Freeze** **Dates**

Every retailer has Code Freeze dates. Dates during which they do not allow for any changes to be delivered to their production IT infrastructure. Usually these Code Freeze dates are dependent on the holiday season (Christmas, New Years, national holidays etc.).

**Knapp Code Freeze Dates**

These are the dates during which Knapp will NOT be planning to complete any Knapp deploys.

**Takeoff Code Freeze** **Dates**

These are the dates during which Takeoff will NOT be planning to deploy any code to Production (except for any unplanned hotfixes).

**How can I access the Code Freeze schedule for Knapp, our retailers, and Takeoff?**

Check out the [Takeoff Deployment Calendar.](https://calendar.google.com/calendar/embed?src=takeoff.com_reb4devrajh8tu5ndahrpkpdk4%40group.calendar.google.com&ctz=America%2FNew_York "https://calendar.google.com/calendar/embed?src=takeoff.com_reb4devrajh8tu5ndahrpkpdk4%40group.calendar.google.com&ctz=America%2FNew_York")

**What is a Code Freeze?**

Simply put, during a freeze no changes are permitted unless specifically authorized. In our organization, this means -

-   No release trains are to be rolled out
    
-   No off train deployments are permitted
    
-   No hotfixes are permitted during the freeze period unless approved as per “What about hotfixes?” section below
    
-   No feature switch changes are permitted
    
-   No configuration changes (TSC) are permitted
    
-   No KNAPP updates are permitted
    
-   No networking changes either in MFC or GCP are permitted
    

**What is Frozen?**

All production environments that are in production are Frozen. The freeze does not apply to other environments (QAI, UAT and so on).  
  

**What about Incidents?**

If an incident occurs, you are permitted to do whatever is necessary to resolve the incident. Please keep careful records of what is changed (preferably in the Slack incident channel).

**What about hotfixes? How do I get an exception during a Code Freeze?**

If something occurs that requires an immediate change, you must gain the following approvals.  
  

-   Your domain leadership must approve the change AND one of Evgeniy Balter, Jim Collins or Matthew Barnes must approve.
    
-   The retailer must also approve if the hotfix is to occur during the retailer’s Code Freeze. Follow up with the TAM to get the retailer’s approval.
    

All approvers are required to indicate their approval in the appropriate #prod-support-Xxx channel before the deployment is started. No change is permitted until the approvals are present in Slack.

Comments, questions or concerns, please raise them to your manager. Thank you!
