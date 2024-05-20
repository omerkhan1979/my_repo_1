The Environment Configurations Repository is a repo designed to store default configuration items that are applied when
building a fresh on-demand environment. Its primary purpose is to provide a centralized location for managing and
retrieving default configurations for fresh ODE for further development and testing.

## Why?

_Centralized Storage_: This Repository serves as a centralized storage location for default configuration items. It's
intended use is to support development and testing on the ODE environment by applying default configs per retailer. We
hope in the future this tool can be used to accelerate the spin up of new environments for customers. <br />
_Version Control_: The repository supports version control, enabling tracking of changes made to configurations over
time. <br />
_Configurations Separation_: The tool clearly distinguishes configurations stored in the repository. <br />
_Easy Retrieval_: Users can easily access and retrieve default configurations when building new on-demand environments
with the help of tools in RQT. <br />
_Flexibility_: The tool is designed to be adaptable and can accommodate different types of configurations. <br />

### Service Catalog configs (leveraged by copy-config tool)

The following config items are supported in the tool and will be copied to the env:

* mfc level config-items
* env level config-items
* location configs
* staging locations
* routes
* flow racks
* tote types
* spokes
* addresses
* fulfillment profiles

Some of the environment specific items are intentionally filtered out before execution

## Repository Structure

environment-configs Repository follows a structured layout to ensure ease of use and organization. Here's an overview of
the repository structure:

```
environment-configs/
├── service-catalog-configs/
│   ├── retailer1/
│   │   ├── mfc1-config.yaml
│   │   ├── mfc2-config.yaml
│   │   └── ...
│   ├─── retailer2
│   │    ├── mfc1-config.yaml
│   │    ├── mfc2-config.yaml
│   │    └── ...
│   └── ...
└── README.md
```

environment-configs/config/: The directory where all applicable service catalog configuration items are stored.
environment-configs/service-catalog-configs/retailerX/: Individual directories per retailer per mfc.
environment-configs/service-catalog-configs/retailerX/mfcX.yaml: Current prod configuration files for specific mfc.
README.md: The file you're currently reading.

## Feature configs

As we move towards feature testing a
new [env_setup_tool](https://github.com/takeoff-com/release-qualification-tools/tree/master/env_setup_tool) was created
and will use a new approach of setting configurations per feature. Please
see [features_data folder](features_data/README.md)