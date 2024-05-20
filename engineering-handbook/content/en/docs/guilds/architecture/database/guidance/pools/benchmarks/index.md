---
title: "Connection Pool Performance Benchmarks"
linkTitle: "Benchmarks"
weight: 1
date: 2022-03-21
description: >
    *Results of benchmarking PostgeSQL with various connection pool limits.*
---

{{% alert color="primary" %}}

Bencharmking was performed against PostgreSQL with various connection pool limits to provide concrete data before proposing pool configuration guidance. This page outlines the conditions under which the experiments were performed and the results.

{{% /alert %}}

## Setup

* A CloudSQL Postgres instance was created in a sandbox project with the same configuration as production instances.
  * Version 11
  * 8 vCPUs
  * 16Gb ram
  * us-east1-b
* The instance contained a test database initialized with the [pgbench] defaults and a scale factor of 80, resulting in an accounts table with 8,000,000 rows and size of roughly 1.3GB.
* The [Bitnami PgBouncer Docker image][pgbouncer-docker] was used for connection pool.

Also see [Configuration](#configuration).

## Benchmarking Steps

* All tests were run from a CloudShell VM also residing in us-east1-b to the public IP address of the instance.
* For each run, the following steps were performed:
  1. Run `gcloud sql connect perf-test-instance-1 --user=<me> -d perf-test-db --quiet` to allowlist the CloudShell IP on the Postgres instance network for 5 minutes.
  2. Start Docker in a shell session: `docker run -it --rm --name pgbouncer -p6432:6432 -e POSTGRESQL_USERNAME=<me> -e POSTGRESQL_PASSWORD=<password> -e POSTGRESQL_DATABASE=perf-test-db -e POSTGRESQL_HOST=<public IP> -v $(pwd)/pg_perf/pgbouncer/:/bitnami/pgbouncer/conf/ bitnami/pgbouncer:latest`
     1. You must create pgbouncer.ini and userlist.txt files in a directory and bind mount them. See the [Configuration section](#configuration).
  3. Run pgbench with variable parameters, e.g., `pgbench -c 200 -j 20 -T 60 -h 127.0.0.1 -p 6432 -U <me> perf-test-db`, where `c` is the number of concurrent client connections, `j` is the number of threads available to pgbench, and `-T` is the number of seconds to continuously run transactions.
  4. Monitor pools using `psql -h localhost -p 6432 -U <user> pgbouncer` and the `SHOW POOLS` command. Pools and waiting queue should be fully saturated.
  5. Record resulting transactions per second.

## Results

The [results] of both tests loosely align with the outcomes in [About Pool Sizing][poolsizing] - increasing the pool size has a large initial impact, but the marginal increase in transactions per second decreases as the gap between server cores and concurrent connections increases. Further, the raw TPS numbers suggest most if not all of our existing Postgres-connected applications will not suffer performance issues with a single-digit connection pool.


{{< tabpane_md >}}
{{< tab_md header="Test 1 (Read/Write)" >}}
* Each client performs the default 7 read/write statements in each transaction
* 80 concurrent clients
* Run for 3 minutes
* Equal max and min pool sizes, increased from 10 to 80 by 10
* PgBouncer run in transaction mode

![Test 1 Chart](/images/en/docs/Guilds/Architecture/Database/Pools/benchmarks/test_1_chart.png)
{{< /tab_md >}}

{{< tab_md header="Test 2 (Select Only)" >}}
* Each client performs the default read-only statements in each transaction
* 200 concurrent clients
* Run for 1 minute
* Equal max and min pool sizes, increased from 10 to 200
* PgBouncer run in transaction mode

![Test 2 Chart](/images/en/docs/Guilds/Architecture/Database/Pools/benchmarks/test_2_chart.png)
{{< /tab_md >}}
{{< /tabpane_md >}}

## Caveats

All results are meant to inform general guidance and should be taken with a grain (or several grains) of salt. There are a few caveats to this approach that must be considered:

* Pool size will affect different workflows and database interaction patterns differently. It's important to understand how your application interacts with the database before choosing a number of connections.
* The tests were generally reproducible, though environmental factors like VM contention and network noise may affect the numbers on any given run. Some documentation suggests running benchmarks on the matter of hours to get truly stable numbers.
* The number of clients, size of the databases, and contention for updating rows may also affect these numbers, but not all variable combinations were attempted. This is an exercise for the reader!

## Configuration

{{< card-code header="**Example Terraform**" lang="tf" >}}
terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 4.14.0"
    }
  }
}

provider "google" {
  project = <project-id>
  region  = "us-east1"
  zone    = "us-east1-b"
}

resource "google_sql_database_instance" "perf-test" {
  name             = "perf-test-instance-1"
  database_version = "POSTGRES_11"
  deletion_protection = false

  settings {
    # Second-generation instance tiers are based on the machine
    # type. See argument reference below.
    tier = "db-custom-8-16384"
    disk_autoresize = false
    activation_policy = "NEVER"

    backup_configuration {
      enabled = false
      point_in_time_recovery_enabled = false
    }
  }
}

resource "google_sql_database" "perf-test-database" {
  name     = "perf-test-db"
  instance = google_sql_database_instance.perf-test.name
}

resource "google_sql_user" "users" {
  name     = <user>
  instance = google_sql_database_instance.perf-test.name
  password = <password>
  deletion_policy = "ABANDON"
}
{{< /card-code >}}

{{< card-code header="**pgbouncer.ini**" lang="ini" >}}
# This file should be mounted in the conf folder with userlist.txt.
[databases]
perf-test-db = host=<public IP> port=5432 dbname=perf-test-db

[pgbouncer]
listen_port = 6432
listen_addr = 0.0.0.0
auth_type = md5
auth_file = /bitnami/pgbouncer/conf/userlist.txt
admin_users = <user>
pool_mode = transaction
max_client_conn = 500
max_db_connections = 500
default_pool_size = 40    # Change
min_pool_size = 40        # Change
{{< /card-code >}}

{{< card-code header="**PgBouncer userlist.txt**" lang="ini" >}}
# This file should be mounted in the conf folder with pgbouncer.ini.
# <user> <md5 + md5(password + user)>
"first.last" "md5las348dlfkhwekn5i7"
{{< /card-code >}}

## References

- [pgbench]
- [pgbouncer]
- [About Pool Sizing][poolsizing]
- [Tuning PostreSQL with pgbench](https://www.cloudbees.com/blog/tuning-postgresql-with-pgbench)

[pgbench]: https://www.postgresql.org/docs/11/pgbench.html

[pgbouncer-docker]: https://hub.docker.com/r/bitnami/pgbouncer/

[pgbouncer]: https://www.pgbouncer.org/

[poolsizing]: https://github.com/brettwooldridge/HikariCP/wiki/About-Pool-Sizing

[results]: https://docs.google.com/spreadsheets/d/1X7R3aG6w9-NxiFVRNxqa5tPcS2gsPrCsiFyZDqaSqsA/edit?usp=sharing
