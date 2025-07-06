resource "google_storage_bucket" "migration_bucket" {
  name                        = "${var.resource_prefix}-mig-bucket-${random_id.bucket_suffix.hex}"
  location                    = var.gcp_region
  force_destroy               = true
  uniform_bucket_level_access = true
}
resource "random_id" "bucket_suffix" {
  byte_length = 4
}
