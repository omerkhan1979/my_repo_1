---
title: "Change Management"
linkTitle: "Change Management"
weight: 2
description: >
    *Guidelines for managing schema and data changes.*
---

{{% pageinfo %}}
_**What is database change management?**_

As a DevOps organization, developers are responsible for all aspects of the database management systems (DBMS) in use, including DBMS creation and configuration, schema design and deployment, and data manipulation. This section covers the expectations for managing changes to the schema and stored data.

The concepts covered on this page:
- Schema representation and management tools
- Schema change compatibility
- Schema deployment processes
- Schema versioning
- Manipulating data in production
{{% /pageinfo %}}

## Requirements

The following [MoSCoW][moscow] requirements apply to any implementation of database change management. They are intended to be a guide toward the end goal: _ensuring quality when making changes_.

### MUST

1. support rollbacks
1. divorce schema migration from server code and server startup
1. unify migration approach across teams/services
1. use explicit, standardized, and accessible schema versions
1. run data manipulation jobs independently of schema changes
1. support triggers and sequences
1. provide a fluid developer experience
1. guard against concurrent migrations

### SHOULD

1. support policies for preventing certain types of changes
2. automatically verify rollbacks
1. automatically verify backwards compatibility
3. provide a cross-environment view of applied schema versions

### COULD

1. include running non-SQL jobs with a similar process
2. include schema change rollups/squashing
3. include tools to port old schema system to new system
4. enforce minimum required schema version on code deployments

## Schema Tool Support

## References
- [Database Terminology][glossary]
- [DevOps Tech: Database Change Management](https://cloud.google.com/architecture/devops/devops-tech-database-change-management)
- [Evolutionary Database Design](https://www.martinfowler.com/articles/evodb.html)

[glossary]: {{% relref "glossary" %}}
[moscow]: https://www.volkerdon.com/pages/moscow-prioritisation#:~:text=MoSCoW%20(Must%20Have%2C%20Should%20Have,with%2040%25%20Shoulds%20and%20Coulds.
