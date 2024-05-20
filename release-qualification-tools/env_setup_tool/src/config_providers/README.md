[Back to env-setup tool main documentation](../../README.md)

## Sleeping Area Rules

Update sleeping area rules using the Distiller REST API.

## TSC (Service-Catalog configurations)

Update environment configuration using Service Catalog REST Api.

### Supported service catalog configs

* config_items
* flow_racks
* spokes
* tote_types
* staging_config
* staging_locations
* routes
* locations

### Staging-locations

Only 1 default location can be POSTed on the environment. The tool does not validate provided data to follow this rule.
If multiple `default=true` locations are specified,they will be POSTed one by one overriding each other

## Product Catalog

Uploads provided Product Catalog. Only PCv6 is supported. Tool will re-name provided file to
match [PCv6 file requirements](https://support.takeoff.com/hc/en-us/articles/4414087539601-Common-Product-Catalog-Item-Master-v6-Overview-Format-Requirements) "
Takeoff_product_catalog_"+<YYYYmmddHHMMSS>+"

### Assumptions

The data in the [environment-configs](https://github.com/takeoff-com/environment-configs/tree/master) repository is
assumed to be valid and ready for immediate upload into the environment.

### Functionality

**Data Upload**: The tool reads the provided configuration file, appends a timestamp to the title, and uploads the file
into the designated integration-etl GCP bucket.\
**Operation Validation**: The success of the upload operation is verified by checking the change in the `revision-max`
value in the Distiller.

### Current Support

**Supported Product Catalogs**: The tool supports only PCv6 product catalog.\
**Environment Compatibility**: These catalogs can be uploaded to any environment, assuming the correct schema is
present. As of the current version, all required schemas are available in every ODE.

### Limitations

Custom ABS Product Catalog: The tool does not support the custom ABS product catalog, which requires an encryption
mechanism. This functionality is currently outside the scope of the env-setup tool. However, the relevant testing for
this feature is available in the RQT suite.
