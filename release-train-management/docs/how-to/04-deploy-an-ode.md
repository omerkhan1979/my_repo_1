Deploy an On-Demand Environment
==
[[Table of Contents](../../README.md#table-of-contents)] : [Deploy an ODE](./04-deploy-an-ode.md)

## How to trigger an On-Demand Environmnent deploy

 1. Go to the [Actions tab](https://github.com/takeoff-com/release-train-management/actions) of the release-train-management repo.
 1. Select [Deploy to ODE](https://github.com/takeoff-com/release-train-management/actions/workflows/deploy-to-ode.yaml) from the Workflows >> All workflows list.
 1. Select `Run workflow`.
 1. In the drop-down that appears, enter the `RT Version` in the correct format (e.g., RT44-23).
 1. Enter one or more clients in the `Comma delimited client list` using the names listed in `ALL_CLIENTS.yaml` or `ODE_CLIENTS.yaml`.
 1. Select `Run rq & Report To Testrail` if you want the workflow to run [Release Qualification Tests](https://github.com/takeoff-com/release-qualification-tools) and report the results to a new test plan and test run in Testrail. 
 1. Select `Tear down (fast-delete) the ODE env in the end` if you want the workflow to automatically delete the ODE once it has completed building the environment and running tests. This step is generally only recommended if you are performing Release Train testing because the environment is immediately destroyed.
 1. Click `run workflow` to begin the process of building the ODE.  

`NOTE`: For more information about ODEs, see the [on-demand-env repo](https://github.com/takeoff-com/on-demand-env)https://github.com/takeoff-com/on-demand-env docs, and for information about reporting results to Testrail, see the [pytest-reporting repo](https://github.com/takeoff-com/pytest-reporting)https://github.com/takeoff-com/pytest-reporting. 
