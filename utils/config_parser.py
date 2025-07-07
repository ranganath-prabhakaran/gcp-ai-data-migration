import hcl2
import os

def get_tf_config(file_path="terraform/terraform.tfvars"):
    """Parses a .tfvars file and returns a dictionary of variables."""
    if not os.path.exists(file_path):
        return {}
    
    with open(file_path, 'r') as f:
        try:
            # hcl2 parser is used as it correctly handles HCL syntax
            tf_vars = hcl2.load(f)
            return tf_vars
        except Exception as e:
            print(f"Error parsing {file_path}: {e}")
            return {}