resource "google_sql_database_instance" "target_instance" {
  name                 = "${var.resource_prefix}-cloudsql-instance"
  database_version     = "MYSQL_8_0"
  region               = var.gcp_region
  deletion_protection  = false
  settings {
    tier = "db-n1-standard-2"
    ip_configuration {
      ipv4_enabled    = false
      private_network = google_compute_network.vpc_network.id
    }
  }
  depends_on = [google_service_networking_connection.private_vpc_connection]
}
