---
title: "Datalake PubSub Permissioning"
linkTitle: "Datalake PubSub Permissioning"
date: 2022-08-30
weight: 9
description: >
  Assigning your application access to Datalake PubSub
---

## Multi-Tenant project configuration

A multi-tenant project is first configured in the `tf-tg-live` repo. [Here](https://github.com/takeoff-com/tf-tg-live/blob/master/org-gcp/nonprod/shared-services/tkf-assortment-management-nonprod/terragrunt.hcl) is an example of a nonprod multi-tenant service configuration.


Please validate that the terraform module `tf-delegated-service-project-module` is using v0.2.5 or higher. You can see the implementation [here](https://github.com/takeoff-com/tf-tg-live/blob/master/org-gcp/nonprod/shared-services/tkf-assortment-management-nonprod/terragrunt.hcl#L52)
```hcl
terraform {
  source = "git@github.com:takeoff-com/tf-delegated-service-project-module.git//modules/tg-root?ref=v0.2.5"
}
```

To allow your service account to get access to publish to the datalake pub sub topics you must define a delegate role grant `roles/pubsub.publisher`. An example of this can be found [here](https://github.com/takeoff-com/tf-tg-live/blob/master/org-gcp/nonprod/shared-services/tkf-assortment-management-nonprod/terragrunt.hcl#L37).
```hcl
delegated_role_grants = ["roles/pubsub.publisher"]
```

## Application configuration
The application being deployed in this multi-tenant service project must be granted the correct permissions in terraform. After creating the service account used by your cloud function, cloud run or app engine add it as a iam member with the following terraform configuration. Where `var.big_query_pub_sub_project_id` is the datalake pub sub GCP project ID.
```hcl
resource "google_project_iam_member" "pub_sub_default" {
  project = var.big_query_pub_sub_project_id
  role    = "roles/pubsub.publisher"
  member  = "serviceAccount:${google_service_account.default.email}"
}
```
You can see an example of creating a service account with datalake pubsub permissions [here](https://github.com/takeoff-com/assortment-management/blob/master/ops/terraform/modules/service_account/main.tf).

