# Environment and Feature Based Configs

This repo stores the configuration items and data that are applied when building a fresh on-demand environment. The data
is stored per feature and represents the required data to test a specific feature. Its primary purpose is to provide a
centralized location for managing and retrieving configurations for fresh ODE for further development and testing.

```
environment-configs/
│    
├──features_data
│   ├─── base/
│   │      ├── base.yaml
│   │      ├── tsc-config-items-base.yaml
│   │      ├── ims-addresses-base.yaml
│   │      ├── tsc-locations-base.yaml
│   │      └──  ... 
│   ├── templates/
│   │      ├── tsc-config-items.yaml
│   │      ├── ims-addresses.yaml 
│   │      ├── itemmaster.yaml
│   │      └── ...
│   ├── Feature1/
│   │      ├── feature1.yaml
│   │      ├── tsc-routes-feature1.yaml 
│   │      ├── ims-addresses-feature1.yaml
│   │      ├── ...
│   │      └── Feature1-1/
│   │           ├── feature1-1.yaml
│   │           ├── tsc-locations-feature1-1.yaml
│   │           ├── ims-addresses-feature1-1.yaml
│   │           └── ...
│   ├── Feature2/
│   │      ├── feature2.yaml
│   │      ├── tsc-config-items-feature2.yaml
│   │      └── itemmaster-feature2.yaml
│   └── ...   
├── schemas/                                            # Schemas to validate configuration files
│   ├── base_schema.json
│   ├── sleeping-areas.json
│   └── ...
├── tests/                                              # Test cases
│   ├── __init__.py
│   └── test_schema_validation.py                       # Tests for feature yaml validation
├── validators/                                         # Code for validating data files against schemas
│   ├── __init__.py
│   └── schema_validator.py
│
├── feature_mapping.json
│            
└── README.md
```

features_data - top folder for configs storage

**base** - folder for base configuration mapping and data of various base configurations. It provides a set of essential
settings or parameters that are common across all features or components of the system. The base config might not be
feature-specific but rather establishes the basic environment in which features can be enabled or disabled and specific
configurations can be layered on top of it.

**FeatureN folders** - each folder contains a yaml file with attributes and links for all required configurations.
Config files are stored in the same folder with expansion and/or override of the base config. When a feature is
activated or selected to be applied to the environment/for testing, its corresponding configurations will applied on top
the Base config. \
Features should contain a config mapping yaml file with links/values to needed configs. Files for each feature specific
configurations should be in format feature_name-config-type.yaml/json/txt whatever is applicable.

**feature_mapping.json** - a file that contains a mapping of features to their corresponding short names or tags. It
will help easily identify and select the appropriate feature. The json is in a tree-like format. (Possibility to build
it automatically from a features_data folder structure??)

**templates** - This directory holds templates for different types of configurations. These templates serve as a
starting point for creating specific configurations for each feature.

README.md: The file you're currently reading.

**schemas**
The schemas directory contains JSON schema files that define the expected structure for configuration data.
feature_schema.json: This schema validates the structure of individual feature files. \

These schemas ensure that the configuration data is correctly formatted and contains all the necessary fields. If you
wish to understand the specific requirements or modify them, you should refer to these schema files.

# Adding a New Feature and it's Configurations

