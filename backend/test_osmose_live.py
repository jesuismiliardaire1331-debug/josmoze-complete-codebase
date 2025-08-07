#!/usr/bin/env python3
"""
🌊 TEST OSMOSE LIVE - Agents IA avec APIs Réelles
================================================
Test complet du système OSMOSE avec vraies APIs Twilio et OpenAI
Numéro de test : +15068893760

Usage: python3 test_osmose_live.py
"""

import openai
from twilio.rest import Client
import os
from datetime import datetime
import asyncio
import json

# Configuration depuis .env
openai.api_key = os.environ.get('OPENAI_API_KEY')
TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.environ.get('TWILIO_PHONE_NUMBER')
TEST_CLIENT_NUMBER = os.environ.get('TEST_CLIENT_NUMBER')
TEST_CLIENT_NAME = os.environ.get('TEST_CLIENT_NAME', "Client Test")

class OSMOSEAgentTester:
    def __init__(self):
        self.twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        self.results = []
        
    def log_result(self, agent, action, success, message, details=""):
        """Logger les résultats des tests"""
        result = {
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "agent": agent,
            "action": action,
            "success": success,
            "message": message,
            "details": details
        }
        self.results.append(result)
        status = "✅" if success else "❌"
        print(f"{status} {agent} {action}: {message}")
        if details:
            print(f"   📋 {details}")

    def generate_agent_message(self, agent_name, client_info, message_type="sms"):
        """Génère un message personnalisé avec OpenAI selon l'agent"""
        
        agent_prompts = {
            "socrate": f"""
            Tu es Socrate 🧠, agent de prospection philosophique pour purificateurs d'eau.
            
            Client: {client_info['name']} 
            Contexte: Premier contact - prospection intelligente
            
            Utilise la méthode socratique avec des questions qui amènent le client à réfléchir.
            Message {message_type.upper()} de maximum 160 caractères.
            Ton empathique, curieux, jamais agressif.
            
            Créé un message de prospection qui pose une question intéressante sur l'eau.
            """,
            
            "aristote": f"""
            Tu es Aristote 📞, agent d'appels commerciaux avec logique parfaite.
            
            Client: {client_info['name']}
            Contexte: Appel commercial - qualification et closing
            
            Structure ton discours en 3 points logiques comme un syllogisme.
            Pour un appel vocal, message de 30-45 secondes maximum.
            Professionnel, persuasif mais respectueux.
            
            Créé un discours d'appel qui présente 3 bénéfices clairs des purificateurs d'eau.
            """,
            
            "ciceron": f"""
            Tu es Cicéron 💬, maître de l'empathie par SMS.
            
            Client: {client_info['name']}
            Contexte: Suivi relationnel par SMS
            
            Message court, chaleureux, avec emojis appropriés.
            Maximum 160 caractères pour SMS.
            Crée une connexion émotionnelle.
            
            Créé un SMS de suivi qui montre de l'intérêt pour le bien-être du client.
            """,
            
            "demosthene": f"""
            Tu es Démosthène 🛒, expert récupération paniers abandonnés.
            
            Client: {client_info['name']}
            Contexte: Panier abandonné - urgence douce
            
            Crée une urgence sans pression aggressive.
            Message qui réveille l'intérêt sans forcer.
            Maximum 160 caractères pour SMS.
            
            Créé un message qui donne envie de finaliser l'achat abandonné.
            """,
            
            "platon": f"""
            Tu es Platon 📊, analyste stratégique.
            
            Client: {client_info['name']}
            Contexte: Insights et recommandations
            
            Message analytique avec des données intéressantes.
            Présente des statistiques ou insights utiles.
            Maximum 160 caractères.
            
            Créé un message avec un insight sur la qualité de l'eau qui interpelle.
            """
        }
        
        try:
            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Tu es un expert en communication commerciale éthique et empathique."},
                    {"role": "user", "content": agent_prompts[agent_name]}
                ],
                max_tokens=150,
                temperature=0.7
            )
            
            message = response.choices[0].message.content.strip()
            return message
            
        except Exception as e:
            return f"Message de {agent_name} (Erreur IA: {str(e)})"

    def send_sms_test(self, agent_name, message):
        """Envoie un SMS de test"""
        try:
            sms = self.twilio_client.messages.create(
                body=f"[TEST OSMOSE - {agent_name.upper()}] {message}",
                from_=TWILIO_PHONE_NUMBER,
                to=TEST_CLIENT_NUMBER
            )
            
            self.log_result(
                agent=f"{agent_name} 💬", 
                action="SMS",
                success=True,
                message="SMS envoyé avec succès",
                details=f"SID: {sms.sid}, Longueur: {len(message)} caractères"
            )
            return True
            
        except Exception as e:
            self.log_result(
                agent=f"{agent_name} 💬",
                action="SMS", 
                success=False,
                message="Erreur envoi SMS",
                details=str(e)
            )
            return False

    def make_call_test(self, agent_name, message):
        """Effectue un appel de test avec synthèse vocale"""
        try:
            # TwiML pour synthèse vocale française
            twiml_content = f"""
            <Response>
                <Say voice="Polly.Celine" language="fr-FR">
                    Bonjour, c'est {agent_name} du système OSMOSE. 
                    {message}
                    Ceci était un test du système d'agents IA. 
                    Merci de votre attention. Au revoir.
                </Say>
            </Response>
            """
            
            call = self.twilio_client.calls.create(
                twiml=twiml_content,
                to=TEST_CLIENT_NUMBER,
                from_=TWILIO_PHONE_NUMBER,
                record=False  # Pas d'enregistrement pour les tests
            )
            
            self.log_result(
                agent=f"{agent_name} 📞",
                action="APPEL",
                success=True,
                message="Appel lancé avec succès",
                details=f"Call SID: {call.sid}, Durée estimée: 30s"
            )
            return True
            
        except Exception as e:
            self.log_result(
                agent=f"{agent_name} 📞",
                action="APPEL",
                success=False,
                message="Erreur appel",
                details=str(e)
            )
            return False

    def test_openai_connection(self):
        """Teste la connexion OpenAI"""
        try:
            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": "Test OSMOSE : dis juste 'Connexion OpenAI réussie!'"}],
                max_tokens=10
            )
            
            message = response.choices[0].message.content.strip()
            self.log_result("SYSTÈME", "OpenAI", True, message)
            return True
            
        except Exception as e:
            self.log_result("SYSTÈME", "OpenAI", False, f"Erreur: {str(e)}")
            return False

    def test_twilio_connection(self):
        """Teste la connexion Twilio"""
        try:
            # Récupérer les infos du compte
            account = self.twilio_client.api.accounts(TWILIO_ACCOUNT_SID).fetch()
            
            self.log_result(
                "SYSTÈME", "Twilio", True, 
                f"Connexion réussie - Compte: {account.friendly_name}",
                f"Statut: {account.status}, Numéro: {TWILIO_PHONE_NUMBER}"
            )
            return True
            
        except Exception as e:
            self.log_result("SYSTÈME", "Twilio", False, f"Erreur: {str(e)}")
            return False

    async def run_complete_test(self):
        """Lance le test complet du système OSMOSE"""
        print("🌊" * 50)
        print("🌊" + " " * 16 + "TEST OSMOSE LIVE COMPLET" + " " * 16 + "🌊")
        print("🌊" + " " * 12 + "Agents IA avec APIs Réelles" + " " * 12 + "🌊") 
        print("🌊" * 50)
        print()
        
        print(f"📱 Numéro de test: {TEST_CLIENT_NUMBER}")
        print(f"📞 Numéro Twilio: {TWILIO_PHONE_NUMBER}")
        print(f"👤 Client test: {TEST_CLIENT_NAME}")
        print()
        
        # Test des connexions
        print("🔍 TESTS DE CONNEXION:")
        openai_ok = self.test_openai_connection()
        twilio_ok = self.test_twilio_connection()
        
        if not openai_ok or not twilio_ok:
            print("\n❌ ÉCHEC DES TESTS DE CONNEXION - ARRÊT")
            return False
        
        print("\n🤖 TESTS DES AGENTS IA:")
        
        client_info = {
            "name": TEST_CLIENT_NAME,
            "phone": TEST_CLIENT_NUMBER,
            "personality": "ANALYTIQUE"  # Pour le test
        }
        
        agents_to_test = [
            ("socrate", "🧠", "sms"),
            ("ciceron", "💬", "sms"), 
            ("demosthene", "🛒", "sms"),
            ("aristote", "📞", "call")  # Appel en dernier
        ]
        
        # Tests SMS d'abord
        for agent_name, emoji, action_type in agents_to_test:
            print(f"\n--- Test {agent_name.upper()} {emoji} ---")
            
            # Génération du message IA
            message = self.generate_agent_message(agent_name, client_info, action_type)
            print(f"💭 Message généré: {message}")
            
            # Envoi selon le type
            if action_type == "sms":
                success = self.send_sms_test(agent_name, message)
            elif action_type == "call":
                success = self.make_call_test(agent_name, message)
            
            # Pause entre les tests
            if success:
                await asyncio.sleep(3)  # 3 secondes entre chaque test
        
        # Test final Platon (Analytics)
        print(f"\n--- Test PLATON 📊 (Analytics) ---")
        platon_insights = self.generate_agent_message("platon", client_info, "sms")
        print(f"💭 Insights générés: {platon_insights}")
        self.send_sms_test("platon", platon_insights)
        
        # Résumé final
        print("\n" + "🌊" * 50)
        print("🌊" + " " * 18 + "RÉSUMÉ DES TESTS" + " " * 18 + "🌊")
        print("🌊" * 50)
        
        total_tests = len(self.results)
        success_tests = len([r for r in self.results if r["success"]])
        
        print(f"📊 Total tests: {total_tests}")
        print(f"✅ Réussis: {success_tests}")
        print(f"❌ Échecs: {total_tests - success_tests}")
        print(f"📈 Taux de réussite: {(success_tests/total_tests)*100:.1f}%")
        
        print(f"\n📱 Vérifiez votre téléphone {TEST_CLIENT_NUMBER}")
        print("   Vous devriez avoir reçu:")
        print("   📨 4-5 SMS des différents agents")
        print("   📞 1 appel d'Aristote avec discours commercial")
        
        return True

# Point d'entrée
async def main():
    """Fonction principale"""
    
    # Vérification des variables d'environnement
    required_vars = [
        'OPENAI_API_KEY', 'TWILIO_ACCOUNT_SID', 
        'TWILIO_AUTH_TOKEN', 'TWILIO_PHONE_NUMBER', 'TEST_CLIENT_NUMBER'
    ]
    
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    
    if missing_vars:
        print(f"❌ Variables manquantes: {', '.join(missing_vars)}")
        print("Vérifiez le fichier backend/.env")
        return False
    
    # Lancement des tests
    tester = OSMOSEAgentTester()
    await tester.run_complete_test()
    
    return True

if __name__ == "__main__":
    asyncio.run(main())