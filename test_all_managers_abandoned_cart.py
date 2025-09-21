#!/usr/bin/env python3
"""
Test all managers can access abandoned cart dashboard
"""

import requests
import json
from datetime import datetime

# Backend URL from environment
BACKEND_URL = "https://chatbot-debug-2.preview.emergentagent.com/api"

def test_manager_access(email, password, name):
    """Test a specific manager's access to abandoned cart dashboard"""
    session = requests.Session()
    
    # Authenticate
    login_data = {
        "username": email,
        "password": password
    }
    
    response = session.post(
        f"{BACKEND_URL}/auth/login",
        json=login_data,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code != 200:
        print(f"❌ {name} authentication failed: {response.status_code}")
        return False
    
    data = response.json()
    if "access_token" not in data:
        print(f"❌ {name} no access token received")
        return False
    
    # Set authorization header
    session.headers.update({
        "Authorization": f"Bearer {data['access_token']}"
    })
    
    # Test abandoned cart dashboard access
    dashboard_response = session.get(f"{BACKEND_URL}/crm/abandoned-carts/dashboard")
    
    if dashboard_response.status_code == 200:
        dashboard_data = dashboard_response.json()
        if "statistics" in dashboard_data and "recent_carts" in dashboard_data:
            recent_count = len(dashboard_data.get("recent_carts", []))
            print(f"✅ {name} can access abandoned cart dashboard - {recent_count} recent carts")
            return True
        else:
            print(f"❌ {name} dashboard response missing required fields")
            return False
    else:
        print(f"❌ {name} dashboard access failed: {dashboard_response.status_code}")
        return False

def main():
    print("🚀 Testing all managers' access to abandoned cart dashboard...")
    print("=" * 80)
    
    managers = [
        ("naima@josmose.com", "Naima@2024!Commerce", "Naima"),
        ("aziza@josmose.com", "Aziza@2024!Director", "Aziza"),
        ("antonio@josmose.com", "Antonio@2024!Secure", "Antonio")
    ]
    
    successful_managers = []
    
    for email, password, name in managers:
        if test_manager_access(email, password, name):
            successful_managers.append(name)
    
    print("\n" + "=" * 80)
    print("📋 SUMMARY:")
    print("=" * 80)
    
    if len(successful_managers) == 3:
        print("🎉 SUCCESS! All 3 managers can access the abandoned cart dashboard:")
        for name in successful_managers:
            print(f"  ✅ {name}")
        print("\n✅ The bug fix is working correctly for all managers!")
    else:
        print(f"⚠️  Only {len(successful_managers)}/3 managers have access:")
        for name in successful_managers:
            print(f"  ✅ {name}")
        
        failed_managers = [name for _, _, name in managers if name not in successful_managers]
        for name in failed_managers:
            print(f"  ❌ {name}")

if __name__ == "__main__":
    main()