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

variable "managed_domain" {
  type = string
}
