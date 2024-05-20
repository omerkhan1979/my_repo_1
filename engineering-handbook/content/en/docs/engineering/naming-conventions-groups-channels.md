---
title: "Naming Conventions for Groups + Slack Channels"
linkTitle: "Naming Conventions for Groups + Slack Channels"
date: 2021-08-03
weight: 4
description: >
  
---

{{% alert title="Note" color="warning" %}} Although this page geared towards Slack channels and groups. The same naming conventions are meant to apply for all of our systems (Slack, OpsGenie, GitHub, Okta, G-Suite, etc.)  to make browsing groups and finding the right one for your needs more intuitive. {{% /alert %}}

---

## General rules for naming:

*   Dashes (not underscores)
*   All lowercase
*   Keywords are fully qualified (“engineering” over “eng”, “product” over “prod”)
*   Well-known abbreviations allowed (“cop” for “Community of Practice”)
*   Hierarchy should be indicated by starting broad and getting narrower
*   Suffixes should be used as a modifier to any channel/group name (ie. `-private` is the private version of any channel)
    

## Teams (Okta Groups, Google Groups, and Slack Groups)
---

*   **@team-**<span style="color:#72bcd4">_**\[Team Name\]**_</span>
    
    *   includes Dev Team, Manager(s) of Team Members, SM, and Sprint PO
        
*   **@domain-**<span style="color:#72bcd4">_**\[Domain Name\]**_</span>
    
    *   includes Dev Team(s), Manager(s), all SMs, andSprint POs of a domain
        
*   **@domain-**<span style="color:#72bcd4">_**\[Domain Name\]**_</span>**-sprint-product-owners**
    
    *   includes all sprint product owners assigned to a domain
        
*   **@domain-**<span style="color:#72bcd4">_**\[Domain Name\]**_</span>**\-leadership**
    
    *   includes Domain Director of Engineering + Domain Architect + Domain Director of Product
        
*   **@coe-**<span style="color:#72bcd4">_**\[Center of Excellence Name\]**_</span>
    
    *   includes roster of CoE members
        
*   **@coe-**<span style="color:#72bcd4">_**\[Center of Excellence Name\]**_</span>**\-sprint-product-owners**
    
    *   includes all sprint product owners assigned to a Center of Excellence
        
*   **@coe-**<span style="color:#72bcd4">_**\[Center of Excellence Name\]**_</span>**\-leadership**
    
    *   includes Director of Engineering + Architect of the guild
        
*   **@guild-**<span style="color:#72bcd4">_**\[Guild Name\]**_</span>
    
    *   includes roster of virtual guild members
        
*   **@guild-**<span style="color:#72bcd4">_**\[Guild Name\]**_</span>**\-leadership**
    
    *   includes Director of Engineering + Architect of the guild
        
*   **@leadership-engineering**, **@leadership-product**, **@leadership-support**
    
    *   includes leaders designated by the head of the given department
        
*   **@management-engineering**, **@management-product**, **@management-support**
    
    *   includes all people managers of the named department
        
*   **@directs-**<span style="color:#72bcd4">_**\[Manager Name\]**_</span>
    
    *   includes all direct reports of the named manager
        
*   **@staff-**<span style="color:#72bcd4">_**\[Manager Name\]**_</span>
    
    *   includes all direct + indirect reports of the named manager
        
*   **@all-engineering**, **@all-product**, **@all-support**
    
    *   includes all members of the named department
        
*   **@all-scrum-masters**
    
    *   includes all Scrum Masters
        
*   **@all-product-owners**
    
    *   includes all Domain and Sprint Product Owners

*   **@all-cto**
    
    *   includes @all-engineering, @all-product, @all-support
        

## Slack Channels (Naming should be broad → narrow)
---

*   **#team-**<span style="color:#72bcd4">_**\[Team Name\]**_</span> _(only -private version needed)_
    
*   **#domain-**<span style="color:#72bcd4">_**\[Domain Name\]**_</span>
    
*   **#coe-**<span style="color:#72bcd4">_**\[Center of Excellence Name\]**_</span>
    
*   **#guild-**<span style="color:#72bcd4">_**\[Guild Name\]**_</span>
    
*   **#project-**<span style="color:#72bcd4">_**\[Project Name\]**_</span>
    
    *   for cross domain project collaboration
        
*   **#project-**<span style="color:#72bcd4">_**\[Project Name\]**_</span>
    
*   **#cop-**<span style="color:#72bcd4">_**\[Community of Practice Name\]**_</span>
    
*   **#announcements-cto**
    
*   **#department-**<span style="color:#72bcd4">_**\[Department Name\]**_</span>
    
*   **#leadership-**<span style="color:#72bcd4">_**\[Department Name\]**_</span>**-private**
    
*   **#management-**<span style="color:#72bcd4">_**\[Department Name\]**_</span>**-private**
    
*   **#learn-**<span style="color:#72bcd4">_**\[Topic\]**_</span>
    
    *   for learning/training channels
        
*   **#prod-support-**<span style="color:#72bcd4">_**\[Customer Name\]**_</span>
    
*   **#incident-**<span style="color:#72bcd4">_**\[Customer Name\]**_</span>**\-**<span style="color:#72bcd4">_**\[Incident Number\]**_</span>
    
*   **#alerts-**<span style="color:#72bcd4">_**\[Domain Name\]**_</span>
    
*   **#alerts-**<span style="color:#72bcd4">_**\[Team Name\]**_</span>
    
*   **#implementation-**<span style="color:#72bcd4">_**\[Retailer Name\]**_</span>**\-**<span style="color:#72bcd4">_**\[MFC ID\]**_</span>
    

## Modifiers
--- 

_(in order of usage - ie. \[???\]-collaboration-private not \[???\]-private-collaboration)_

*   **#**<span style="color:#72bcd4">_**\[???\]**_</span>**\-collaboration**
    
    *   for cross domain project collaboration including 3rd party vendors (ie. KNAPP or Softserve)
        
*   **#**<span style="color:#72bcd4">_**\[???\]**_</span>**\-private**
    
    *   private version of the any of the above