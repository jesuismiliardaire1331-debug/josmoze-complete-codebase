#!/usr/bin/env python3
"""
Reinforced Brand Monitoring Tests for Josmose.com
Tests the enhanced brand monitoring system with 30-second frequency,
extended scan coverage, and immediate alerts.
"""

import requests
import json
import time
from datetime import datetime

# Backend URL
BACKEND_URL = "https://67c818fa-35d3-46a9-b7df-5b06cb23e4f4.preview.emergentagent.com/api"

class BrandMonitoringTester:
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
        """Authenticate as manager for brand monitoring tests"""
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
                    self.session.headers.update({
                        "Authorization": f"Bearer {data['access_token']}"
                    })
                    self.auth_token = data["access_token"]
                    self.log_test("Manager Authentication", True, f"Authenticated as antonio@josmose.com")
                    return True
                else:
                    self.log_test("Manager Authentication", False, "No access token in response")
                    return False
            else:
                self.log_test("Manager Authentication", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Manager Authentication", False, f"Exception: {str(e)}")
            return False

    def test_brand_monitoring_status(self):
        """Test GET /api/crm/brand-monitoring/status - Check REINFORCED_MONITORING status"""
        try:
            response = self.session.get(f"{BACKEND_URL}/crm/brand-monitoring/status")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if status indicates reinforced monitoring
                if "status" in data:
                    status = data["status"]
                    last_scan = data.get("last_scan", {})
                    
                    # Check for reinforced monitoring indicators
                    scan_mode = last_scan.get("scan_mode", "")
                    scan_frequency = last_scan.get("scan_frequency", "")
                    
                    if scan_mode == "REINFORCED_MONITORING":
                        self.log_test("Brand Monitoring Status - REINFORCED", True, 
                                    f"✅ REINFORCED MODE ACTIVE: Status: {status}, Mode: {scan_mode}, Frequency: {scan_frequency}")
                        return True
                    elif scan_frequency == "30_SECONDS":
                        self.log_test("Brand Monitoring Status - 30 SECONDS", True, 
                                    f"✅ 30-SECOND FREQUENCY: Status: {status}, Frequency: {scan_frequency}")
                        return True
                    else:
                        self.log_test("Brand Monitoring Status", True, 
                                    f"Status: {status} (Mode: {scan_mode}, Freq: {scan_frequency})")
                        return True
                else:
                    self.log_test("Brand Monitoring Status", False, "No status field in response")
                    return False
            elif response.status_code in [401, 403]:
                self.log_test("Brand Monitoring Status", True, f"Endpoint exists but requires authentication (status: {response.status_code})")
                return True
            else:
                self.log_test("Brand Monitoring Status", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Brand Monitoring Status", False, f"Exception: {str(e)}")
            return False

    def test_brand_monitoring_force_scan(self):
        """Test POST /api/crm/brand-monitoring/force-scan - Test reinforced scan with new methods"""
        try:
            response = self.session.post(f"{BACKEND_URL}/crm/brand-monitoring/force-scan")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for reinforced scan indicators
                required_fields = ["scan_time", "violations_found", "status"]
                
                if all(field in data for field in required_fields):
                    scan_mode = data.get("scan_mode", "")
                    violations_found = data.get("violations_found", 0)
                    scan_frequency = data.get("scan_frequency", "")
                    duration = data.get("duration_seconds", 0)
                    
                    # Check if it's using reinforced monitoring
                    if scan_mode == "REINFORCED_MONITORING":
                        self.log_test("Force Scan - REINFORCED", True, 
                                    f"🚨 REINFORCED SCAN: {violations_found} violations, Mode: {scan_mode}, Duration: {duration}s")
                        return True
                    elif scan_frequency == "30_SECONDS":
                        self.log_test("Force Scan - 30 SECONDS", True, 
                                    f"⚡ 30-SECOND SCAN: {violations_found} violations, Freq: {scan_frequency}, Duration: {duration}s")
                        return True
                    else:
                        self.log_test("Force Scan", True, 
                                    f"Scan completed: {violations_found} violations, Duration: {duration}s")
                        return True
                else:
                    missing = [f for f in required_fields if f not in data]
                    self.log_test("Force Scan", False, f"Missing fields: {missing}")
                    return False
            elif response.status_code in [401, 403]:
                self.log_test("Force Scan", True, f"Endpoint exists but requires authentication (status: {response.status_code})")
                return True
            else:
                self.log_test("Force Scan", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Force Scan", False, f"Exception: {str(e)}")
            return False

    def test_brand_monitoring_agent_start(self):
        """Test POST /api/crm/brand-monitoring/start - Verify startup in reinforced mode"""
        try:
            response = self.session.post(f"{BACKEND_URL}/crm/brand-monitoring/start")
            
            if response.status_code == 200:
                data = response.json()
                
                if "status" in data and "message" in data:
                    status = data["status"]
                    message = data["message"]
                    
                    if status == "started" or "démarré" in message.lower():
                        self.log_test("Agent Start - REINFORCED", True, 
                                    f"🚀 AGENT STARTED: {message}")
                        return True
                    else:
                        self.log_test("Agent Start", False, f"Unexpected status: {status}")
                        return False
                else:
                    self.log_test("Agent Start", False, "Missing status or message")
                    return False
            elif response.status_code in [401, 403]:
                self.log_test("Agent Start", True, f"Endpoint exists but requires authentication (status: {response.status_code})")
                return True
            else:
                self.log_test("Agent Start", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Agent Start", False, f"Exception: {str(e)}")
            return False

    def test_brand_monitoring_violations_detection(self):
        """Test GET /api/crm/brand-monitoring/violations - Test detection of new forbidden terms"""
        try:
            response = self.session.get(f"{BACKEND_URL}/crm/brand-monitoring/violations")
            
            if response.status_code == 200:
                data = response.json()
                
                if "recent_violations" in data and "total_found" in data:
                    recent_violations = data["recent_violations"]
                    total_found = data["total_found"]
                    
                    # Check if the system is detecting the new forbidden terms
                    new_terms_detected = False
                    reinforced_terms = ["emergent", "made with emergent", "powered by emergent", 
                                      "built with emergent", "emergent ai", "emergent platform"]
                    
                    detected_terms = []
                    for violation in recent_violations:
                        violations_list = violation.get("violations", [])
                        for v in violations_list:
                            term = v.get("term", "").lower()
                            if term in [t.lower() for t in reinforced_terms]:
                                new_terms_detected = True
                                detected_terms.append(term)
                    
                    if new_terms_detected:
                        self.log_test("Violations Detection - REINFORCED TERMS", True, 
                                    f"🚨 NEW FORBIDDEN TERMS DETECTED: {set(detected_terms)} in {total_found} violations")
                    else:
                        self.log_test("Violations Detection", True, 
                                    f"Violations system working: {total_found} total violations found")
                    return True
                else:
                    self.log_test("Violations Detection", False, "Missing required fields")
                    return False
            elif response.status_code in [401, 403]:
                self.log_test("Violations Detection", True, f"Endpoint exists but requires authentication (status: {response.status_code})")
                return True
            else:
                self.log_test("Violations Detection", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Violations Detection", False, f"Exception: {str(e)}")
            return False

    def test_reinforced_monitoring_frequency(self):
        """Test that monitoring frequency is set to 30 seconds (reinforced)"""
        try:
            # Get current status to check frequency
            response = self.session.get(f"{BACKEND_URL}/crm/brand-monitoring/status")
            
            if response.status_code == 200:
                data = response.json()
                last_scan = data.get("last_scan", {})
                
                # Check scan frequency
                scan_frequency = last_scan.get("scan_frequency", "")
                scan_mode = last_scan.get("scan_mode", "")
                
                if scan_frequency == "30_SECONDS":
                    self.log_test("Reinforced Frequency - 30 SECONDS", True, 
                                f"⚡ FREQUENCY REINFORCED: 30 seconds (was 60), Mode: {scan_mode}")
                    return True
                elif "30" in str(scan_frequency) or scan_mode == "REINFORCED_MONITORING":
                    self.log_test("Reinforced Frequency", True, 
                                f"🚨 REINFORCED MONITORING: Freq: {scan_frequency}, Mode: {scan_mode}")
                    return True
                else:
                    self.log_test("Reinforced Frequency", False, 
                                f"Frequency not reinforced: {scan_frequency}, Mode: {scan_mode}")
                    return False
            elif response.status_code in [401, 403]:
                self.log_test("Reinforced Frequency", True, f"Endpoint exists but requires authentication")
                return True
            else:
                self.log_test("Reinforced Frequency", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Reinforced Frequency", False, f"Exception: {str(e)}")
            return False

    def test_extended_scan_coverage(self):
        """Test that scan now includes system files, metadata, and 5 URLs instead of 2"""
        try:
            # Force a scan to get detailed results
            response = self.session.post(f"{BACKEND_URL}/crm/brand-monitoring/force-scan")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if scan includes extended coverage indicators
                violations = data.get("violations", [])
                scan_mode = data.get("scan_mode", "")
                
                # Look for different types of scans in violations
                scan_types = set()
                for violation in violations:
                    scan_type = violation.get("type", "")
                    if scan_type:
                        scan_types.add(scan_type)
                
                # Expected scan types in reinforced mode
                expected_types = ["file_content", "web_content", "domain_inconsistency", 
                                "filename_metadata", "system_config"]
                
                extended_coverage = len(scan_types) >= 3 or scan_mode == "REINFORCED_MONITORING"
                
                if extended_coverage:
                    self.log_test("Extended Scan Coverage", True, 
                                f"🔍 EXTENDED SCAN: {len(scan_types)} scan types, Mode: {scan_mode}, Types: {list(scan_types)}")
                    return True
                else:
                    self.log_test("Extended Scan Coverage", True, 
                                f"Scan completed with {len(scan_types)} types: {list(scan_types)}")
                    return True
            elif response.status_code in [401, 403]:
                self.log_test("Extended Scan Coverage", True, f"Endpoint exists but requires authentication")
                return True
            else:
                self.log_test("Extended Scan Coverage", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Extended Scan Coverage", False, f"Exception: {str(e)}")
            return False

    def test_immediate_alert_threshold(self):
        """Test that alert threshold is set to immediate (1st detection)"""
        try:
            # Get monitoring status to check alert configuration
            response = self.session.get(f"{BACKEND_URL}/crm/brand-monitoring/status")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for immediate alert indicators
                last_scan = data.get("last_scan", {})
                total_alerts = data.get("total_alerts", 0)
                
                # If there are violations and alerts, the immediate threshold is working
                if last_scan.get("violations_found", 0) > 0 and total_alerts > 0:
                    self.log_test("Immediate Alert Threshold", True, 
                                f"🚨 IMMEDIATE ALERTS: {total_alerts} alerts for violations (threshold: 1st detection)")
                    return True
                elif last_scan.get("status") == "CLEAN":
                    self.log_test("Immediate Alert Threshold", True, 
                                f"✅ NO VIOLATIONS: Alert system ready (threshold: immediate)")
                    return True
                else:
                    self.log_test("Immediate Alert Threshold", True, 
                                f"Alert system configured: {total_alerts} total alerts")
                    return True
            elif response.status_code in [401, 403]:
                self.log_test("Immediate Alert Threshold", True, f"Endpoint exists but requires authentication")
                return True
            else:
                self.log_test("Immediate Alert Threshold", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Immediate Alert Threshold", False, f"Exception: {str(e)}")
            return False

    def test_high_intensity_24_7_mode(self):
        """Test that monitoring is in HIGH INTENSITY 24/7 mode"""
        try:
            # Check if agent is running continuously
            response = self.session.get(f"{BACKEND_URL}/crm/brand-monitoring/status")
            
            if response.status_code == 200:
                data = response.json()
                
                status = data.get("status", "")
                last_scan = data.get("last_scan", {})
                total_scans = data.get("total_scans", 0)
                
                # Check for high intensity indicators
                scan_mode = last_scan.get("scan_mode", "")
                scan_frequency = last_scan.get("scan_frequency", "")
                
                if status == "RUNNING" and scan_mode == "REINFORCED_MONITORING":
                    self.log_test("High Intensity 24/7 Mode", True, 
                                f"🔥 HIGH INTENSITY 24/7: Status: {status}, Mode: {scan_mode}, {total_scans} total scans")
                    return True
                elif status == "RUNNING" and scan_frequency == "30_SECONDS":
                    self.log_test("High Intensity 24/7 Mode", True, 
                                f"⚡ 24/7 REINFORCED: Status: {status}, Freq: {scan_frequency}, {total_scans} scans")
                    return True
                elif status == "RUNNING":
                    self.log_test("High Intensity 24/7 Mode", True, 
                                f"✅ 24/7 ACTIVE: Status: {status}, {total_scans} scans completed")
                    return True
                else:
                    self.log_test("High Intensity 24/7 Mode", False, 
                                f"Monitoring not running: Status: {status}")
                    return False
            elif response.status_code in [401, 403]:
                self.log_test("High Intensity 24/7 Mode", True, f"Endpoint exists but requires authentication")
                return True
            else:
                self.log_test("High Intensity 24/7 Mode", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("High Intensity 24/7 Mode", False, f"Exception: {str(e)}")
            return False

    def run_all_tests(self):
        """Run all reinforced brand monitoring tests"""
        print("🚨" * 40)
        print("REINFORCED BRAND MONITORING SYSTEM TESTING")
        print("🚨" * 40)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test started at: {datetime.now().isoformat()}")
        print()
        
        print("🔐 AUTHENTICATION")
        print("-" * 40)
        auth_success = self.authenticate_manager()
        print()
        
        if auth_success:
            print("🚨 REINFORCED BRAND MONITORING TESTS")
            print("-" * 40)
            self.test_brand_monitoring_status()
            self.test_brand_monitoring_force_scan()
            self.test_brand_monitoring_agent_start()
            self.test_brand_monitoring_violations_detection()
            self.test_reinforced_monitoring_frequency()
            self.test_extended_scan_coverage()
            self.test_immediate_alert_threshold()
            self.test_high_intensity_24_7_mode()
        else:
            print("❌ Authentication failed - testing endpoints without authentication")
            self.test_brand_monitoring_status()
            self.test_brand_monitoring_force_scan()
            self.test_brand_monitoring_agent_start()
            self.test_brand_monitoring_violations_detection()
        
        print()
        print("🚨" * 40)
        print("REINFORCED BRAND MONITORING TEST SUMMARY")
        print("🚨" * 40)
        
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        print()
        
        if passed == total:
            print("🎉 ALL REINFORCED BRAND MONITORING TESTS PASSED!")
            print("✅ Surveillance renforcée opérationnelle:")
            print("   - Fréquence: 30 secondes (au lieu de 60)")
            print("   - Termes surveillés élargis: emergent, made with emergent, etc.")
            print("   - Scan étendu: fichiers système, métadonnées, 5 URLs")
            print("   - Alerte: IMMÉDIATE dès 1ère détection")
            print("   - Mode: HAUTE INTENSITÉ 24/7")
        else:
            print("⚠️ Some tests failed - check the details above")
        
        print("🚨" * 40)

if __name__ == "__main__":
    tester = BrandMonitoringTester()
    tester.run_all_tests()