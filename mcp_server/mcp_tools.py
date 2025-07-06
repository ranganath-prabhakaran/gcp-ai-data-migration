import subprocess
from sqlalchemy import create_engine, text
from utils.gcp_secrets import get_gcp_secret

def _get_db_engine(project_id: str):
    """Creates a SQLAlchemy engine by fetching secrets directly from Secret Manager."""
    user = get_gcp_secret(project_id, "source-db-user")
    password = get_gcp_secret(project_id, "source-db-password")
    # This secret is created by Terraform with the private IP of the source DB server
    host = get_gcp_secret(project_id, "source-db-host-internal") 
    
    if not all([user, password, host]):
        raise ValueError("Could not fetch all required DB secrets from Secret Manager.")
    return create_engine(f"mysql+pymysql://{user}:{password}@{host}/")

def get_db_metadata(db_name: str, project_id: str) -> dict:
    """Connects to the source DB and retrieves its size."""
    try:
        engine = _get_db_engine(project_id)
        with engine.connect() as connection:
            query = text("SELECT table_schema, SUM(data_length + index_length) / 1024 / 1024 / 1024 AS size_gb FROM information_schema.TABLES WHERE table_schema = :db_name GROUP BY table_schema;")
            result = connection.execute(query, {'db_name': db_name}).fetchone()
            if result:
                return {"database": db_name, "size_gb": float(result.size_gb)}
            return {"database": db_name, "size_gb": 0}
    except Exception as e:
        return {"error": str(e)}

def run_gcs_import_workflow(db_name, gcs_bucket, instance_name, project_id):
    """Executes the GCS Import migration by calling the bash script."""
    try:
        script_path = "scripts/gcs_import_workflow.sh"
        command = ["bash", script_path, db_name, gcs_bucket, instance_name, project_id]
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        return f"SUCCESS: GCS import workflow script output:\n{result.stdout}"
    except subprocess.CalledProcessError as e:
        return f"ERROR during GCS import script execution: {e.stderr}"

def run_dms_workflow(db_name: str, project_id: str, region: str, source_db_ip: str, cloud_sql_instance_id: str):
    """Executes the DMS workflow by calling the bash script."""
    try:
        script_path = "scripts/dms_workflow.sh"
        command = ["bash", script_path, db_name, project_id, region, source_db_ip, cloud_sql_instance_id]
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        return f"SUCCESS: DMS workflow script output:\n{result.stdout}"
    except subprocess.CalledProcessError as e:
        return f"ERROR during DMS script execution: {e.stderr}"
