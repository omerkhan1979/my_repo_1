Quick Reference
==
[[Table of Contents](../../README.md#table-of-contents)] : [Getting Started](../../getting-started/00-getting-started.md)

## Contents

- [Quick Reference](#quick-reference)
  - [Contents](#contents)
    - [RQ Tools Retailer-specific commands](#rq-tools-retailer-specific-commands)
    - [Connect to an on-demand-env and run tests](#connect-to-an-on-demand-env-and-run-tests)
    - [Use Docker to connect to an environment and run tests](#use-docker-to-connect-to-an-environment-and-run-tests)
    - [Use a Github Workflow to deploy an ODE and automatically run tests](#use-a-github-workflow-to-deploy-an-ode-and-automatically-run-tests)
    - [How to copy configuration from one environment to another (copy-config)](#how-to-copy-configuration-from-one-environment-to-another-copy-config)
    - [Run a specific test using the test marker](#run-a-specific-test-using-the-test-marker)
    - [Report a Test Failure](#report-a-test-failure)
    - [Update RQ-Tools pod with a specific version and run tests](#update-rq-tools-pod-with-a-specific-version-and-run-tests)

### RQ Tools Retailer-specific commands

Use the following commands to run the full suite of tests for a given retailer, using the default MFC-ID and User Role. Environment is required (`ode`, `uat`, `qai`, `dev`).

| Retailer | Command |
| - | - |
| Albertsons | ```pytest -v -s -m rq --r abs --e <env> ``` |
| MAF | ```pytest -v -s -m rq --r maf --e <env> ``` |
| Pinemelon | ```pytest -v -s -m rq --r pinemelon --e <env> ``` |
| SMU | ```pytest -v -s -m rq --r smu --e <env> ``` |
| Tienda | ```pytest -v -s -m rq --r tienda --e <env> ``` |
| Wakefern | ```pytest -v -s -m rq --r winter --e <env> ``` |
| Woolworths | ```pytest -v -s -m rq --r wings --e <env> ``` |

Additional information about pytest usage and marks can be found in [Pytest Tests](/docs/usage/01-pytest-tests.md).

### Connect to an on-demand-env and run tests

1. Connect to the `rq-tools` Pod:
```sh
gcloud container clusters get-credentials ode-gke --zone us-central1 --project <ODE GKE PROJECT_ID>
```
You may be prompted to authenticate using the [latest changes to kubectl](https://cloud.google.com/blog/products/containers-kubernetes/kubectl-auth-changes-in-gke). 
1. Use kubectl to run pytest tests (make sure you provide the mark (e.g., `rq`). Location is optional and can be reomved).
```sh
kubectl exec -n ode -it deployments/rq-tools -- /bin/bash -lc "pytest -s -m <mark> --r <retailer> --e ode --l <mfc-id>"
```

### Use Docker to connect to an environment and run tests

This assumes that you have set up and authenticated accordingly with `gcloud cli`, `gh cli`, and have authenticated to the gcr.io registry, run `gcloud auth configure-docker`.

1. Make sure you are connected to the right project in Gcloud.
`gcloud config set projec <PROJDECT_ID>`

2. Run:
```bash
docker run --pull=always --platform linux/amd64 \
    --entrypoint bash -it --rm \
    -v ~/.config/gcloud:/root/.config/gcloud \
    -v ~/.config/gh/config.yml:/root/.config/gh/config.yml \
    -v ~/.config/gh/hosts.yml:/root/.config/gh/hosts.yml \
    gcr.io/takeoff-204116/rq-tools:latest
```
3. Then run the pytest command for your client and env. For example: `pytest -v -s -m rq --r abs --e ode`

### Use a Github Workflow to deploy an ODE and automatically run tests

The [Deploy to ODE](https://github.com/takeoff-com/release-train-management/actions/workflows/deploy-to-ode.yaml) github workflow can also be used to create an ODE for a given Release Train version and automatically run tests. 

To trigger the deployment of an ODE and run tests: 
1. Navigate to the  [Deploy to ODE](https://github.com/takeoff-com/release-train-management/actions/workflows/deploy-to-ode.yaml) workflow in the Release Train Management repo. 
2. Expand the Run Workflow drop-down and complete the available fields as needed:

   ![Deploy to ODE](/docs/images/deploy-to-ode.png)
   
   Note that **Run RQ & Report to TestRail** should only be used when reporting results for Release Trains to Testrail.
4. Click **Run**. 
For more information, see the [Release Train Management](https://github.com/takeoff-com/release-train-management/blob/master/docs/how-to/04-deploy-an-ode.md) repo documentation.

### How to copy configuration from one environment to another (copy-config)
1. Go to the [Actions secton of the Release Qualifications Tools](https://github.com/takeoff-com/release-qualification-tools/actions/workflows/copy_config.yml) repo. 
2. Select **Copy Configuration from a source to a target**.
3. Expand the **Run Workflow** drop-down.
4. Fill out fields accordingly, and click **Run Workflow**. For example:

   ![](/docs/images/copycfg.png) 

See the [copy-config readme](/src/copy_config/README.md) for more information. 

### Run a specific test using the test marker
Pytest uses `@mark` to identify the tests that need to be run. You can run all tests (`rq`, a group like `outbound`, or a single test mark like `isps`). To find the mark for a specific test: 

  1. Search for the test by name, case ID, or some other identifiable attribute in the [Release-Qualification-Tools repo](https://github.com/takeoff-com/release-qualification-tools). 
  2. Open the pytest script (these are in the `/tests` directory), and find the `@mark` for the test. 
  You can run the specific test using that mark.  

### Report a Test Failure
- Reach out to `@team-chamaeleon` on `#domain-production` channel in Slack.
  
### Update RQ-Tools pod with a specific version and run tests

1. Build an image using a custom tag for the branch you want to use. For example, ran in release-qualification-tools repo: `docker build --platform="linux/amd64" -t gcr.io/takeoff-204116/rq-tools:$CUSTOMTAG --build-arg=GH_PAT=$GH_TOKEN . && docker push gcr.io/takeoff-204116/rq-tools:$CUSTOMTAG`
2. Set the necessary environment variables on your local machine to connect to your on-demand-environment as desribed [here](/docs/getting-started/01-on-demand-envs.md). 
3. In your `ode.env` file, also set `VERSION_IMAGE_RQ_TOOLS` to that image. So, `VERSION_IMAGE_RQ_TOOLS=$CUSTOMTAG`
4. Run `task garden-deploy -- rq-tools --force`   
   If you encounter credential issues, run `task create-kubeconfig first`

Additionally, you want to switch to an existing prior version of rq-tools, see here: https://console.cloud.google.com/gcr/images/takeoff-204116/GLOBAL/rq-tools.

More information about updating versions in ODE is available in the [ODE Documentation](https://github.com/takeoff-com/on-demand-env/blob/master/docs/usage/07-Setting-Versions.md).
