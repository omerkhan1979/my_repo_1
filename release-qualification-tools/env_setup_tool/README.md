Environment Setup Tool
==
[[Table of Contents](../README.md#table-of-contents)]

## Overview

The environment setup tool was designed to facilitate the application of specified configurations during the ODE spin-up process and enhancement of BDD and Feature Testing processes. 

Its primary role is to deploy base level configuration settings on every ODE when a specific feature is requested.

## Our philosophy around the tool

Our philosophy around the tool is to be data, retailer and location agnostic.  The goal is to help you configure ***features***.

The tool will take data that you provide and add it to the configuration for your environment.  But we do not check values for correctness.

## Supported configurations

The tool currently supports the following configuration types:

* The Service Catalog (TSC)
* Inventory Management System (IMS)
* Sleeping Area Rules
* Product Catalog

## How to add a new configuration

To add a new configuration, you will need to implement the following in this repo:

* A Provider
* A ConfigType
* CLI processing
* Unit Testing

In addition to that, you will also need to do the following in the  **[environment-configs](https://github.com/takeoff-com/environment-configs)** repo:

* Update base and template schema validation

Finally you will need to update the documentation in both this repo and the **environment-configs** repo.

### Provider

To implement a provider, use the existing providers as a model.

You can find the existing providers in this source folder:

* ***env_setup_tool / src / config_providers***

A new provider should be:

* added to the folder above
* derived from `BaseConfigProvider`
* added to **config_providers**

### ConfigType

To add a new configuration type to the code, do the following:

* edit **env_setup_tool / src / config_types.py**
* add the type to `class ConfigType(Enum)`

If the new configuration type requires a subtype, see TSC and IMS examples for a model of how to implement it.
 
### CLI (Command Line Interface)

The tools CLI (command line interface) uses the **Typer** python library to process arguments. 

To add command line options for the new configuration, do the following:

* add a CLI helper to ***env_setup_tool / src / cli_helpers***
* every new cli helper needs to be added to the main app (for example):
```py
env_setup_tool.add_typer( ims_cli.app, name="ims", help="Subcommand to access IMS Configurations" )
```


See the [Typer](https://typer.tiangolo.com/) documentation for more info.

### Unit Testing

When adding a new configuration, you should also add unit tests.

Unit tests for the tool can be found here:

* **env_setup_tool > tests**

To run the tool tests only, use this command from the root of the repo:

```sh
poetry run pytest env_setup_tool/tests/
```

To run a specific test (test_apply_configs.py for example), use this command:

```sh
poetry run pytest env_setup_tool/tests/test_env_setup.py
```

### Base/Template and validation in environment-config repo

To add a set of features do the following (in this example we will call your features **my_features**):

In the **[environment-configs](https://github.com/takeoff-com/environment-configs)** repo, do the following:

1. Create a branch for your set of features (example branch: `feature/PROD-12345`)
2. Create a new folder for your features under the **features_data** folder (for example `/features_data/my_features`)
3. Add the feature files to the folder
4. In your new folder, create a file with the name `features-(your feature key).yaml` (example: `features-my_features.yaml`)
5. Set the contents with paths to your files and save the file:

For example:

```yaml
key: my_features
title: my_features configuration
description: my_features configuration
configs:
  ims:
    addresses:
      path: features_data/my_features/ims-addresses-my_features.yaml
  tsc:
    config_items:
      path: features_data/my_features/tsc-config-items-my_features.yaml
    flow_racks:
      path: features_data/my_features/tsc-flow-racks-my_features.yaml
    locations:
      path: features_data/my_features/tsc-locations-my_features.yaml
    routes:
      path: features_data/my_features/tsc-routes-my_features.yaml
    staging_config:
      path: features_data/my_features/tsc-staging-config-my_features.yaml
    staging_locations:
      path: features_data/my_features/tsc-staging-locations-my_features.yaml
    tote_types:
      path: features_data/my_features/tsc-tote-types-my_features.yaml
  sleeping_area_rules:
    path: features_data/my_features/sleeping-area-rules-my_features.json
  product-catalog:
    path: features_data/my_features/product-catalog-my_features.json
```

### Uppdate in both the env-setup tool and environment-config repos

When adding new configuration types, be sure to update the documention in both repos

### Limitations of the Tools

The tool only validates the schema of the input files.

It does not attempt to make sense of the actual configuration data.

* * *

## How to run the tool

To run the tool you have to:

* First, create and push a branch and folder in the **[environment-configs](https://github.com/takeoff-com/environment-configs)** repo
* Then from this repo, run a command line referencing the branch and folder in that repot

Here are those steps in more detail:

In the **[environment-configs](https://github.com/takeoff-com/environment-configs)** repo, do the following:

1. Create a branch for your set of features (example branch: `feature/PROD-12345`) 
2. For more details on the files, see: [Base/Template and validation in environment-config repo](#basetemplate-and-validation-in-environment-config-repo) )
3. Create a new folder for your features to the **features_data** folder (for example `my_features`)
4. Add the feature files to the folder
5. Push the updated branch to the repo

In this repo (**release-qualifications-tools**)

6. Run the tool, referencing the branch in the first repo (`--branch`) and the folder (`--feature`)

For example (replace with your branch and feature folder name from the first repo):

```sh
python -m env_setup_tool.src.env_setup --branch=feature/PROD-12345 --feature=my_features apply-configs
```

Or via `poetry run`:

```sh
poetry run python env_setup_tool.src.env_setup --branch=feature/PROD-12345 --feature=my_features apply-configs
```

* * *

## Feature Configs Application

When you specify a feature (by passing an argument ``--feature <feature_name`` to the cli command), the tool finds and
applies the settings from that feature and all its parent features, starting from the highest level down. This makes
sure your environment is set up correctly for testing and development focused on that specific feature.

* * *

## Documentation Links

* The **documentation** links below point to an autogenerated help file
* See the [Doc Generation](#doc-generation) section for more info

* [env-setup documentation (Auto Generated)](ENV_SETUP.md)

* [apply-configs](ENV_SETUP.md#env-setup-apply-configs) Apply base configurations
* [apply-isps](ENV_SETUP.md#env-setup-apply-isps)
* [apply-sleeping-areas](ENV_SETUP.md#env-setup-apply-sleeping-areas) - Apply sleeping-area configurations
* [load-config-file](ENV_SETUP.md#env-setup-load-config-file)
* [product_catalog](ENV_SETUP.md#env-setup-product_catalog)
* [product catalog upload pc](ENV_SETUP.md#env-setup-product_catalog-upload-pc)

### TSC (sub command)

* [tsc](ENV_SETUP.md#setup-env-tsc) - Subcommand to access TSC Configurations

* [tsc apply config items](ENV_SETUP.md#env-setup-tsc-apply-config-items) - Apply TSC-Config-Items configurations
* [tsc apply configs](ENV_SETUP.md#env-setup-tsc-apply-configs) - Apply all TSC configurations
* [tsc apply flow racks](ENV_SETUP.md#env-setup-tsc-apply-flow-racks) - Apply TSC-Flow-Racks configurations
* [tsc apply locations](ENV_SETUP.md#env-setup-tsc-apply-locations) - Apply TSC-Locations configurations
* [tsc apply routes](ENV_SETUP.md#env-setup-tsc-apply-routes) - Apply TSC-Routes configurations
* [tsc apply spokes](ENV_SETUP.md#env-setup-tsc-apply-spokes) - Apply TSC-Spokes configurations
* [tsc apply staging config](ENV_SETUP.md#env-setup-tsc-apply-staging-config) - Apply TSC-Staging-Config configurations
* [tsc apply staging locations](ENV_SETUP.md#env-setup-tsc-apply-staging-locations) - Apply TSC-Staging-Locations
  configurations
* [tsc apply tote types](ENV_SETUP.md#env-setup-tsc-apply-tote-types) - Apply TSC-Tote-Types configurations
* [tsc pull from prod](ENV_SETUP.md#env-setup-tsc-pull-from-prod) - Takes a prod TSC configuration per...

* * *

## Doc Generation

To generate the documentation for the **Environment Setup Tool** do the following:

```sh
# from the root of the repo:
env_setup_tool/readme_update.sh
```

This will generate a fresh copy of **ENV_SETUP.md** that is linked to above
