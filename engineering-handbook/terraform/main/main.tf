########################## The basics ################################
provider "google" {
  project = var.project_id
  region  = var.provider_region
}

provider "google-beta" {
  project = var.project_id
  region  = var.provider_region
}

########################## storage bucket ################################

resource "google_storage_bucket" "takeoffhandbook" {
  location                    = "US-EAST1"
  name                        = "site-bucket-takeoffhandbook"
  project                     = "roi-takeoff-user96"
  uniform_bucket_level_access = "true"

  website {
    main_page_suffix = "index.html"
    not_found_page   = "404.html"
  }
}

resource "google_storage_bucket_iam_binding" "binding" {
  bucket = "b/site-bucket-takeoffhandbook"
  role = "roles/storage.objectViewer"
  members = [
    "allUsers"
  ]
}

########################## load balancer ################################
module "load_balancer" {
  source                     = "./modules/load_balancer"
  static_content_bucket_name = var.static_content_bucket_name
  managed_domain             = var.managed_domain
}