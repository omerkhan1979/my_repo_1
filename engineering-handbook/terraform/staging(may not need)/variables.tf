variable "project_id" {
  type = string
}

variable "provider_region" {
  type    = string
  default = "us-central1"
}

variable "static_content_bucket_name" {
  type = string
}

variable "google_apis" {
  type = list(string)
  default = [
    "servicemanagement.googleapis.com",
    "servicecontrol.googleapis.com",
    "iam.googleapis.com",
    "dns.googleapis.com",
    "cloudresourcemanager.googleapis.com",
    "cloudfunctions.googleapis.com",
    "cloudbuild.googleapis.com",
  ]
}

variable "managed_domain" {
  type = string
}
