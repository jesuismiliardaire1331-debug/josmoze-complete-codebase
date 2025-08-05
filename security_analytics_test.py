#!/usr/bin/env python3
"""
Security and Analytics Testing for Josmose.com
Focus on new role-based security and analytics endpoints
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Any

# Backend URL from environment
BACKEND_URL = "https://1c073e61-17ce-4025-b38e-c822c7ab6961.preview.emergentagent.com/api"

class SecurityAnalyticsTester:
    def __init__(self):
        self.session = requests.Session()
        self.test_results = []
        self.role_tokens = {}
        
    def log_test(self, test_name: str, success: bool, details: str = "", response_data: Any = None):
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
    
    def authenticate_with_role(self, email, password, expected_role):
        """Authenticate with specific role credentials"""
        try:
            auth_data = {
                "username": email,
                "password": password
            }
            
            response = self.session.post(
                f"{BACKEND_URL}/auth/login",
                json=auth_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                token = data.get("access_token")
                user = data.get("user", {})
                role = user.get("role")
                
                if role == expected_role:
                    self.log_test(f"Auth {email} ({expected_role})", True, f"Successfully authenticated as {expected_role}")
                    return token
                else:
                    self.log_test(f"Auth {email} ({expected_role})", False, f"Expected role {expected_role}, got {role}")
                    return None
            else:
                self.log_test(f"Auth {email} ({expected_role})", False, f"Auth failed: {response.status_code}")
                return None
        except Exception as e:
            self.log_test(f"Auth {email} ({expected_role})", False, f"Exception: {str(e)}")
            return None

    def test_new_role_authentication(self):
        """Test authentication with new role-based credentials"""
        print("🔐 TESTING NEW ROLE-BASED AUTHENTICATION")
        print("-" * 50)
        
        test_credentials = [
            ("naima@josmose.com", "Naima@2024!Commerce", "manager"),
            ("aziza@josmose.com", "Aziza@2024!Director", "agent"),
            ("antonio@josmose.com", "Antonio@2024!Secure", "agent"),
            ("support@josmose.com", "Support@2024!Help", "technique")
        ]
        
        successful_auths = 0
        
        for email, password, expected_role in test_credentials:
            time.sleep(1)  # Avoid rate limiting
            token = self.authenticate_with_role(email, password, expected_role)
            if token:
                successful_auths += 1
                self.role_tokens[expected_role] = token
        
        if successful_auths == len(test_credentials):
            self.log_test("New Role Authentication System", True, f"All {successful_auths}/{len(test_credentials)} role-based logins successful")
            return True
        else:
            self.log_test("New Role Authentication System", False, f"Only {successful_auths}/{len(test_credentials)} role-based logins successful")
            return False

    def test_user_info_endpoint(self):
        """Test GET /api/auth/user-info with different roles"""
        print("\n👤 TESTING USER INFO ENDPOINT")
        print("-" * 50)
        
        if not self.role_tokens:
            self.log_test("User Info Endpoint", False, "No role tokens available from authentication tests")
            return False
        
        successful_tests = 0
        total_tests = len(self.role_tokens)
        
        for role, token in self.role_tokens.items():
            try:
                time.sleep(1)  # Avoid rate limiting
                headers = {"Authorization": f"Bearer {token}"}
                response = self.session.get(f"{BACKEND_URL}/auth/user-info", headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success") and "user" in data and "permissions" in data:
                        user = data["user"]
                        permissions = data["permissions"]
                        
                        if user.get("role") == role:
                            self.log_test(f"User Info {role}", True, f"Role: {role}, Permissions: {len(permissions)} items")
                            successful_tests += 1
                        else:
                            self.log_test(f"User Info {role}", False, f"Role mismatch: expected {role}, got {user.get('role')}")
                    else:
                        self.log_test(f"User Info {role}", False, "Invalid response structure", data)
                else:
                    self.log_test(f"User Info {role}", False, f"Status: {response.status_code}")
                    
            except Exception as e:
                self.log_test(f"User Info {role}", False, f"Exception: {str(e)}")
        
        if successful_tests == total_tests:
            self.log_test("User Info Endpoint System", True, f"All {successful_tests}/{total_tests} user info tests successful")
            return True
        else:
            self.log_test("User Info Endpoint System", False, f"Only {successful_tests}/{total_tests} user info tests successful")
            return False

    def test_analytics_dashboard_permissions(self):
        """Test GET /api/crm/analytics/dashboard with Manager/Agent roles"""
        print("\n📊 TESTING ANALYTICS DASHBOARD PERMISSIONS")
        print("-" * 50)
        
        if not self.role_tokens:
            self.log_test("Analytics Dashboard Permissions", False, "No role tokens available")
            return False
        
        results = []
        
        # Test Manager access
        manager_token = self.role_tokens.get("manager")
        if manager_token:
            try:
                time.sleep(1)
                headers = {"Authorization": f"Bearer {manager_token}"}
                response = self.session.get(f"{BACKEND_URL}/crm/analytics/dashboard", headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success") and "data" in data:
                        self.log_test("Analytics Dashboard (Manager)", True, "Manager can access analytics dashboard")
                        results.append(True)
                    else:
                        self.log_test("Analytics Dashboard (Manager)", False, "Invalid response structure", data)
                        results.append(False)
                else:
                    self.log_test("Analytics Dashboard (Manager)", False, f"Manager access failed: {response.status_code}")
                    results.append(False)
            except Exception as e:
                self.log_test("Analytics Dashboard (Manager)", False, f"Exception: {str(e)}")
                results.append(False)
        else:
            self.log_test("Analytics Dashboard (Manager)", False, "No manager token available")
            results.append(False)
        
        # Test Agent access
        agent_token = self.role_tokens.get("agent")
        if agent_token:
            try:
                time.sleep(1)
                headers = {"Authorization": f"Bearer {agent_token}"}
                response = self.session.get(f"{BACKEND_URL}/crm/analytics/dashboard", headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success") and "data" in data:
                        self.log_test("Analytics Dashboard (Agent)", True, "Agent can access analytics dashboard")
                        results.append(True)
                    else:
                        self.log_test("Analytics Dashboard (Agent)", False, "Invalid response structure", data)
                        results.append(False)
                else:
                    self.log_test("Analytics Dashboard (Agent)", False, f"Agent access failed: {response.status_code}")
                    results.append(False)
            except Exception as e:
                self.log_test("Analytics Dashboard (Agent)", False, f"Exception: {str(e)}")
                results.append(False)
        else:
            self.log_test("Analytics Dashboard (Agent)", False, "No agent token available")
            results.append(False)
        
        # Test Technique access (should fail)
        technique_token = self.role_tokens.get("technique")
        if technique_token:
            try:
                time.sleep(1)
                headers = {"Authorization": f"Bearer {technique_token}"}
                response = self.session.get(f"{BACKEND_URL}/crm/analytics/dashboard", headers=headers)
                
                if response.status_code in [401, 403]:
                    self.log_test("Analytics Dashboard (Technique)", True, "Technique correctly denied access to analytics")
                    results.append(True)
                else:
                    self.log_test("Analytics Dashboard (Technique)", False, f"Technique should be denied access, got: {response.status_code}")
                    results.append(False)
            except Exception as e:
                self.log_test("Analytics Dashboard (Technique)", False, f"Exception: {str(e)}")
                results.append(False)
        else:
            self.log_test("Analytics Dashboard (Technique)", False, "No technique token available")
            results.append(False)
        
        return all(results)

    def test_analytics_csv_export_permissions(self):
        """Test GET /api/crm/analytics/export/csv (Manager only)"""
        print("\n📈 TESTING CSV EXPORT PERMISSIONS")
        print("-" * 50)
        
        if not self.role_tokens:
            self.log_test("Analytics CSV Export Permissions", False, "No role tokens available")
            return False
        
        results = []
        
        # Test Manager access (should work)
        manager_token = self.role_tokens.get("manager")
        if manager_token:
            try:
                time.sleep(1)
                headers = {"Authorization": f"Bearer {manager_token}"}
                response = self.session.get(f"{BACKEND_URL}/crm/analytics/export/csv", headers=headers)
                
                if response.status_code == 200:
                    # Check if it's a CSV response
                    content_type = response.headers.get('content-type', '')
                    if 'text/csv' in content_type or 'application/csv' in content_type:
                        self.log_test("CSV Export (Manager)", True, "Manager can export CSV analytics")
                        results.append(True)
                    else:
                        self.log_test("CSV Export (Manager)", True, f"Manager access granted (content-type: {content_type})")
                        results.append(True)
                else:
                    self.log_test("CSV Export (Manager)", False, f"Manager access failed: {response.status_code}")
                    results.append(False)
            except Exception as e:
                self.log_test("CSV Export (Manager)", False, f"Exception: {str(e)}")
                results.append(False)
        else:
            self.log_test("CSV Export (Manager)", False, "No manager token available")
            results.append(False)
        
        # Test Agent access (should fail)
        agent_token = self.role_tokens.get("agent")
        if agent_token:
            try:
                time.sleep(1)
                headers = {"Authorization": f"Bearer {agent_token}"}
                response = self.session.get(f"{BACKEND_URL}/crm/analytics/export/csv", headers=headers)
                
                if response.status_code in [401, 403]:
                    self.log_test("CSV Export (Agent)", True, "Agent correctly denied CSV export access")
                    results.append(True)
                else:
                    self.log_test("CSV Export (Agent)", False, f"Agent should be denied access, got: {response.status_code}")
                    results.append(False)
            except Exception as e:
                self.log_test("CSV Export (Agent)", False, f"Exception: {str(e)}")
                results.append(False)
        else:
            self.log_test("CSV Export (Agent)", False, "No agent token available")
            results.append(False)
        
        return all(results)

    def test_security_stats_permissions(self):
        """Test GET /api/crm/security/stats (Manager/Technique roles)"""
        print("\n🔒 TESTING SECURITY STATS PERMISSIONS")
        print("-" * 50)
        
        if not self.role_tokens:
            self.log_test("Security Stats Permissions", False, "No role tokens available")
            return False
        
        results = []
        
        # Test Manager access
        manager_token = self.role_tokens.get("manager")
        if manager_token:
            try:
                time.sleep(1)
                headers = {"Authorization": f"Bearer {manager_token}"}
                response = self.session.get(f"{BACKEND_URL}/crm/security/stats", headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success") and "security_stats" in data:
                        self.log_test("Security Stats (Manager)", True, "Manager can access security stats")
                        results.append(True)
                    else:
                        self.log_test("Security Stats (Manager)", False, "Invalid response structure", data)
                        results.append(False)
                else:
                    self.log_test("Security Stats (Manager)", False, f"Manager access failed: {response.status_code}")
                    results.append(False)
            except Exception as e:
                self.log_test("Security Stats (Manager)", False, f"Exception: {str(e)}")
                results.append(False)
        else:
            self.log_test("Security Stats (Manager)", False, "No manager token available")
            results.append(False)
        
        # Test Technique access
        technique_token = self.role_tokens.get("technique")
        if technique_token:
            try:
                time.sleep(1)
                headers = {"Authorization": f"Bearer {technique_token}"}
                response = self.session.get(f"{BACKEND_URL}/crm/security/stats", headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success") and "security_stats" in data:
                        self.log_test("Security Stats (Technique)", True, "Technique can access security stats")
                        results.append(True)
                    else:
                        self.log_test("Security Stats (Technique)", False, "Invalid response structure", data)
                        results.append(False)
                else:
                    self.log_test("Security Stats (Technique)", False, f"Technique access failed: {response.status_code}")
                    results.append(False)
            except Exception as e:
                self.log_test("Security Stats (Technique)", False, f"Exception: {str(e)}")
                results.append(False)
        else:
            self.log_test("Security Stats (Technique)", False, "No technique token available")
            results.append(False)
        
        # Test Agent access (should fail)
        agent_token = self.role_tokens.get("agent")
        if agent_token:
            try:
                time.sleep(1)
                headers = {"Authorization": f"Bearer {agent_token}"}
                response = self.session.get(f"{BACKEND_URL}/crm/security/stats", headers=headers)
                
                if response.status_code in [401, 403]:
                    self.log_test("Security Stats (Agent)", True, "Agent correctly denied security stats access")
                    results.append(True)
                else:
                    self.log_test("Security Stats (Agent)", False, f"Agent should be denied access, got: {response.status_code}")
                    results.append(False)
            except Exception as e:
                self.log_test("Security Stats (Agent)", False, f"Exception: {str(e)}")
                results.append(False)
        else:
            self.log_test("Security Stats (Agent)", False, "No agent token available")
            results.append(False)
        
        return all(results)

    def test_cache_clear_permissions(self):
        """Test POST /api/crm/cache/clear (Manager only)"""
        print("\n🗑️ TESTING CACHE CLEAR PERMISSIONS")
        print("-" * 50)
        
        if not self.role_tokens:
            self.log_test("Cache Clear Permissions", False, "No role tokens available")
            return False
        
        results = []
        
        # Test Manager access (should work)
        manager_token = self.role_tokens.get("manager")
        if manager_token:
            try:
                time.sleep(1)
                headers = {"Authorization": f"Bearer {manager_token}", "Content-Type": "application/json"}
                response = self.session.post(f"{BACKEND_URL}/crm/cache/clear", json={"pattern": "*"}, headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        self.log_test("Cache Clear (Manager)", True, "Manager can clear cache")
                        results.append(True)
                    else:
                        self.log_test("Cache Clear (Manager)", False, "Cache clear failed", data)
                        results.append(False)
                else:
                    self.log_test("Cache Clear (Manager)", False, f"Manager access failed: {response.status_code}")
                    results.append(False)
            except Exception as e:
                self.log_test("Cache Clear (Manager)", False, f"Exception: {str(e)}")
                results.append(False)
        else:
            self.log_test("Cache Clear (Manager)", False, "No manager token available")
            results.append(False)
        
        # Test Agent access (should fail)
        agent_token = self.role_tokens.get("agent")
        if agent_token:
            try:
                time.sleep(1)
                headers = {"Authorization": f"Bearer {agent_token}", "Content-Type": "application/json"}
                response = self.session.post(f"{BACKEND_URL}/crm/cache/clear", json={"pattern": "*"}, headers=headers)
                
                if response.status_code in [401, 403]:
                    self.log_test("Cache Clear (Agent)", True, "Agent correctly denied cache clear access")
                    results.append(True)
                else:
                    self.log_test("Cache Clear (Agent)", False, f"Agent should be denied access, got: {response.status_code}")
                    results.append(False)
            except Exception as e:
                self.log_test("Cache Clear (Agent)", False, f"Exception: {str(e)}")
                results.append(False)
        else:
            self.log_test("Cache Clear (Agent)", False, "No agent token available")
            results.append(False)
        
        return all(results)

    def run_security_analytics_tests(self):
        """Run all security and analytics tests"""
        print("=" * 80)
        print("JOSMOSE.COM - SECURITY & ANALYTICS TESTING")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test started at: {datetime.now().isoformat()}")
        print()
        
        # Run tests
        auth_success = self.test_new_role_authentication()
        
        if auth_success:
            self.test_user_info_endpoint()
            self.test_analytics_dashboard_permissions()
            self.test_analytics_csv_export_permissions()
            self.test_security_stats_permissions()
            self.test_cache_clear_permissions()
        else:
            print("\n⚠️ SKIPPING PERMISSION TESTS - Authentication failed")
        
        # Summary
        print("\n" + "=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        print()
        
        # Show failed tests
        failed_tests = [r for r in self.test_results if not r["success"]]
        if failed_tests:
            print("❌ FAILED TESTS:")
            for test in failed_tests:
                print(f"  - {test['test']}: {test['details']}")
        else:
            print("✅ ALL TESTS PASSED!")
        
        print("\n" + "=" * 80)

if __name__ == "__main__":
    tester = SecurityAnalyticsTester()
    tester.run_security_analytics_tests()