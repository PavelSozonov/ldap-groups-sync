#!/usr/bin/env python3
"""Script to update config with real API key."""

import os
import yaml
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.read_api_key import read_api_key

def update_config_with_api_key(config_path: str = "config/config.yaml", api_key: str = None):
    """Update config file with API key."""
    if not api_key:
        api_key = read_api_key()
    
    if not api_key:
        print("No API key available", file=sys.stderr)
        return False
    
    try:
        # Read current config
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
        
        # Update API key
        for service in config.get("services", []):
            if service.get("type") == "openwebui":
                service["auth"]["api_key"] = api_key
                break
        
        # Write updated config
        with open(config_path, "w") as f:
            yaml.dump(config, f, default_flow_style=False)
        
        print(f"✅ Updated {config_path} with API key")
        return True
        
    except Exception as e:
        print(f"❌ Error updating config: {e}", file=sys.stderr)
        return False

def main():
    """Main function."""
    api_key = read_api_key()
    if not api_key:
        print("No API key found. Run setup first.", file=sys.stderr)
        return 1
    
    success = update_config_with_api_key(api_key=api_key)
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())
