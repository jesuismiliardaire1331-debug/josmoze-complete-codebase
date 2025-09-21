#!/usr/bin/env python3
"""
DIAGNOSTIC APPROFONDI PHASE 1 - PROBLÈMES PERSISTANTS
Tests spécifiques pour diagnostiquer les problèmes rapportés par l'utilisateur:

1. PROBLÈME LANGUE: Site ne se charge pas en français par défaut
2. PROBLÈME PRODUITS STOCK: Certains produits restent "Unavailable"  
3. PROBLÈME NAVIGATION/CSS: Texte brut encore présent
4. ENDPOINTS CRITIQUES: Vérification détaillée des APIs
"""

import requests
import json
import time
import logging
from datetime import datetime
from typing import Dict, List, Any

# Backend URL from environment
BACKEND_URL = "https://chatbot-debug-2.preview.emergentagent.com/api"

class DiagnosticTester:
    def __init__(self):
        self.session = requests.Session()
        self.test_results = []
        
    def log_test(self, test_name: str, success: bool, details: str = "", response_data: Any = None):
        """Log test results with detailed information"""
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
            print(f"   Response Data: {json.dumps(response_data, indent=2)}")
    
    def test_backend_root_endpoint(self):
        """Test GET / (racine backend) - Vérifier en-têtes et configuration CORS"""
        try:
            response = self.session.get(f"{BACKEND_URL}/")
            
            # Vérifier le statut de réponse
            if response.status_code == 200:
                data = response.json()
                
                # Vérifier le contenu de la réponse
                if "message" in data and "Josmose.com" in data["message"]:
                    # Vérifier les en-têtes CORS
                    headers = response.headers
                    cors_headers = {
                        'access-control-allow-origin': headers.get('access-control-allow-origin'),
                        'access-control-allow-credentials': headers.get('access-control-allow-credentials'),
                        'access-control-allow-methods': headers.get('access-control-allow-methods'),
                        'access-control-allow-headers': headers.get('access-control-allow-headers'),
                        'content-type': headers.get('content-type')
                    }
                    
                    self.log_test("Backend Root Endpoint", True, 
                                f"✅ API racine fonctionnelle: {data['message']}", 
                                {"response": data, "cors_headers": cors_headers})
                    return True
                else:
                    self.log_test("Backend Root Endpoint", False, 
                                "Format de réponse inattendu", data)
                    return False
            else:
                self.log_test("Backend Root Endpoint", False, 
                            f"Status HTTP: {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("Backend Root Endpoint", False, f"Exception: {str(e)}")
            return False
    
    def test_localization_detect_endpoint(self):
        """Test GET /api/localization/detect - Détection automatique langue française"""
        try:
            # Test avec en-têtes français simulés
            headers = {
                'Accept-Language': 'fr-FR,fr;q=0.9,en;q=0.8',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = self.session.get(f"{BACKEND_URL}/localization/detect", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                
                # Vérifier les champs requis
                required_fields = ["detected_language", "detected_country", "currency", "available_languages", "ip_address"]
                
                if all(field in data for field in required_fields):
                    detected_language = data["detected_language"]
                    detected_country = data["detected_country"]
                    currency = data["currency"]
                    available_languages = data["available_languages"]
                    
                    # Vérifier si le français est détecté par défaut
                    is_french_default = detected_language.upper() == "FR"
                    is_france_default = detected_country.upper() == "FR"
                    is_euro_currency = currency.get("code") == "EUR" if isinstance(currency, dict) else currency == "EUR"
                    
                    # Vérifier les langues disponibles
                    has_french_available = "FR" in available_languages or "fr" in available_languages
                    
                    if is_french_default and is_france_default and is_euro_currency:
                        self.log_test("Détection Langue Automatique", True, 
                                    f"✅ Français détecté par défaut: {detected_language}/{detected_country}, Devise: {currency}", 
                                    data)
                        return True
                    else:
                        self.log_test("Détection Langue Automatique", False, 
                                    f"❌ Langue par défaut incorrecte: {detected_language}/{detected_country}, Devise: {currency} (attendu: FR/FR/EUR)", 
                                    data)
                        return False
                else:
                    missing = [f for f in required_fields if f not in data]
                    self.log_test("Détection Langue Automatique", False, 
                                f"Champs manquants: {missing}", data)
                    return False
            else:
                self.log_test("Détection Langue Automatique", False, 
                            f"Status: {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("Détection Langue Automatique", False, f"Exception: {str(e)}")
            return False
    
    def test_products_stock_status(self):
        """Test GET /api/products - Vérifier que TOUS les produits ont in_stock: true"""
        try:
            response = self.session.get(f"{BACKEND_URL}/products")
            
            if response.status_code == 200:
                products = response.json()
                
                if isinstance(products, list) and len(products) > 0:
                    total_products = len(products)
                    unavailable_products = []
                    products_without_stock_info = []
                    
                    for product in products:
                        product_id = product.get("id", "unknown")
                        
                        # Vérifier in_stock au niveau racine
                        root_in_stock = product.get("in_stock", None)
                        
                        # Vérifier stock_info
                        stock_info = product.get("stock_info", {})
                        stock_info_in_stock = stock_info.get("in_stock", None)
                        
                        # Analyser le statut de stock
                        if root_in_stock is False or stock_info_in_stock is False:
                            unavailable_products.append({
                                "id": product_id,
                                "name": product.get("name", "Unknown"),
                                "root_in_stock": root_in_stock,
                                "stock_info_in_stock": stock_info_in_stock,
                                "stock_info": stock_info
                            })
                        
                        # Vérifier présence stock_info
                        if not stock_info:
                            products_without_stock_info.append(product_id)
                    
                    # Résultats du diagnostic
                    available_count = total_products - len(unavailable_products)
                    
                    if len(unavailable_products) == 0:
                        self.log_test("Statut Stock Produits", True, 
                                    f"✅ TOUS les produits sont disponibles: {available_count}/{total_products} produits in_stock: true", 
                                    {"total_products": total_products, "available_products": available_count})
                        return True
                    else:
                        self.log_test("Statut Stock Produits", False, 
                                    f"❌ {len(unavailable_products)} produits INDISPONIBLES sur {total_products}", 
                                    {
                                        "total_products": total_products,
                                        "available_products": available_count,
                                        "unavailable_products": unavailable_products,
                                        "products_without_stock_info": products_without_stock_info
                                    })
                        return False
                else:
                    self.log_test("Statut Stock Produits", False, 
                                f"Aucun produit retourné ou format invalide: {type(products)}")
                    return False
            else:
                self.log_test("Statut Stock Produits", False, 
                            f"Status: {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("Statut Stock Produits", False, f"Exception: {str(e)}")
            return False
    
    def test_products_translated_french(self):
        """Test GET /api/products/translated?language=FR - Produits traduits en français"""
        try:
            response = self.session.get(f"{BACKEND_URL}/products/translated?language=FR")
            
            if response.status_code == 200:
                data = response.json()
                
                if isinstance(data, dict) and "products" in data:
                    products = data["products"]
                    language = data.get("language", "Unknown")
                    
                    if isinstance(products, list) and len(products) > 0:
                        total_products = len(products)
                        unavailable_products = []
                        french_content_check = []
                        
                        for product in products:
                            product_id = product.get("id", "unknown")
                            product_name = product.get("name", "")
                            product_description = product.get("description", "")
                            
                            # Vérifier statut stock
                            stock_info = product.get("stock_info", {})
                            if not stock_info.get("in_stock", True):
                                unavailable_products.append({
                                    "id": product_id,
                                    "name": product_name,
                                    "stock_info": stock_info
                                })
                            
                            # Vérifier contenu français (mots-clés français)
                            french_keywords = ["osmoseur", "filtration", "eau", "pure", "système", "garantie"]
                            has_french_content = any(keyword in product_name.lower() or keyword in product_description.lower() 
                                                   for keyword in french_keywords)
                            
                            if has_french_content:
                                french_content_check.append(product_id)
                        
                        # Résultats
                        available_count = total_products - len(unavailable_products)
                        french_content_count = len(french_content_check)
                        
                        if len(unavailable_products) == 0:
                            self.log_test("Produits Traduits Français", True, 
                                        f"✅ Langue: {language}, {available_count}/{total_products} produits disponibles, {french_content_count} avec contenu français", 
                                        {
                                            "language": language,
                                            "total_products": total_products,
                                            "available_products": available_count,
                                            "french_content_products": french_content_count
                                        })
                            return True
                        else:
                            self.log_test("Produits Traduits Français", False, 
                                        f"❌ {len(unavailable_products)} produits indisponibles en français", 
                                        {
                                            "language": language,
                                            "total_products": total_products,
                                            "unavailable_products": unavailable_products
                                        })
                            return False
                    else:
                        self.log_test("Produits Traduits Français", False, 
                                    f"Aucun produit dans la réponse traduite")
                        return False
                else:
                    self.log_test("Produits Traduits Français", False, 
                                "Format de réponse invalide", data)
                    return False
            else:
                self.log_test("Produits Traduits Français", False, 
                            f"Status: {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("Produits Traduits Français", False, f"Exception: {str(e)}")
            return False
    
    def test_products_detailed_analysis(self):
        """Analyse détaillée des données produits pour identifier les problèmes"""
        try:
            response = self.session.get(f"{BACKEND_URL}/products")
            
            if response.status_code == 200:
                products = response.json()
                
                if isinstance(products, list):
                    analysis = {
                        "total_products": len(products),
                        "products_by_category": {},
                        "products_by_target_audience": {},
                        "stock_analysis": {
                            "with_stock_info": 0,
                            "without_stock_info": 0,
                            "in_stock_true": 0,
                            "in_stock_false": 0,
                            "stock_info_details": []
                        },
                        "price_analysis": {
                            "min_price": float('inf'),
                            "max_price": 0,
                            "products_with_prices": 0
                        },
                        "product_details": []
                    }
                    
                    for product in products:
                        # Analyse par catégorie
                        category = product.get("category", "unknown")
                        analysis["products_by_category"][category] = analysis["products_by_category"].get(category, 0) + 1
                        
                        # Analyse par audience
                        target_audience = product.get("target_audience", "unknown")
                        analysis["products_by_target_audience"][target_audience] = analysis["products_by_target_audience"].get(target_audience, 0) + 1
                        
                        # Analyse stock
                        stock_info = product.get("stock_info", {})
                        root_in_stock = product.get("in_stock", None)
                        
                        if stock_info:
                            analysis["stock_analysis"]["with_stock_info"] += 1
                            stock_in_stock = stock_info.get("in_stock", None)
                            
                            if stock_in_stock is True:
                                analysis["stock_analysis"]["in_stock_true"] += 1
                            elif stock_in_stock is False:
                                analysis["stock_analysis"]["in_stock_false"] += 1
                            
                            analysis["stock_analysis"]["stock_info_details"].append({
                                "product_id": product.get("id"),
                                "root_in_stock": root_in_stock,
                                "stock_info_in_stock": stock_in_stock,
                                "available_stock": stock_info.get("available_stock"),
                                "show_stock_warning": stock_info.get("show_stock_warning")
                            })
                        else:
                            analysis["stock_analysis"]["without_stock_info"] += 1
                        
                        # Analyse prix
                        price = product.get("price", 0)
                        if price > 0:
                            analysis["price_analysis"]["products_with_prices"] += 1
                            analysis["price_analysis"]["min_price"] = min(analysis["price_analysis"]["min_price"], price)
                            analysis["price_analysis"]["max_price"] = max(analysis["price_analysis"]["max_price"], price)
                        
                        # Détails produit
                        analysis["product_details"].append({
                            "id": product.get("id"),
                            "name": product.get("name"),
                            "price": price,
                            "category": category,
                            "target_audience": target_audience,
                            "in_stock": root_in_stock,
                            "stock_info": stock_info
                        })
                    
                    # Évaluation
                    all_products_available = analysis["stock_analysis"]["in_stock_false"] == 0
                    has_stock_info = analysis["stock_analysis"]["with_stock_info"] > 0
                    
                    if all_products_available and has_stock_info:
                        self.log_test("Analyse Détaillée Produits", True, 
                                    f"✅ Analyse complète: {analysis['total_products']} produits, tous disponibles", 
                                    analysis)
                        return True
                    else:
                        self.log_test("Analyse Détaillée Produits", False, 
                                    f"❌ Problèmes détectés dans l'analyse produits", 
                                    analysis)
                        return False
                else:
                    self.log_test("Analyse Détaillée Produits", False, 
                                "Format de réponse invalide")
                    return False
            else:
                self.log_test("Analyse Détaillée Produits", False, 
                            f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Analyse Détaillée Produits", False, f"Exception: {str(e)}")
            return False
    
    def test_cors_configuration(self):
        """Test configuration CORS pour problèmes navigation/CSS"""
        try:
            # Test avec différents origins
            test_origins = [
                "https://chatbot-debug-2.preview.emergentagent.com",
                "https://josmoze.com",
                "https://www.josmoze.com"
            ]
            
            cors_results = []
            
            for origin in test_origins:
                headers = {
                    'Origin': origin,
                    'Access-Control-Request-Method': 'GET',
                    'Access-Control-Request-Headers': 'Content-Type'
                }
                
                # Test preflight OPTIONS
                options_response = self.session.options(f"{BACKEND_URL}/", headers=headers)
                
                # Test GET avec Origin
                get_response = self.session.get(f"{BACKEND_URL}/", headers={'Origin': origin})
                
                cors_result = {
                    "origin": origin,
                    "options_status": options_response.status_code,
                    "get_status": get_response.status_code,
                    "options_headers": dict(options_response.headers),
                    "get_headers": dict(get_response.headers)
                }
                
                cors_results.append(cors_result)
            
            # Évaluer les résultats CORS
            cors_working = all(result["get_status"] == 200 for result in cors_results)
            
            if cors_working:
                self.log_test("Configuration CORS", True, 
                            f"✅ CORS configuré correctement pour {len(test_origins)} origins", 
                            cors_results)
                return True
            else:
                self.log_test("Configuration CORS", False, 
                            f"❌ Problèmes CORS détectés", 
                            cors_results)
                return False
        except Exception as e:
            self.log_test("Configuration CORS", False, f"Exception: {str(e)}")
            return False
    
    def run_diagnostic_tests(self):
        """Exécuter tous les tests de diagnostic"""
        print("🔍 DÉMARRAGE DIAGNOSTIC APPROFONDI PHASE 1 - PROBLÈMES PERSISTANTS")
        print("=" * 80)
        
        tests = [
            ("1. Backend Root Endpoint", self.test_backend_root_endpoint),
            ("2. Détection Langue Automatique", self.test_localization_detect_endpoint),
            ("3. Statut Stock Produits", self.test_products_stock_status),
            ("4. Produits Traduits Français", self.test_products_translated_french),
            ("5. Analyse Détaillée Produits", self.test_products_detailed_analysis),
            ("6. Configuration CORS", self.test_cors_configuration)
        ]
        
        passed = 0
        failed = 0
        
        for test_name, test_func in tests:
            print(f"\n🧪 Test: {test_name}")
            try:
                if test_func():
                    passed += 1
                else:
                    failed += 1
            except Exception as e:
                print(f"❌ ERREUR dans {test_name}: {str(e)}")
                failed += 1
            
            time.sleep(1)  # Pause entre les tests
        
        # Résumé final
        print("\n" + "=" * 80)
        print("📊 RÉSUMÉ DIAGNOSTIC PHASE 1")
        print("=" * 80)
        print(f"✅ Tests réussis: {passed}")
        print(f"❌ Tests échoués: {failed}")
        print(f"📈 Taux de réussite: {(passed/(passed+failed)*100):.1f}%")
        
        # Analyse des problèmes critiques
        critical_issues = []
        for result in self.test_results:
            if not result["success"]:
                critical_issues.append({
                    "test": result["test"],
                    "issue": result["details"]
                })
        
        if critical_issues:
            print(f"\n🚨 PROBLÈMES CRITIQUES IDENTIFIÉS ({len(critical_issues)}):")
            for i, issue in enumerate(critical_issues, 1):
                print(f"{i}. {issue['test']}: {issue['issue']}")
        else:
            print("\n✅ AUCUN PROBLÈME CRITIQUE DÉTECTÉ")
        
        return passed, failed, critical_issues

def main():
    """Fonction principale"""
    tester = DiagnosticTester()
    passed, failed, issues = tester.run_diagnostic_tests()
    
    # Sauvegarder les résultats détaillés
    results_file = f"/app/diagnostic_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump({
            "summary": {
                "passed": passed,
                "failed": failed,
                "success_rate": f"{(passed/(passed+failed)*100):.1f}%"
            },
            "critical_issues": issues,
            "detailed_results": tester.test_results
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Résultats détaillés sauvegardés: {results_file}")
    
    return passed == len(tester.test_results)

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)