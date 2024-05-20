---
title: "Site Infrastructure"
linkTitle: "Site Infrastructure"
weight: 3
date: 2017-10-22
description: About the Handbook site Infrastructure and Deployment 
---

## Site Overview

- This handbook uses Golang-based [Hugo](https://gohugo.io/about/what-is-hugo/). We chose Hugo because it is created by Google and written in Go, so it was the natural choice for our all-in approach to GCP. 
- Hugo uses [Goldmark](https://github.com/yuin/goldmark/) as its Markdown parser by default.
- For code syntax highlighting, Hugo uses [Chroma](https://gohugo.io/content-management/syntax-highlighting/). 
- The theme template we use is called [Docsy](https://www.docsy.dev/about/). 

### Build Pipeline and Hosting Infrastructure Overview

* The infrastructure for this site is created using Terraform in the [tf-tg-live repo](https://github.com/takeoff-com/tf-tg-live/tree/master/org-gcp/shared_folder)
* The Terraform was derived partly from the [mfe-platform repo](https://github.com/takeoff-com/mfe-platform/tree/master/terraform)
* The project in gcp is [prj-engineering-handbook](https://console.cloud.google.com/home/dashboard?project=prj-engineering-handbook-50fe&organizationId=252201914815).
* The static site is hosted on [App Engine](https://console.cloud.google.com/appengine?project=prj-engineering-handbook-50fe&organizationId=252201914815&serviceId=default) with an [HTTP Load Balancer](https://console.cloud.google.com/net-services/loadbalancing/loadBalancers/list?project=prj-engineering-handbook-50fe&organizationId=252201914815), which routes traffic to a [Network Endpoint Group](https://console.cloud.google.com/compute/networkendpointgroups/list?referrer=search&organizationId=252201914815&project=prj-engineering-handbook-50fe).
* [Identity Aware Proxy](https://console.cloud.google.com/security/iap?organizationId=252201914815&project=prj-engineering-handbook-50fe) required some manual configuration, but is ultimately applied on top of this.


#### Points about this implementation

* [Estimated cost is about $20/month](https://console.cloud.google.com/billing/018D35-5F6963-05E83A/reports;grouping=GROUP_BY_SKU;projects=prj-engineering-handbook-50fe?project=prj-engineering-handbook-50fe&organizationId=252201914815).


#### Why App Engine? 

* We explored storing the files in a bucket and using Cloud Run, but App Engine was ultimately a more simple solution. There were also some challenges using IAP with a bucket.
* In addition, [App Engine is a fully managed solution](https://cloud.google.com/appengine#all-features).
* With this solution, we can also use [Traffic Splitting](https://cloud.google.com/appengine/docs/standard/python/splitting-traffic) to support routing traffic to different versions of the site (for things like A/B testing, or for previewing major changes in advance). 
* App Engine firewall and managed SSL/TLS certificates by default on our custom domain at no additional cost.
* Using the Hugo site theme versioning feature, we could also eventually enhance the site to support multiple versions of the documentation if, for example, we wanted to use it for a [central product documentation site](https://v0-2.kubeflow.org/) to replace Zendesk.


### Source Code and Deployment



* The Terraform initially creates and stores the needed secrets in the [engineering-handbook repository](https://github.com/takeoff-com/engineering-handbook). 
* On push, the site is built and deployed using a [github action](https://github.com/takeoff-com/engineering-handbook/blob/master/.github/workflows/gh-pages.yml). 
* Deployment takes about 3-5 minutes to complete.
* Rollbacks can be completed through github commits.


### Major Site Sections: 



* **[About](https://sandbox-20210927-xadnp6.uc.r.appspot.com/about/)** - Flashy, high-level page about the site. 
* **[Engineering Handbook](https://sandbox-20210927-xadnp6.uc.r.appspot.com/docs/)** - Budding Engineering team documentation. Much more to come in Q4, and the structure will also be cleaned up further. Includes info about: 
    * **Handbook**
    * **Onboarding**
    * **Culture**
    * **Agile**
    * **Engineering**
    * **Architecture**
* **[Blog](https://sandbox-20210927-xadnp6.uc.r.appspot.com/blog/)** - Engineering Blog Posts and All-hands content. 
* **[Learning](https://sandbox-20210927-xadnp6.uc.r.appspot.com/learning/)** - Learning paths and educational resources. The sub-structure is well-thought-out and ready for populating.
    * **[Programming Languages](https://engineering-handbook.takeofftech.org/learning/programming_languages/)**
    * **[Architecture](https://engineering-handbook.takeofftech.org/learning/architecture/)**
    * **[Google Cloud Platform](https://engineering-handbook.takeofftech.org/learning/gcp/)**
    * **[Database Management](https://engineering-handbook.takeofftech.org/learning/database_management/)**
    * **[System Monitoring](https://engineering-handbook.takeofftech.org/learning/system_monitoring/)**
    * **[Testing](https://engineering-handbook.takeofftech.org/learning/testing/)**
    * **[Deployment](https://engineering-handbook.takeofftech.org/learning/deployment/)**
    * **[API Development](https://engineering-handbook.takeofftech.org/learning/api_development/)**
    * **[Other Skills](https://engineering-handbook.takeofftech.org/learning/other_skills/)**
* **Search** - This is currently a site local search. The UI will improve once we switch to a google custom search engine, but it is at least functional.


### Content:

Some examples of relatively developed pages: 



* [Incident management](https://sandbox-20210927-xadnp6.uc.r.appspot.com/docs/engineering/incidentmgmt/) (Scrolling right-hand TOC for long form articles)
* [Handbook Intro page](https://sandbox-20210927-xadnp6.uc.r.appspot.com/docs/) (fancy header image)
* [Architecture > Data Model > Domains](https://literate-meme-e2241634.pages.github.io/docs/architecture/data-model/domains/) (Plant UML Diagram)
* [Architecture > … > Data Flows](https://literate-meme-e2241634.pages.github.io/docs/architecture/data-model/domains/inbound/assortment/data-flows/) (deeply nested page with interactive diagram)
* [Page with embedded video ](https://sandbox-20210927-xadnp6.uc.r.appspot.com/docs/onboarding/)
* [Git at Takeoff](https://sandbox-20210927-xadnp6.uc.r.appspot.com/docs/engineering/github/)
* [12 agile principles](https://sandbox-20210927-xadnp6.uc.r.appspot.com/docs/agile/principles/)


## Other small things: 

* The links at the right of the documentation pages are all functional. If you click **Create Project Issue**, it takes you directly to a Handbook ticket form (instead of just the board).

![alt_text](/images/en/docs/Handbook/handbook-infra/side-menu.jpg "image_tooltip")


* In the site footer, there are some handy icons with links to things like the **IT Portal** and the **Handbook Slack Channel**. 

![alt_text](/images/en/docs/Handbook/handbook-infra/bottom-bar.jpg "image_tooltip")