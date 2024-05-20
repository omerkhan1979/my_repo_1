Interactive Test Scripts
==
[[Table of Contents](../README.md#table-of-contents)] : [Getting Started](../../getting-started/00-getting-started.md)

This repo includes a set of interactive Python test scripts.
To run the script, use command `python3 -m scripts.script_name` (without `.py` !!!) from the project root.

## Arguments

Most of the scripts by default support 4 arguments:
 - `retailer`: retailer-codename, e.g. `winter`, `wings`, etc, NOT real brand names like "wakefern"
 - `env`: env type, e.g. `dev`, `qai`
 - `location-code-tom`: location-id of the MFC, against which the script is executed. To check available locations for particular retailer and env, run `python3 -m scripts.locations retailer env`
 - `user-role (--ur)` : User role with which you want to execute a test. A new user will be created and assigned with the role you mentioned e.g. `mfc-manager, operator, admin, retailer,scf-manager,supervisor,viewer`
    default role is 'operator'
 
**Arguments must be passed in the appropriate order after script name in the command. For example:**

```
python3 -m scripts.script_name retailer env location-code user-role
```

Some of the scripts support additional optional arguments, including:

- ```user``` (used to obtain Bearer token from Google API for Firestore)
- ```password``` (used to obtain Bearer token from Google API for Firestore)
- ```-p tom_id_1 tom_id_2 ... tom_id_n``` (tom_ids for custom products in orderflow.py script)

## Scripts

### clear_picking_queue

This script does not test anything. It is used for clearing manual picking queues. 

### inbound_flow

Tests inbound flows, including PO processing with various types of products, Decanting, and Putaway processes. 

### product_catalog_upload

Tests Product Catalog upload for retailers that use Cloud Storage Buckets, or SFTP. 

### locations

This script does not test anything. It gets mfc location IDs from config.

### mod71_itemmaster_upload

Tests Product Catalog upload on environments that have [MOD71]([url](https://takeofftech.atlassian.net/wiki/spaces/PD/pages/3632431110/Testing+MOD71+functionality+in+OSR+emulator)) functionality enabled.

### orderflow

Tests one or more combinations of order flows, including OSR and FLO, including Manual, etc. If you do not have an Android device for using Takeoff Mobile to complete manual orders, this script also has a provision to perform those tests using API calls instead. You can also test truck load and express orders with this script. 

To run: `python3 -m scripts.orderflow --r [retailer] --e [env] --l [location-code-tom]`, for example:

```
python3 -m scripts.orderflow --r abs --e qai --l 0068
```

You can also run the orderflow script with custom tom-ids. They will be checked for validity and treated accordingly in order flow - if they are FLO items, stock will be cleared and dynamic addesses for putaway will be suggested, if they are weighted - weight value will be inserted into the barcode, etc.

To insert custom tom ids, add `p` argument and your tom-ids separated by space:

```
python3 -m scripts.orderflow abs qai 0068 p tom-id1 tom-id2
```
### organic_split

Creates a set of three orders with a `service_window_start` and `stage_by_datetime` in the near future so that organic split functionality can be tested (by checking if the orders split at the expected date/time). 
