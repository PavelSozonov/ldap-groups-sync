#!/usr/bin/env python3
"""Script with instructions to create demo user in OpenWebUI."""

def main():
    print("🔧 Manual Demo User Creation Instructions:")
    print("Since OpenWebUI API doesn't allow creating users via API,")
    print("you need to create the demo user manually through the web interface.")
    print()
    print("📋 Steps to create demo user:")
    print("1. Open http://localhost:8080 in your browser")
    print("2. Login as admin@example.com / adminpassword")
    print("3. Go to Settings > Users (or similar)")
    print("4. Create a new user with the following details:")
    print("   - Name: Demo User")
    print("   - Email: demo@example.com")
    print("   - Password: demopassword")
    print("   - Role: user")
    print()
    print("🔍 After creating the user, you can verify it with:")
    print("curl -H 'Authorization: Bearer sk-e3f1e5dde3f54c5aa4df7563eafadeb3' http://localhost:8080/api/v1/users/")
    print()
    print("✅ Once the user is created, the sync service will be able to")
    print("   add the user to groups automatically.")

if __name__ == "__main__":
    main()
