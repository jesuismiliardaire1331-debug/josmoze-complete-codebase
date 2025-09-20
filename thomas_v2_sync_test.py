#!/usr/bin/env python3
"""
🤖 VALIDATION THOMAS V2 SYNCHRONISATION BACKEND-FRONTEND
=======================================================
Test complet de synchronisation Thomas V2 après mise à jour backend thomas_chatbot_fixed.py

TESTS CRITIQUES DE SYNCHRONISATION :
1. **Nouveau Prompt V2** : Vérifier utilisation des response_templates
2. **Prix Corrects** : 449€ Essentiel, 549€ Premium, 899€ Prestige, 39.90€ Filtre Douche
3. **Ton Bienveillant** : Pas de pression agressive, accompagnement
4. **Accueil Professionnel** : Message d'accueil selon template V2
5. **Objections Budget** : Réponse "budget serré" avec solution Essentiel

MESSAGES DE TEST :
- "Bonjour" → Template accueil V2
- "Quels sont vos prix ?" → Affichage prix corrects (449€, 549€, 899€, 39.90€)
- "C'est trop cher" → Réponse bienveillante budget + Essentiel 449€
- "Parlez-moi du Premium" → Info Premium 549€ avec thomas_pitch
- "Filtre douche" → Info 39.90€ correct

🎯 OBJECTIF : 80%+ de réussite pour valider synchronisation
"""

import requests
import json
import time
import logging
from datetime import datetime
from typing import Dict, List, Any

# Backend URL from environment
BACKEND_URL = "https://water-ecom-admin.preview.emergentagent.com/api"

