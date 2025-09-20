#!/usr/bin/env python3
"""
Quick test for the abandoned cart authentication fix
"""

import requests
import json
from datetime import datetime

# Backend URL from environment
BACKEND_URL = "https://josmoze-ecom-fix.preview.emergentagent.com/api"

def test_abandoned_cart_authentication_fix():
    """Test the specific authentication fix for abandoned cart endpoints - Antonio credentials"""
    session = requests.Session()
    
    try:
        print("🔧 Testing Authentication Fix for Abandoned Cart Endpoints")
        print("=" * 60)
        
        # Test with Antonio's credentials specifically mentioned in the review
        login_data = {
            "username": "antonio@josmose.com",
            "password": "Antonio@2024!Secure"
        }
        
        print(f"1. Authenticating with antonio@josmose.com...")
        
        # Authenticate
        login_response = session.post(
            f"{BACKEND_URL}/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        
        if login_response.status_code == 200:
            login_data_response = login_response.json()
            if "access_token" in login_data_response:
                print("✅ Authentication successful")
                
                # Set authorization header
                session.headers.update({
                    "Authorization": f"Bearer {login_data_response['access_token']}"
                })
                
                print("2. Testing GET /api/crm/abandoned-carts/dashboard...")
                
                # Test 1: GET /api/crm/abandoned-carts/dashboard (should return 200, not 401)
                dashboard_response = session.get(f"{BACKEND_URL}/crm/abandoned-carts/dashboard")
                
                if dashboard_response.status_code == 200:
                    dashboard_data = dashboard_response.json()
                    
                    # Verify structure returns statistics and recent_carts
                    if "statistics" in dashboard_data and "recent_carts" in dashboard_data:
                        print("✅ Dashboard returns 200 OK with correct structure (statistics + recent_carts)")
                        print(f"   Statistics keys: {list(dashboard_data['statistics'].keys())}")
                        print(f"   Recent carts count: {len(dashboard_data['recent_carts'])}")
                        
                        print("3. Testing POST /api/crm/process-recovery-emails...")
                        
                        # Test 2: POST /api/crm/process-recovery-emails
                        process_response = session.post(f"{BACKEND_URL}/crm/process-recovery-emails")
                        
                        if process_response.status_code == 200:
                            process_data = process_response.json()
                            if "success" in process_data and process_data["success"]:
                                print("✅ Process recovery emails returns 200 OK with success: true")
                                print(f"   Response: {process_data}")
                                
                                print("\n🎉 AUTHENTICATION FIX VERIFIED SUCCESSFULLY!")
                                print("✅ No more 401 Unauthorized errors")
                                print("✅ Both endpoints return 200 OK")
                                print("✅ current_user.email is accessible without errors")
                                return True
                            else:
                                print(f"❌ Process emails failed: {process_data}")
                                return False
                        else:
                            print(f"❌ Process emails status: {process_response.status_code}")
                            print(f"   Response: {process_response.text}")
                            return False
                    else:
                        print(f"❌ Dashboard missing required structure. Got: {list(dashboard_data.keys())}")
                        return False
                else:
                    print(f"❌ Dashboard still returns {dashboard_response.status_code} instead of 200")
                    print(f"   Response: {dashboard_response.text}")
                    return False
            else:
                print("❌ No access token in login response")
                return False
        else:
            print(f"❌ Login failed with status: {login_response.status_code}")
            print(f"   Response: {login_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_abandoned_cart_authentication_fix()
    if success:
        print("\n✅ ALL TESTS PASSED - Authentication fix is working!")
    else:
        print("\n❌ TESTS FAILED - Authentication fix needs more work")