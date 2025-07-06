import subprocess
import os
import json

def run_terraform_apply():
    """
    Initializes and applies Terraform configurations, then returns the outputs as a JSON object.
    """
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
            ["terraform", "output", "-json"],
            cwd=terraform_dir, check=True, capture_output=True, text=True
        )
        outputs = json.loads(output_result.stdout)
        print("✅ Terraform Outputs Captured.")
        return outputs
    except subprocess.CalledProcessError as e:
        print(f"ERROR during Terraform execution: {e.stderr}")
        return None