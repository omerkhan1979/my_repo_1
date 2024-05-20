resource "google_cloud_run_service" "cloudruntfk" {
  provider = google-beta
  name     = "cloudrun-img"
  location = var.region
  template {
    spec {
      containers {
        image = var.imagename
      }
    }
  }
  traffic {
    percent = 100
    latest_revision = true
  }
}

resource "google_cloud_run_service_iam_policy" "run_all_users" {
  location = google_cloud_run_service.cloudruntf.location
  project = google_cloud_run_service.cloudruntf.project
  service  = google_cloud_run_service.cloudruntf.name
  policy_data = data.google_iam_policy.noauth.policy_data
}

data "google_iam_policy" "noauth" {
  binding {
    role = "roles/run.invoker"
    members = [
      "allUsers",
    ]
  }
}