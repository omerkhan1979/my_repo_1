---
title: "Engineering Onboarding"
linkTitle: "Engineering Onboarding"
weight: 2
description: >
  Takeoff Engineering Onboarding
---

##  Onboarding phases
![employee-onboarding](/images/en/docs/Onboarding/employee-onboarding.png)

#### **Pre-onboarding:**
- Line manager to **assign a "buddy"** - member from the same team where a newcomer is placed.   
- The goal for the “buddy”:  
    - is to direct questions to that manager is not equipped to help with or not required the involvement of the manager (technical questions mostly or product/component  related questions)   
- Line manager ***has to control and monitor the progress of each stage***
- Engineering department would really appreciate if ***newcomer updates oboarding document once he/she identified outdated items in it***

{{% alert title="Note" %}} Each week of the onboarding split by time ratio (time allocation) for onboarding and development activities to give more flexibility in onboarding for people with low and high seniority (i.e. junior / middle / senior se) {{% /alert %}}

#### **Stage 1**
##### **1st & 2nd days:**

Activity | Time allocation
--------- | --------- |
Onboarding | 100%
Development | 0%

##### Onboarding
1. Meet with your line manager to get to know each other
    - Line manager set expectations for the newcomer for the adaptation period (ensure understanding of adaptaion period success)
    - Line manager set up a 3 person meet - LM, “buddy”, newcomer
        - Explain what “buddy” is for and introduce “buddy” to the newcomer
