Developemnt Environment Testing Setup
==
[[Table of Contents](../../README.md#table-of-contents)] : [Getting Started](/docs/getting-started/00-getting-started.md)

This page explains how to set up your local development environment to run tests.

#### 1. **Python**
:warning: Your **Python** version must be `3.10` or later.
- **[Python-Windows](https://www.python.org/downloads/windows/)**
- **[Python](https://www.python.org/downloads/)**
- **[Python-brew](https://docs.brew.sh/Homebrew-and-Python)**

#### 2. **GCloud**

   1. **[gcloud CLI](https://cloud.google.com/sdk/docs/install)** must be installed.

   2. Set application-default credentials: 
  ```sh
  bash
  gcloud auth application-default login --disable-quota-project
  ```
     
  **To Check Google Cloud Platform account connected**
  
  In order to check GCP connected account use:
  
  ```sh
  gcloud auth list
  ```
  If your your Takeoff google account is not connected, you can connect it by running:
  
  ```sh
  gcloud auth login `ACCOUNT`
  ```

#### 3. Clone the Release-Qualification-tools repo

- git clone
  ```sh
  git clone https://github.com/takeoff-com/on-demand-env.git
  ```
  OR 
- gh cli
  ```sh
  gh repo clone takeoff-com/on-demand-env
  ```

#### 3. **Environment**

  [Python Poetry](https://python-poetry.org/) is used to manage dependencies in this project.

  The repository has been updated to work with `poetry ~= 1.4.0` and `python 3.10` or `python 3.11` flavors.


   1. **Connect shared-tokens**

       To use service tokens, `shared-tokens` are connected to the project as git submodule.
       You need to initialize git submodule:

       ```bash
       git submodule init
       git submodule update
       ```

       ***Troubleshouting errors with shared-tokens***

       If you've encountered errors during this step, kindly try next:

       ```sh
       git submodule update --recursive --remote
       ```

       In case this didn't help - try to remove cached submodule and try again with connect `shared-tokens`.

       ```sh
       git rm --cached shared-tokens
       ```
     
   1. **Install Poetry**
       
       :warning: Poetry Shell does not SEEM to work correctly in zsh shell... use bash shell.
     
       On Mac, run `chsh -s /bin/bash` and restart the terminal to switch to bash.
     
       **[Poetry Install](https://python-poetry.org/docs/#installation) is used for dependency management**

   - **Create and activate the virtual environment, and install the dependencies from `poetry.lock`**

     In ```/release-qualification-tools```, run: 

        ```bash
        poetry shell
        poetry install
        ```

       At this point, you should be able to run tests. See [Usage](/docs/usage/00-Usage.md) for more information.   


       **More information about [dependencies](https://python-poetry.org/docs/basic-usage/#installing-dependencies)**

       If you encounter the following error:

       ```bash
       Failed to clone https://github.com/takeoff-com/pytest-reporting.git,
       Check your git configuration and permissions for this repository.
       ```

     update your git configs:

       ```bash
       git config --global url."https://github.com/".insteadOf "https://token@github.com/"
       ```

   - **Add new dependency**

       ```sh
       poetry add <package>
       ```
       
       **More information about [poetry add](https://python-poetry.org/docs/cli/#add)**

       Performing the `poetry add` will automatically update the files `pyproject.toml` and `poetry.lock`.

### Calling env-setup-tool from a dev enviroment

* Ensure that you have all of these values set:

```sh
export ODE_RETAILER=$ODE_RETAILER
export INTEGRATION_ETL_BUCKET_NAME=$INTEGRATION_ETL_BUCKET_NAME
export GOOGLE_PROJECT_ID=$GOOGLE_PROJECT_ID
export BASE_DOMAIN=$BASE_DOMAIN
export FIREBASE_PROJECT=$FIREBASE_PROJECT
export FIREBASE_KEY=$FIREBASE_KEY
export SERVICE_WORKER_TOKEN=$SERVICE_WORKER_TOKEN
export IAP_CLIENT_ID=$IAP_CLIENT_ID
export GH_PAT='$(gh auth token)
```

* Run this command, adapting for the branch and location that you would like to pass to the environment setup tool.

```sh
poetry run python -m env_setup_tool.src.env_setup --location 0068 --branch demo apply-configs
```

