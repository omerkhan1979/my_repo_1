terraform {
  backend "gcs" {
    bucket = "site-bucket-takeoffhandbook"
    prefix = "main"
  }
}
