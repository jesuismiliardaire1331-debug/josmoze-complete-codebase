#!/usr/bin/env python3
"""
Focused test for @osmose.com professional email system
Tests the new team contacts endpoint and authentication mapping
"""

import requests
import json
from datetime import datetime

# Backend URL from environment
BACKEND_URL = "https://ecomm-rescue.preview.emergentagent.com/api"

class OsmoseEmailTester:
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
    
    def test_team_contacts_endpoint(self):
        """Test GET /api/crm/team-contacts - New professional email addresses @osmose.com"""
        try:
            response = self.session.get(f"{BACKEND_URL}/crm/team-contacts")
            
            if response.status_code == 200:
                data = response.json()
                required_sections = ["managers", "services", "contact_general"]
                
                if all(section in data for section in required_sections):
                    managers = data["managers"]
                    services = data["services"]
                    
                    # Check for expected @osmose.com email addresses
                    expected_manager_emails = [
                        "antonio@osmose.com",
                        "aziza@osmose.com", 
                        "naima@osmose.com"
                    ]
                    
                    expected_service_emails = [
                        "commercial@osmose.com",
                        "support@osmose.com"
                    ]
                    
                    # Verify manager emails
                    manager_emails = [manager.get("email") for manager in managers]
                    managers_found = all(email in manager_emails for email in expected_manager_emails)
                    
                    # Verify service emails
                    service_emails = [service.get("email") for service in services]
                    services_found = all(email in service_emails for email in expected_service_emails)
                    
                    if managers_found and services_found:
                        self.log_test("Team Contacts Endpoint", True, 
                                    f"All @osmose.com emails found: {len(manager_emails)} managers, {len(service_emails)} services")
                        
                        # Print detailed information
                        print("   📧 Manager emails found:")
                        for manager in managers:
                            print(f"      - {manager.get('name')} ({manager.get('position')}) -> {manager.get('email')}")
                        
                        print("   📧 Service emails found:")
                        for service in services:
                            print(f"      - {service.get('name')} ({service.get('position')}) -> {service.get('email')}")
                        
                        return True
                    else:
                        missing_managers = [email for email in expected_manager_emails if email not in manager_emails]
                        missing_services = [email for email in expected_service_emails if email not in service_emails]
                        self.log_test("Team Contacts Endpoint", False, 
                                    f"Missing emails - Managers: {missing_managers}, Services: {missing_services}")
                        return False
                else:
                    missing = [section for section in required_sections if section not in data]
                    self.log_test("Team Contacts Endpoint", False, f"Missing sections: {missing}")
                    return False
            else:
                self.log_test("Team Contacts Endpoint", False, f"Status: {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("Team Contacts Endpoint", False, f"Exception: {str(e)}")
            return False

    def test_authentication_with_professional_emails(self):
        """Test authentication system with new @josmose.com login -> @osmose.com professional emails"""
        try:
            # Test credentials mapping: login@josmose.com -> professional@osmose.com
            test_credentials = [
                {
                    "login_email": "antonio@josmose.com",
                    "password": "Antonio@2024!Secure",
                    "expected_professional_email": "antonio@osmose.com",
                    "expected_role": "manager",
                    "expected_name": "Antonio"
                },
                {
                    "login_email": "aziza@josmose.com", 
                    "password": "Aziza@2024!Director",
                    "expected_professional_email": "aziza@osmose.com",
                    "expected_role": "manager",
                    "expected_name": "Aziza"
                },
                {
                    "login_email": "naima@josmose.com",
                    "password": "Naima@2024!Commerce", 
                    "expected_professional_email": "naima@osmose.com",
                    "expected_role": "manager",
                    "expected_name": "Naima"
                },
                {
                    "login_email": "commercial@josmose.com",
                    "password": "Commercial@2024!Sales",
                    "expected_professional_email": "commercial@osmose.com", 
                    "expected_role": "commercial",
                    "expected_name": "Commercial"
                }
            ]
            
            successful_auths = 0
            
            for cred in test_credentials:
                try:
                    print(f"\n   🔐 Testing login: {cred['login_email']}")
                    
                    # Test login
                    login_data = {
                        "username": cred["login_email"],
                        "password": cred["password"]
                    }
                    
                    response = self.session.post(
                        f"{BACKEND_URL}/auth/login",
                        json=login_data,  # JSON data for UserAuth model
                        headers={"Content-Type": "application/json"}
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        if "access_token" in data:
                            # Get user info with token
                            token = data["access_token"]
                            headers = {"Authorization": f"Bearer {token}"}
                            
                            user_response = self.session.get(f"{BACKEND_URL}/auth/user-info", headers=headers)
                            
                            if user_response.status_code == 200:
                                user_data = user_response.json()
                                user_info = user_data.get("user", {})
                                
                                # Check if professional email mapping is correct
                                professional_email = user_info.get("email")
                                role = user_info.get("role")
                                name = user_info.get("full_name", "")
                                username = user_info.get("username", "")
                                
                                print(f"      Login successful: {username} -> {professional_email} (Role: {role})")
                                
                                # Check if the mapping is working (login@josmose.com -> professional@osmose.com)
                                if professional_email == cred["expected_professional_email"]:
                                    self.log_test(f"Auth {cred['expected_name']} Email Mapping", True, 
                                                f"Correct mapping: {cred['login_email']} -> {professional_email}")
                                    successful_auths += 1
                                else:
                                    self.log_test(f"Auth {cred['expected_name']} Email Mapping", False, 
                                                f"Wrong email mapping: expected {cred['expected_professional_email']}, got {professional_email}")
                                
                                # Check role
                                if role == cred["expected_role"]:
                                    self.log_test(f"Auth {cred['expected_name']} Role", True, f"Correct role: {role}")
                                else:
                                    self.log_test(f"Auth {cred['expected_name']} Role", False, f"Wrong role: expected {cred['expected_role']}, got {role}")
                                    
                            else:
                                self.log_test(f"Auth {cred['expected_name']}", False, f"User info failed: {user_response.status_code}")
                        else:
                            self.log_test(f"Auth {cred['expected_name']}", False, "No access token in response")
                    else:
                        self.log_test(f"Auth {cred['expected_name']}", False, f"Login failed: {response.status_code}")
                        
                except Exception as auth_e:
                    self.log_test(f"Auth {cred['expected_name']}", False, f"Exception: {str(auth_e)}")
            
            if successful_auths >= 3:  # At least 3 out of 4 should work
                self.log_test("Professional Email Authentication", True, f"{successful_auths}/4 authentications successful")
                return True
            else:
                self.log_test("Professional Email Authentication", False, f"Only {successful_auths}/4 authentications successful")
                return False
                
        except Exception as e:
            self.log_test("Professional Email Authentication", False, f"Exception: {str(e)}")
            return False

    def test_commercial_role_permissions(self):
        """Test that commercial@josmose.com has appropriate permissions"""
        try:
            print(f"\n   🔐 Testing commercial role permissions...")
            
            # Login as commercial user
            login_data = {
                "username": "commercial@josmose.com",
                "password": "Commercial@2024!Sales"
            }
            
            response = self.session.post(
                f"{BACKEND_URL}/auth/login",
                json=login_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                if "access_token" in data:
                    token = data["access_token"]
                    headers = {"Authorization": f"Bearer {token}"}
                    
                    # Test CRM permissions
                    crm_response = self.session.get(f"{BACKEND_URL}/crm/user-permissions", headers=headers)
                    
                    if crm_response.status_code == 200:
                        permissions_data = crm_response.json()
                        permissions = permissions_data.get("permissions", {})
                        user_info = permissions_data.get("user", {})
                        
                        print(f"      Commercial user info: {user_info.get('email')} (Role: {user_info.get('role')})")
                        print(f"      Permissions: {list(permissions.keys())}")
                        
                        # Check if commercial role has appropriate permissions
                        expected_permissions = [
                            "view_dashboard", "edit_leads", "view_orders"
                        ]
                        
                        has_permissions = all(permissions.get(perm, False) for perm in expected_permissions)
                        
                        if has_permissions and user_info.get("role") == "commercial":
                            self.log_test("Commercial Role Permissions", True, 
                                        f"Commercial role has appropriate permissions: {list(permissions.keys())}")
                            return True
                        else:
                            missing_perms = [perm for perm in expected_permissions if not permissions.get(perm, False)]
                            self.log_test("Commercial Role Permissions", False, 
                                        f"Missing permissions: {missing_perms}, Role: {user_info.get('role')}")
                            return False
                    else:
                        self.log_test("Commercial Role Permissions", False, f"Permissions check failed: {crm_response.status_code}")
                        return False
                else:
                    self.log_test("Commercial Role Permissions", False, "No access token received")
                    return False
            else:
                self.log_test("Commercial Role Permissions", False, f"Commercial login failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Commercial Role Permissions", False, f"Exception: {str(e)}")
            return False

    def test_email_system_consistency(self):
        """Test consistency between team contacts and authentication system"""
        try:
            print(f"\n   📊 Testing email system consistency...")
            
            # Get team contacts
            contacts_response = self.session.get(f"{BACKEND_URL}/crm/team-contacts")
            
            if contacts_response.status_code == 200:
                contacts_data = contacts_response.json()
                
                # Extract all professional emails
                all_contacts = []
                all_contacts.extend(contacts_data.get("managers", []))
                all_contacts.extend(contacts_data.get("services", []))
                
                # Check consistency of names, positions, and departments
                consistency_checks = []
                
                for contact in all_contacts:
                    email = contact.get("email", "")
                    name = contact.get("name", "")
                    position = contact.get("position", "")
                    department = contact.get("department", "")
                    speciality = contact.get("speciality", "")
                    
                    print(f"      Checking: {name} ({position}) -> {email}")
                    
                    # Verify expected mappings
                    if email == "antonio@osmose.com":
                        expected = {"name": "Antonio", "position": "Directeur Général", "department": "Direction Générale"}
                        actual = {"name": name, "position": position, "department": department}
                        consistency_checks.append(("Antonio", expected == actual, f"Expected: {expected}, Got: {actual}"))
                    
                    elif email == "aziza@osmose.com":
                        expected = {"name": "Aziza", "position": "Directrice Adjointe", "department": "Direction Adjointe"}
                        actual = {"name": name, "position": position, "department": department}
                        consistency_checks.append(("Aziza", expected == actual, f"Expected: {expected}, Got: {actual}"))
                    
                    elif email == "naima@osmose.com":
                        expected = {"name": "Naima", "position": "Directrice Commerciale", "department": "Direction Commerciale"}
                        actual = {"name": name, "position": position, "department": department}
                        consistency_checks.append(("Naima", expected == actual, f"Expected: {expected}, Got: {actual}"))
                    
                    elif email == "commercial@osmose.com":
                        expected = {"name": "Service Commercial", "position": "Équipe Commerciale", "department": "Service Commercial"}
                        actual = {"name": name, "position": position, "department": department}
                        consistency_checks.append(("Commercial", expected == actual, f"Expected: {expected}, Got: {actual}"))
                    
                    elif email == "support@osmose.com":
                        expected = {"name": "Support Technique", "position": "Technicien Support", "department": "Support Technique"}
                        actual = {"name": name, "position": position, "department": department}
                        consistency_checks.append(("Support", expected == actual, f"Expected: {expected}, Got: {actual}"))
                
                # Check results
                all_consistent = all(check[1] for check in consistency_checks)
                
                if all_consistent:
                    self.log_test("Email System Consistency", True, 
                                f"All {len(consistency_checks)} contacts have consistent information")
                    return True
                else:
                    failed_checks = [check for check in consistency_checks if not check[1]]
                    self.log_test("Email System Consistency", False, 
                                f"Inconsistent data for: {[check[0] for check in failed_checks]}")
                    for check in failed_checks:
                        print(f"      ❌ {check[0]}: {check[2]}")
                    return False
            else:
                self.log_test("Email System Consistency", False, f"Could not get team contacts: {contacts_response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Email System Consistency", False, f"Exception: {str(e)}")
            return False

    def run_osmose_email_tests(self):
        """Run all @osmose.com email system tests"""
        print("=" * 80)
        print("📧 TESTING NEW @OSMOSE.COM PROFESSIONAL EMAIL SYSTEM")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test started at: {datetime.now().isoformat()}")
        print()
        
        # Run the tests
        print("🔍 Testing team contacts endpoint...")
        self.test_team_contacts_endpoint()
        print()
        
        print("🔐 Testing authentication with professional emails...")
        self.test_authentication_with_professional_emails()
        print()
        
        print("👤 Testing commercial role permissions...")
        self.test_commercial_role_permissions()
        print()
        
        print("📊 Testing email system consistency...")
        self.test_email_system_consistency()
        print()
        
        # Print summary
        print("=" * 80)
        print("📧 @OSMOSE.COM EMAIL SYSTEM TEST SUMMARY")
        print("=" * 80)
        
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        if total - passed > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"   - {result['test']}: {result['details']}")
        
        print("\n✅ PASSED TESTS:")
        for result in self.test_results:
            if result["success"]:
                print(f"   - {result['test']}: {result['details']}")

if __name__ == "__main__":
    tester = OsmoseEmailTester()
    tester.run_osmose_email_tests()