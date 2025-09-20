#!/usr/bin/env python3
"""
Comprehensive test for all manager authentication and abandoned cart endpoints
"""

import requests
import json
from datetime import datetime

# Backend URL from environment
BACKEND_URL = "https://water-ecom-admin.preview.emergentagent.com/api"

def test_all_managers_abandoned_cart_access():
    """Test that all 3 managers can access abandoned cart endpoints"""
    
    managers = [
        ("naima@josmose.com", "Naima@2024!Commerce", "Naima"),
        ("aziza@josmose.com", "Aziza@2024!Director", "Aziza"),
        ("antonio@josmose.com", "Antonio@2024!Secure", "Antonio")
    ]
    
    print("🔧 Testing All Managers Access to Abandoned Cart Endpoints")
    print("=" * 70)
    
    successful_tests = []
    
    for email, password, name in managers:
        session = requests.Session()
        
        try:
            print(f"\n👤 Testing {name} ({email})...")
            
            # Authenticate
            login_data = {
                "username": email,
                "password": password
            }
            
            login_response = session.post(
                f"{BACKEND_URL}/auth/login",
                json=login_data,
                headers={"Content-Type": "application/json"}
            )
            
            if login_response.status_code == 200:
                login_data_response = login_response.json()
                if "access_token" in login_data_response:
                    print(f"  ✅ Authentication successful")
                    
                    # Set authorization header
                    session.headers.update({
                        "Authorization": f"Bearer {login_data_response['access_token']}"
                    })
                    
                    # Test abandoned cart dashboard
                    dashboard_response = session.get(f"{BACKEND_URL}/crm/abandoned-carts/dashboard")
                    
                    if dashboard_response.status_code == 200:
                        dashboard_data = dashboard_response.json()
                        if "statistics" in dashboard_data and "recent_carts" in dashboard_data:
                            print(f"  ✅ Dashboard access: 200 OK with correct structure")
                            
                            # Test process recovery emails
                            process_response = session.post(f"{BACKEND_URL}/crm/process-recovery-emails")
                            
                            if process_response.status_code == 200:
                                process_data = process_response.json()
                                if "success" in process_data and process_data["success"]:
                                    print(f"  ✅ Process recovery emails: 200 OK with success")
                                    successful_tests.append(name)
                                else:
                                    print(f"  ❌ Process recovery emails failed: {process_data}")
                            else:
                                print(f"  ❌ Process recovery emails: {process_response.status_code}")
                        else:
                            print(f"  ❌ Dashboard missing structure: {list(dashboard_data.keys())}")
                    else:
                        print(f"  ❌ Dashboard access: {dashboard_response.status_code}")
                        print(f"     Response: {dashboard_response.text}")
                else:
                    print(f"  ❌ No access token in response")
            else:
                print(f"  ❌ Authentication failed: {login_response.status_code}")
                
        except Exception as e:
            print(f"  ❌ Exception: {str(e)}")
    
    print("\n" + "=" * 70)
    print("📊 FINAL RESULTS")
    print("=" * 70)
    
    if len(successful_tests) == 3:
        print("🎉 ALL TESTS PASSED!")
        print(f"✅ All 3 managers successfully tested: {', '.join(successful_tests)}")
        print("✅ Authentication fix is working perfectly")
        print("✅ No more 401 Unauthorized errors")
        print("✅ Both abandoned cart endpoints return 200 OK")
        return True
    else:
        print(f"❌ Only {len(successful_tests)}/3 managers passed all tests")
        print(f"✅ Successful: {', '.join(successful_tests)}")
        return False

if __name__ == "__main__":
    success = test_all_managers_abandoned_cart_access()
    if success:
        print("\n🎯 AUTHENTICATION FIX VERIFICATION COMPLETE - ALL SYSTEMS WORKING!")
    else:
        print("\n⚠️  Some issues remain - check individual test results above")