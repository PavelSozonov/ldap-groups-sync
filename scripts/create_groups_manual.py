#!/usr/bin/env python3
"""Script to create groups manually in OpenWebUI via web interface."""

import requests
import json
import time

def create_groups_manual():
    """Create groups manually in OpenWebUI."""
    base_url = "http://localhost:8080"
    api_key = "sk-e3f1e5dde3f54c5aa4df7563eafadeb3"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    groups = ["Demo Group A", "Demo Group B"]
    
    print("🔧 Manual Group Creation Instructions:")
    print("Since OpenWebUI doesn't have API endpoints for group creation,")
    print("you need to create groups manually through the web interface.")
    print()
    print("📋 Steps to create groups:")
    print(f"1. Open {base_url} in your browser")
    print("2. Login with admin@example.com / adminpassword")
    print("3. Go to Settings > Groups (or similar)")
    print("4. Create the following groups:")
    
    for i, group in enumerate(groups, 1):
        print(f"   {i}. {group}")
    
    print()
    print("🔍 After creating groups, you can verify them with:")
    print(f"curl -H 'Authorization: Bearer {api_key}' {base_url}/api/v1/groups/")
    print()
    print("✅ Once groups are created, the sync service will be able to")
    print("   add users to these groups automatically.")

if __name__ == "__main__":
    create_groups_manual()
