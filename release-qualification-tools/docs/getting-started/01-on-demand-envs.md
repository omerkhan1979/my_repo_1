On-Demand Environment Testing Setup
==
[[Table of Contents](../../README.md#table-of-contents)] : [Getting Started](/docs/getting-started/00-getting-started.md)

This page explains how to set up your On-Demand Environment to run tests.

For more information about running Pytest tests or test scripts, see [Usage](/docs/usage/00-Usage.md).

#### **On-demand environment**

### Connect to the rq-tools Pod and run tests

You can also connect to `rq-tools` and run tests using the following commands: 
```sh
gcloud container clusters get-credentials ode-gke --zone us-central1 --project <YOUR RETAILER ODE PROJECT>

kubectl exec -n ode -it deployments/rq-tools -- /bin/bash -lc "pytest -s -m <mark> --r <retailer> --e ode --l <mfc-id>"
```

#### Navigate to the Pod and run in Cloud Shell

You can also naviagte to the `rq-tools` pod in cloud console and run tests from Cloud Shell there.

1. Open Cloud Console in your browser and navigate to **Workloads** > **rq-tools**.
2. Under **Managed Pods**, click the name of your rq-tools pod (e.g., `rq-tools-767cc77c4c-wwfgf`).
3. At the top of the screen, expand **KubeCTL** > **Exec** > **rq-tools**. The Cloud Shell terminal opens. 
4. In the pre-populated command that appears, replace `-- ls` with `-it -- bash` and execute it. 
5. This opens rq-tools in bash and you can run pytest commands. 
    <img src="/docs/images/cloudshell.png" height=auto max-width=auto>


### Set Env Vars and run locally

If you are not able to successfully connect using the above methods, you can also also set the following environment variables and run the pytest tests from your local machine. 
```sh
export ODE_RETAILER=
export INTEGRATION_ETL_BUCKET_NAME=<>
export GOOGLE_PROJECT_ID=
export BASE_DOMAIN=
export FIREBASE_PROJECT=
export FIREBASE_KEY=
export SERVICE_WORKER_TOKEN=
export IAP_CLIENT_ID=
```
Depending on how you deployed your On-Demand Environment, these can be found in several places:   
- ```cat garden.global.yaml``` - if deployed using Task
- [Workflow logs](https://github.com/takeoff-com/release-train-management/actions/workflows/deploy-to-ode.yaml)
- From the `rq-tools` pod on your retailer environment and copying the rq-tools container `Environment` values which can be found by running the following command while in the correct kubernetes context:
```sh
kubectl describe pod rq-tools --namespace ode
```

The firebase secret is hidden and can be found in the [firebase secret manager](https://console.cloud.google.com/security/secret-manager/secret/firebase_project_info_on-demand/versions?project=prj-on-demand-fb-15c0) in `firebase-project-info` under the key `firebase_api_key` (Actions > View secret value).

After you fill in your environment variables you can simply run the pytest command:
```sh
poetry run pytest -v -s -m <mark> --r <retailer> --e ode --l <location>
```

### Calling env-setup-tool from the RQT container that gets spun up with the ODE

* Follow the steps above to get the proper **gcloud credentials** to connect to the ODE via Kubernetes.
* Run this command, adapting for the branch and location that you would like to pass to the environment setup tool.

```sh
kubectl exec -n ode -it deployments/rq-tools -- /bin/bash -c 'export GH_PAT='$(gh auth token)'; python -m env_setup_tool.src.env_setup --location 0068 --branch demo apply-configs'
```
