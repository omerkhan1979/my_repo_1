How to update an RT service version
==
[[Table of Contents](../../README.md#table-of-contents)] : [Update Services](./05-update-services.md)

## How to update service-version(s) on an RT 

Occasionally we need to update a service for a given RT due to a hotfix, rolling back a version, check in a late-breaking change, or for some other request from a scrum team.
   
   ### Update a service version for all clients      
   1. Create a branch from `master`.
   2. Navigate to the release train's `services.yaml` file (e.g., ReleaseTrains > [current year] (e.g., 2023) > [release train] (e.g., RT44-23) > block-deploy-to.yaml).
   3. In `services.yaml`, update the `helm_chart_version` (and `image` version if applicable) for the service.
   4. Open a PR for your change.
   5. Push the PR to the `master` branch. This will will automatically trigger a new deploy to ABS and Winter QAI. Any ODEs will need to be updated manually or re-deployed.

   ### Update a service version for a specific client
   1. Create a branch from `master`.
   2. Navigate to the RT's directory (e.g., ReleaseTrains > [current year] (e.g., 2023) > [release train] (e.g., RT44-23)).
   3. Create a directory named for the client's codename (as listed in [ALLCLIENTS.yaml](https://github.com/takeoff-com/release-train-management/blob/feature/PROD-12103-update-RTM-readme/ALL_CLIENTS.yaml)).
   4. In the directory, create a `services.yaml` file with the service name and `helm_chart_version` (and `image` if applicable) version. See [RT28-23 for an example](https://github.com/takeoff-com/release-train-management/blob/feature/PROD-12103-update-RTM-readme/ReleaseTrains/2022/RT18-22/abs/services.yaml)). 
   5. Open a PR for your change.
   6. Push the PR to the `master` branch.
   
   This will trigger an update for all qai environments; however, only the `{client}` you updated will be effectively changed, as all other deloys will be no-op-deploys.
   
   `Caution:` Only versions that are for the Release Train should go into these directories. 
