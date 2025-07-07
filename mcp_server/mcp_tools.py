import subprocess
import os
from sqlalchemy import create_engine, text
from utils.gcp_secrets import get_gcp_secret

def _get_db_engine(project_id: str):
    """Creates a SQLAlchemy engine by fetching secrets directly from Secret Manager."""
    user = get_gcp_secret(project_id, "source-db-user")
    password = get_gcp_secret(project_id, "source-db-password")
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

def _run_script(script_path, command_args, project_id):
    """Helper to run a script with credentials injected as environment variables."""
    # Create a copy of the current environment
    env = os.environ.copy()
    
    # Securely fetch secrets and add them to the script's environment
    env["SOURCE_DB_USER"] = get_gcp_secret(project_id, "source-db-user")
    env["SOURCE_DB_PASSWORD"] = get_gcp_secret(project_id, "source-db-password")
    env["SOURCE_DB_HOST"] = get_gcp_secret(project_id, "source-db-host-internal")

    command = ["bash", script_path] + command_args
    result = subprocess.run(command, check=True, capture_output=True, text=True, env=env)
    return f"SUCCESS: Script '{script_path}' output:\n{result.stdout}"

def run_gcs_import_workflow(db_name, gcs_bucket, instance_name, project_id):
    """Executes the GCS Import migration by calling the bash script with a secure env."""
    try:
        args = [db_name, gcs_bucket, instance_name, project_id]
        return _run_script("scripts/gcs_import_workflow.sh", args, project_id)
    except subprocess.CalledProcessError as e:
        return f"ERROR during GCS import script execution: {e.stderr}"

def run_dms_workflow(db_name: str, project_id: str, region: str, source_db_ip: str, cloud_sql_instance_id: str):
    """Executes the DMS workflow by calling the bash script."""
    try:
        args = [db_name, project_id, region, source_db_ip, cloud_sql_instance_id]
        # DMS script doesn't need DB credentials directly, as it uses connection profiles
        # that reference secrets, but we'll use the same helper for consistency if needed.
        script_path = "scripts/dms_workflow.sh"
        command = ["bash", script_path] + args
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        return f"SUCCESS: DMS workflow script output:\n{result.stdout}"
    except subprocess.CalledProcessError as e:
        return f"ERROR during DMS script execution: {e.stderr}"