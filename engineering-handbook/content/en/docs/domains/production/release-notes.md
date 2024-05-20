---
title: "Release Notes"
linkTitle: "Release Notes"
weight: 10
description: >-
     How to publish release notes from Jira to Zendesk.
---
This article explains how publish release note descriptions from Jira to [Zendesk](https://support.takeoff.com/hc/en-us/articles/4417757892753), and how to manage previously published descriptions.

At Takeoff, our release notes in Zendesk are designed to be a simple, automated process in the format of a simple software changelog. For information about other release-related communication, see [Release Communication Best Practices](https://docs.google.com/presentation/d/1IxrKhZv_jre5S4hcBLBWOQ5ifp_qR12Xmz6ENMWUYqw). For information about rolling out changes to clients, see the [Change Control process](https://takeofftech.atlassian.net/wiki/spaces/APCOE/pages/3858235586/Change+Control+Process+Communication). 

Relase note descriptions for Release Train services and non-Release-Train services, as well as KNAPP can all be published using this workflow. 

### Publishing Release Notes

The release notes fields that are included in published release notes are **Product Area**, **Fix Versions** (optional), **Issue Key** (Jira ticket number), and **Release Note Description**. 
Additionally, **Release Note Required**, and **Release Type** are both required fields, but are not included in the published content itself.

In order to publish a release note:
1. Populate the required fields: **Release Type**, **Product Area**, and **Release Note Description** - _The Description must be populated with a brief, complete description of the bug fix or new feature. Complex formatting, images, tables, etc. should be saved for more in-depth documentation_.   
1. **Release Type** - Set **Release Notes Required** to **Yes - Ready to Publish**.
1. The documentation will be automatically generated and a Pull Request will be created in the [Release Notes repository](https://github.com/takeoff-com/release-notes).
1. The description will be reviewed according to the [required publishing criteria](https://takeofftech.atlassian.net/wiki/spaces/TE/pages/3714285645/Release+Notes+Automation+Rollout), and if there are no changes needed, the description will be published within 1 business day. 

### Updating Published Release Notes
Updated release note descriptions will be automatically sent through the same publishing process as described in steps **3** and **4** above.
  
### Deleting Published Release Notes
To delete a previously published release note, you must reach out to [@team-chamaeleon](https://takeofftech.atlassian.net/jira/people/team/bde44f31-3d2a-4dba-b037-44cd57874e0f?ref=jira). 

### Hotfix Issues
If a release note description must be published quickly for things like hotfixes, follow the publishing process decribed above, then reach out to [@team-chamaeleon](https://takeofftech.atlassian.net/jira/people/team/bde44f31-3d2a-4dba-b037-44cd57874e0f?ref=jira) to request expedited publishing. 
