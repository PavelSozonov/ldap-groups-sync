#!/usr/bin/env python3
"""Script to automatically setup OpenWebUI via web interface."""

import os
import time
import requests
import json
import sys
from typing import Optional

class OpenWebUIWebSetup:
    def __init__(self, base_url: str = "http://localhost:8080"):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json"
        })
    
    def wait_for_service(self, timeout: int = 60) -> bool:
        """Wait for OpenWebUI service to be ready."""
        print(f"Waiting for OpenWebUI at {self.base_url}...")
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                response = self.session.get(f"{self.base_url}/", timeout=5)
                if response.status_code == 200:
                    print("✅ OpenWebUI is ready!")
                    return True
            except requests.exceptions.RequestException:
                pass
            
            print("⏳ Waiting for OpenWebUI to start...")
            time.sleep(2)
        
        print("❌ Timeout waiting for OpenWebUI")
        return False
    
    def check_setup_status(self) -> bool:
        """Check if OpenWebUI needs initial setup."""
        try:
            response = self.session.get(f"{self.base_url}/auth", timeout=5)
            # Check if we're redirected to setup page
            return "setup" in response.url or "auth" in response.url
        except requests.exceptions.RequestException:
            return False
    
    def create_admin_via_web(self, name: str, email: str, password: str) -> bool:
        """Create admin account via web interface."""
        print(f"Creating admin account for {email} via web interface...")
        
        # First, get the setup page to get any CSRF tokens
        try:
            response = self.session.get(f"{self.base_url}/auth", timeout=10)
            if response.status_code != 200:
                print(f"❌ Failed to access setup page: {response.status_code}")
                return False
            
            # Try to submit the setup form
            setup_data = {
                "name": name,
                "email": email,
                "password": password
            }
            
            # Try different possible endpoints
            endpoints = [
                "/api/v1/auth/setup",
                "/api/auth/setup", 
                "/auth/setup",
                "/api/v1/users",
                "/api/users"
            ]
            
            for endpoint in endpoints:
                try:
                    response = self.session.post(
                        f"{self.base_url}{endpoint}",
                        json=setup_data,
                        timeout=10
                    )
                    print(f"Tried {endpoint}: {response.status_code}")
                    
                    if response.status_code in [200, 201]:
                        print(f"✅ Admin account created via {endpoint}!")
                        return True
                    elif response.status_code == 422:
                        # Validation error, try next endpoint
                        continue
                        
                except requests.exceptions.RequestException:
                    continue
            
            print("❌ Failed to create admin account via any endpoint")
            return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Error creating admin account: {e}")
            return False
    
    def login_via_web(self, email: str, password: str) -> bool:
        """Login to OpenWebUI via web interface."""
        print(f"Logging in as {email}...")
        
        login_data = {
            "email": email,
            "password": password
        }
        
        # Try different possible login endpoints
        endpoints = [
            "/api/v1/auth/login",
            "/api/auth/login",
            "/auth/login"
        ]
        
        for endpoint in endpoints:
            try:
                response = self.session.post(
                    f"{self.base_url}{endpoint}",
                    json=login_data,
                    timeout=10
                )
                print(f"Tried login {endpoint}: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    if "access_token" in data:
                        self.session.headers["Authorization"] = f"Bearer {data['access_token']}"
                        print("✅ Login successful!")
                        return True
                    elif "token" in data:
                        self.session.headers["Authorization"] = f"Bearer {data['token']}"
                        print("✅ Login successful!")
                        return True
                        
            except requests.exceptions.RequestException:
                continue
        
        print("❌ Login failed via all endpoints")
        return False
    
    def create_api_key_via_web(self, name: str = "sync-service-key") -> Optional[str]:
        """Create API key via web interface."""
        print(f"Creating API key: {name}...")
        
        key_data = {
            "name": name,
            "permissions": ["read", "write"]
        }
        
        # Try different possible API key endpoints
        endpoints = [
            "/api/v1/auth/api-keys",
            "/api/auth/api-keys",
            "/api/v1/users/me/api-keys",
            "/api/users/me/api-keys"
        ]
        
        for endpoint in endpoints:
            try:
                response = self.session.post(
                    f"{self.base_url}{endpoint}",
                    json=key_data,
                    timeout=10
                )
                print(f"Tried API key {endpoint}: {response.status_code}")
                
                if response.status_code in [200, 201]:
                    data = response.json()
                    api_key = data.get("key") or data.get("api_key") or data.get("token")
                    if api_key:
                        print("✅ API key created successfully!")
                        return api_key
                        
            except requests.exceptions.RequestException:
                continue
        
        print("❌ Failed to create API key via any endpoint")
        return None
    
    def get_user_info_via_web(self) -> Optional[dict]:
        """Get current user information via web interface."""
        endpoints = [
            "/api/v1/auth/me",
            "/api/auth/me",
            "/api/v1/users/me",
            "/api/users/me"
        ]
        
        for endpoint in endpoints:
            try:
                response = self.session.get(f"{self.base_url}{endpoint}", timeout=10)
                if response.status_code == 200:
                    return response.json()
            except requests.exceptions.RequestException:
                continue
        return None
    
    def setup_complete(self, name: str, email: str, password: str) -> Optional[str]:
        """Complete OpenWebUI setup process."""
        print("🚀 Starting OpenWebUI web setup...")
        
        # Wait for service to be ready
        if not self.wait_for_service():
            return None
        
        # Check if setup is needed
        if not self.check_setup_status():
            print("ℹ️ OpenWebUI appears to be already configured")
            # Try to login with provided credentials
            if self.login_via_web(email, password):
                user_info = self.get_user_info_via_web()
                if user_info:
                    print(f"✅ Logged in as: {user_info.get('name', 'Unknown')}")
                    # Try to create API key
                    api_key = self.create_api_key_via_web()
                    return api_key
            return None
        
        # Create admin account
        if not self.create_admin_via_web(name, email, password):
            return None
        
        # Login with created account
        if not self.login_via_web(email, password):
            return None
        
        # Create API key
        api_key = self.create_api_key_via_web()
        if api_key:
            print(f"🎉 Setup complete! API Key: {api_key}")
            return api_key
        
        return None

def main():
    """Main setup function."""
    # Configuration
    name = os.getenv("OWUI_ADMIN_NAME", "Admin User")
    email = os.getenv("OWUI_ADMIN_EMAIL", "admin@example.com")
    password = os.getenv("OWUI_ADMIN_PASSWORD", "adminpassword")
    base_url = os.getenv("OWUI_BASE_URL", "http://localhost:8080")
    
    print(f"OpenWebUI Web Setup Configuration:")
    print(f"  Base URL: {base_url}")
    print(f"  Admin Name: {name}")
    print(f"  Admin Email: {email}")
    print(f"  Admin Password: {'*' * len(password)}")
    print()
    
    # Run setup
    setup = OpenWebUIWebSetup(base_url)
    api_key = setup.setup_complete(name, email, password)
    
    if api_key:
        print("\n📋 Setup Summary:")
        print(f"  Admin Email: {email}")
        print(f"  API Key: {api_key}")
        print(f"  Base URL: {base_url}")
        
        # Save API key to file for easy access
        with open(".owui_api_key", "w") as f:
            f.write(api_key)
        print("  API key saved to .owui_api_key")
        
        return True
    else:
        print("\n❌ Setup failed!")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
