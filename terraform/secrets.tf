resource "google_service_account" "gce_service_account" {
  account_id   = "${var.resource_prefix}-gce-sa"
}
resource "random_password" "db_password" {
  length  = 16
  special = true
}
resource "google_secret_manager_secret" "db_user" {
  secret_id = "source-db-user"
  replication { automatic = true }
}
resource "google_secret_manager_secret_version" "db_user_version" {
  secret      = google_secret_manager_secret.db_user.id
  secret_data = "migration_user"
}
resource "google_secret_manager_secret" "db_password" {
  secret_id = "source-db-password"
  replication { automatic = true }
}
resource "google_secret_manager_secret_version" "db_password_version" {
  secret      = google_secret_manager_secret.db_password.id
  secret_data = random_password.db_password.result
}
resource "google_secret_manager_secret" "source_db_host" {
  secret_id = "source-db-host-internal"
  replication { automatic = true }
}
resource "google_secret_manager_secret" "gemini_api_key" {
  secret_id = "gemini-api-key"
  replication { automatic = true }
}
resource "google_secret_manager_secret_iam_member" "secret_access" {
  for_each  = toset([google_secret_manager_secret.db_user.secret_id, google_secret_manager_secret.db_password.secret_id, google_secret_manager_secret.source_db_host.secret_id])
  secret_id = each.key
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.gce_service_account.email}"
}
data "google_project" "project" {}
resource "google_project_iam_member" "dms_service_agent_role" {
  project = var.gcp_project_id
  role    = "roles/datamigration.serviceAgent"
  member  = "serviceAccount:service-${data.google_project.project.number}@gcp-sa-datamigration.iam.gserviceaccount.com"
}
