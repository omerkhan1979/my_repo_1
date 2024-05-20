
########################## The basics ################################
provider "google" {
  project = var.project_id
  region  = var.provider_region
}

provider "google-beta" {
  project = var.project_id
  region  = var.provider_region
}
########################## APIs ################################
resource "google_project_service" "default" {
  for_each           = toset(var.google_apis)
  provider           = google
  service            = each.value
  disable_on_destroy = false
}

########################## The rest ################################
module "load_balancer" {
  source                     = "../modules/load_balancer"
  static_content_bucket_name = var.static_content_bucket_name
  managed_domain             = var.managed_domain
  depends_on = [
    google_project_service.default
  ]
}
