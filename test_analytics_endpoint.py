#!/usr/bin/env python3
"""
Test analytics endpoint directly
"""

import requests
import json

# Backend URL
BACKEND_URL = "https://api.josmose.com/api"

def test_analytics_endpoint():
    # First authenticate as manager
    auth_data = {
        "username": "naima@josmose.com",
        "password": "Naima@2024!Commerce"
    }
    
    response = requests.post(
        f"{BACKEND_URL}/auth/login",
        json=auth_data,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        data = response.json()
        token = data.get("access_token")
        print(f"✅ Authentication successful, token: {token[:20]}...")
        
        # Test analytics endpoint
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test different endpoints
        endpoints = [
            "/crm/analytics/dashboard",
            "/crm/security/stats", 
            "/crm/analytics/export/csv"
        ]
        
        for endpoint in endpoints:
            print(f"\n🔍 Testing {endpoint}")
            try:
                response = requests.get(f"{BACKEND_URL}{endpoint}", headers=headers)
                print(f"Status: {response.status_code}")
                if response.status_code != 200:
                    print(f"Response: {response.text[:200]}")
                else:
                    print("✅ Success!")
            except Exception as e:
                print(f"❌ Error: {e}")
    else:
        print(f"❌ Authentication failed: {response.status_code}")

if __name__ == "__main__":
    test_analytics_endpoint()