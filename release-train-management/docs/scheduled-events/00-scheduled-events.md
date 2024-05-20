Scheduled Automation Events
==
[[Table of Contents](../../README.md#table-of-contents)]

## Scheduled Events

This repo uses the following automatically scheduled events:

   - `Release Train Cut` - **Even Weeks:** Wednesdays at 12:00 pm (noon) EST (_managed in_ [create_train.yaml](https://github.com/takeoff-com/release-train-management/blob/master/.github/workflows/create-train.yml#L4)).
   - `Latest Master Updates (QAI Envs)` - **Odd Weeks:** Thursdays & Fridays at 5:30 AM UTC (_managed in_ [qai-update-latest-master.yaml](https://github.com/takeoff-com/release-train-management/blob/master/.github/workflows/qai-update-latest-master.yaml#L3)).
   - `UAT Deployments` - **Odd Weeks:** Runs on Monday, Tuesday, and Wednesday at 12:15 AM EST, for different sets of clients each day (_managed in_ [deploy_to_uat.yaml](https://github.com/takeoff-com/release-train-management/blob/master/.github/workflows/deploy_to_uat.yaml)).
   - `Prod Deployments` - Runs on a specific schedule for each client that corresponds to the [Primary Window](https://docs.google.com/spreadsheets/d/1FBR3cNin3fUXxM3Rrx0gqqPW0uXJGks0Gxq5sRtwwkc/edit#gid=0) (_managed in_ [deploy-to-prod.yaml](https://github.com/takeoff-com/release-train-management/blob/master/.github/workflows/deploy-to-prod.yaml)).
   - `Pre Go-Live Deployments` - **Odd Weeks:** Thursdays at 12:45 AM EST (_managed in_ [deploy_pre_go_live_clients.yaml](https://github.com/takeoff-com/release-train-management/blob/master/.github/workflows/deploy_pre_go_live_clients.yaml)).
