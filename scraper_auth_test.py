#!/usr/bin/env python3
"""
Scraper Agent Authentication Test for JOSMOSE.COM
Tests the Scraper Agent endpoints with proper manager authentication
"""

import requests
import json
import time
from datetime import datetime

# Backend URL from environment
BACKEND_URL = "https://buildfix-josmoze.preview.emergentagent.com/api"

class ScraperAuthTester:
    def __init__(self):
        self.session = requests.Session()
        self.test_results = []
        self.auth_token = None
        
    def log_test(self, test_name: str, success: bool, details: str = ""):
        """Log test results"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {details}")
    
    def authenticate_manager(self):
        """Authenticate as manager (Naima) with correct credentials"""
        try:
            login_data = {
                "username": "naima@josmoze.com",
                "password": "Naima@2024!Commerce"
            }
            
            response = self.session.post(
                f"{BACKEND_URL}/auth/login",
                json=login_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                if "access_token" in data:
                    self.auth_token = data['access_token']
                    self.session.headers.update({
                        "Authorization": f"Bearer {data['access_token']}"
                    })
                    user_info = data.get('user', {})
                    self.log_test("Manager Authentication", True, 
                                f"Authenticated as {user_info.get('full_name', 'Manager')} with role: {user_info.get('role', 'unknown')}")
                    return True
                else:
                    self.log_test("Manager Authentication", False, "No access token in response")
                    return False
            else:
                self.log_test("Manager Authentication", False, f"Status: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            self.log_test("Manager Authentication", False, f"Exception: {str(e)}")
            return False

    def test_scraper_with_auth(self):
        """Test Scraper endpoints with authentication"""
        try:
            # Test scraper status with auth
            response = self.session.get(f"{BACKEND_URL}/scraper/status")
            
            if response.status_code == 200:
                data = response.json()
                scraper_status = data.get("scraper_status", {})
                gdpr_compliance = data.get("gdpr_compliance", {})
                
                self.log_test("Scraper Status with Auth", True, 
                            f"Status: {scraper_status.get('task_status', 'unknown')}, "
                            f"GDPR compliant: {len(gdpr_compliance) > 0}")
                
                # Test run session with auth
                session_response = self.session.post(f"{BACKEND_URL}/scraper/run-session?max_prospects=5")
                
                if session_response.status_code == 200:
                    session_data = session_response.json()
                    stats = session_data.get("stats", {})
                    
                    self.log_test("Scraper Run Session with Auth", True, 
                                f"Session completed: {session_data.get('session_completed', False)}, "
                                f"Pages scraped: {stats.get('pages_scraped', 0)}")
                    return True
                else:
                    self.log_test("Scraper Run Session with Auth", False, 
                                f"Session failed: {session_response.status_code}")
                    return False
            else:
                self.log_test("Scraper Status with Auth", False, f"Status failed: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Scraper with Auth", False, f"Exception: {str(e)}")
            return False

    def test_manager_only_endpoints(self):
        """Test endpoints that require manager authentication"""
        try:
            # Test scheduled scraping (manager only)
            start_response = self.session.post(f"{BACKEND_URL}/scraper/start-scheduled?interval_hours=24")
            
            if start_response.status_code == 200:
                start_data = start_response.json()
                status = start_data.get("status", "")
                
                self.log_test("Manager-Only Start Scheduled", True, 
                            f"Scheduled scraping: {status}")
                
                # Test stop scheduled
                stop_response = self.session.post(f"{BACKEND_URL}/scraper/stop-scheduled")
                
                if stop_response.status_code == 200:
                    stop_data = stop_response.json()
                    stop_status = stop_data.get("status", "")
                    
                    self.log_test("Manager-Only Stop Scheduled", True, 
                                f"Stop scraping: {stop_status}")
                    return True
                else:
                    self.log_test("Manager-Only Stop Scheduled", False, 
                                f"Stop failed: {stop_response.status_code}")
                    return False
            else:
                self.log_test("Manager-Only Start Scheduled", False, 
                            f"Start failed: {start_response.status_code}")
                return False
        except Exception as e:
            self.log_test("Manager-Only Endpoints", False, f"Exception: {str(e)}")
            return False

    def run_auth_tests(self):
        """Run authentication tests for Scraper Agent"""
        print("🔐 Starting Scraper Agent Authentication Testing")
        print(f"Backend URL: {BACKEND_URL}")
        print("="*80)
        
        # Authenticate first
        auth_success = self.authenticate_manager()
        
        if auth_success:
            print("\n🕷️ TESTING SCRAPER ENDPOINTS WITH AUTHENTICATION")
            print("="*60)
            
            self.test_scraper_with_auth()
            self.test_manager_only_endpoints()
        else:
            print("\n❌ Authentication failed - cannot test authenticated endpoints")
        
        # Generate summary
        self.generate_summary()

    def generate_summary(self):
        """Generate test summary"""
        print("\n" + "="*80)
        print("📊 AUTHENTICATION TEST RESULTS")
        print("="*80)
        
        passed = sum(1 for result in self.test_results if result["success"])
        failed = len(self.test_results) - passed
        
        print(f"Total Tests: {len(self.test_results)}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"Success Rate: {(passed/len(self.test_results)*100):.1f}%")
        
        # Show all test results
        print("\n📋 DETAILED RESULTS:")
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            print(f"  {status} {result['test']}: {result['details']}")

if __name__ == "__main__":
    tester = ScraperAuthTester()
    tester.run_auth_tests()