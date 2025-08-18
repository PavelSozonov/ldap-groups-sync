#!/usr/bin/env python3
"""Script to automatically setup OpenWebUI with admin account and API key."""

import os
import time
import requests
import json
from typing import Optional

class OpenWebUISetup:
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
                response = self.session.get(f"{self.base_url}/healthz", timeout=5)
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
            # If we get redirected to setup page, it means setup is needed
            return "setup" in response.url or response.status_code == 200
        except requests.exceptions.RequestException:
            return False
    
    def create_admin_account(self, name: str, email: str, password: str) -> bool:
        """Create admin account via setup API."""
        print(f"Creating admin account for {email}...")
        
        setup_data = {
            "name": name,
            "email": email,
            "password": password
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/v1/auth/setup",
                json=setup_data,
                timeout=10
            )
            
            if response.status_code == 200:
                print("✅ Admin account created successfully!")
                return True
            else:
                print(f"❌ Failed to create admin account: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Error creating admin account: {e}")
            return False
    
    def login(self, email: str, password: str) -> bool:
        """Login to OpenWebUI."""
        print(f"Logging in as {email}...")
        
        login_data = {
            "email": email,
            "password": password
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/v1/auth/login",
                json=login_data,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if "access_token" in data:
                    self.session.headers["Authorization"] = f"Bearer {data['access_token']}"
                    print("✅ Login successful!")
                    return True
            
            print(f"❌ Login failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Error during login: {e}")
            return False
    
    def create_api_key(self, name: str = "sync-service-key") -> Optional[str]:
        """Create API key for the service."""
        print(f"Creating API key: {name}...")
        
        key_data = {
            "name": name,
            "permissions": ["read", "write"]  # Adjust permissions as needed
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/v1/auth/api-keys",
                json=key_data,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                api_key = data.get("key")
                if api_key:
                    print("✅ API key created successfully!")
                    return api_key
            
            print(f"❌ Failed to create API key: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Error creating API key: {e}")
            return None
    
    def get_user_info(self) -> Optional[dict]:
        """Get current user information."""
        try:
            response = self.session.get(f"{self.base_url}/api/v1/auth/me", timeout=10)
            if response.status_code == 200:
                return response.json()
        except requests.exceptions.RequestException:
            pass
        return None
    
    def setup_complete(self, name: str, email: str, password: str) -> Optional[str]:
        """Complete OpenWebUI setup process."""
        print("🚀 Starting OpenWebUI setup...")
        
        # Wait for service to be ready
        if not self.wait_for_service():
            return None
        
        # Check if setup is needed
        if not self.check_setup_status():
            print("ℹ️ OpenWebUI appears to be already configured")
            # Try to login with provided credentials
            if self.login(email, password):
                user_info = self.get_user_info()
                if user_info:
                    print(f"✅ Logged in as: {user_info.get('name', 'Unknown')}")
                    # Try to create API key
                    api_key = self.create_api_key()
                    return api_key
            return None
        
        # Create admin account
        if not self.create_admin_account(name, email, password):
            return None
        
        # Login with created account
        if not self.login(email, password):
            return None
        
        # Create API key
        api_key = self.create_api_key()
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
    
    print(f"OpenWebUI Setup Configuration:")
    print(f"  Base URL: {base_url}")
    print(f"  Admin Name: {name}")
    print(f"  Admin Email: {email}")
    print(f"  Admin Password: {'*' * len(password)}")
    print()
    
    # Run setup
    setup = OpenWebUISetup(base_url)
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
