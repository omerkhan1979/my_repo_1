Block RT deploys to a specific client and environment
==
[[Table of Contents](../../README.md#table-of-contents)] : [How to block deploys](./02-block-deploy-to.md)

## How to block RT deploys to a specific client and environment

Blocking an automated RT deploy to a client and environment allows us to omit them from automated Relese Train deployment processes. This is used, for example, in cases where a client is in a code-freeze period, or when we need to perform other deploys during the clients RT deploy window and so we need to be able to perform their RT deploy manually.

   1. Create a branch from `master`. 
   1. On your branch, navigate to ReleaseTrains > [current year] (e.g., 2023) > [release train] (e.g., RT44-23) > `block-deploy-to.yaml`
   1. Add `{client}-{env}` to the RT's `block-deploy-to.yaml` file (one per line).
      For example, if you wanted to block ALL deploys to Albertsons for a particular RT, you would add:
         `abs-qai`
         `abs-uat`
         `abs-prod`
   **NOTE**: the full list of client names are available in the `ALL_CLIENTS.yaml` at the root directory, except for `tienda` and`pinemelon`
   1. Create PR and push to `master`.
      
 ## To block RT deploys as part of an RT cut process

Once the RT Cut PR is generated, but _before_ merging, you can add the `{client}-{env}` to the RT's `block-deploy-to.yaml` file (one per line as above), and commit your changes to the RT branch. 
You may then continue with the rest of the RT cut process as described in [How to Perform an RT-Cut](https://github.com/takeoff-com/release-train-management/docs/how-to/00-perform-rt-cut.md).
