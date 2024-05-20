---
title: "Beta test with opt-in, as new UI page release strategy"
linkTitle: "Beta a new UI page"
date: 2022-05-24
weight: 10
description: >
   A release strategy for getting Beta feedback on a new UI page, using a banner and the user-profile service.
---

## Release strategy for a new UI pages - Engineering

### Short description

The main idea of the Beta test with opt-in release strategy is that 
user will be able to choose which version to use (new or old page) and provide feedback on how the page works. 
After reviewing the feedback and making any necessary adjustments to the page, we can ensure that the final release 
when we remove the banner is ready for all clients to use.
This way of releasing can also prevent sev1 incidents because if the new page has a bug, users
will be able to use old version and continue serving the orders.

### Business value

- Safe release: gather feedback from end users without hurting their productivity. 
Releasing a new UI page with an opt-in banner allows users to use old version of the page, so there 
will be no SEV1 issue cased by the new UI page.
- Smooth transition from old version of page to the new UI page. The user can choose what 
version to use (new UI page or old) and as the result we will be able to receive 
feedback from user about the new UI page and make updates to make this page more 
comfortable and useful for the client.
- The banner-based release allows us to release a version that is maybe not 100% of the way complete, 
but 'good enough' to get feedback. By reacting to the feedback (maybe tweaking the look and feel, or fixing some bugs) 
we can prepare the page for final release with all functionality and without banner.

### What it looks like

As you can see from the screenshot, the end user is able to choose between the old and new page, 
using the link in the banner. 

![New UI page release banner](/images/en/docs/Engineering/MFE_release_banner/MFE_release_banner.png)

### How to implement

Follow this guide:

1. Add new configuration to the user-profile project.
   https://github.com/takeoff-com/user-profile \
   Example:
   https://github.com/takeoff-com/user-profile/pull/44
2. Add banner.\
   Example:
   https://github.com/takeoff-com/Platform/pull/5281
3. Enjoy your super smooth transition to the new UI page

### How to remove banner and fully release new UI page

Example: \
https://github.com/takeoff-com/Platform/pull/5339

#### Guide was added by the @team-iris - Oleksii Ovsiannikov
#### Please, contact me if you need help



