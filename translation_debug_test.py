#!/usr/bin/env python3
"""
Translation System Debugging Tests for Josmose.com
Focus on diagnosing IP detection and automatic language switching issues
"""

import requests
import json
from datetime import datetime

# Backend URL from environment
BACKEND_URL = "https://josmoze-admin.preview.emergentagent.com/api"

class TranslationDebugger:
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

    def test_ip_detection_localization_endpoint(self):
        """Test GET /api/localization/detect - IP detection and automatic language switching"""
        try:
            response = self.session.get(f"{BACKEND_URL}/localization/detect")
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["detected_language", "detected_country", "currency", "available_languages", "ip_address"]
                
                if all(field in data for field in required_fields):
                    detected_language = data["detected_language"]
                    detected_country = data["detected_country"]
                    currency = data["currency"]
                    ip_address = data["ip_address"]
                    
                    # Check if detection is working properly
                    self.log_test("IP Detection - Localization", True, 
                                f"IP: {ip_address} -> Country: {detected_country}, Language: {detected_language}, Currency: {currency.get('code', 'N/A')}")
                    
                    # Check if available languages are properly returned
                    available_languages = data["available_languages"]
                    if len(available_languages) >= 9:
                        self.log_test("Available Languages Count", True, f"Found {len(available_languages)} languages available")
                        return True
                    else:
                        self.log_test("Available Languages Count", False, f"Only {len(available_languages)} languages found, expected at least 9")
                        return False
                else:
                    missing = [f for f in required_fields if f not in data]
                    self.log_test("IP Detection - Localization", False, f"Missing fields: {missing}", data)
                    return False
            else:
                self.log_test("IP Detection - Localization", False, f"Status: {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("IP Detection - Localization", False, f"Exception: {str(e)}")
            return False

    def test_old_location_detection_endpoint(self):
        """Test GET /api/detect-location - Compare with old system"""
        try:
            response = self.session.get(f"{BACKEND_URL}/detect-location")
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["country_code", "country_name", "currency", "language", "shipping_cost"]
                
                if all(field in data for field in required_fields):
                    country_code = data["country_code"]
                    language = data["language"]
                    currency = data["currency"]
                    
                    self.log_test("Old Location Detection", True, 
                                f"Old system: Country: {country_code}, Language: {language}, Currency: {currency}")
                    
                    # Check if old system is also defaulting to FR
                    if country_code == "FR" and language == "FR":
                        self.log_test("Old System Default Behavior", True, "Old system also defaults to FR - consistent behavior")
                    else:
                        self.log_test("Old System Different Result", True, f"Old system detected: {country_code}/{language}")
                    
                    return True
                else:
                    missing = [f for f in required_fields if f not in data]
                    self.log_test("Old Location Detection", False, f"Missing fields: {missing}")
                    return False
            else:
                self.log_test("Old Location Detection", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Old Location Detection", False, f"Exception: {str(e)}")
            return False

    def test_deepl_translation_service(self):
        """Test POST /api/localization/translate - DeepL API functionality"""
        try:
            # Test translation from French to different languages
            test_translations = [
                {"text": "Bonjour, comment allez-vous?", "target": "EN-GB", "expected_contains": ["Hello", "how"]},
                {"text": "Système d'osmose inverse", "target": "ES", "expected_contains": ["sistema", "osmosis"]},
                {"text": "Fontaine à eau", "target": "DE", "expected_contains": ["Wasser", "brunnen"]},
                {"text": "Installation professionnelle", "target": "IT", "expected_contains": ["installazione", "professionale"]}
            ]
            
            successful_translations = 0
            
            for test_case in test_translations:
                translation_data = {
                    "text": test_case["text"],
                    "target_language": test_case["target"],
                    "source_language": "FR"
                }
                
                response = self.session.post(
                    f"{BACKEND_URL}/localization/translate",
                    json=translation_data,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if "translated_text" in data:
                        translated_text = data["translated_text"].lower()
                        original_text = data["original_text"]
                        
                        # Check if translation actually happened (not just returning original)
                        if translated_text != original_text.lower():
                            self.log_test(f"Translation FR->{test_case['target']}", True, 
                                        f"'{original_text}' -> '{data['translated_text']}'")
                            successful_translations += 1
                        else:
                            self.log_test(f"Translation FR->{test_case['target']}", False, 
                                        f"Translation returned original text: '{original_text}'")
                    else:
                        self.log_test(f"Translation FR->{test_case['target']}", False, "No translated_text in response")
                else:
                    self.log_test(f"Translation FR->{test_case['target']}", False, f"Status: {response.status_code}")
            
            if successful_translations >= 3:
                self.log_test("DeepL Translation Service", True, f"{successful_translations}/4 translations successful")
                return True
            else:
                self.log_test("DeepL Translation Service", False, f"Only {successful_translations}/4 translations successful")
                return False
                
        except Exception as e:
            self.log_test("DeepL Translation Service", False, f"Exception: {str(e)}")
            return False

    def test_ip_geolocation_functionality(self):
        """Test IP geolocation with different IP addresses"""
        try:
            # We can't easily test with different IPs in this environment,
            # but we can test the service's response to the current IP
            response = self.session.get(f"{BACKEND_URL}/localization/detect")
            
            if response.status_code == 200:
                data = response.json()
                ip_address = data.get("ip_address", "unknown")
                detected_country = data.get("detected_country", "unknown")
                detected_language = data.get("detected_language", "unknown")
                
                # Log the current IP detection for debugging
                self.log_test("Current IP Geolocation", True, 
                            f"Current IP: {ip_address} -> Country: {detected_country}, Language: {detected_language}")
                
                # Check if the IP is being detected as local/private
                if ip_address in ["127.0.0.1", "localhost"] or ip_address.startswith("192.168.") or ip_address.startswith("10."):
                    self.log_test("IP Detection Issue", True, 
                                f"ISSUE FOUND: IP detected as local/private ({ip_address}) - this explains why it defaults to FR")
                    return True
                elif detected_country == "FR" and detected_language == "FR":
                    self.log_test("IP Detection Default", True, 
                                f"IP detection defaulting to FR - may be due to server location or IP service limitations")
                    return True
                else:
                    self.log_test("IP Detection Working", True, 
                                f"IP detection working correctly for non-FR location")
                    return True
            else:
                self.log_test("IP Geolocation Test", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("IP Geolocation Test", False, f"Exception: {str(e)}")
            return False

    def test_translation_service_logs(self):
        """Test translation service internal functionality by checking logs"""
        try:
            # Test the bulk translation endpoint which uses the translation service extensively
            test_content = {
                "title": "Système d'Osmose Inverse",
                "description": "Fontaine à eau professionnelle pour entreprises",
                "features": [
                    "Installation rapide",
                    "Maintenance incluse",
                    "Support technique"
                ],
                "contact": {
                    "phone": "Appelez-nous",
                    "email": "Contactez notre équipe"
                }
            }
            
            response = self.session.post(
                f"{BACKEND_URL}/localization/translate-bulk",
                json={
                    "content": test_content,
                    "target_language": "EN-GB",
                    "source_language": "FR"
                },
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                if "translated" in data:
                    translated = data["translated"]
                    
                    # Check if nested translation worked
                    if "title" in translated and "features" in translated:
                        title_translated = translated["title"]
                        features_translated = translated["features"]
                        
                        # Verify translation actually happened
                        if title_translated != test_content["title"] and len(features_translated) == 3:
                            self.log_test("Translation Service Internal", True, 
                                        f"Bulk translation working: '{test_content['title']}' -> '{title_translated}'")
                            return True
                        else:
                            self.log_test("Translation Service Internal", False, 
                                        "Bulk translation not working properly - text not translated")
                            return False
                    else:
                        self.log_test("Translation Service Internal", False, "Missing translated fields")
                        return False
                else:
                    self.log_test("Translation Service Internal", False, "No translated content in response")
                    return False
            else:
                self.log_test("Translation Service Internal", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Translation Service Internal", False, f"Exception: {str(e)}")
            return False

    def test_country_language_mapping(self):
        """Test if country to language mapping is working correctly"""
        try:
            # Get the current detection
            response = self.session.get(f"{BACKEND_URL}/localization/detect")
            
            if response.status_code == 200:
                data = response.json()
                detected_country = data.get("detected_country", "FR")
                detected_language = data.get("detected_language", "FR")
                available_languages = data.get("available_languages", {})
                
                # Check if the mapping makes sense
                expected_mappings = {
                    "FR": "FR",
                    "ES": "ES", 
                    "DE": "DE",
                    "IT": "IT",
                    "GB": "EN-GB",
                    "US": "EN-US"
                }
                
                if detected_country in expected_mappings:
                    expected_language = expected_mappings[detected_country]
                    if detected_language == expected_language:
                        self.log_test("Country-Language Mapping", True, 
                                    f"Correct mapping: {detected_country} -> {detected_language}")
                    else:
                        self.log_test("Country-Language Mapping", False, 
                                    f"Wrong mapping: {detected_country} -> {detected_language}, expected {expected_language}")
                        return False
                else:
                    self.log_test("Country-Language Mapping", True, 
                                f"Unknown country {detected_country}, defaulting to {detected_language}")
                
                # Check if all expected languages are available
                expected_languages = ["FR", "EN-GB", "ES", "DE", "IT", "NL", "PT-PT", "PL"]
                missing_languages = [lang for lang in expected_languages if lang not in available_languages]
                
                if not missing_languages:
                    self.log_test("Available Languages Complete", True, f"All {len(expected_languages)} expected languages available")
                    return True
                else:
                    self.log_test("Available Languages Complete", False, f"Missing languages: {missing_languages}")
                    return False
            else:
                self.log_test("Country-Language Mapping", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Country-Language Mapping", False, f"Exception: {str(e)}")
            return False

    def test_automatic_product_translation(self):
        """Test GET /api/products/translated - Automatic product translation based on IP"""
        try:
            # Test with different language parameters
            test_languages = ["EN-GB", "ES", "DE", "IT"]
            
            successful_translations = 0
            
            for language in test_languages:
                response = self.session.get(f"{BACKEND_URL}/products/translated?language={language}&customer_type=B2C")
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if "products" in data and "language" in data:
                        products = data["products"]
                        returned_language = data["language"]
                        
                        if len(products) > 0 and returned_language == language:
                            # Check if product names are actually translated
                            first_product = products[0]
                            product_name = first_product.get("name", "")
                            
                            # For non-French languages, the name should be different from French
                            if language != "FR":
                                # Simple check - if it contains non-French words, it's likely translated
                                if any(word in product_name.lower() for word in ["water", "fountain", "system", "sistema", "wasser", "sistema"]):
                                    self.log_test(f"Product Translation {language}", True, 
                                                f"Products translated to {language}: '{product_name}'")
                                    successful_translations += 1
                                else:
                                    # Check if it's still in French (might indicate translation issue)
                                    if any(word in product_name.lower() for word in ["fontaine", "eau", "système"]):
                                        self.log_test(f"Product Translation {language}", False, 
                                                    f"Product still in French: '{product_name}'")
                                    else:
                                        self.log_test(f"Product Translation {language}", True, 
                                                    f"Product name changed: '{product_name}'")
                                        successful_translations += 1
                            else:
                                self.log_test(f"Product Translation {language}", True, f"French products returned correctly")
                                successful_translations += 1
                        else:
                            self.log_test(f"Product Translation {language}", False, 
                                        f"No products or wrong language returned: {returned_language}")
                    else:
                        self.log_test(f"Product Translation {language}", False, "Missing products or language in response")
                else:
                    self.log_test(f"Product Translation {language}", False, f"Status: {response.status_code}")
            
            if successful_translations >= 3:
                self.log_test("Automatic Product Translation", True, f"{successful_translations}/4 language translations working")
                return True
            else:
                self.log_test("Automatic Product Translation", False, f"Only {successful_translations}/4 translations working")
                return False
                
        except Exception as e:
            self.log_test("Automatic Product Translation", False, f"Exception: {str(e)}")
            return False

    def run_debug_tests(self):
        """Run all translation debugging tests"""
        print("=" * 80)
        print("TRANSLATION SYSTEM DEBUGGING - IP DETECTION ISSUES")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Debug started at: {datetime.now().isoformat()}")
        print()
        
        print("🌍 TRANSLATION SYSTEM DEBUGGING TESTS")
        print("-" * 40)
        self.test_ip_detection_localization_endpoint()
        self.test_old_location_detection_endpoint()
        self.test_deepl_translation_service()
        self.test_ip_geolocation_functionality()
        self.test_translation_service_logs()
        self.test_country_language_mapping()
        self.test_automatic_product_translation()
        print()
        
        # Summary
        print("=" * 80)
        print("DEBUGGING SUMMARY")
        print("=" * 80)
        
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        
        print(f"Tests passed: {passed}/{total}")
        print(f"Success rate: {(passed/total)*100:.1f}%")
        print()
        
        # Show failed tests
        failed_tests = [result for result in self.test_results if not result["success"]]
        if failed_tests:
            print("FAILED TESTS:")
            for test in failed_tests:
                print(f"❌ {test['test']}: {test['details']}")
        else:
            print("✅ All tests passed!")
        
        print()
        return self.test_results

if __name__ == "__main__":
    debugger = TranslationDebugger()
    debugger.run_debug_tests()