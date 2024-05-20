resource "google_storage_bucket" "rq_service_bucket" {
  name                        = "prj-release-qual-tools-2c2c-state"
  location                    =var.region
  uniform_bucket_level_access = true
  public_access_prevention    = "enforced"
  cors {
    origin          = ["*"]
    method          = ["GET"]
    max_age_seconds = 3600
  }
  versioning {
    enabled = false
  }
}