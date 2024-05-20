---
title: "Storages"
linkTitle: "Storages"
weight: 1
date: 2021-11-04
description: >
    *Storages and Databases used across Takeoff*
---

{{% pageinfo %}}
_**What is storage technology?**_

By **storage technology** we mean **persistent storage** for both **structured and unstructured** data. The list includes
relational databases, nosql databases, document-oriented database, key value storages, persistent queues, file storages and so on

{{% /pageinfo %}}

## Index

- ✅ [Postgres](#postgres)
- ✅ [CouchDB](#couchdb)
- ✅ [Elasticsearch](#elasticsearch)
- ✅ [Redis](#redis)
- ✅ [Snowflake](#snowflake)
- ✅ [BigQuery](#bigquery)
- Firebase
- ✅ [Firestore](#firestore)
- ✅ [Spanner](#spanner)
- SFTP
- Google Cloud Storage

## Postgres

> [PostgreSQL](https://www.postgresql.org) is a powerful, open source **object-relational database system** with over 30 years of active development that has earned it a strong reputation for reliability, feature robustness, and performance.

In Takeoff we use PostgreSQL offering from Google CloudSQL. 
It is used as a default generic purpose database for all kind of needs.
 
{{% storage_list dataProvider="data-model/storages" type="cloudsql" diagramBaseDir="../data-flows" %}}

## CouchDB

> [CouchDB](https://docs.couchdb.org/en/stable/index.html) is an open-source **document-oriented NoSQL database**, implemented in Erlang. CouchDB uses multiple formats and protocols to store, transfer, and process its data. It uses JSON to store data, JavaScript as its query language using MapReduce, and HTTP for an API.

In Takeoff we use CouchDB as a centralized datastore for multiple purposes.
The most known is as source of **customer orders** information, however there are several in-flight initiatives to reduce their usage.

{{% storage_list dataProvider="data-model/storages" type="couchdb" diagramBaseDir="../data-flows" %}}

## Elasticsearch

> [Elasticsearch](https://www.elastic.co/elasticsearch/) is a **search engine** based on the Lucene library. It provides a distributed, multitenant-capable full-text search engine with an HTTP web interface and schema-free JSON documents.

In Takeoff we use Elasticsearch as a part of ELK stack to store logs information, hosted in [Elastic Cloud](https://kibana-cloud.tom.takeoff.com/).

## Redis 

> [Redis](https://redis.io) is an open source (BSD licensed), **in-memory data structure store**, used as a **database**, **cache**, and **message broker**. Redis provides data structures such as strings, hashes, lists, sets, sorted sets with range queries, bitmaps, hyperloglogs, geospatial indexes, and streams. 
 
In Takeoff we use Redis as a communication pattern and store some random data GraphQL queries, workers state, etc.

{{% storage_list dataProvider="data-model/storages" type="redis" diagramBaseDir="../data-flows" %}}

## Snowflake
> [Snowflake](https://docs.snowflake.com/en/) is an advanced data platform provided as Software-as-a-Service (SaaS). Snowflake enables data storage, processing, and analytic solutions.

In Takeoff we use Snowflake as cloud DWH solution.

{{% storage_list dataProvider="data-model/storages" type="snowflake" diagramBaseDir="../data-flows" %}}

## BigQuery
> [BigQuery](https://cloud.google.com/bigquery/) us a serverless, highly scalable, and cost-effective multicloud data warehouse designed for business agility.

In Takeoff we use BigQuery to store data for analytics purposes.

{{% storage_list dataProvider="data-model/storages" type="bigquery" diagramBaseDir="../data-flows" %}}

## Firestore
> [Firestore](https://firebase.google.com/products/firestore) is a Cloud Firestore is a NoSQL document database that lets you easily store, sync, and query data for your mobile and web apps - at global scale.

In Takeoff we use Firestore as storage for mobile applications.

{{% storage_list dataProvider="data-model/storages" type="firestore" diagramBaseDir="../data-flows" %}}

## Spanner

> [Spanner](https://cloud.google.com/spanner) Spanner is a distributed SQL database management and storage service developed by Google. It provides features such as global transactions, strongly consistent reads, and automatic multi-site replication and failover.

In Takeoff we use Spanner as a general-purpose multi-tenant relational database.

{{% storage_list dataProvider="data-model/storages" type="spanner" diagramBaseDir="../data-flows" %}}