Manually kick of an RT deploy to a client
==
[[Table of Contents](../../README.md#table-of-contents)] : [Manual RT Deploy](./03-manual-rt-deploy.md)

## How to manually kick off an RT deploy to a specific client

Manual RT deploys are used when we have [blocked a specific client and env](https://github.com/takeoff-com/release-train-management/docs/how-to/02-block-deploy-to.md) from being deployed as part of automated RT deploy processes.
   
   1. Create a temp branch in [Release-train-management](https://github.com/takeoff-com/release-train-management) repo.
   2. On your temp branch:
      - Remove `[your_client]-prod` from [block-deploy-to.yaml](https://github.com/takeoff-com/release-train-management/blob/df-temp-rt44-example/ReleaseTrains/2023/RT44-23/block-deploy-to.yaml) ([example branch](https://github.com/takeoff-com/release-train-management/compare/master...df-temp-rt44-example?quick_pull=1)) and commit the change.
   	 - Run the [Client-Env Specific Deploys](https://github.com/takeoff-com/release-train-management/actions/workflows/deploy-to.yaml) workflow:
   		   - `Branch`: your temp branch
   		   - `RT Version`: RT44-23
   		   - `Client list`: codename value from `ALL_CLIENTS.yaml`, or `ODE_CLIENTS.yaml`.
   		   - `Env`: `prod` or whichever env you are deploying to.
   		   - `Close Maintenance Event`:
               - **De-select** if other deployment activities need to take place _after_ the release train deploy is complete, but _before_ the maintenance window is closed.
               - **Select** if the maintenance event can be auto-closed (e.g., the RT is being deployed during the client's secondary window). 
   4. After the deploy completes, if `Close Maintenance Event` was de-selected, go to Statuspage and [manually complete the Scheduled Maintenance](https://engineering-handbook.takeofftech.org/docs/domains/production/statuspage/change_schedule/#complete-maintenance-early) and [verify that the site is set to operational](https://engineering-handbook.takeofftech.org/docs/domains/production/statuspage/change_schedule/#set-component-status-back-to-operational).
   5. Notify `@team-chamaeleon` in Slack that the deploy is complete, and delete the temp branch you created. Additionally, if previously agreed upon with `@team-chamaeleon`, make sure you also move the RT deploy ticket to the `Deployed`. 
