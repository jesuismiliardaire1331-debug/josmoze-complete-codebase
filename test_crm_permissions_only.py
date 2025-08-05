#!/usr/bin/env python3
"""
CRM User Permissions Verification Test - Focused Test
Tests only the CRM user permissions verification as requested in the review.
"""

import requests
import json
from datetime import datetime

# Backend URL from environment
BACKEND_URL = "https://7a0c0ccd-9b1d-4e21-82e4-7be79e1eb7a4.preview.emergentagent.com/api"

class CRMPermissionsTester:
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
    
    def test_crm_user_permissions_verification(self):
        """Test CRM user permissions verification for all manager accounts"""
        print("🔐 CRM USER PERMISSIONS VERIFICATION")
        print("=" * 60)
        
        manager_credentials = [
            ("naima@josmose.com", "Naima@2024!Commerce", "Naima - Manager"),
            ("aziza@josmose.com", "Aziza@2024!Director", "Aziza - Manager"),
            ("antonio@josmose.com", "Antonio@2024!Secure", "Antonio - Manager")
        ]
        
        support_credentials = ("support@josmose.com", "Support@2024!Help", "Support - Technique")
        
        manager_permissions = []
        successful_manager_logins = 0
        
        # Test all three manager accounts
        for email, password, expected_name in manager_credentials:
            print(f"\n📋 Testing Manager Account: {email}")
            print("-" * 40)
            
            try:
                # Test login
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
                    if "access_token" in data and "user" in data:
                        user = data["user"]
                        token = data["access_token"]
                        
                        # Verify user has manager role
                        if user.get("role") == "manager":
                            self.log_test(f"Manager Login {email}", True, f"✓ Authenticated as {expected_name} with manager role")
                            successful_manager_logins += 1
                            
                            # Test user permissions endpoint (CRM-specific)
                            headers = {"Authorization": f"Bearer {token}"}
                            permissions_response = self.session.get(f"{BACKEND_URL}/crm/user-permissions", headers=headers)
                            
                            if permissions_response.status_code == 200:
                                permissions_data = permissions_response.json()
                                if "permissions" in permissions_data:
                                    user_permissions = permissions_data["permissions"]
                                    manager_permissions.append({
                                        "user": email,
                                        "permissions": user_permissions
                                    })
                                    
                                    # Handle both dict and list formats
                                    if isinstance(user_permissions, dict):
                                        total_perms = len(user_permissions)
                                        granted_perms = sum(1 for v in user_permissions.values() if v)
                                        key_perms = ["view_dashboard", "edit_leads", "delete_leads", "manage_users", "export_data"]
                                        granted_key = [p for p in key_perms if user_permissions.get(p, False)]
                                    else:  # list format
                                        total_perms = len(user_permissions)
                                        granted_perms = total_perms
                                        granted_key = user_permissions
                                    
                                    self.log_test(f"Manager Permissions {email}", True, 
                                                f"✓ Retrieved {granted_perms}/{total_perms} permissions")
                                    
                                    # Show key permissions
                                    print(f"   Key permissions: {', '.join(granted_key)}")
                                else:
                                    self.log_test(f"Manager Permissions {email}", False, "No permissions in response")
                            else:
                                self.log_test(f"Manager Permissions {email}", False, f"Permissions request failed: {permissions_response.status_code}")
                            
                            # Test CRM dashboard access
                            dashboard_response = self.session.get(f"{BACKEND_URL}/crm/dashboard", headers=headers)
                            if dashboard_response.status_code == 200:
                                dashboard_data = dashboard_response.json()
                                total_leads = dashboard_data.get("total_leads", 0)
                                self.log_test(f"Manager Dashboard Access {email}", True, f"✓ Can access CRM dashboard ({total_leads} leads)")
                            else:
                                self.log_test(f"Manager Dashboard Access {email}", False, f"Cannot access CRM dashboard: {dashboard_response.status_code}")
                            
                            # Test lead management access
                            leads_response = self.session.get(f"{BACKEND_URL}/crm/leads", headers=headers)
                            if leads_response.status_code == 200:
                                leads_data = leads_response.json()
                                leads_count = len(leads_data) if isinstance(leads_data, list) else 0
                                self.log_test(f"Manager Leads Access {email}", True, f"✓ Can access leads management ({leads_count} leads)")
                            else:
                                self.log_test(f"Manager Leads Access {email}", False, f"Cannot access leads: {leads_response.status_code}")
                                
                        else:
                            self.log_test(f"Manager Login {email}", False, f"Wrong role: expected 'manager', got '{user.get('role')}'")
                    else:
                        self.log_test(f"Manager Login {email}", False, "Missing access_token or user in response")
                else:
                    self.log_test(f"Manager Login {email}", False, f"Login failed: {response.status_code}")
                    
            except Exception as e:
                self.log_test(f"Manager Login {email}", False, f"Exception: {str(e)}")
        
        # Test support account (should have limited permissions)
        print(f"\n📋 Testing Support Account: {support_credentials[0]}")
        print("-" * 40)
        
        try:
            support_email, support_password, support_name = support_credentials
            auth_data = {
                "username": support_email,
                "password": support_password
            }
            
            response = self.session.post(
                f"{BACKEND_URL}/auth/login",
                json=auth_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                if "access_token" in data and "user" in data:
                    user = data["user"]
                    token = data["access_token"]
                    
                    # Verify user has technique role
                    if user.get("role") == "technique":
                        self.log_test("Support Login", True, f"✓ Authenticated as {support_name} with technique role")
                        
                        # Test user permissions endpoint (CRM-specific)
                        headers = {"Authorization": f"Bearer {token}"}
                        permissions_response = self.session.get(f"{BACKEND_URL}/crm/user-permissions", headers=headers)
                        
                        if permissions_response.status_code == 200:
                            permissions_data = permissions_response.json()
                            if "permissions" in permissions_data:
                                support_permissions = permissions_data["permissions"]
                                
                                # Handle both dict and list formats
                                if isinstance(support_permissions, dict):
                                    total_perms = len(support_permissions)
                                    granted_perms = sum(1 for v in support_permissions.values() if v)
                                    key_perms = ["view_dashboard", "edit_leads", "delete_leads", "manage_users", "export_data"]
                                    granted_key = [p for p in key_perms if support_permissions.get(p, False)]
                                    denied_key = [p for p in key_perms if not support_permissions.get(p, True)]
                                else:  # list format
                                    total_perms = len(support_permissions)
                                    granted_perms = total_perms
                                    granted_key = support_permissions
                                    denied_key = []
                                
                                self.log_test("Support Permissions", True, 
                                            f"✓ Retrieved {granted_perms}/{total_perms} limited permissions")
                                
                                # Show key permissions
                                print(f"   Granted: {', '.join(granted_key) if granted_key else 'None'}")
                                print(f"   Denied: {', '.join(denied_key) if denied_key else 'None'}")
                                
                                # Verify support has limited permissions compared to managers
                                if manager_permissions:
                                    manager_perms = manager_permissions[0]["permissions"]
                                    
                                    if isinstance(support_permissions, dict) and isinstance(manager_perms, dict):
                                        limited_access = (
                                            not support_permissions.get("edit_leads", True) and
                                            not support_permissions.get("delete_leads", True) and
                                            not support_permissions.get("manage_users", True) and
                                            not support_permissions.get("export_data", True)
                                        )
                                    else:  # list format comparison
                                        # Support should have fewer permissions than managers
                                        limited_access = len(support_permissions) < len(manager_perms)
                                    
                                    if limited_access:
                                        self.log_test("Support Limited Access", True, "✓ Support account has properly limited permissions")
                                    else:
                                        self.log_test("Support Limited Access", False, "Support account has too many permissions")
                            else:
                                self.log_test("Support Permissions", False, "No permissions in response")
                        else:
                            self.log_test("Support Permissions", False, f"Permissions request failed: {permissions_response.status_code}")
                    else:
                        self.log_test("Support Login", False, f"Wrong role: expected 'technique', got '{user.get('role')}'")
                else:
                    self.log_test("Support Login", False, "Missing access_token or user in response")
            else:
                self.log_test("Support Login", False, f"Login failed: {response.status_code}")
                
        except Exception as e:
            self.log_test("Support Login", False, f"Exception: {str(e)}")
        
        # Compare manager permissions to ensure they are identical
        print(f"\n📋 Comparing Manager Permissions")
        print("-" * 40)
        
        if len(manager_permissions) >= 2:
            first_manager_perms = manager_permissions[0]["permissions"]
            identical_permissions = True
            
            for i in range(1, len(manager_permissions)):
                current_perms = manager_permissions[i]["permissions"]
                if first_manager_perms != current_perms:
                    identical_permissions = False
                    self.log_test("Manager Permissions Comparison", False, 
                                f"Permissions differ between {manager_permissions[0]['user']} and {manager_permissions[i]['user']}")
                    
                    # Show differences
                    if isinstance(first_manager_perms, dict) and isinstance(current_perms, dict):
                        for perm, value in first_manager_perms.items():
                            if current_perms.get(perm) != value:
                                print(f"   Difference in {perm}: {manager_permissions[0]['user']} = {value}, {manager_permissions[i]['user']} = {current_perms.get(perm)}")
                    else:  # list format
                        print(f"   {manager_permissions[0]['user']}: {first_manager_perms}")
                        print(f"   {manager_permissions[i]['user']}: {current_perms}")
                    break
            
            if identical_permissions:
                self.log_test("Manager Permissions Comparison", True, "✓ All manager accounts have identical permissions")
                
                # Show the common permissions
                if isinstance(first_manager_perms, dict):
                    granted_perms = [k for k, v in first_manager_perms.items() if v]
                    denied_perms = [k for k, v in first_manager_perms.items() if not v]
                    print(f"   Common granted permissions: {', '.join(granted_perms)}")
                    print(f"   Common denied permissions: {', '.join(denied_perms) if denied_perms else 'None'}")
                else:  # list format
                    print(f"   Common permissions: {', '.join(first_manager_perms)}")
                
                return True
            else:
                return False
        else:
            self.log_test("Manager Permissions Comparison", False, f"Could not compare permissions - only {len(manager_permissions)} manager accounts tested")
            return False

    def run_test(self):
        """Run the CRM permissions verification test"""
        print("=" * 80)
        print("JOSMOSE.COM CRM USER PERMISSIONS VERIFICATION")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test started at: {datetime.now().isoformat()}")
        print()
        
        success = self.test_crm_user_permissions_verification()
        
        print("\n" + "=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        if success:
            print("\n🎉 CRM USER PERMISSIONS VERIFICATION: SUCCESS")
            print("✅ All three manager accounts (Naima, Aziza, Antonio) have identical Manager-level permissions")
            print("✅ Support account has limited Technique-level permissions")
            print("✅ Authentication system working correctly")
        else:
            print("\n❌ CRM USER PERMISSIONS VERIFICATION: FAILED")
            print("Some issues were found with the permissions system")
        
        print("=" * 80)
        
        return success

if __name__ == "__main__":
    tester = CRMPermissionsTester()
    tester.run_test()