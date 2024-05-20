Copy Config
==
[[Table of Contents](../README.md#table-of-contents)]

Use this feature to make a target environment configuration to be as much like a source environment configuration as much as possible. 

## Summary

The application provides a means to update the service catalog of a target environment's specific location or a list of
locations if one's provides them otherwise the applications uses a known enabled default location with the selected
client and their environment. If one of the selected locations on the target evironment does not exist the application
will create the location and perform the necessary operations to get it ready to continue with the remainder of the
process. The `prod` environment cannot be the target environment, but the others are fair game.
<p>
The main reason behind this project was to support on-demand-env as the
replacement for `qai` as a more cost-effective means for testing, etc. The
application provides a means to get on-demand-env as close as possible to the
service catalog content of a `prod` or `uat` environment. Certain items like
osr ftp passwords, osr ftp usernames, slack channels, obselete config items 
with not be copied. For newly created environment a default staging profile
will be applied and then specific NON Production FTP configuration will be 
used. This gets `bifrost` and the `osr_emulator` up and running.
<p>
Currently the configuration items that do fail to be updated causes the
process to stop and an error to caller mechanism is generated. 
<p>
We have an open request 
[Rollback on Failure](https://takeofftech.atlassian.net/browse/PROD-9746) to
address that situation a little bit better. If updates are successful, the 
application triggers the sync of locations again. 
<p>
Finally, a sanity check is performed to confirm that the intended changes 
indeed took place.

## Workflow

See [Copy Config Workflow](https://lucid.app/lucidchart/2a8f48f4-ce09-40d0-8dce-fa381e8fc3ff/edit?invitationId=inv_8cb1f56b-d740-4c86-af12-f16b1f2c1ca7)
If access denied, send a message in [Takeoff Slack](https://takeofftech.slack.com/)
to `#team-chamaeleon-private`

### Procedure

1. Parses the cli for the options
    - Available commands: pull_from_prod, copy_config
    - Client/Retailer Source and Target needs to be the same
    - Target environment cannot be Production
    - Checks if preview was enabled
2. Retrieves the following from source environment
    - config items per environment and selected location(s)
    - tote types
    - staging configuration
    - staging locations
    - routes
    - locations/spokes
3. Filters out config items that should remain unique
4. If command == pull_from_prod
    - Saves config items into yaml and finishes execution
5. Preview is requested
    - Output of the filtered values would be printed to the console and exits
6. Preview is NOT requested the flow continues
7. Location/Spokes are created/updated
8. If a location and/or a spoke is created service Sync request is sent
9. Filtered config items are put on the target
10. Update all the non standard tsc on target's selected location(s):
    - flow_racks,
    - tote_types
    - staging_config
    - staging_locations
    - routes
11. Perform sanity check
12. Report results to console

## Execution

- Use Actions of the
  GitHub [Copy Config Action](https://github.com/takeoff-com/release-qualification-tools/actions/workflows/copy_config.yml)
- Execute the python script directly with the proper options
- Uses `shared_token` for token to communicate with environments

### Options

```
poetry run python3 src/copy_config/main.py copy_config -r RETAILER --source {env}
          --target {env} --locations {location}...
          --preview ${{ github.event.inputs.preview }}
          --ode_prj {ode_proj_name}
```

    1. Command: `copy_config` or pull_from_prod`
    2. Retailer to mimic configs from
       - Required
       - Use `-r or `--retailer`
       - Example `abs`  

    3. Source environment to copy configs from
        - Required
        - Use `-s` or `--source_env`
        - Argument should be in this format - `{env}`
        - Example `prod` or `file`
    
    4. Path to file to copy configs from. Should be used for custom configs. If not provided script will look for 
    retailer-location.yaml file. File should be checked in the [environment-configs](https://github.com/takeoff-com/environment-configs) 
    repository 
        - Optional
        - Use `--path`
        - argument should be in the format `service-catalog-configs/retailer/retailer-location.yaml`
        - Example `service-catalog-configs/abs/abs-test001.yaml`
    
    5. Target environment to copy configs to
        - Required
        - Use `-t` or `--target_env`
        - Argument should be in this format - `{env}`
        - Example `qai` or `ode`

    6. Location
        - Not Required
        - Use `-l` or `--locations`
        - Argument should be in this format - `{location1} {location2}`
        - Example 9999 1234 or 9999
        - If location is not provided the default location for client is used.
    
    7. ODE Project
        - Required only if ODE env selected
        - Use `-ode` or `--ode_project_name`
        - Argument should be the unique name given when the ODE ENV was created 
        - Example schaves-maf

    8. Preview
        - Optional
        - Use `-p` or `--preview`
        - Allow to preview the changes before they happen otherwise update.

Example of the command to copy configs from abs prod to ode env for location 0068:

```
 poetry run python3 src/copy_config/main.py copy_config --retailer abs -s prod -t ode --ode_project_name prj-oz05-retailer-gke-d5aa --locations 0068
```

## Limitations

- SKIPPING updating Flowracks as their is an open \
  [Manual Picking / Flow Rack Bug ](https://takeofftech.atlassian.net/browse/OUTBOUND-4755) waiting for deployment.

## Reference

See [Copy Config Jira Epic Link](https://takeofftech.atlassian.net/browse/PROD-4812)