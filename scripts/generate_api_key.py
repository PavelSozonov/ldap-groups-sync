#!/usr/bin/env python3
"""Script to generate a mock API key for OpenWebUI testing."""

import os
import secrets
import string
import sys

def generate_api_key(length: int = 64) -> str:
    """Generate a random API key."""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def main():
    """Main function."""
    # Generate API key
    api_key = generate_api_key()
    
    # Save to file
    with open(".owui_api_key", "w") as f:
        f.write(api_key)
    
    print("🔑 Generated API Key for OpenWebUI testing:")
    print(f"  API Key: {api_key}")
    print("  Saved to: .owui_api_key")
    print()
    print("📋 Manual Setup Instructions:")
    print("  1. Open http://localhost:8080 in your browser")
    print("  2. Create admin account with:")
    print(f"     Email: {os.getenv('OWUI_ADMIN_EMAIL', 'admin@example.com')}")
    print(f"     Password: {os.getenv('OWUI_ADMIN_PASSWORD', 'adminpassword')}")
    print("  3. Go to Settings > Account")
    print("  4. Create API key with the generated key above")
    print("  5. Or use the generated key directly in your config")
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
