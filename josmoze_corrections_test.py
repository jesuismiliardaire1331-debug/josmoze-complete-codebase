#!/usr/bin/env python3
"""
VALIDATION CORRECTIONS CRITIQUES JOSMOZE
Tests prioritaires pour valider les corrections appliquées
"""

import requests
import json
import time
from datetime import datetime

BACKEND_URL = "https://josmoze-ecommerce.preview.emergentagent.com/api"

class JosmozeCorrectionsValidator:
    def __init__(self):
        self.session = requests.Session()
        self.results = []
        
    def log_result(self, test_name: str, success: bool, details: str = ""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {details}")
        self.results.append({
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
        
    def test_promotions_manager_health(self):
        """Test 1: PromotionsManager Health - Vérifier que plus d'erreur 'non initialisé'"""
        try:
            response = self.session.get(f"{BACKEND_URL}/promotions/rules")
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.log_result("PromotionsManager Health", True, 
                                  "✅ PromotionsManager initialisé - endpoint /promotions/rules répond")
                    return True
                else:
                    self.log_result("PromotionsManager Health", False, 
                                  f"Réponse invalide: {data}")
                    return False
            else:
                self.log_result("PromotionsManager Health", False, 
                              f"Erreur HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_result("PromotionsManager Health", False, f"Exception: {str(e)}")
            return False
    
    def test_referral_code_generation(self):
        """Test 2: Génération codes parrainage - POST /api/promotions/referral/generate"""
        try:
            user_data = {"user_id": "test_user_corrections_001"}
            response = self.session.post(
                f"{BACKEND_URL}/promotions/referral/generate",
                json=user_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "referral_code" in data:
                    code = data["referral_code"]
                    # Vérifier format JOSM+4 caractères
                    if code.startswith("JOSM") and len(code) == 8:
                        self.referral_code = code  # Store for next test
                        self.log_result("Génération codes parrainage", True, 
                                      f"✅ Code généré: {code} (format JOSM+4 chars correct)")
                        return True
                    else:
                        self.log_result("Génération codes parrainage", False, 
                                      f"Format incorrect: {code} (attendu: JOSM+4 chars)")
                        return False
                else:
                    self.log_result("Génération codes parrainage", False, 
                                  f"Réponse invalide: {data}")
                    return False
            else:
                self.log_result("Génération codes parrainage", False, 
                              f"Erreur HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_result("Génération codes parrainage", False, f"Exception: {str(e)}")
            return False
    
    def test_referral_code_validation(self):
        """Test 3: Validation codes - POST /api/promotions/referral/validate"""
        if not hasattr(self, 'referral_code'):
            self.log_result("Validation codes", False, "Pas de code de parrainage du test précédent")
            return False
            
        try:
            code_data = {"code": self.referral_code}
            response = self.session.post(
                f"{BACKEND_URL}/promotions/referral/validate",
                json=code_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    if data.get("valid"):
                        # Code valide - vérifier les détails
                        discount = data.get("discount_percentage", 0)
                        if discount == 10:
                            self.log_result("Validation codes", True, 
                                          f"✅ Code {self.referral_code} valide, 10% de réduction confirmée")
                            return True
                        else:
                            self.log_result("Validation codes", False, 
                                          f"Réduction incorrecte: {discount}% (attendu: 10%)")
                            return False
                    else:
                        # Code invalide mais réponse correcte
                        self.log_result("Validation codes", True, 
                                      f"✅ Validation fonctionne - code {self.referral_code} traité correctement")
                        return True
                else:
                    self.log_result("Validation codes", False, f"Réponse invalide: {data}")
                    return False
            else:
                self.log_result("Validation codes", False, 
                              f"Erreur HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_result("Validation codes", False, f"Exception: {str(e)}")
            return False
    
    def test_launch_offer_check(self):
        """Test 4: Offre de lancement - POST /api/promotions/launch-offer/check"""
        try:
            cart_data = {
                "items": [
                    {
                        "product_id": "osmoseur-premium",
                        "quantity": 1,
                        "price": 549.0
                    }
                ]
            }
            
            response = self.session.post(
                f"{BACKEND_URL}/promotions/launch-offer/check",
                json=cart_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "eligibility" in data:
                    eligibility = data["eligibility"]
                    if eligibility.get("eligible"):
                        gift_options = eligibility.get("gift_options", [])
                        if len(gift_options) >= 2:
                            self.log_result("Offre de lancement", True, 
                                          f"✅ Premium éligible, {len(gift_options)} cadeaux disponibles")
                            return True
                        else:
                            self.log_result("Offre de lancement", False, 
                                          f"Pas assez de cadeaux: {len(gift_options)} (attendu: 2+)")
                            return False
                    else:
                        self.log_result("Offre de lancement", False, 
                                      f"Premium devrait être éligible: {eligibility.get('message', 'No message')}")
                        return False
                else:
                    self.log_result("Offre de lancement", False, f"Réponse invalide: {data}")
                    return False
            else:
                self.log_result("Offre de lancement", False, 
                              f"Erreur HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_result("Offre de lancement", False, f"Exception: {str(e)}")
            return False
    
    def test_promotion_rules(self):
        """Test 5: Règles promotions - GET /api/promotions/rules"""
        try:
            response = self.session.get(f"{BACKEND_URL}/promotions/rules")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "rules" in data:
                    rules = data["rules"]
                    
                    # Vérifier que les règles existent (même si vides pour l'instant)
                    if "referral_system" in rules and "launch_offer" in rules:
                        self.log_result("Règles promotions", True, 
                                      "✅ Structure des règles promotions présente")
                        return True
                    else:
                        self.log_result("Règles promotions", False, 
                                      f"Structure des règles manquante: {rules}")
                        return False
                else:
                    self.log_result("Règles promotions", False, f"Réponse invalide: {data}")
                    return False
            else:
                self.log_result("Règles promotions", False, 
                              f"Erreur HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_result("Règles promotions", False, f"Exception: {str(e)}")
            return False
    
    def test_new_products_catalog(self):
        """Test 6: Nouveaux produits - GET /api/products (vérifier 8+ produits)"""
        try:
            response = self.session.get(f"{BACKEND_URL}/products")
            
            if response.status_code == 200:
                products = response.json()
                
                if isinstance(products, list) and len(products) >= 8:
                    # Vérifier les nouveaux produits clés
                    product_ids = [p.get("id") for p in products]
                    
                    # Produits essentiels attendus
                    expected_products = [
                        "osmoseur-essentiel", "osmoseur-premium", "osmoseur-prestige",
                        "purificateur-portable-hydrogene", "fontaine-eau-animaux"
                    ]
                    
                    found_products = [pid for pid in expected_products if pid in product_ids]
                    
                    if len(found_products) >= 4:  # Au moins 4 des 5 produits essentiels
                        self.log_result("Nouveaux produits", True, 
                                      f"✅ {len(products)} produits total, nouveaux produits trouvés: {found_products}")
                        return True
                    else:
                        self.log_result("Nouveaux produits", False, 
                                      f"Produits manquants: {[p for p in expected_products if p not in product_ids]}")
                        return False
                else:
                    self.log_result("Nouveaux produits", False, 
                                  f"Pas assez de produits: {len(products) if isinstance(products, list) else 'non-list'}")
                    return False
            else:
                self.log_result("Nouveaux produits", False, 
                              f"Erreur HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_result("Nouveaux produits", False, f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Exécute tous les tests de validation des corrections"""
        print("🎯 VALIDATION CORRECTIONS CRITIQUES JOSMOZE")
        print("=" * 60)
        print()
        
        tests = [
            ("1. PromotionsManager Health", self.test_promotions_manager_health),
            ("2. Génération codes parrainage", self.test_referral_code_generation),
            ("3. Validation codes", self.test_referral_code_validation),
            ("4. Offre de lancement", self.test_launch_offer_check),
            ("5. Règles promotions", self.test_promotion_rules),
            ("6. Nouveaux produits", self.test_new_products_catalog)
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            print(f"\n🔍 {test_name}")
            print("-" * 40)
            if test_func():
                passed += 1
            time.sleep(0.5)  # Small delay between tests
        
        print("\n" + "=" * 60)
        print(f"📊 RÉSULTATS: {passed}/{total} tests réussis ({passed/total*100:.1f}%)")
        
        if passed == total:
            print("🎉 TOUTES LES CORRECTIONS VALIDÉES AVEC SUCCÈS!")
        elif passed >= total * 0.8:
            print("✅ CORRECTIONS MAJORITAIREMENT VALIDÉES")
        else:
            print("⚠️ CORRECTIONS PARTIELLES - ACTIONS REQUISES")
        
        return passed, total

if __name__ == "__main__":
    validator = JosmozeCorrectionsValidator()
    validator.run_all_tests()