2. Go through the HR Onboarding process
    - Onboarding [UA](https://takeofftech.atlassian.net/wiki/spaces/HR/pages/861470849/Onboarding); US; UK
    - HR Policies [UA](https://takeofftech.atlassian.net/wiki/spaces/HR/pages/1612218669/UA+HR+Policies) (tools, portals)
3. Visit Accountant (UA specific)
4. Set up system and tools
    - Get all accesses (github, calyx, opsgenie, jira, jenkins, test rail, chart shop, IDE and github access from it, etc.)
        - Ensure access and licenses with IT
            - Oleksandr Ryzhov (UA)
            - Meng Un (US, UK)
5. [Takeoff IT support](https://takeofftech.atlassian.net/servicedesk/customer/portal/3) for any requests (devices, licences, access, etc.)
6. [Meet Takeoff team](https://app.charthop.com/takeoff-technologies/org?data=department&date=2022-04-20&job=60d4e2731fd81b761af687b7&zoom=0.5)
7. [Service ownership map](https://takeofftech.atlassian.net/wiki/spaces/SE/pages/1335755980/List+of+Takeoff+services)


##### **1st-2nd week:**

Activity | Time allocation
--------- | --------- |
Onboarding | 75%
Development | 25%

##### Onboarding 
1. The high-level design of the solution ([link 1](/docs/domains/production/architecture_diagrams/), 
[link 2](/docs/guilds/architecture/data-model/))
2. [Architecture Guild](/docs/guilds/architecture/)
    - Go through architecture guild documents
3. [Quality Guild](/docs/guilds/quality/)
    - Go through quality guild documents
4. [Agile Guild](/docs/guilds/agile/)
    - Go through agile guild documents
5. Review [Git at Takeoff](/docs/engineering/github/)
    - Push test PR 
    - If all is ok: close PR
    - If doesn't work: verify with your team that all configs are set in IDE properly, accesses, etc.
6. Learn about the [Engineering Handbook]({{< ref "/docs/handbook/_index.md" >}})
7. Meet your SM to get introduction to a team processes (Agile)
8. Understand the Takeoff Release Process 
    - [Change Control Process](https://takeofftech.atlassian.net/wiki/spaces/APCOE/pages/3874488436/Change+Control+Process)
    - [Production Deployment Process]({{< ref "deploy_sop.md" >}})
    - [About Release Trains]({{< ref "release-trains.md" >}})
    - [Release Train Management](https://github.com/takeoff-com/release-train-management/?tab=readme-ov-file#release-train-management)
    - [Takeoff's Statuspage]({{< ref "/docs/domains/production/statuspage/_index.md" >}})

9. Training alignment to align with company standards:
    - IT should have provided you with a Coursera login invitation
    - If on Coursera a course says something about a "7-day trial" instead of "Sponsored by Takeoff Technologies" -- then file an IT ticket
    - [Introduction to Infrastructure as Code with Terraform](https://learn.hashicorp.com/collections/terraform/gcp-get-started)
    - [Digital Transformation with Google Cloud](https://www.coursera.org/learn/digital-transformation-google-cloud)
    - [Learn GitHub Actions](https://docs.github.com/en/actions/learn-github-actions)
    - [Managing Change when Moving to Google Cloud](https://www.coursera.org/learn/managing-change-when-moving-to-google-cloud)
    - [Getting Started with Go](https://www.coursera.org/learn/golang-getting-started)
    - [Functions, Methods, and Interfaces in Go](https://www.coursera.org/learn/golang-functions-methods)
    - [Concurrency in Go](https://www.coursera.org/programs/engineers-huaef/learn/golang-concurrency)
    - [Developing Applications with Cloud Run on Google Cloud: Fundamentals](https://www.coursera.org/learn/developing-applications-with-cloud-run-on-gcp-fundamentals)
    - [Managing Google Cloud's Apigee API Platform for Hybrid Cloud Specialization](https://www.coursera.org/specializations/managing-apigee-api-platform-for-hybrid-cloud) (3 Course Series)
    - [Getting Started with Google Kubernetes Engine](https://www.coursera.org/learn/google-kubernetes-engine)
    - [Intro to Apigee Management](https://www.youtube.com/watch?v=vGe38icp0n4&list=PLIivdWyY5sqIYex7RAyE7fCKeKZBTLAJl) (YouTube Playlist)
10. Opsgenie Mobile App installation and service Configuration : [Opsgenie is Takeoff Incident Managers and Responders](https://takeofftech.atlassian.net/wiki/spaces/EN/pages/3175972883/Opsgenie+Mobile+App+Installation+and+Service+Configuration)
   
11. Progress review with LM

##### Development
1. Pair programming/testing with your buddy
2. TBD ---> what your manager decides

#### **Stage 2**
##### **3rd week:**

Activity | Time allocation
--------- | --------- |
Onboarding | 50%
Development | 50%

##### Onboarding
Dive into Product
1. General presentation about MFC
    - [Video from MFC](https://cartfresh.atlassian.net/wiki/spaces/HR/pages/1175486607/Video+from+MFC)
    - [MFC 3D Tour](https://takeoff.1password.com/vaults/all/allitems/gb2rormzs5fn3igxkizqidisqm)
2. Intro documentation
    - [Takeoff intro (language RU/UA)](https://drive.google.com/file/d/158raxSaGyHeSFQ-vrHjXjoG-WL2f-6Gp/view)
    - [Takeoff intro (language US)](https://drive.google.com/file/d/1LZ3lOukgIwqpcwZZAelwOElROs2ldaxG/view)
3. Strategy and goals in 202X (ask your SM for doc)
4. Learning of Go Language
    - [Go](/academy/programming_languages/go/)
    - [Getting Started with Go](https://www.coursera.org/learn/golang-getting-started)
    - [Functions, Methods, and Interfaces in Go](https://www.coursera.org/learn/golang-functions-methods)
5. Training alignment to fit company standards:
    - [Managing Change when Moving to Google Cloud](https://www.coursera.org/learn/managing-change-when-moving-to-google-cloud?specialization=organizational-change-and-culture-for-adopting-google-cloud)
    - [Takeoff User Interface Training](https://takeofftech.atlassian.net/wiki/spaces/UIUX/blog/2021/09/24/3220668458/Takeoff+User+Interface+Training+Path)
6. Onboarding to your domain (go through only **your** domain)
    - [Outbound Onboarding Brainstorm](https://docs.google.com/document/d/1KouTVz6ZIrBWc8BwL9hxsdbSGRKBv9wLlHqIf7PULIE/edit?usp=sharing)
    - [Inbound Domain Onboarding](https://docs.google.com/document/d/12UgyiHSedD5fRJ_eI8jcKL5kzp1fVOgksCgPF3DoYow/edit?usp=sharing)
    - [INC](https://takeofftech.atlassian.net/wiki/spaces/RINT/pages/1575190580/Onboarding+Wiki)
    - Others
        - Contact your Product Owner for Q&A
7. Progress review with LM

##### Development
1. Work in a scrum team


##### **4th-5th week (sprint):**

Activity | Time allocation
--------- | --------- |
Onboarding | 25%
Development | 75%

##### Onboarding
1. Based on what domain you’re going to work, start with other domains onboarding and gain knowledge to “connect all dots” with your domain.
2. Training alignment to fit company standards:
    - [Concurrency in Go](https://www.coursera.org/learn/golang-concurrency?specialization=google-golang)
3. Cross-Domain onboarding (go through other domains)
    - [Outbound Onboarding Brainstorm](https://docs.google.com/document/d/1KouTVz6ZIrBWc8BwL9hxsdbSGRKBv9wLlHqIf7PULIE/edit?usp=sharing)
    - [Inbound Domain Onboarding](https://docs.google.com/document/d/12UgyiHSedD5fRJ_eI8jcKL5kzp1fVOgksCgPF3DoYow/edit?usp=sharing)
    - [INC](https://takeofftech.atlassian.net/wiki/spaces/RINT/pages/1575190580/Onboarding+Wiki)
    - [Production](https://docs.google.com/document/d/1kY-_SpG8kmhpAX48_IWVRunzwGRRdJRNZb7paQBY8-Y)
    - Others
    
##### Development
1. Work in a scrum team    
    
#### **Stage 3 (final)**
##### **6th week:**

Activity | Time allocation
--------- | --------- |
Onboarding | 5%
Development | 95%

##### Onboarding
- Continue onboarding related to other domains in addition try to cover all “blind spots” that you have

##### Development
- Work in a scrum team

##### **7th week:**
- End of adaptation period
- Meeting with your LM to sum up your onboarding

#### **Stage 4 (additional onboarding)**
- Visiting MFC site

#### **Post-onboarding:**
- All newcomers that successfully passed onboarding should fill out the survey form so we can improve our onboarding guide for another new upcoming mates:
   - [Engineering onboarding survey](https://docs.google.com/forms/d/e/1FAIpQLSfJB11LGxGFSZVFIppc7FAn748IbdPkMu4keUuB3xnMYAcwIw/viewform?usp=sf_link)
