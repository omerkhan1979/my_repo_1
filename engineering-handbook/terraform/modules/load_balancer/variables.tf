variable "name" {
  type    = string
  default = "engineering-handbook-lb-forwarding-rule"
}

variable "static_content_bucket_name" {
  type = string
  default = "site-bucket-takeoffhandbook"
}

variable "dns_project_id" {
  type    = string
  default = "dan.finn@takeoff.com"
}

variable "managed_zone" {
  type    = string
  default = "engineering-handbook"
}

variable "managed_domain" {
  type = string
  default="engineering-handbook.takeofftech.org"
}
