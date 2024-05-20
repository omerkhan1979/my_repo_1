terraform {
  backend "gcs" {
    bucket = "tf-tkf-mfe-staging"
    prefix = "staging"
  }
}
