---
title: "Integrating a Micro frontend with TomUI"
date: 2021-12-28
type: docs
tags: ["how-to"]
weight: 8
---

Historically, TomUI has been developed as a Single Page Application (SPA), and all of its menu items and distinct pieces of functionality have been added to a single repository. As the app grew in functionality, many components have been added and its manageabilty has decreased.

In an effort to make our UI development more dynamic and manageable, Takeoff adopted the Micro frontend (MFE) pattern for TomUI. In this model, components can be developed independently, live in their own repositories, and be deployed separately.

This document aims to describe the high level process on how to integrate a new MFE with TomUI.

### Developing an MFE

The first step in developing an MFE for TomUI is to create a new repository from the [MFE Template repo](https://github.com/takeoff-com/mfe-template-repo). Instructions for how to use the template are in the template's [README](https://github.com/takeoff-com/mfe-template-repo/blob/master/README.md).

This template will provide:

- Access to `core-ui`, the Takeoff UI library. This will give you access to a set of components and a style library.
- Pre-configured pipelines for continuous integration and delivery. These pipelines will ensure that the MFE is deployed to a Google Cloud bucket at the pull request and merge to master stages.
- An integration library (`mfe-common`) that will provide the integration between the container (TomUI) and the deployed MFE.
- An example page that you can use as a baseline for your MFE.

### CI/CD

At the pull request and merge to master stages of the source control cycle, a Github Actions pipeline deploys the MFE to a Google Cloud bucket.

- Pull requests and master merges are deployed to the [staging bucket](https://console.cloud.google.com/storage/browser/takeoff-micro-frontends-staging;tab=objects?forceOnBucketsSortingFiltering=false&project=tkf-mfe-staging-0791&prefix=&forceOnObjectsSortingFiltering=false)
- Master merges are also deployed to the [prod bucket](https://console.cloud.google.com/storage/browser/takeoff-micro-frontends;tab=objects?forceOnBucketsSortingFiltering=false&project=tkf-mfe-ce42&prefix=&forceOnObjectsSortingFiltering=false)

The contents of the Google Cloud bucket are behind a Content Delivery Network (CDN), making the buckets highly available regardless of the location of the client.

For each commit to an open pull request, the pipeline will create a version with the format `PR[PR-NUMBER].[RUN-NUMBER]` (for example, `PR45.2`)

When a pull request is merged to master, the pipeline will create a version with the format `[YY-MM-DD].[RUN-NUMBER]` (for example, `21-12-29.5`).  Also, the `latest` version in the prod bucket will be updated match the new version's contents.

### Versioning and remote configuration

TomUI and the MFE environment provide a remote configuration feature that can be used to quickly enable/disable a MFE, and to define the version that will be used in TomUI. This feature is useful for supporting rollout processes, as well as to help testing out different versions of the MFE during the development cycle.

The configuration can be found at:

- [TKF MFE Staging](https://console.firebase.google.com/u/0/project/tkf-mfe-staging-0791/config)
- [TKF MFE Prod](https://console.firebase.google.com/u/0/project/tkf-mfe-ce42/config)

Each MFE should have its own configuration value, and should match the name in TomUI.

The value is a JSON file that has this structure:

```json
{
    "version": "latest",
    "clients": {
        "abs": {
            "disabled": true
        }
    },
    "environment-types": {
        "dev": {
            "disabled": true
        },
        "uat": {
            "clients": {
                "tangerine": {
                    "version": "PR5.41"
                },
                "maf": {
                    "version": "PR5.41"
                },
                "sunbird": {
                    "disabled": true
                }
            }
        }
    }
}
```

This JSON file allows you to implement the following rules:

- Disable the MFE for a specific environment, retailer, or combination of retailer + environment

    ```json
    {
        "environment-types": {
            "dev": {
                "disabled": true
            },
            "uat": {
                "clients": {
                    "sunbird": {
                        "disabled": true
                    }
                }
            }
        },
        "clients": {
            "abs": {
                "disabled": true
            }
        }
    }
    ```

- Set a version for retailers, environments, or retailers + environments

    ```json
    {
        "clients": {
            "abs": {
                "version": "21-11-05.22"
            }
        },
        "environment-types": {
            "uat": {
                "clients": {
                    "tangerine": {
                        "version": "PR5.41"
                    },
                    "maf": {
                        "version": "PR5.41"
                    }
                }
            }
        }
    }
    ```

- Set a global version for all retailers

    ```json
    {
        "version": "21-11-05.22"
    }
    ```

For more information about how these rules are applied in TomUI, see [`tomui.micro-frontends.utils`](https://github.com/takeoff-com/Platform/blob/master/TomUI/src/cljs/tomui/micro_frontends/utils.cljs)

### Integrating with TomUI

To integrate an MFE with TomUI as an element in the TomUI Menu, [tomui.configuration](https://github.com/takeoff-com/Platform/blob/master/TomUI/src/cljs/tomui/configuration.cljs) needs to be modified. For example:

```clojure
 :shelf-address {:title       (_t "t_shelf_address_management_title")
                 :sub-title   (_t "t_shelf_address_management")
                 :menu-string (_t "menu_shelf_address_management")
                 :sort        9
                 :icon        "fork"
                 :roles       roles/shelf-address-roles
                 :component   (micro-frontends/Page {:mfe-name   "shelf-address"
                                                     :version-fn #(micro-frontends-utils/version-from-remote-config :mfe-shelf-address "latest")
                                                     :window-add {"MFE_SHELF_ADDRESS_PARAMS" {"locationId" (storage/current-user-location!)}}})
                 :enabled-fn  #(micro-frontends-utils/enabled-from-remote-config? :mfe-shelf-address)}
```

In this example, the `micro-frontends/Page` component will provide all the elements required to integrate the MFE. This will allow TomUI to dynamically download the required files from the Google Cloud bucket and load them onto the page.

`version-fn` sets the version that is configured, using `micro-frontends-utils/version-from-remote-config` to extract the appropriate version for the current retailer + environment from the remote configuration JSON.

`window-add` will allow you to pass parameters or contextual variables from TomUI to the MFE.

`enabled-fn` uses `micro-frontends-utils/enabled-from-remote-config?` to determine if the MFE is enabled for the current retailer + environment based on the remote configuration JSON.
