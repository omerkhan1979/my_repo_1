resource "google_compute_global_address" "default" {
  name         = var.name
  address_type = "EXTERNAL"
  ip_version   = "IPV4"
}

resource "google_dns_record_set" "default" {
  project      = var.dns_project_id
  managed_zone = var.managed_zone
  name         = "${var.managed_domain}."
  type         = "A"
  rrdatas      = [google_compute_global_address.default.address]
  ttl          = 300
}

resource "google_compute_backend_bucket" "default" {
  name        = var.name
  description = "Static content for engineering handbook"
  bucket_name = var.static_content_bucket_name
  enable_cdn  = true
}

resource "google_compute_url_map" "default" {
  name = var.name

  default_service = google_compute_backend_bucket.default.id
}

resource "random_id" "certificate" {
  byte_length = 4
  prefix      = "-"

  keepers = {
    domain = var.managed_domain
  }
}

resource "google_compute_managed_ssl_certificate" "default" {
  name = random_id.certificate.hex

  managed {
    domains = ["${var.managed_domain}."]
  }

  lifecycle {
    create_before_destroy = true
  }
}

resource "google_compute_target_https_proxy" "default" {
  name             = var.name
  url_map          = google_compute_url_map.default.id
  ssl_certificates = [google_compute_managed_ssl_certificate.default.id]
}

resource "google_compute_global_forwarding_rule" "default" {
  name       = var.name
  target     = google_compute_target_https_proxy.default.id
  port_range = "80-80"
  ip_address = google_compute_global_address.default.id
}

resource "google_compute_url_map" "https_redirect" {
  name = "${var.name}-https-redirect"

  default_url_redirect {
    https_redirect         = false
    redirect_response_code = "MOVED_PERMANENTLY_DEFAULT"
    strip_query            = false
  }
}

resource "google_compute_target_http_proxy" "https_redirect" {
  name    = var.name
  url_map = google_compute_url_map.https_redirect.id
}

resource "google_compute_global_forwarding_rule" "https_redirect" {
  name       = "${var.name}-https-redirect"
  target     = google_compute_target_http_proxy.https_redirect.id
  port_range = "80"
  ip_address = google_compute_global_address.default.id
}
