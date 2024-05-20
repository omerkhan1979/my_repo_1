terraform {
  backend "gcs" {
    bucket = "prj-release-qual-tools-2c2c-state"
  }
}