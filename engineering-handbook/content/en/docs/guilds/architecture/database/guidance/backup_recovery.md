---
title: "Backing Up and Restoring Data"
linkTitle: "Backup and Recovery"
weight: 2
description: >
    *How to backup and restore data reliably.*
---

{{% alert color="primary" %}}
The purpose of storing incremental backups is to recover to a known good state and resume normal business operations after a data catastrophe: accidental deletion of a database, data corruption, etc. As such, you should only perform a backup recovery when a catastrophe has occurred and there are no other options. This page outlines the expectations and standard procedures for backing up and restoring data.
{{% /alert %}}

{{% alert color="warning" %}}
**Policies**

_Policies apply to production instances only. Non-production instances should have backups disabled to avoid unnecessary cost._

* All business-related data will be periodically backed up using standard Google tools, procedures, and storage, unless otherwise noted.
* Backups will be encrypted at rest.
* Access to backups and restore capabilities will be limited to least privilege access.
* Data should be backed up at least once daily.
* In general, daily backups should be retained for 7 days and then automatically deleted, though longer or shorter durations may be used given adequate reason.
* Database owners should routinely practice restores in an *on-demand or other non-production* instance to stay familiar with the procedures and confirm they are still accurate.
{{% /alert %}}

## Cloud Spanner

Each Cloud Spanner database can be backed up and restored individually. Developers should adhere to the following guidelines.

{{% alert color="info" %}}
The [Cloud Spanner Terraform Module](https://github.com/takeoff-com/tf-cloud-spanner-module) is the recommended tool to implement this guidance.
{{% /alert %}}

### Backup

* You should utilize two types of Spanner backups: [Point In Time Recovery][pitr] and [explicitly created daily backups][create-backup].
* [Point In Time Recovery][pitr] must be enabled for databases and configured to retain 3 days of data.
    * PITR logs will be your main recovery mechanism for most failures. They allow for restoration at any point in time within the retainment window. Think "Oops, we dropped a table."
* Other backups should be performed once per day. This can be achieved with a combination of [Cloud Scheduler][cloud-scheduler] and [Workflows][workflows].
    * Explicit backups are stored independently from the database and can be used as a fallback for cases where PITR will not help. Think "Oops, we deleted the database."
* Use the backup procedure, not the import/export procedure.
    * This procedure has no performance impact, automatically encrypts and stores data, automatically removes old backups, and has a faster time to restore (see [Google's choice table][backup-choice]).
* If you are running a single-region Spanner instance, backups should be copied to a different region.

### Recovery

_These steps are based on Google documentation, which should be regarded as authoritative._

In the case of a data catastrophe, perform the following steps to recover from backup:

1. Identify the latest time the data was known to be in a good state.
2. If the time falls within the point in time recovery window and the database still exists, follow guidance for [restoring from backup using point in time recovery][pitr-restore].
3. Otherwise, follow guidance on [restoring from a backup][restore] to identify and restore a backup.
4. Data must be restored to a new database (that does not yet exist) within the existing instance.
5. After the restore completes, modify the associated application's configuration to point to the restored database and redeploy it.
6. Reapply any [TTL][ttl] retention policies on the tables. (Remember that existing data will have older timestamps, so be careful not to delete the data that was just restored.)
7. When you are confident that the application is working with the recovered database, backup and delete the original database. (It's always prudent to back up a database before deleting it, even if you don't think you'll need it. Keep the backup for 30 days for good measure.)
8. If you manage your Spanner database with Terraform:
    * Remove the original database resource from the Terraform file.
    * Add a new resource for the recovered database to the Terraform file.
    * Import the new database into managed state.<br>
      Example: `terraform import google_spanner_database.database instances/test/databases/restored-db`
    * Confirm `terraform plan` matches the current state of infrastructure.

[backup-choice]: https://cloud.google.com/spanner/docs/backup/choose-backup-import
[create-backup]: https://cloud.google.com/spanner/docs/backup/create-backup
[cloud-scheduler]: https://cloud.google.com/scheduler
[workflows]: https://cloud.google.com/workflows
[pitr]: https://cloud.google.com/spanner/docs/pitr
[pitr-restore]: https://cloud.google.com/spanner/docs/use-pitr#backup_and_restore
[restore]: https://cloud.google.com/spanner/docs/backup/gcloud#restore
[ttl]: https://cloud.google.com/spanner/docs/ttl