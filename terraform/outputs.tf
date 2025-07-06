output "mcp_instance_public_ip" {
  description = "The public IP address of the MCP server instance."
  value       = google_compute_instance.mcp_instance.network_interface[0].access_config[0].nat_ip
}
output "source_db_private_ip" {
  description = "The private IP address of the source database server instance."
  value       = google_compute_instance.source_db_server.network_interface[0].network_ip
}
output "cloud_sql_instance_name" {
  description = "The name of the Cloud SQL instance."
  value       = google_sql_database_instance.target_instance.name
}
output "migration_gcs_bucket" {
  description = "The name of the GCS bucket for staging migration files."
  value       = google_storage_bucket.migration_bucket.name
}
