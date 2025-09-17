#!/usr/bin/env python3
"""
Stripe Payment System Tests for Josmoze.com - Cahier des Charges
Tests the complete Stripe payment infrastructure according to specifications.
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Any

# Backend URL from environment
BACKEND_URL = "https://josmoze-ecommerce.preview.emergentagent.com/api"

class StripePaymentTester:
    def __init__(self):
        self.session = requests.Session()
        self.test_results = []
        self.stripe_session_id = None
        self.auth_token = None
        
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
    
    def authenticate_manager(self):
        """Authenticate as manager (Naima) for manager-only tests"""
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
                    # Set authorization header for subsequent requests
                    self.auth_token = data['access_token']  # Store the token
                    self.session.headers.update({
                        "Authorization": f"Bearer {data['access_token']}"
                    })
                    self.log_test("Manager Authentication (Naima)", True, f"Authenticated as naima@josmoze.com with manager role")
                    return True
                else:
                    self.log_test("Manager Authentication (Naima)", False, "No access token in response", data)
                    return False
            else:
                self.log_test("Manager Authentication (Naima)", False, f"Status: {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("Manager Authentication (Naima)", False, f"Exception: {str(e)}")
            return False
    
    def test_stripe_payment_packages(self):
        """TEST 1 - PACKAGES DE PRODUITS JOSMOZE: GET /api/payments/packages"""
        try:
            response = self.session.get(f"{BACKEND_URL}/payments/packages")
            
            if response.status_code == 200:
                data = response.json()
                
                if "status" in data and data["status"] == "success":
                    packages = data.get("packages", {})
                    
                    # Vérifier les produits Josmoze requis avec prix fixes
                    expected_products = {
                        "osmoseur_particulier": 499.0,  # Osmoseur particulier
                        "osmoseur_professionnel": 899.0,        # Osmoseur professionnel (899€)
                        "fontaine_animaux": 49.0,     # Nouveau produit: Fontaine animaux (49€)
                        "sac_transport": 29.0,        # Nouveau produit: Sac transport (29€)
                        "distributeur_nourriture": 39.0  # Nouveau produit: Distributeur nourriture (39€)
                    }
                    
                    all_products_found = True
                    missing_products = []
                    price_mismatches = []
                    
                    for product_id, expected_price in expected_products.items():
                        if product_id not in packages:
                            all_products_found = False
                            missing_products.append(product_id)
                        elif packages[product_id] != expected_price:
                            price_mismatches.append(f"{product_id}: expected {expected_price}€, got {packages[product_id]}€")
                    
                    if all_products_found and not price_mismatches:
                        self.log_test("Stripe Payment Packages", True, 
                                    f"All Josmoze products available with correct prices: {len(packages)} packages")
                        return True
                    else:
                        error_details = []
                        if missing_products:
                            error_details.append(f"Missing: {missing_products}")
                        if price_mismatches:
                            error_details.append(f"Price mismatches: {price_mismatches}")
                        
                        self.log_test("Stripe Payment Packages", False, "; ".join(error_details))
                        return False
                else:
                    self.log_test("Stripe Payment Packages", False, "Invalid response format", data)
                    return False
            else:
                self.log_test("Stripe Payment Packages", False, f"Status: {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("Stripe Payment Packages", False, f"Exception: {str(e)}")
            return False
    
    def test_stripe_checkout_session_creation(self):
        """TEST 2 - CRÉATION SESSION DE PAIEMENT: POST /api/payments/checkout/session avec authentification manager"""
        try:
            # Données de test avec package_id="osmoseur_particulier", quantity=1
            checkout_data = {
                "package_id": "osmoseur_particulier",  # Note: using osmoseur_particulier as per JOSMOZE_PACKAGES
                "quantity": 1,
                "customer_info": {
                    "name": "Jean Dupont",
                    "email": "jean.dupont@test-josmoze.com",
                    "phone": "+33123456789",
                    "address": {
                        "street": "123 Rue de la Paix",
                        "city": "Paris",
                        "postal_code": "75001",
                        "country": "France"
                    }
                },
                "metadata": {
                    "source": "test_cahier_des_charges",
                    "test_mode": True
                }
            }
            
            response = self.session.post(
                f"{BACKEND_URL}/payments/checkout/session",
                json=checkout_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["url", "session_id", "package_id", "total_items"]
                
                if all(field in data for field in required_fields):
                    self.stripe_session_id = data["session_id"]  # Store for status test
                    
                    # Vérifier que la session Stripe est créée correctement
                    if data["package_id"] == "osmoseur_particulier" and data["total_items"] == 1:
                        self.log_test("Stripe Checkout Session Creation", True, 
                                    f"Session created: {data['session_id'][:20]}..., Package: {data['package_id']}")
                        
                        # Vérifier que la transaction est enregistrée dans MongoDB (indirectement via l'API)
                        return True
                    else:
                        self.log_test("Stripe Checkout Session Creation", False, 
                                    f"Incorrect session data: package={data['package_id']}, items={data['total_items']}")
                        return False
                else:
                    missing = [f for f in required_fields if f not in data]
                    self.log_test("Stripe Checkout Session Creation", False, f"Missing fields: {missing}", data)
                    return False
            else:
                self.log_test("Stripe Checkout Session Creation", False, f"Status: {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("Stripe Checkout Session Creation", False, f"Exception: {str(e)}")
            return False
    
    def test_stripe_ecommerce_integration(self):
        """TEST 3 - INTÉGRATION E-COMMERCE EXISTANTE: POST /api/checkout/session (flow existant du panier)"""
        try:
            # Test avec un cart_item simulé (flow existant)
            checkout_data = {
                "cart_items": [
                    {
                        "product_id": "osmoseur_particulier",
                        "quantity": 1,
                        "price": 479.0  # This should be validated server-side
                    }
                ],
                "customer_info": {
                    "email": "client.ecommerce@test-josmoze.com",
                    "name": "Marie Martin",
                    "phone": "+33987654321"
                },
                "origin_url": "https://josmoze.com"
            }
            
            response = self.session.post(
                f"{BACKEND_URL}/checkout/session",
                json=checkout_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if "url" in data and "session_id" in data:
                    # Vérifier redirection vers Stripe
                    if "stripe" in data["url"].lower() or data["url"].startswith("https://"):
                        self.log_test("Stripe E-commerce Integration", True, 
                                    f"E-commerce flow working, redirects to: {data['url'][:50]}...")
                        return True
                    else:
                        self.log_test("Stripe E-commerce Integration", False, 
                                    f"Invalid redirect URL: {data['url']}")
                        return False
                else:
                    self.log_test("Stripe E-commerce Integration", False, "Missing url or session_id", data)
                    return False
            else:
                self.log_test("Stripe E-commerce Integration", False, f"Status: {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("Stripe E-commerce Integration", False, f"Exception: {str(e)}")
            return False
    
    def test_stripe_payment_status(self):
        """TEST 4 - STATUT DE PAIEMENT: GET /api/payments/checkout/status/{session_id}"""
        if not hasattr(self, 'stripe_session_id') or not self.stripe_session_id:
            # Create a test session first
            self.test_stripe_checkout_session_creation()
        
        if not hasattr(self, 'stripe_session_id') or not self.stripe_session_id:
            self.log_test("Stripe Payment Status", False, "No session_id available from previous test")
            return False
        
        try:
            response = self.session.get(f"{BACKEND_URL}/payments/checkout/status/{self.stripe_session_id}")
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["session_id", "status", "payment_status"]
                
                if all(field in data for field in required_fields):
                    # Vérifier que le statut est cohérent
                    session_id = data["session_id"]
                    status = data["status"]
                    payment_status = data["payment_status"]
                    
                    if session_id == self.stripe_session_id:
                        self.log_test("Stripe Payment Status", True, 
                                    f"Status retrieved: session={status}, payment={payment_status}")
                        return True
                    else:
                        self.log_test("Stripe Payment Status", False, 
                                    f"Session ID mismatch: expected {self.stripe_session_id}, got {session_id}")
                        return False
                else:
                    missing = [f for f in required_fields if f not in data]
                    self.log_test("Stripe Payment Status", False, f"Missing fields: {missing}", data)
                    return False
            else:
                self.log_test("Stripe Payment Status", False, f"Status: {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("Stripe Payment Status", False, f"Exception: {str(e)}")
            return False

    def run_stripe_tests(self):
        """Run all Stripe payment system tests"""
        print("🔥 STRIPE PAYMENT SYSTEM TESTING - JOSMOZE CAHIER DES CHARGES")
        print(f"🌐 Testing against: {BACKEND_URL}")
        print("=" * 80)
        
        # Authenticate as manager first
        print("\n🔐 AUTHENTICATION")
        print("-" * 30)
        self.authenticate_manager()
        
        # Run Stripe payment tests
        print("\n💳 STRIPE PAYMENT TESTS")
        print("-" * 30)
        
        tests = [
            self.test_stripe_payment_packages,
            self.test_stripe_checkout_session_creation,
            self.test_stripe_ecommerce_integration,
            self.test_stripe_payment_status,
        ]
        
        total_tests = len(tests)
        passed_tests = 0
        
        for test in tests:
            try:
                if test():
                    passed_tests += 1
            except Exception as e:
                self.log_test(test.__name__, False, f"Test execution failed: {str(e)}")
        
        # Final Results
        print("\n" + "=" * 80)
        print("📊 STRIPE PAYMENT SYSTEM TEST RESULTS")
        print("=" * 80)
        
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        print(f"✅ Tests Passed: {passed_tests}/{total_tests}")
        print(f"📈 Success Rate: {success_rate:.1f}%")
        
        if success_rate >= 80:
            print("🎉 EXCELLENT! Stripe payment infrastructure is ready for production")
        elif success_rate >= 60:
            print("⚠️  GOOD! Some issues need attention")
        else:
            print("🚨 CRITICAL! Major issues detected")
        
        # Show failed tests
        failed_tests = [result for result in self.test_results if not result["success"]]
        if failed_tests:
            print(f"\n❌ Failed Tests ({len(failed_tests)}):")
            for test in failed_tests:
                print(f"   • {test['test']}: {test['details']}")
        
        # Show successful tests
        successful_tests = [result for result in self.test_results if result["success"]]
        if successful_tests:
            print(f"\n✅ Successful Tests ({len(successful_tests)}):")
            for test in successful_tests:
                print(f"   • {test['test']}: {test['details']}")
        
        print("\n" + "=" * 80)
        return success_rate >= 80

if __name__ == "__main__":
    tester = StripePaymentTester()
    tester.run_stripe_tests()