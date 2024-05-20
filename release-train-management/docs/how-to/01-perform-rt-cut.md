Perform an RT cut
==
[[Table of Contents](../../README.md#table-of-contents)] : [Perform an RT Cut](./01-perform-rt-cut.md)

## How to create a Release Train by performing an "RT Cut"

Performing an "RT Cut" is a mostly-automated process that compiles the latest RT services versions into a testable release candidate and deploys that to our remaining QAI environments. It also triggers the creation of On-Demand Environments for each client, creation of a Test Plan and Test Runs in Testrail, and runs Release Qualification tests on each ODE and reports the results to Testrail. It also automatically triggers the removal of each ODE once testing is complete.

   1. After the scheduled RT Cut runs (Even Wednesdays at Noon Eastern, but can start as much as 10 minutes late), a PR is created in the repo ([RT44-23 example](https://github.com/takeoff-com/release-train-management/pull/432)).
   1. Ensure that the workflow step [rtm-pr-checker](https://github.com/takeoff-com/release-train-management/actions/runs/6722054179/job/18269145546) is green.
   1. Check to make sure `releasetrains.yaml` got updated.
   1. Check versions in `services.yaml`, particularly for Distiller and IMS - make sure Helm Chart version is correct:
      a. Go to [distiller-deploy](https://github.com/takeoff-com/distiller-deploy) repo (not distiller repo). 
      b. Search for the **build tag** and go into `values.yaml`
      c. look for image > tag (for Distiller) and make sure that value matches `image` for distiller in the `services.yaml` file. 
      d. Do the same thing in [Deploy-IMS](https://github.com/takeoff-com/Deploy-IMS) repo > search for **build tag**. IMS/helm > values.yaml - search for image version value.
      **NOTE**: If versions do NOT match, or if there are any other issues, go to the appropriate Slack channels and post a message explaining the problem.
   1. Approve the PR and merge to `master`.
    - Pushing a commit to the `master` branch that includes changes to `ReleaseTrains.yaml` triggers triggers the `Deploy after RT cut` GitHub Actions Workflow which deploys
   to the qai static environments defined in the latest RT directory. 
    - Additionally, upon merge of the PR the [Deploy to ODE](https://github.com/takeoff-com/release-train-management/actions/runs/6563586946) workflow is triggered.
   1. **Important** follow the steps in the [Statuspage readme](https://github.com/takeoff-com/release-notes/blob/master/src/schedule/README.md) to review and merge the Scheduled Maintenance Data, as well as the subsequent PR for the incidents data.  

   You can check deployments in Slack by going to [release-train-deployment](https://takeofftech.slack.com/archives/C01F5F36NDT) channel and check for messages confirming deployments. 
   You can also check the [RTM-Deployments](https://takeofftech.slack.com/archives/C04CX2M3GMB) channel in case there are any Opsgenie alerts.
		- If a deploy fails, alerts will be generated. If you receive an alert that a deployment failed, you can ran re-run verify-deployment workflow. Sometimes its just timing issue and everything is fine. 
		- If deploy succeeded but a version is wrong, alerts will also be generated.