class ThomasV2SyncTester:
    def __init__(self):
        self.session = requests.Session()
        self.test_results = []
        self.success_count = 0
        self.total_tests = 0
        
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
        self.total_tests += 1
        if success:
            self.success_count += 1
            
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {details}")
        if response_data and not success:
            print(f"   Response: {response_data}")
    
    def test_thomas_v2_accueil_template(self):
        """Test 1: Message d'accueil selon template V2"""
        try:
            chat_data = {
                "message": "Bonjour",
                "session_id": "test_accueil_v2"
            }
            
            response = self.session.post(
                f"{BACKEND_URL}/ai-agents/chat",
                json=chat_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                response_message = data.get("response", "").lower()
                
                # Vérifier éléments template accueil V2
                v2_elements = [
                    "thomas" in response_message,
                    "conseiller" in response_message or "expert" in response_message,
                    "josmoze" in response_message or "josmose" in response_message,
                    "osmoseur" in response_message,
                    "famille" in response_message or "aider" in response_message
                ]
                
                success_rate = sum(v2_elements) / len(v2_elements)
                
                if success_rate >= 0.8:  # 80% des éléments présents
                    self.log_test("ACCUEIL V2 Template", True, 
                                f"✅ Template V2 détecté ({success_rate*100:.0f}%): Thomas conseiller Josmoze présent")
                    return True
                else:
                    self.log_test("ACCUEIL V2 Template", False, 
                                f"❌ Template V2 incomplet ({success_rate*100:.0f}%): {response_message[:100]}...")
                    return False
            else:
                self.log_test("ACCUEIL V2 Template", False, f"Status: {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("ACCUEIL V2 Template", False, f"Exception: {str(e)}")
            return False

    def test_thomas_v2_prix_corrects(self):
        """Test 2: Prix corrects (449€, 549€, 899€, 39.90€)"""
        try:
            chat_data = {
                "message": "Quels sont vos prix ?",
                "session_id": "test_prix_v2"
            }
            
            response = self.session.post(
                f"{BACKEND_URL}/ai-agents/chat",
                json=chat_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                response_message = data.get("response", "")
                
                # Vérifier prix corrects V2
                prix_corrects = [
                    "449" in response_message and "€" in response_message,  # Essentiel 449€
                    "549" in response_message and "€" in response_message,  # Premium 549€
                    "899" in response_message and "€" in response_message,  # Prestige 899€
                    "39.90" in response_message or "39,90" in response_message  # Filtre Douche 39.90€
                ]
                
                prix_found = sum(prix_corrects)
                
                if prix_found >= 3:  # Au moins 3 prix corrects sur 4
                    self.log_test("PRIX CORRECTS V2", True, 
                                f"✅ Prix V2 détectés ({prix_found}/4): 449€, 549€, 899€, 39.90€")
                    return True
                else:
                    self.log_test("PRIX CORRECTS V2", False, 
                                f"❌ Prix V2 manquants ({prix_found}/4): {response_message[:200]}...")
                    return False
            else:
                self.log_test("PRIX CORRECTS V2", False, f"Status: {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("PRIX CORRECTS V2", False, f"Exception: {str(e)}")
            return False

    def test_thomas_v2_objection_budget_bienveillant(self):
        """Test 3: Objection budget avec ton bienveillant + Essentiel 449€"""
        try:
            chat_data = {
                "message": "C'est trop cher",
                "session_id": "test_budget_v2"
            }
            
            response = self.session.post(
                f"{BACKEND_URL}/ai-agents/chat",
                json=chat_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                response_message = data.get("response", "").lower()
                
                # Vérifier ton bienveillant V2
                ton_bienveillant = [
                    "comprends" in response_message or "compréhensible" in response_message,
                    "budget" in response_message,
                    "essentiel" in response_message,
                    "449" in response_message,
                    not any(word in response_message for word in ["urgent", "maintenant", "rapidement", "vite"])
                ]
                
                bienveillance_score = sum(ton_bienveillant) / len(ton_bienveillant)
                
                if bienveillance_score >= 0.8:
                    self.log_test("OBJECTION BUDGET Bienveillant", True, 
                                f"✅ Ton bienveillant V2 ({bienveillance_score*100:.0f}%): Essentiel 449€ proposé")
                    return True
                else:
                    self.log_test("OBJECTION BUDGET Bienveillant", False, 
                                f"❌ Ton insuffisamment bienveillant ({bienveillance_score*100:.0f}%): {response_message[:150]}...")
                    return False
            else:
                self.log_test("OBJECTION BUDGET Bienveillant", False, f"Status: {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("OBJECTION BUDGET Bienveillant", False, f"Exception: {str(e)}")
            return False

    def test_thomas_v2_premium_info_pitch(self):
        """Test 4: Info Premium 549€ avec thomas_pitch"""
        try:
            chat_data = {
                "message": "Parlez-moi du Premium",
                "session_id": "test_premium_v2"
            }
            
            response = self.session.post(
                f"{BACKEND_URL}/ai-agents/chat",
                json=chat_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                response_message = data.get("response", "").lower()
                
                # Vérifier info Premium V2 avec thomas_pitch
                premium_elements = [
                    "premium" in response_message,
                    "549" in response_message and "€" in response_message,
                    "bestseller" in response_message or "populaire" in response_message,
                    "familles" in response_message and ("4-5" in response_message or "4" in response_message),
                    "technologie" in response_message or "avancée" in response_message
                ]
                
                premium_score = sum(premium_elements) / len(premium_elements)
                
                if premium_score >= 0.8:
                    self.log_test("PREMIUM INFO Thomas_Pitch", True, 
                                f"✅ Premium V2 pitch complet ({premium_score*100:.0f}%): 549€ bestseller familles 4-5")
                    return True
                else:
                    self.log_test("PREMIUM INFO Thomas_Pitch", False, 
                                f"❌ Premium pitch incomplet ({premium_score*100:.0f}%): {response_message[:150]}...")
                    return False
            else:
                self.log_test("PREMIUM INFO Thomas_Pitch", False, f"Status: {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("PREMIUM INFO Thomas_Pitch", False, f"Exception: {str(e)}")
            return False

    def test_thomas_v2_filtre_douche_prix(self):
        """Test 5: Filtre douche 39.90€ correct"""
        try:
            chat_data = {
                "message": "Filtre douche",
                "session_id": "test_filtre_v2"
            }
            
            response = self.session.post(
                f"{BACKEND_URL}/ai-agents/chat",
                json=chat_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                response_message = data.get("response", "")
                
                # Vérifier filtre douche V2
                filtre_elements = [
                    "filtre" in response_message.lower() and "douche" in response_message.lower(),
                    "39.90" in response_message or "39,90" in response_message,
                    "€" in response_message,
                    "peau" in response_message.lower() or "cheveux" in response_message.lower(),
                    "bien-être" in response_message.lower() or "complément" in response_message.lower()
                ]
                
                filtre_score = sum(filtre_elements) / len(filtre_elements)
                
                if filtre_score >= 0.8:
                    self.log_test("FILTRE DOUCHE Prix Correct", True, 
                                f"✅ Filtre douche V2 complet ({filtre_score*100:.0f}%): 39.90€ bien-être")
                    return True
                else:
                    self.log_test("FILTRE DOUCHE Prix Correct", False, 
                                f"❌ Filtre douche incomplet ({filtre_score*100:.0f}%): {response_message[:150]}...")
                    return False
            else:
                self.log_test("FILTRE DOUCHE Prix Correct", False, f"Status: {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("FILTRE DOUCHE Prix Correct", False, f"Exception: {str(e)}")
            return False

    def test_thomas_v2_response_templates_usage(self):
        """Test 6: Utilisation des response_templates V2"""
        try:
            # Test avec message générique pour vérifier templates
            chat_data = {
                "message": "Comment ça marche ?",
                "session_id": "test_templates_v2"
            }
            
            response = self.session.post(
                f"{BACKEND_URL}/ai-agents/chat",
                json=chat_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                response_message = data.get("response", "").lower()
                suggestions = data.get("suggestions", [])
                
                # Vérifier structure response_templates V2
                template_elements = [
                    "thomas" in response_message,
                    "expert" in response_message or "conseiller" in response_message,
                    "josmoze" in response_message or "josmose" in response_message,
                    len(suggestions) >= 2,  # Suggestions présentes
                    "osmoseur" in response_message
                ]
                
                template_score = sum(template_elements) / len(template_elements)
                
                if template_score >= 0.8:
                    self.log_test("RESPONSE TEMPLATES V2 Usage", True, 
                                f"✅ Templates V2 utilisés ({template_score*100:.0f}%): Structure professionnelle")
                    return True
                else:
                    self.log_test("RESPONSE TEMPLATES V2 Usage", False, 
                                f"❌ Templates V2 insuffisants ({template_score*100:.0f}%): {response_message[:100]}...")
                    return False
            else:
                self.log_test("RESPONSE TEMPLATES V2 Usage", False, f"Status: {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("RESPONSE TEMPLATES V2 Usage", False, f"Exception: {str(e)}")
            return False

    def run_thomas_v2_sync_validation(self):
        """Exécute tous les tests de synchronisation Thomas V2"""
        print("🤖 DÉMARRAGE VALIDATION THOMAS V2 SYNCHRONISATION BACKEND-FRONTEND")
        print("=" * 70)
        
        # Tests de synchronisation V2
        tests = [
            self.test_thomas_v2_accueil_template,
            self.test_thomas_v2_prix_corrects,
            self.test_thomas_v2_objection_budget_bienveillant,
            self.test_thomas_v2_premium_info_pitch,
            self.test_thomas_v2_filtre_douche_prix,
            self.test_thomas_v2_response_templates_usage
        ]
        
        for test in tests:
            try:
                test()
                time.sleep(0.5)  # Pause entre tests
            except Exception as e:
                print(f"❌ ERREUR TEST {test.__name__}: {str(e)}")
        
        # Calcul du taux de réussite
        success_rate = (self.success_count / self.total_tests) * 100 if self.total_tests > 0 else 0
        
        print("\n" + "=" * 70)
        print(f"🎯 RÉSULTATS VALIDATION THOMAS V2 SYNCHRONISATION")
        print(f"📊 Taux de réussite: {success_rate:.1f}% ({self.success_count}/{self.total_tests})")
        
        if success_rate >= 80:
            print("✅ SYNCHRONISATION THOMAS V2 VALIDÉE - Objectif 80%+ atteint!")
            validation_status = "SUCCESS"
        else:
            print("❌ SYNCHRONISATION THOMAS V2 ÉCHOUÉE - Objectif 80%+ non atteint")
            validation_status = "FAILED"
        
        print("\n📋 DÉTAIL DES TESTS:")
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            print(f"{status} {result['test']}: {result['details']}")
        
        return {
            "validation_status": validation_status,
            "success_rate": success_rate,
            "tests_passed": self.success_count,
            "total_tests": self.total_tests,
            "detailed_results": self.test_results
        }

def main():
    """Point d'entrée principal"""
    tester = ThomasV2SyncTester()
    results = tester.run_thomas_v2_sync_validation()
    
    # Retourner le code de sortie approprié
    return 0 if results["validation_status"] == "SUCCESS" else 1

if __name__ == "__main__":
    exit(main())