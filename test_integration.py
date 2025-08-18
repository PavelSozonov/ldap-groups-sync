#!/usr/bin/env python3
"""Simple integration test script."""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sync_service.adapters.openwebui_adapter import OpenWebUIAdapter
from sync_service.settings import load_config
from pathlib import Path

def main():
    print("Loading config...")
    config = load_config(Path('config/config.yaml'))
    
    print("Config services:", config.services)
    print("First service:", config.services[0])
    
    service_config = config.services[0]
    print("Service config type:", type(service_config))
    print("Service config dict:", dict(service_config) if hasattr(service_config, 'items') else "Not dict-like")
    
    # Try direct access to config values
    import httpx
    client = httpx.Client(
        base_url="http://openwebui:8080",
        headers={"Authorization": "Bearer sk-e3f1e5dde3f54c5aa4df7563eafadeb3"},
        verify=False,
        timeout=10
    )

    print("\n=== Testing Groups ===")
    try:
        resp = client.get("/api/v1/groups/")
        print(f"Groups response status: {resp.status_code}")
        if resp.status_code == 200:
            groups = resp.json()
            print(f"Found {len(groups)} groups:")
            for g in groups:
                print(f"  - {g['name']} (id: {g['id']})")
        else:
            print(f"Error response: {resp.text}")
    except Exception as e:
        print(f"Error getting groups: {e}")

    print("\n=== Testing Users ===")
    try:
        resp = client.get("/api/v1/users/")
        print(f"Users response status: {resp.status_code}")
        if resp.status_code == 200:
            users_data = resp.json()
            if 'users' in users_data:
                users = users_data['users']
                print(f"Found {len(users)} users:")
                for u in users:
                    print(f"  - {u['email']} (id: {u['id']})")
            else:
                print(f"Users data: {users_data}")
        else:
            print(f"Error response: {resp.text}")
    except Exception as e:
        print(f"Error getting users: {e}")
    
    client.close()

if __name__ == "__main__":
    main()
