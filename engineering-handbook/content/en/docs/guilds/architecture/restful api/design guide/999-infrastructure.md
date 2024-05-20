---
title: Infrastructure
linkTitle: Infrastructure
weight: 10
date: 2021-09-10
description: >
  How to set up infrastructure related to your API

draft: true
---

APIs must be deployed according to *Takeoff deployment best practices link here*.

APIs infrastructure such as proxies/gateways and backing servers must be
managed by terraform and/or automation which allows it to be created without
administrators manually applying changes to environments (e.g. through Google
Cloud Console, command lines, or other user interfaces).

API infrastructure such as gateway configuration must be version controlled.

APIs must have some programmable ingress technology in front of the backing service.
- **Good**: API is exposed to users via Apigee gateway which forwards requests some backing service
- **Bad**: API is exposed to users as backing service directly (e.g. `https://my-project.cloudfunctions.net/function`)

TODO:

- Get precise: What gateway are we using?
- Do we need policy here? Maybe start with possibility space and then move into
  what the best parts are for policy?
  - APIs should be exposed via a [Insert some ingress here(cloud endpoints vs
	apigee)].
	- Other constraints here (E.g. domain names, how you get them reserved?)
	    - Which top level takeoff domain for prod/non-prod
		- 
- Service to service https://cloud.google.com/apigee/docs/api-platform/get-started/accessing-internal-proxies

