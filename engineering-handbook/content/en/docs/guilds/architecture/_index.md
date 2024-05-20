---
title: "Architecture"
linkTitle: "Architecture"
weight: 1
date: 2022-03-25
description: >
  Where to find Takeoff's technology Patterns, Principles, and Practices (PPP)
---

{{% pageinfo %}}
Navigate to <a href="https://takeofftech.slack.com/archives/C027PSEH7L2">#guild-architecture</a> Slack channel for questions, comments, discussions, etc.
{{% /pageinfo %}}

## GitHub Repositories

`https://github.com/takeoff-com/architecture`

## Proof-of-Concepts

Project Name | Domain | Team | Repositories | Technologies
------------ | ------------- | ------------ | ------------ | ------------
[GCP Data Lakehouse](https://drive.google.com/file/d/1xGSGzhkwe1UZsDtZM6AxVx8cnWmCjiR2/view?usp=sharing) | [Business Intelligence](https://takeofftech.slack.com/archives/C027948UTC7) | [@team-luigi](https://groups.google.com/a/takeoff.com/g/team-luigi/members) | https://github.com/takeoff-com/data-lakehouse-poc | <ul> <li> BigQuery <li> Cloud Storage <li> Cloud Pub/Sub <li> Cloud Dataflow <li> Cloud Composer <li> Data Catalog <li> [DBT](https://www.getdbt.com/) <li> [Flyway](https://flywaydb.org/) </ul>
[Order Details](https://drive.google.com/file/d/1Z8E6tLTWWW-n_35WPa9mtUVFLMN1MH4y/view?usp=sharing) | [Outbound](https://takeofftech.slack.com/archives/CPBQSGQKT) | [@team-iris](https://groups.google.com/a/takeoff.com/g/team-iris/members) | https://github.com/takeoff-com/mfe-order-details <br> https://github.com/takeoff-com/mfe-backend-order | <ul> <li> Terraform <li> Cloud Functions <li> GitHub Actions <li> Load Balancer <li> API Gateway </ul>
Purchase Order CRUD | [Inbound](https://takeofftech.slack.com/archives/C027HMXLH60) | [@team-fusion](https://groups.google.com/a/takeoff.com/g/team-fusion/members) | https://github.com/takeoff-com/poc-purchase-order | <ul> <li> Terraform <li> Cloud Build <li> Cloud Run <li> API Gateway <li> Postgres <li> [gorilla/mux](https://pkg.go.dev/github.com/gorilla/mux) <li> [Wire](https://github.com/google/wire) </ul>
Python CI/CD Template | [Production](https://takeofftech.slack.com/archives/C027W27MHEY) | [@team-hydra](https://groups.google.com/a/takeoff.com/g/team-hydra/members)   | https://github.com/takeoff-com/poc-templated-cicd-python | <ul> <li> GitHub Actions <li> Python <li> [Black](https://github.com/psf/black) <li> [Pytest](https://docs.pytest.org/en/6.2.x/) <li> [Coverage](https://coverage.readthedocs.io/en/6.3.1/) <li> [Slack API](https://api.slack.com/) </ul>
[Products Audit](https://docs.google.com/presentation/d/1YGlb4RGINKD_pXkaWT5Wfmo5HmEyVn4YYPjRGskLDqw/edit?usp=sharing) | [Inbound](https://takeofftech.slack.com/archives/C027HMXLH60) | [@team-jazz](https://groups.google.com/a/takeoff.com/g/team-jazz/members) | https://github.com/takeoff-com/products-audit | <ul> <li> Cloud Functions <li> Cloud Pub/Sub <li> Load Balancer <li> BigQuery <li> GitHub Actions <li> Terraform <li> [Cloud Logging and Monitoring](https://cloud.google.com/products/operations) <li> Slack API </ul>
[Outbound Backend](https://docs.google.com/presentation/d/1IzJBWv0RtuhVTJ234nbNkvKMahr53lAtwL85aWOjaLI/edit) | [Outbound](https://takeofftech.slack.com/archives/CPBQSGQKT) | [@team-zeus](https://groups.google.com/a/takeoff.com/g/team-zeus/members) | https://github.com/takeoff-com/outbound-backend | <ul> <li> Terraform <li> Load Balancer <li> Cloud Storage <li> Cloud Functions <li> Github Actions </ul>
[Fulfillment Task Queue](https://docs.google.com/presentation/d/1ESUHyacq1bDBXFnR0W51-LRDlBJNZg1RI6H5wdJGEAY/edit#slide=id.g7226bb96ba_0_2) | [Outbound](https://takeofftech.slack.com/archives/CPBQSGQKT) | [@team-zeus](https://groups.google.com/a/takeoff.com/g/team-zeus/members) | https://github.com/takeoff-com/poc-fulfillment-task-queue | <ul> <li> Terraform <li> Load Balancer <li> Cloud Run <li> gRPC <li> Cloud Spanner <li> Github Actions </ul>
## Initatives

PPP = Patterns, Principles, Practices

Initiative | Epic | Lead | Participants
------------ | ------------- | ------------ | ------------
RESTful API PPP | [ARCH-110](https://takeofftech.atlassian.net/browse/ARCH-110) | <ul> <li> Eugene Marcotte </ul>
Go PPP | [ARCH-154](https://takeofftech.atlassian.net/browse/ARCH-154) | <ul> <li> (TBD)) </ul>
Python PPP | [ARCH-161](https://takeofftech.atlassian.net/browse/ARCH-161) | <ul> <li> (TBD) </ul> | <ul> <li> (TBD) </ul>
Database PPP | [ARCH-155](https://takeofftech.atlassian.net/browse/ARCH-155) | <ul> <li> Dave Mancinelli </ul> | <ul>  <li> Neil Dowgun </ul>
Data Model | [ARCH-109](https://takeofftech.atlassian.net/browse/ARCH-109) | <ul> <li> (TBD)  </ul> 
On-Demand Environments | [ARCH-148](https://takeofftech.atlassian.net/browse/ARCH-148) | <ul> <li> Kevin Scheunemann <li> Erik Schweller | <ul> <li> Team Chamaeleon <li> Team Orion </ul>

## Takeoff Architecture Documentation