To apply configurations to the environment, they must be included as data files. When a feature name is specified in the
relevant command,
the [env_setup_tool](https://github.com/takeoff-com/release-qualification-tools/tree/master/env_setup_tool)
will utilize the data from these files.

## Quick Start

1. Create a new folder `<feature_name>`. If it's a sub-feature/child feature create it as sub-folder of existing feature
2. Create a feature configs file ``<feature_name>/feature-<feature_name>.yaml``. <feature_name> should be **UNIQUE**!
3. Update the ``feature-<feature_name>.yaml``: add **_unique_** **key**, **title**, **description**
4. Add feature related configs into ``<feature_name>/`` folder
5. Update the ``feature-<feature_name>.yaml``: add paths to all relevant feature config files
6. Run validator
7. Commit your changes
8. Make sure CI passes
9. Run [env_setup_tool](https://github.com/takeoff-com/release-qualification-tools/tree/master/env_setup_tool) and tests
   to validate your configs
10. Create PR when ready

## Detailed Overview

### 1. Adding New Feature configs file

**Naming Convention**: Ensure that your feature configs file is named appropriately, starting with "feature", like
`feature-ISPS.yaml`. `<feature_name>` should be unique and not repeat in any other folder within the repo. \

**Format**: Adhere to the format defined in `schemas/feature-schema.json`. This is crucial for validation.
Use `templates/` as an example\

**Feature configs file properties and content**:

* key - required field. Should be unique field, match the feature_name, underscores if multi-word
* title - required field. Title of the feature, mostly to represent the Business feature
* description - required field. Business description of the feature
* configs - required field. Use `templates\feature.yaml` as an example.
* Each config type to be updated have to be specified in the Feature configs file in the correct format (
  use `templates/feature.yaml` as a full example):

````
configs:
  tsc:
    config_items:
      path: path_to_feature_specific_config_items_file
  sleeping_area_rules:
    path: path_to_feature_specific_sleeping_area_rules_file    
````

**Location**: Place your new feature configs file and all config files related to it in
the `features_data/<feature_name>/` directory.

## Configs and Data

**Best practices:**

* On the feature level, only configurations directly related to the specific feature should be added or modified. This
  implies that configurations should be updated only if they enable or alter the behavior of the respective feature.
* Feature configs file name have to follow the pattern `feature-<feature-name>.yaml`, <feature_name> have to be unique
* Configuration files can have any name. It is advised to name the file ``<config_name>-<feature-name>``
* Place feature related configs in the same folder with feature. It is possible though to re-use configs from other
  features by providing the path to the corresponding file (for example use 1 product catalog for various features on
  the same level)

### Data Integrity

> **⚠ IMPORTANT**  
> Ensure consistency of the data across configuration files. ***Example 1***: if configuration is added for a specific mfc and has
> a reference to it, make sure that such mfc is added as part of the current feature configuration data or on the parent
> feature level.  ***Example 2***: to add staging_config make sure routes and staging-locations are added as part of the current or parent feature

### Service Catalog (TSC)

Supported tsc configs:

* config-items
* flow-racks
* locations
* routes
* staging-config
* staging-locations
* tote-types

### Sleeping-area rules

Only sleeping-area rules from the Distiller are supported.

### Product Catalog

Only PCv6 is supported. There is no extra validation of the provided file. The file will be uploaded as is, except the
filename (please see below). All the validations are done as part of the processing of the file in the integration-etl
as in the regular file processing to any other environment. Make sure the `mfc-id` corresponds to existed location

As
per [documentation](https://support.takeoff.com/hc/en-us/articles/4414087539601-Common-Product-Catalog-Item-Master-v6-Overview-Format-Requirements)
the env_setup_tool will change the provided filename to "Takeoff_product_catalog_" and will add a timestamp at time of
upload

### IMS

Supported IMS configs:

* addresses
* reason-codes

Let us know if support for other config items is needed.

## Final Steps

* **Validation**: Before committing, validate your feature file and config files against schemas using the provided
  validators. This will help in catching any discrepancies or errors in the format. Usage:

````
python3 validators/schema_validation.py features_data/<feature_name>/<feature_name>.yaml
````

* **Commit**: Once validated, you can commit and push your changes. The CI pipeline will also validate the configuration
  files as a part of its process.

Remember, the structure and integrity of these feature files and config files are crucial for the application. Adhering
to the defined schemas ensures that the configurations will be correctly interpreted by
the [env_setup_tool](https://github.com/takeoff-com/release-qualification-tools/tree/master/env_setup_tool).

* **Test your configs**

> **⚠ IMPORTANT**  
> Use [env_setup_tool](https://github.com/takeoff-com/release-qualification-tools/tree/master/env_setup_tool)
> to apply your configuration from the branch to environment and run tests.

### Feedback

Feedback and PRs are welcome. Please reach out to `@team-chamaeleon` if you have any questions/issues/suggestions :) 
