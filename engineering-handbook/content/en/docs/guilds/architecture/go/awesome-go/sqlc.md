---
title: "sqlc"
linkTitle: "sqlc"
weight: 24
date: 2022-07-14
description: Write SQL queries for PostgreSQL (CloudSQL)

---

https://github.com/kyleconroy/sqlc

sqlc allows you to write templated SQL queries.

It then generates code based on those queries and database schema.

You should use sqlc along with [pgx](https://github.com/jackc/pgx) (in sqlc.yaml):

```yml
packages:
  - name: "db"
    path: "your/package/db"
    engine: "postgresql"
    schema: "ops/db/migrations"
    queries: "your/package/sql/query/"
    sql_package: "pgx/v4"
```

Limitations:
- Database schema should be supplied to generate proper code, which may be problematic in some cases
- Limited support for ["dynamic"](https://github.com/kyleconroy/sqlc/discussions/364) queries.
