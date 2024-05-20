---
title: "Data Mart / Looker"
---

Interprets raw upstream data into meaningful metrics and provides ways to visualize that data through Looker.

# Data Mart

**Git Repo**: [datawarehouse-etl](https://github.com/takeoff-com/datawarehouse-etl)

| Environment     | GCP Project                |
|-----------------|----------------------------|
| Production      | prj-daas-n-dev-dw-etl-8f53 |
| NonProd/Staging | prj-daas-n-stg-dw-etl-3676 |
| Dev (PR Review) | prj-daas-n-dev-dw-etl-8f53 |

Transforms and loads data from the data lake into big query tables better optimized for querying meaningful data
such as picks across all sources (fact_picked_items) and productivity of users (fact_productivity).
It utilizes the Data Build Tool ([dbt](https://docs.getdbt.com/docs/introduction)) to perform these transformations.

It also contains some analytics scripts for calculating outliers and median, which generates the `analytics` datasets.
Lastly, it deploys a data accessibility cloud run job to verify it can access the tables from Looker.

# Looker

**Git Repo**: [takeoff-looker](https://github.com/takeoff-com/takeoff-looker)

| Environment              | GCP Project                | Looker                       |
|--------------------------|----------------------------|------------------------------|
| Production               | prj-daas-p-prd-looker-532d | https://takeoff.looker.com   |
| NonProd/Staging (unused) | prj-daas-n-stg-looker-522b | decommissioned to save money |
| Dev (unused)             | prj-daas-n-dev-looker-7976 | unused                       |

Looker is utilized as the primary way of accessing the data mart. It exposes data and relationships of data using
`Explores`. `Dashboards` then utilize these `explores` to convey meaningful overviews of client performance such
as MFC performance of days to weeks. The infrastructure sets up client connections to looker that limit what `Models`
they can access. Clients are essentially split by `Model` which enables re-use of explores while restricting users
access to specific datasets at the client scope.

The GCP projects exist to manage big query service accounts and looker connections to those service accounts.