#!/usr/bin/env python3
"""
Team Structure Testing for Josmose.com - New Role-Based Permissions
Tests the updated team structure with Naima as manager, Aziza and Antonio as agents.
"""

import requests
import json
from datetime import datetime

# Backend URL from environment
BACKEND_URL = "https://water-ecom-admin.preview.emergentagent.com/api"

class TeamStructureTester:
    def __init__(self):
        self.session = requests.Session()
        self.test_results = []
        
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
        """Authenticate as manager (Naima)"""
        try:
            login_data = {
                "username": "naima@josmose.com",
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
                    self.session.headers.update({
                        "Authorization": f"Bearer {data['access_token']}"
                    })
                    return True
            return False
        except Exception:
            return False

    def authenticate_agent_aziza(self):
        """Authenticate as agent (Aziza)"""
        try:
            login_data = {
                "username": "aziza@josmose.com",
                "password": "Aziza@2024!Director"
            }
            
            response = self.session.post(
                f"{BACKEND_URL}/auth/login",
                json=login_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                if "access_token" in data:
                    self.session.headers.update({
                        "Authorization": f"Bearer {data['access_token']}"
                    })
                    return True
            return False
        except Exception:
            return False

    def authenticate_agent_antonio(self):
        """Authenticate as agent (Antonio)"""
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
                    self.session.headers.update({
                        "Authorization": f"Bearer {data['access_token']}"
                    })
                    return True
            return False
        except Exception:
            return False

    def test_team_structure_authentication(self):
        """Test authentication for all team members with new roles"""
        try:
            # Clear any existing auth
            self.session.headers.pop("Authorization", None)
            
            # Test Naima (Manager)
            naima_success = self.authenticate_manager()
            
            # Clear auth and test Aziza (Agent)
            self.session.headers.pop("Authorization", None)
            aziza_success = self.authenticate_agent_aziza()
            
            # Clear auth and test Antonio (Agent)
            self.session.headers.pop("Authorization", None)
            antonio_success = self.authenticate_agent_antonio()
            
            # Test Support (Technique)
            self.session.headers.pop("Authorization", None)
            support_login_data = {
                "username": "support@josmose.com",
                "password": "Support@2024!Help"
            }
            
            support_response = self.session.post(
                f"{BACKEND_URL}/auth/login",
                json=support_login_data,
                headers={"Content-Type": "application/json"}
            )
            
            support_success = support_response.status_code == 200
            
            if naima_success and aziza_success and antonio_success and support_success:
                self.log_test("Team Structure Authentication", True, 
                            "All team members authenticated: Naima (manager), Aziza (agent), Antonio (agent), Support (technique)")
                return True
            else:
                failed_auths = []
                if not naima_success: failed_auths.append("Naima")
                if not aziza_success: failed_auths.append("Aziza")
                if not antonio_success: failed_auths.append("Antonio")
                if not support_success: failed_auths.append("Support")
                
                self.log_test("Team Structure Authentication", False, f"Failed authentications: {', '.join(failed_auths)}")
                return False
                
        except Exception as e:
            self.log_test("Team Structure Authentication", False, f"Exception: {str(e)}")
            return False

    def test_team_contacts_structure(self):
        """Test GET /api/crm/team-contacts returns new team structure"""
        try:
            response = self.session.get(f"{BACKEND_URL}/crm/team-contacts")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check structure
                required_sections = ["managers", "agents", "services"]
                if all(section in data for section in required_sections):
                    
                    # Check managers section - should only have Naima
                    managers = data["managers"]
                    if len(managers) == 1 and managers[0]["name"] == "Naima" and managers[0]["position"] == "Manager":
                        managers_correct = True
                    else:
                        managers_correct = False
                    
                    # Check agents section - should have Aziza and Antonio
                    agents = data["agents"]
                    agent_names = [agent["name"] for agent in agents]
                    agent_positions = [agent["position"] for agent in agents]
                    
                    if (len(agents) == 2 and 
                        "Aziza" in agent_names and "Antonio" in agent_names and
                        all(pos == "Agent" for pos in agent_positions)):
                        agents_correct = True
                    else:
                        agents_correct = False
                    
                    # Check services section
                    services = data["services"]
                    service_names = [service["name"] for service in services]
                    
                    if "Service Commercial" in service_names and "Support" in service_names:
                        services_correct = True
                    else:
                        services_correct = False
                    
                    if managers_correct and agents_correct and services_correct:
                        self.log_test("Team Contacts Structure", True, 
                                    f"Correct structure: 1 manager (Naima), 2 agents (Aziza, Antonio), 2 services")
                        return True
                    else:
                        issues = []
                        if not managers_correct: issues.append("managers section incorrect")
                        if not agents_correct: issues.append("agents section incorrect")
                        if not services_correct: issues.append("services section incorrect")
                        
                        self.log_test("Team Contacts Structure", False, f"Structure issues: {', '.join(issues)}")
                        return False
                else:
                    missing = [s for s in required_sections if s not in data]
                    self.log_test("Team Contacts Structure", False, f"Missing sections: {missing}")
                    return False
            else:
                self.log_test("Team Contacts Structure", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Team Contacts Structure", False, f"Exception: {str(e)}")
            return False

    def test_manager_only_endpoints(self):
        """Test that only manager (Naima) can access manager-only endpoints"""
        try:
            # Test with manager authentication (Naima)
            self.session.headers.pop("Authorization", None)
            if not self.authenticate_manager():
                self.log_test("Manager-Only Endpoints", False, "Could not authenticate as manager")
                return False
            
            # Test brand monitoring endpoints (manager-only)
            brand_status_response = self.session.get(f"{BACKEND_URL}/crm/brand-monitoring/status")
            brand_scan_response = self.session.post(f"{BACKEND_URL}/crm/brand-monitoring/force-scan")
            
            manager_access_success = (brand_status_response.status_code == 200 and 
                                    brand_scan_response.status_code == 200)
            
            # Now test with agent authentication (Aziza) - should be denied
            self.session.headers.pop("Authorization", None)
            if not self.authenticate_agent_aziza():
                self.log_test("Manager-Only Endpoints", False, "Could not authenticate as agent")
                return False
            
            # Test same endpoints with agent - should get 403
            agent_brand_status = self.session.get(f"{BACKEND_URL}/crm/brand-monitoring/status")
            agent_brand_scan = self.session.post(f"{BACKEND_URL}/crm/brand-monitoring/force-scan")
            
            agent_access_denied = (agent_brand_status.status_code == 403 and 
                                 agent_brand_scan.status_code == 403)
            
            if manager_access_success and agent_access_denied:
                self.log_test("Manager-Only Endpoints", True, 
                            "Manager has access, agents correctly denied access to brand monitoring")
                return True
            else:
                self.log_test("Manager-Only Endpoints", False, 
                            f"Manager access: {manager_access_success}, Agent denied: {agent_access_denied}")
                return False
                
        except Exception as e:
            self.log_test("Manager-Only Endpoints", False, f"Exception: {str(e)}")
            return False

    def test_manager_agent_shared_endpoints(self):
        """Test that both manager and agents can access shared endpoints"""
        try:
            # Test with manager authentication (Naima)
            self.session.headers.pop("Authorization", None)
            if not self.authenticate_manager():
                self.log_test("Manager-Agent Shared Endpoints", False, "Could not authenticate as manager")
                return False
            
            # Test abandoned cart dashboard (manager + agent access)
            manager_abandoned_carts = self.session.get(f"{BACKEND_URL}/crm/abandoned-carts/dashboard")
            
            manager_shared_access = manager_abandoned_carts.status_code == 200
            
            # Test with agent authentication (Aziza)
            self.session.headers.pop("Authorization", None)
            if not self.authenticate_agent_aziza():
                self.log_test("Manager-Agent Shared Endpoints", False, "Could not authenticate as agent")
                return False
            
            # Test same endpoints with agent - should also work
            agent_abandoned_carts = self.session.get(f"{BACKEND_URL}/crm/abandoned-carts/dashboard")
            
            agent_shared_access = agent_abandoned_carts.status_code == 200
            
            # Test with Antonio as well
            self.session.headers.pop("Authorization", None)
            if not self.authenticate_agent_antonio():
                self.log_test("Manager-Agent Shared Endpoints", False, "Could not authenticate as Antonio")
                return False
            
            antonio_abandoned_carts = self.session.get(f"{BACKEND_URL}/crm/abandoned-carts/dashboard")
            antonio_shared_access = antonio_abandoned_carts.status_code == 200
            
            if manager_shared_access and agent_shared_access and antonio_shared_access:
                self.log_test("Manager-Agent Shared Endpoints", True, 
                            "Manager and both agents have access to abandoned cart dashboard")
                return True
            else:
                self.log_test("Manager-Agent Shared Endpoints", False, 
                            f"Manager: {manager_shared_access}, Aziza: {agent_shared_access}, Antonio: {antonio_shared_access}")
                return False
                
        except Exception as e:
            self.log_test("Manager-Agent Shared Endpoints", False, f"Exception: {str(e)}")
            return False

    def run_team_structure_tests(self):
        """Run all team structure tests"""
        print("=" * 80)
        print("JOSMOSE.COM TEAM STRUCTURE TESTING - NEW ROLE-BASED PERMISSIONS")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test started at: {datetime.now().isoformat()}")
        print()
        
        print("👥 NEW TEAM STRUCTURE & ROLE PERMISSIONS TESTS")
        print("-" * 50)
        
        self.test_team_structure_authentication()
        self.test_team_contacts_structure()
        self.test_manager_only_endpoints()
        self.test_manager_agent_shared_endpoints()
        
        print()
        print("=" * 80)
        print("TEAM STRUCTURE TEST SUMMARY")
        print("=" * 80)
        
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        
        print(f"Tests passed: {passed}/{total} ({(passed/total)*100:.1f}%)")
        
        if passed == total:
            print("🎉 ALL TEAM STRUCTURE TESTS PASSED!")
            print("✅ New team structure is working correctly:")
            print("   - Naima: Manager (full access)")
            print("   - Aziza: Agent (limited access)")
            print("   - Antonio: Agent (limited access)")
            print("   - Support: Technique (very limited access)")
        else:
            print("❌ Some tests failed. Check the details above.")
            
        return passed == total

if __name__ == "__main__":
    tester = TeamStructureTester()
    success = tester.run_team_structure_tests()
    exit(0 if success else 1)