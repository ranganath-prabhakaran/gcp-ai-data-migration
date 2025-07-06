resource "google_compute_network" "vpc_network" {
  name                    = "${var.resource_prefix}-vpc"
  auto_create_subnetworks = false
}
resource "google_compute_subnetwork" "vpc_subnet" {
  name          = "${var.resource_prefix}-subnet"
  ip_cidr_range = "10.10.0.0/24"
  region        = var.gcp_region
  network       = google_compute_network.vpc_network.id
}
resource "google_service_networking_connection" "private_vpc_connection" {
  network                 = google_compute_network.vpc_network.id
  service                 = "servicenetworking.googleapis.com"
  reserved_peering_ranges = [google_compute_global_address.private_ip_address.name]
}
resource "google_compute_global_address" "private_ip_address" {
  name          = "private-ip-for-google-services"
  purpose       = "VPC_PEERING"
  address_type  = "INTERNAL"
  prefix_length = 16
  network       = google_compute_network.vpc_network.id
}
resource "google_compute_firewall" "allow_internal" {
  name    = "${var.resource_prefix}-allow-internal"
  network = google_compute_network.vpc_network.name
  allow { protocol = "all" }
  source_ranges = [google_compute_subnetwork.vpc_subnet.ip_cidr_range]
}
resource "google_compute_firewall" "allow_ssh_iap" {
  name    = "${var.resource_prefix}-allow-ssh-iap"
  network = google_compute_network.vpc_network.name
  allow { protocol = "tcp"; ports = ["22"] }
  source_ranges = ["35.235.240.0/20"]
}
resource "google_compute_firewall" "allow_mcp_public" {
  name    = "${var.resource_prefix}-allow-mcp-public"
  network = google_compute_network.vpc_network.name
  allow { protocol = "tcp"; ports = ["8000"] }
  source_ranges = ["0.0.0.0/0"]
}
