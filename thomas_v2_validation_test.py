#!/usr/bin/env python3
"""
🤖 THOMAS V2 VALIDATION FINALE - CORRECTION COMPLÈTE
Backend API Testing for Thomas Chatbot V2 - Final Validation

TESTS DE VALIDATION FINALE selon review_request:
1. "Bonjour Thomas" → Accueil professionnel
2. "Quel osmoseur pour 4 personnes ?" → DOIT recommander Premium 549€ spécifiquement  
3. "Prix de l'Osmoseur Premium ?" → DOIT mentionner 549€ + caractéristiques détaillées
4. "C'est trop cher" → DOIT répondre avec ton ultra bienveillant + Essentiel 449€
5. "Bonjour" → Message d'accueil Thomas V2

OBJECTIF: 100% réussite pour confirmer que Thomas V2 est complètement fonctionnel
"""

import requests
import json
import time
import logging
from datetime import datetime
from typing import Dict, List, Any

# Backend URL from environment
BACKEND_URL = "https://water-ecom-admin.preview.emergentagent.com/api"

class ThomasV2Validator:
    def __init__(self):
        self.session = requests.Session()
        self.test_results = []
        
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
            print(f"   Response: {str(response_data)[:200]}...")
    
    def test_thomas_v2_greeting_bonjour_thomas(self):
        """Test 1: 'Bonjour Thomas' → Accueil professionnel"""
        try:
            chat_data = {
                "message": "Bonjour Thomas",
                "session_id": "test_session_greeting",
                "agent": "thomas",
                "context": {
                    "conversation_history": [],
                    "prompt": "THOMAS_PROMPT_V2",
                    "knowledge_base": {}
                },
                "language": "fr"
            }
            
            response = self.session.post(
                f"{BACKEND_URL}/ai-agents/chat",
                json=chat_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if "response" in data:
                    response_text = data["response"].lower()
                    
                    # Vérifier les éléments clés du message d'accueil professionnel
                    professional_indicators = [
                        "bonjour" in response_text,
                        "thomas" in response_text,
                        ("conseiller" in response_text or "expert" in response_text),
                        ("josmoze" in response_text or "josmose" in response_text)
                    ]
                    
                    found_count = sum(1 for indicator in professional_indicators if indicator)
                    
                    if found_count >= 3:
                        self.log_test("TEST 1: Bonjour Thomas → Accueil professionnel", True, 
                                    f"✅ Accueil professionnel détecté ({found_count}/4 éléments)")
                        return True
                    else:
                        self.log_test("TEST 1: Bonjour Thomas → Accueil professionnel", False, 
                                    f"❌ Accueil professionnel incomplet ({found_count}/4 éléments)", data['response'])
                        return False
                else:
                    self.log_test("TEST 1: Bonjour Thomas → Accueil professionnel", False, "Pas de réponse dans la structure", data)
                    return False
            else:
                self.log_test("TEST 1: Bonjour Thomas → Accueil professionnel", False, f"Status: {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("TEST 1: Bonjour Thomas → Accueil professionnel", False, f"Exception: {str(e)}")
            return False
    
    def test_thomas_v2_family_recommendation(self):
        """Test 2: 'Quel osmoseur pour 4 personnes ?' → DOIT recommander Premium 549€ spécifiquement"""
        try:
            chat_data = {
                "message": "Quel osmoseur pour 4 personnes ?",
                "session_id": "test_session_family",
                "agent": "thomas",
                "context": {
                    "conversation_history": [],
                    "prompt": "THOMAS_PROMPT_V2",
                    "knowledge_base": {}
                },
                "language": "fr"
            }
            
            response = self.session.post(
                f"{BACKEND_URL}/ai-agents/chat",
                json=chat_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if "response" in data:
                    response_text = data["response"].lower()
                    
                    # Vérifier recommandation spécifique Premium 549€ pour 4 personnes
                    premium_indicators = [
                        "premium" in response_text,
                        "549" in response_text,
                        ("4 personnes" in response_text or "famille de 4" in response_text or "quatre personnes" in response_text),
                        ("recommande" in response_text or "conseille" in response_text or "idéal" in response_text)
                    ]
                    
                    found_count = sum(1 for indicator in premium_indicators if indicator)
                    
                    if found_count >= 3:
                        self.log_test("TEST 2: Famille 4 personnes → Premium 549€", True, 
                                    f"✅ Recommandation Premium 549€ pour 4 personnes détectée ({found_count}/4 éléments)")
                        return True
                    else:
                        self.log_test("TEST 2: Famille 4 personnes → Premium 549€", False, 
                                    f"❌ Recommandation Premium 549€ manquante ({found_count}/4 éléments)", data['response'])
                        return False
                else:
                    self.log_test("TEST 2: Famille 4 personnes → Premium 549€", False, "Pas de réponse dans la structure", data)
                    return False
            else:
                self.log_test("TEST 2: Famille 4 personnes → Premium 549€", False, f"Status: {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("TEST 2: Famille 4 personnes → Premium 549€", False, f"Exception: {str(e)}")
            return False
    
    def test_thomas_v2_premium_price_details(self):
        """Test 3: 'Prix de l'Osmoseur Premium ?' → DOIT mentionner 549€ + caractéristiques détaillées"""
        try:
            chat_data = {
                "message": "Prix de l'Osmoseur Premium ?",
                "session_id": "test_session_premium_price",
                "agent": "thomas",
                "context": {
                    "conversation_history": [],
                    "prompt": "THOMAS_PROMPT_V2",
                    "knowledge_base": {}
                },
                "language": "fr"
            }
            
            response = self.session.post(
                f"{BACKEND_URL}/ai-agents/chat",
                json=chat_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if "response" in data:
                    response_text = data["response"].lower()
                    
                    # Vérifier prix 549€ + caractéristiques détaillées
                    price_details_indicators = [
                        "549" in response_text,
                        "premium" in response_text,
                        ("€" in response_text or "euro" in response_text),
                        ("technologie" in response_text or "avancée" in response_text or "populaire" in response_text or "familles" in response_text)
                    ]
                    
                    found_count = sum(1 for indicator in price_details_indicators if indicator)
                    
                    if found_count >= 3:
                        self.log_test("TEST 3: Prix Premium → 549€ + caractéristiques", True, 
                                    f"✅ Prix 549€ + caractéristiques détaillées mentionnés ({found_count}/4 éléments)")
                        return True
                    else:
                        self.log_test("TEST 3: Prix Premium → 549€ + caractéristiques", False, 
                                    f"❌ Prix 549€ ou caractéristiques manquants ({found_count}/4 éléments)", data['response'])
                        return False
                else:
                    self.log_test("TEST 3: Prix Premium → 549€ + caractéristiques", False, "Pas de réponse dans la structure", data)
                    return False
            else:
                self.log_test("TEST 3: Prix Premium → 549€ + caractéristiques", False, f"Status: {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("TEST 3: Prix Premium → 549€ + caractéristiques", False, f"Exception: {str(e)}")
            return False
    
    def test_thomas_v2_budget_objection_benevolent(self):
        """Test 4: 'C'est trop cher' → DOIT répondre avec ton ultra bienveillant + Essentiel 449€"""
        try:
            chat_data = {
                "message": "C'est trop cher",
                "session_id": "test_session_budget",
                "agent": "thomas",
                "context": {
                    "conversation_history": [
                        {"role": "user", "content": "Prix de l'Osmoseur Premium ?"},
                        {"role": "assistant", "content": "Le Premium BlueMountain coûte 549€..."}
                    ],
                    "prompt": "THOMAS_PROMPT_V2",
                    "knowledge_base": {}
                },
                "language": "fr"
            }
            
            response = self.session.post(
                f"{BACKEND_URL}/ai-agents/chat",
                json=chat_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if "response" in data:
                    response_text = data["response"].lower()
                    
                    # Vérifier ton bienveillant + alternative Essentiel 449€
                    benevolent_indicators = [
                        ("comprends" in response_text or "compréhensible" in response_text or "budget" in response_text),
                        ("essentiel" in response_text),
                        ("449" in response_text),
                        ("alternative" in response_text or "option" in response_text or "solution" in response_text),
                        not any(aggressive_word in response_text for aggressive_word in ["dommage", "tant pis", "malheureusement", "problème"])
                    ]
                    
                    found_count = sum(1 for indicator in benevolent_indicators if indicator)
                    
                    if found_count >= 4:
                        self.log_test("TEST 4: Objection Budget → Ton bienveillant + Essentiel 449€", True, 
                                    f"✅ Ton bienveillant + alternative Essentiel 449€ détectés ({found_count}/5 éléments)")
                        return True
                    else:
                        self.log_test("TEST 4: Objection Budget → Ton bienveillant + Essentiel 449€", False, 
                                    f"❌ Ton bienveillant ou Essentiel 449€ manquant ({found_count}/5 éléments)", data['response'])
                        return False
                else:
                    self.log_test("TEST 4: Objection Budget → Ton bienveillant + Essentiel 449€", False, "Pas de réponse dans la structure", data)
                    return False
            else:
                self.log_test("TEST 4: Objection Budget → Ton bienveillant + Essentiel 449€", False, f"Status: {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("TEST 4: Objection Budget → Ton bienveillant + Essentiel 449€", False, f"Exception: {str(e)}")
            return False
    
    def test_thomas_v2_simple_greeting(self):
        """Test 5: 'Bonjour' → Message d'accueil Thomas V2"""
        try:
            chat_data = {
                "message": "Bonjour",
                "session_id": "test_session_simple_greeting",
                "agent": "thomas",
                "context": {
                    "conversation_history": [],
                    "prompt": "THOMAS_PROMPT_V2",
                    "knowledge_base": {}
                },
                "language": "fr"
            }
            
            response = self.session.post(
                f"{BACKEND_URL}/ai-agents/chat",
                json=chat_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if "response" in data:
                    response_text = data["response"].lower()
                    
                    # Vérifier message d'accueil Thomas V2
                    greeting_indicators = [
                        "bonjour" in response_text,
                        ("thomas" in response_text or "conseiller" in response_text),
                        ("osmoseur" in response_text or "eau" in response_text or "filtration" in response_text),
                        ("aider" in response_text or "accompagner" in response_text or "conseiller" in response_text),
                        len(response_text) > 50  # Message substantiel
                    ]
                    
                    found_count = sum(1 for indicator in greeting_indicators if indicator)
                    
                    if found_count >= 4:
                        self.log_test("TEST 5: Bonjour → Message d'accueil Thomas V2", True, 
                                    f"✅ Message d'accueil Thomas V2 complet ({found_count}/5 éléments)")
                        return True
                    else:
                        self.log_test("TEST 5: Bonjour → Message d'accueil Thomas V2", False, 
                                    f"❌ Message d'accueil incomplet ({found_count}/5 éléments)", data['response'])
                        return False
                else:
                    self.log_test("TEST 5: Bonjour → Message d'accueil Thomas V2", False, "Pas de réponse dans la structure", data)
                    return False
            else:
                self.log_test("TEST 5: Bonjour → Message d'accueil Thomas V2", False, f"Status: {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("TEST 5: Bonjour → Message d'accueil Thomas V2", False, f"Exception: {str(e)}")
            return False
    
    def run_validation_finale(self):
        """Run all Thomas V2 validation tests"""
        print("🎯 VALIDATION FINALE THOMAS V2 - CORRECTION COMPLÈTE")
        print("=" * 80)
        print("🤖 Tester Thomas V2 après corrections de la logique commerciale et du ton bienveillant")
        print()
        print("✅ CORRECTIONS SUPPLÉMENTAIRES APPORTÉES :")
        print("1. **Logique Recommandation** : Ajout détection '4 personnes' → recommande spécifiquement Premium 549€")
        print("2. **Ton Bienveillant Renforcé** : Objections budget avec empathie et explications bienveillantes")
        print("3. **Réponses Personnalisées** : Recommandations spécifiques selon taille famille")
        print()
        print("✅ TESTS DE VALIDATION FINALE :")
        print("1. 'Bonjour Thomas' → Accueil professionnel")
        print("2. 'Quel osmoseur pour 4 personnes ?' → DOIT recommander Premium 549€ spécifiquement")
        print("3. 'Prix de l'Osmoseur Premium ?' → DOIT mentionner 549€ + caractéristiques détaillées")
        print("4. 'C'est trop cher' → DOIT répondre avec ton ultra bienveillant + Essentiel 449€")
        print("5. 'Bonjour' → Message d'accueil Thomas V2")
        print()
        print("🎯 OBJECTIF : 100% réussite pour confirmer que Thomas V2 est complètement fonctionnel")
        print("=" * 80)
        print()
        
        # Run all validation tests
        validation_tests = [
            self.test_thomas_v2_greeting_bonjour_thomas,
            self.test_thomas_v2_family_recommendation,
            self.test_thomas_v2_premium_price_details,
            self.test_thomas_v2_budget_objection_benevolent,
            self.test_thomas_v2_simple_greeting
        ]
        
        passed_tests = 0
        total_tests = len(validation_tests)
        
        for test in validation_tests:
            try:
                if test():
                    passed_tests += 1
                time.sleep(1)  # Small delay between tests
            except Exception as e:
                print(f"❌ Test failed with exception: {str(e)}")
        
        print()
        print("=" * 80)
        print("🎯 RÉSULTATS VALIDATION FINALE THOMAS V2")
        print("=" * 80)
        
        success_rate = (passed_tests / total_tests) * 100
        
        print(f"✅ Tests réussis: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
        
        if passed_tests == total_tests:
            print("🎉 VALIDATION FINALE RÉUSSIE - THOMAS V2 COMPLÈTEMENT FONCTIONNEL!")
            print("✅ Thomas V2 répond correctement à tous les scénarios critiques")
            print("✅ Logique commerciale et ton bienveillant parfaitement implémentés")
            print("✅ Prêt pour validation finale utilisateur")
        else:
            print("🚨 VALIDATION FINALE ÉCHOUÉE - PROBLÈMES CRITIQUES DÉTECTÉS")
            print("❌ Thomas V2 ne passe pas tous les tests de validation")
            print("❌ Correction finale immédiate requise")
            
            # Show failed tests details
            failed_tests = []
            for i, result in enumerate(self.test_results):
                if not result["success"]:
                    failed_tests.append(f"Test {i+1}: {result['test']} - {result['details']}")
            
            if failed_tests:
                print("\n🔍 DÉTAILS DES ÉCHECS :")
                for failed in failed_tests:
                    print(f"   {failed}")
        
        print("=" * 80)
        
        return passed_tests == total_tests

def main():
    """Main function to run Thomas V2 validation"""
    validator = ThomasV2Validator()
    success = validator.run_validation_finale()
    
    if success:
        exit(0)
    else:
        exit(1)

if __name__ == "__main__":
    main()