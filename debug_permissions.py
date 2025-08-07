#!/usr/bin/env python3
"""
Debug script to check the actual structure of permissions response
"""

import requests
import json

BACKEND_URL = "https://38ebfc62-3cd2-4bbe-be3b-666002d5e6cd.preview.emergentagent.com/api"

def debug_permissions():
    session = requests.Session()
    
    # Login as Naima
    auth_data = {
        "username": "naima@josmose.com",
        "password": "Naima@2024!Commerce"
    }
    
    response = session.post(
        f"{BACKEND_URL}/auth/login",
        json=auth_data,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        data = response.json()
        token = data["access_token"]
        
        # Get user info
        headers = {"Authorization": f"Bearer {token}"}
        permissions_response = session.get(f"{BACKEND_URL}/auth/user-info", headers=headers)
        
        if permissions_response.status_code == 200:
            permissions_data = permissions_response.json()
            print("Full response:")
            print(json.dumps(permissions_data, indent=2))
            
            if "permissions" in permissions_data:
                permissions = permissions_data["permissions"]
                print(f"\nPermissions type: {type(permissions)}")
                print(f"Permissions content: {permissions}")
        else:
            print(f"Permissions request failed: {permissions_response.status_code}")
            print(permissions_response.text)
    else:
        print(f"Login failed: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    debug_permissions()