#!/usr/bin/env python3
"""
Focused test for abandoned cart dashboard bug fix
Testing the specific issue mentioned in the review request
"""

import requests
import json
from datetime import datetime

# Backend URL from environment
BACKEND_URL = "https://0d683f65-404e-4436-abda-79303fb40932.preview.emergentagent.com/api"

class AbandonedCartTester:
    def __init__(self):
        self.session = requests.Session()
        self.test_results = []
        
    def log_test(self, test_name: str, success: bool, details: str = "", response_data=None):
        """Log test results"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat(),
            "response_data": response_data
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {details}")
        if response_data and not success:
            print(f"   Response: {response_data}")
    
    def authenticate_antonio(self):
        """Authenticate as Antonio (manager) - the specific user mentioned in the bug report"""
        try:
            login_data = {
                "username": "antonio@josmose.com",
                "password": "Antonio@2024!Secure"
            }
            
            response = self.session.post(
                f"{BACKEND_URL}/auth/login",
                json=login_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                if "access_token" in data:
                    # Set authorization header for subsequent requests
                    self.auth_token = data['access_token']
                    self.session.headers.update({
                        "Authorization": f"Bearer {data['access_token']}"
                    })
                    
                    # Verify the role is manager
                    user_info = data.get("user", {})
                    role = user_info.get("role", "unknown")
                    
                    self.log_test("Antonio Authentication", True, 
                                f"Authenticated as antonio@josmose.com with role: {role}")
                    return True
                else:
                    self.log_test("Antonio Authentication", False, "No access token in response", data)
                    return False
            else:
                self.log_test("Antonio Authentication", False, 
                            f"Status: {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("Antonio Authentication", False, f"Exception: {str(e)}")
            return False
    
    def test_abandoned_cart_dashboard_access(self):
        """Test GET /api/crm/abandoned-carts/dashboard - The specific endpoint that was failing"""
        try:
            print(f"\n🔍 Testing abandoned cart dashboard endpoint...")
            print(f"URL: {BACKEND_URL}/crm/abandoned-carts/dashboard")
            print(f"Authorization: Bearer {getattr(self, 'auth_token', 'NOT_SET')[:20]}...")
            
            response = self.session.get(f"{BACKEND_URL}/crm/abandoned-carts/dashboard")
            
            print(f"Response Status: {response.status_code}")
            print(f"Response Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Response Data Keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                
                # Check for expected structure
                required_fields = ["statistics", "recent_carts"]
                
                if all(field in data for field in required_fields):
                    statistics = data.get("statistics", {})
                    recent_carts = data.get("recent_carts", [])
                    
                    self.log_test("Abandoned Cart Dashboard Access", True, 
                                f"✅ SUCCESS! Dashboard loaded with {len(recent_carts)} recent carts. "
                                f"Statistics: {list(statistics.keys()) if isinstance(statistics, dict) else 'Invalid'}")
                    
                    # Log some details about the response
                    print(f"📊 Statistics fields: {list(statistics.keys()) if isinstance(statistics, dict) else 'None'}")
                    print(f"🛒 Recent carts count: {len(recent_carts)}")
                    
                    return True
                else:
                    missing = [f for f in required_fields if f not in data]
                    self.log_test("Abandoned Cart Dashboard Access", False, 
                                f"Missing required fields: {missing}. Available: {list(data.keys())}", data)
                    return False
                    
            elif response.status_code == 401:
                self.log_test("Abandoned Cart Dashboard Access", False, 
                            "❌ 401 Unauthorized - This is the bug that was supposed to be fixed!", 
                            response.text)
                return False
                
            elif response.status_code == 403:
                self.log_test("Abandoned Cart Dashboard Access", False, 
                            "❌ 403 Forbidden - Access denied", response.text)
                return False
                
            elif response.status_code == 500:
                self.log_test("Abandoned Cart Dashboard Access", False, 
                            "❌ 500 Internal Server Error - Service initialization issue?", 
                            response.text)
                return False
            else:
                self.log_test("Abandoned Cart Dashboard Access", False, 
                            f"❌ Unexpected status: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Abandoned Cart Dashboard Access", False, f"Exception: {str(e)}")
            return False
    
    def test_service_initialization(self):
        """Test if abandoned_cart_service is properly initialized"""
        try:
            # We can't directly test service initialization, but we can test if the endpoint works
            # If it returns proper data structure, the service is likely initialized
            
            response = self.session.get(f"{BACKEND_URL}/crm/abandoned-carts/dashboard")
            
            if response.status_code == 200:
                data = response.json()
                if "statistics" in data and "recent_carts" in data:
                    self.log_test("Service Initialization Check", True, 
                                "✅ abandoned_cart_service appears to be properly initialized")
                    return True
                else:
                    self.log_test("Service Initialization Check", False, 
                                "❌ Service may not be properly initialized - invalid response structure")
                    return False
            elif response.status_code == 500:
                # Check if error message indicates service initialization issue
                error_text = response.text.lower()
                if "service non initialisé" in error_text or "not initialized" in error_text:
                    self.log_test("Service Initialization Check", False, 
                                "❌ abandoned_cart_service is not initialized", response.text)
                    return False
                else:
                    self.log_test("Service Initialization Check", False, 
                                "❌ 500 error but unclear if it's initialization issue", response.text)
                    return False
            else:
                self.log_test("Service Initialization Check", False, 
                            f"❌ Cannot determine service status - HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Service Initialization Check", False, f"Exception: {str(e)}")
            return False
    
    def run_focused_test(self):
        """Run the focused test for the abandoned cart dashboard bug fix"""
        print("🚀 Starting focused test for abandoned cart dashboard bug fix...")
        print("=" * 80)
        
        # Step 1: Authenticate as Antonio (the manager mentioned in the bug report)
        if not self.authenticate_antonio():
            print("❌ Authentication failed - cannot proceed with dashboard test")
            return False
        
        # Step 2: Test the specific endpoint that was failing
        dashboard_success = self.test_abandoned_cart_dashboard_access()
        
        # Step 3: Check service initialization
        service_success = self.test_service_initialization()
        
        print("\n" + "=" * 80)
        print("📋 TEST SUMMARY:")
        print("=" * 80)
        
        for result in self.test_results:
            status = "✅ PASS" if result["success"] else "❌ FAIL"
            print(f"{status} {result['test']}: {result['details']}")
        
        overall_success = dashboard_success and service_success
        
        if overall_success:
            print("\n🎉 BUG FIX VERIFICATION: SUCCESS!")
            print("✅ The abandoned cart dashboard is now working correctly")
            print("✅ No more 401 Unauthorized errors")
            print("✅ Service appears to be properly initialized")
        else:
            print("\n⚠️  BUG FIX VERIFICATION: ISSUES FOUND")
            print("❌ The abandoned cart dashboard still has problems")
            
        return overall_success

if __name__ == "__main__":
    tester = AbandonedCartTester()
    success = tester.run_focused_test()
    exit(0 if success else 1)