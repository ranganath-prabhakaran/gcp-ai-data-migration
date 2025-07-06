from google.cloud import secretmanager

def get_gcp_secret(project_id: str, secret_id: str, version_id: str = "latest") -> str:
    """Retrieves a secret's payload from Google Cloud Secret Manager."""
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")