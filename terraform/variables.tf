variable "gcp_project_id" {
  description = "The GCP project ID to deploy resources into."
  type        = string
}
variable "gcp_region" {
  description = "The GCP region for resources."
  type        = string
  default     = "us-central1"
}
variable "gcp_zone" {
  description = "The GCP zone for resources like the GCE instance."
  type        = string
  default     = "us-central1-a"
}
variable "resource_prefix" {
  description = "A prefix for all created resources."
  type        = string
  default     = "rangie-mig"
}
variable "git_repo_url" {
  description = "The URL of the git repository to clone on the GCE instance."
  type        = string
  default     = "https://github.com/your-username/your-repo-name.git"
}
