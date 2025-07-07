import subprocess
import os
import json
import time
import requests

def _wait_for_server_ready(ip: str, timeout: int = 180, interval: int = 15):
    """Pings the MCP server health check endpoint until it's ready or times out."""
    start_time = time.time()
    url = f"http://{ip}:8000/"
    while time.time() - start_time < timeout:
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                print(f"Server at {ip} is healthy and ready.")
                return True
        except requests.exceptions.ConnectionError:
            print(f"   -> Server not ready yet. Retrying in {interval} seconds...")
        except Exception as e:
            print(f"An unexpected error occurred during health check: {e}")
        
        time.sleep(interval)
    
    print(f"ERROR: Server health check timed out after {timeout} seconds.")
    return False

def run_terraform_apply():
    """Initializes and applies Terraform, waits for server readiness, then returns outputs."""
    terraform_dir = "terraform"
    if not os.path.isdir(terraform_dir):
        return None
    try:
        print("-> Running 'terraform init'...")
        subprocess.run(["terraform", "init", "-upgrade"], cwd=terraform_dir, check=True, capture_output=True)
        
        print("-> Running 'terraform apply'...")
        subprocess.run(["terraform", "apply", "-auto-approve"], cwd=terraform_dir, check=True, capture_output=True)
        
        print("-> Fetching Terraform outputs...")
        output_result = subprocess.run(
            ["terraform", "output", "-json"], cwd=terraform_dir, check=True, capture_output=True, text=True
        )
        outputs = json.loads(output_result.stdout)
        
        mcp_ip = outputs.get("mcp_instance_public_ip", {}).get("value")
        if not mcp_ip:
            print("ERROR: MCP instance IP not found in Terraform outputs.")
            return None
            
        print(f"-> Waiting for MCP server at {mcp_ip} to become healthy...")
        if not _wait_for_server_ready(mcp_ip):
            return None # Health check failed

        print("Terraform apply complete and server is healthy.")
        return outputs

    except subprocess.CalledProcessError as e:
        print(f"ERROR during Terraform execution: {e.stderr}")
        return None