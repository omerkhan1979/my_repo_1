---
title: "Outbound Readme Template"
linkTitle: "Outbound Readme Template"
weight: 2
date: 2022-08-25
description: >
  A template for the Outbound domain (others are welcome to it as well) to have better unified readmes that contain all the needed points.  
---

{{% alert title="Note" %}} If you want to get raw readme with formatting follow the link [here](https://github.com/takeoff-com/engineering-handbook/blob/master/content/en/docs/Engineering/outbound-readme-template.md) and then click the `Copy Raw Contents` button in the top right. {{% /alert %}}

# Human Readable Service Name

Any big things you want to communicate about your service (delete the below divider if you have nothing to put here)

---
## Table of Contents
1. [Monitoring](#monitoring)
1. [Contributing](#contributing)
    - [Repository Structure](#repository-structure)
1. [Development](#development)
    - [Quickstart](#quickstart)
    - [Testing](#testing)
    - [Deployment](#deployment)
1. [Configuration](#configuration)
    - [External Configs](#external-configs)
1. [FAQ](#faq)

## The What: 
Should include the business value and a brief summary of this application. Something like a quick summary or mini whitepaper that anyone who understands Takeoff can understand.

## The How:
Should (ideally) embed architecture diagram(s) or (if needed) link to high-level technical explanation(s) detailing how the service works internally (charts showing core flows) and how it integrates into the greater Takeoff service ecosystem (what services this depends on, what services depend on it, and for what).

# Monitoring
This section should be primarily for people who want to find logs for your service, usually to debug an ongoing issue or gather information.
Quick overview of the main monitoring avenues for this service (links to grafana, kibana, gcp logs, alerts, etc.)

Also good to link to more detailed docs on logs/what to look for if that's been written up. Any sort of playbook can be included here too.

# Contributing
This section should be primarily for people who want to make PRs to your repository, any expectations should be clearly laid out here.
Code review expectations, test coverage expectations, manual testing expectations and anything else you want someone who's going to contribute lines of code to know about.

## Repository Structure
Good to link to repository structure docs here if you have them (e.g. where should code go, what's an easy way to go through the code from the service receiving a request -> giving a response)

# Development
This section should be primarily for people trying to run your service, whether that be for local development/testing or just to try to reproduce/debug a found bug.
A quick blurb on what the best way to develop locally and verify new code is (e.g. test your changes by starting it up locally and using the swagger).

## Quickstart
A user should be able to copy paste commands (or if a file needs to be edited, follow simple instructions with the filename/a file line link) in order to get this service runnable locally. 

If your service needs to call out to other Takeoff services or a database as part of its flows, direct readers to the below sections with [relevant](#database-setup) [links](#service-mocking) as part of this setup. If you need neither of the below things for your service to function, feel free to omit them. These sections are also good candidates to exclude from this upper-level readme and instead link to other markdown files in `doc`.

### Local Database
A section to talk about how to set up a database for your service when developing locally. Similar to the parent quickstart section this should come with a list of commands to bootstrap a database that anyone can copy-paste in order to start running your service locally.

### Service Mocking
A section to talk more in-depth on how to mock out service dependencies when running locally. This is especially important if you have no internal mocking and need to actually reference service URLs in a live environment as part of your local configs. We must make sure local development is not interfering with the health of our remote environments.

## Testing
Set of commands that a user can copy paste (with explanations/prior setup) in order to run unit tests on your service.

If there are integrations tests mention how those can be run, either locally or after deploying to a remote environment.

## Deployment
Quick overview of the deployment mechanism for your service and any other relevant information you might want to add.

Also good to note the deployment cadence/restrictions on this (e.g. release train)

# Configuration

Good to link to a more detailed configuration guide here (another markdown file) if needed, otherwise just a short blurb on where your configs live and how to change them for local and remote versions of your service.

## External Configs

A section to list any external configs (firebase, GCP secrets, TSC, helm charts in a different repo, etc.) that your service might have and how to configure them for services on live environments.

Best to link to how-to confluence pages (or other readme files) instead of putting it all here to keep the readme somewhat small.

Feel free to omit this section if your service does not rely on external configs to function (e.g. they're all in service helm charts within this repository or some local .edn)

# FAQ
I would suggest linking this to a different markdown file to keep the top level readme thinner and make it easier to edit?

Frequently asked question
- Answer
