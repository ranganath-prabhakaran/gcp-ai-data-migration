import argparse
import autogen
from utils.gcp_secrets import get_gcp_secret
from utils.config_parser import get_tf_config
from agents import (
    environment_setup_agent, data_migration_agent, data_validation_agent,
    performance_optimization_agent, schema_conversion_agent, anomaly_detection_agent
)
from agent_tools.infra_tools import run_terraform_apply
from mcp_server import mcp_client

class MigrationState:
    """A state object to hold infrastructure details discovered at runtime."""
    def __init__(self, project_id):
        self.project_id = project_id
        self.mcp_instance_ip = None
        self.source_db_ip = None
        self.cloud_sql_instance_name = None
        self.gcs_bucket_name = None
        print("MigrationState initialized.")

    def update_infra_details(self, terraform_outputs):
        self.mcp_instance_ip = terraform_outputs.get("mcp_instance_public_ip", {}).get("value")
        self.source_db_ip = terraform_outputs.get("source_db_private_ip", {}).get("value")
        self.cloud_sql_instance_name = terraform_outputs.get("cloud_sql_instance_name", {}).get("value")
        self.gcs_bucket_name = terraform_outputs.get("migration_gcs_bucket", {}).get("value")
        print(f"State Updated: MCP IP set to {self.mcp_instance_ip}")

def main(databases_to_migrate: list):
    """Initializes and runs the agentic migration workflow."""
    
    # Read Project ID from terraform.tfvars to ensure consistency
    tf_config = get_tf_config()
    gcp_project_id = tf_config.get("gcp_project_id")
    if not gcp_project_id:
        print("FATAL: gcp_project_id not found in terraform/terraform.tfvars")
        return

    MIGRATION_STATE = MigrationState(gcp_project_id)

    print(f"Initializing AI Agent Team for Project: {gcp_project_id}...")
    try:
        gemini_api_key = get_gcp_secret(gcp_project_id, "gemini-api-key")
    except Exception as e:
        print(f"FATAL: Could not fetch 'gemini-api-key' from Secret Manager. {e}")
        return

    config_list = [{"model": "gemini-1.5-flash-latest", "api_key": gemini_api_key, "api_type": "google"}]
    llm_config = {"config_list": config_list, "temperature": 0.1}

    def terraform_apply_wrapper():
        outputs = run_terraform_apply()
        if outputs:
            MIGRATION_STATE.update_infra_details(outputs)
            return "SUCCESS: Terraform apply completed and server is healthy. Infrastructure details captured."
        return "ERROR: Terraform apply failed or server health check timed out."

    def gcs_import_wrapper(db_name): return mcp_client.run_gcs_import_workflow(MIGRATION_STATE, db_name)
    def dms_import_wrapper(db_name): return mcp_client.run_dms_workflow(MIGRATION_STATE, db_name)
    def metadata_wrapper(db_name): return mcp_client.get_db_metadata(MIGRATION_STATE, db_name)

    user_proxy = autogen.UserProxyAgent(
        name="UserProxy", human_input_mode="NEVER",
        max_consecutive_auto_reply=30, code_execution_config=False,
        is_termination_msg=lambda x: "TERMINATE" in x.get("content", "").upper()
    )

    agents = [
        user_proxy, environment_setup_agent.create_agent(llm_config),
        schema_conversion_agent.create_agent(llm_config),
        data_migration_agent.create_agent(llm_config),
        data_validation_agent.create_agent(llm_config),
        anomaly_detection_agent.create_agent(llm_config),
        performance_optimization_agent.create_agent(llm_config)
    ]

    user_proxy.register_function(
        function_map={
            "run_terraform_apply": terraform_apply_wrapper,
            "get_db_metadata": metadata_wrapper,
            "run_gcs_import_workflow": gcs_import_wrapper,
            "run_dms_workflow": dms_import_wrapper
        }
    )

    groupchat = autogen.GroupChat(agents=agents, messages=[], max_round=60)
    manager = autogen.GroupChatManager(groupchat=groupchat, llm_config=llm_config)

    db_list_str = ", ".join(f"'{db}'" for db in databases_to_migrate)
    initial_task = f"""
    Start the end-to-end MySQL database migration for GCP Project '{gcp_project_id}'.
    Databases to migrate: [{db_list_str}].
    Execute this plan:
    1.  EnvironmentSetupAgent: Provision the GCP environment using `run_terraform_apply`.
    2.  DataMigrationAgent: For each database, get its size, then choose and execute the correct migration workflow (GCS for < 100GB, DMS for >= 100GB).
    3.  DataValidationAgent: After migration, verify data integrity.
    4.  PerformanceOptimizationAgent: Provide optimization recommendations.
    Report 'TERMINATE' upon successful completion.
    """
    user_proxy.initiate_chat(manager, message=initial_task)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run an agentic AI database migration.")
    parser.add_argument('databases', nargs='+', help='A list of database names to migrate.')
    args = parser.parse_args()
    main(args.databases)