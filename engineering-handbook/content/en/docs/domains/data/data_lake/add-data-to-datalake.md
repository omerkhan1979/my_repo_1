---
title: "Delivering Data to the Data Pipeline"
linkTitle: "Delivering Data to the Data Pipeline"
weight: 100
Date: 2023-08-03
---

## Data Delivery Method

While there used to be multiple methods of sending data to the data lake, there is now only one method supported for new data sources.  Existing sources will continue to be supported but  may be convereted in the future.

<a href="https://github.com/takeoff-com/daas-data-lake-ingestion/blob/main/pubsub-provider-api.md" target="_blank">PubSub Data Ingestion API</a>

# Adding a new source

## Process
To push a new data source to the data pipeline, a team, owning the data, does the following:

1. meet with data domain leadership and complete a data sharing agreement  
1. creates a PR following <a href="https://github.com/takeoff-com/daas-data-lake-ingestion/blob/main/README.md#adding-a-new-pubsub-data-source" target="_blank">Adding A New PubSub Data Source</a>
1. coordinates with the data domain to test and deploy integrating the source to our pipeline
