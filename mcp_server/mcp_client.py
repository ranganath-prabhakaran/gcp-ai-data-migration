import requests

def _call_mcp_tool(mcp_ip: str, tool_name: str, params: dict):
    """Helper function to call a tool on the running MCP server."""
    if not mcp_ip:
        return "ERROR: MCP Server IP is not set. Cannot make a real tool call. Environment setup might have failed."
    mcp_server_url = f"http://{mcp_ip}:8000"
    try:
        response = requests.post(f"{mcp_server_url}/call/{tool_name}", json={"params": params})
        response.raise_for_status()
        return response.json().get("result", "No result returned.")
    except requests.exceptions.RequestException as e:
        return f"ERROR: Could not connect to MCP Server at {mcp_server_url}. Details: {e}"

def get_db_metadata(state, db_name: str) -> str:
    """Calls the MCP server to get metadata for a specific database."""
    params = {"db_name": db_name, "project_id": state.project_id}
    return _call_mcp_tool(state.mcp_instance_ip, "get_db_metadata", params)

def run_gcs_import_workflow(state, db_name: str) -> str:
    """Calls the MCP server to execute the GCS import workflow."""
    params = {
        "db_name": db_name,
        "gcs_bucket": state.gcs_bucket_name,
        "instance_name": state.cloud_sql_instance_name,
        "project_id": state.project_id
    }
    return _call_mcp_tool(state.mcp_instance_ip, "run_gcs_import_workflow", params)
    
def run_dms_workflow(state, db_name: str) -> str:
    """Calls the MCP server to execute the DMS workflow."""
    params = {
        "db_name": db_name,
        "project_id": state.project_id,
        "region": "us-central1",
        "source_db_ip": state.source_db_ip,
        "cloud_sql_instance_id": state.cloud_sql_instance_name,
        "user_secret": state.user_secret,
        "pass_secret": state.pass_secret
    }
    return _call_mcp_tool(state.mcp_instance_ip, "run_dms_workflow", params)
