Get latest master service versions
==
[[Table of Contents](../../README.md#table-of-contents)] : [Get latest Master versions](./06-get-latest-master.md)

## Get the latest master service versions

 1. Go to the [Actions tab](https://github.com/takeoff-com/release-train-management/actions) of the release-train-management repo.
 1. Select [Deploy after RT cut](https://github.com/takeoff-com/release-train-management/actions/workflows/run_qai_deploy.yaml) from the Workflows >> All workflows list.
 1. Select `Run workflow`.
 1. In the drop-down that appears, change `Use latest master` and `Get versions & skip deploys` to `True`. Leave the remaining fields as their default (and/or blank). 
 1. Click `Run workflow`. This will generate a new `Deploy after RT cut` entry in the workflow runs section.
 1. Open the resulting `Deploy after RT cut` workflow run and click on the `deploy` job.  
 1. Expand the `Cat local cut services` step.
 1. Copy the services and versions.
