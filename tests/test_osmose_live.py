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
        
        # Nouveaux noms d'agents professionnels et rassurants
        agent_prompts = {
            "thomas": f"""
            Tu es Thomas, conseiller expert en qualité de l'eau et prospection commerciale.
            
            Client: {client_info['name']} 
            Contexte: Premier contact - prospection intelligente
            
            Utilise des questions intelligentes qui amènent le client à réfléchir.
            Message {message_type.upper()} de maximum 140 caractères.
            Ton professionnel, empathique, jamais agressif.
            COMMENCE TOUJOURS par "Bonjour Monsieur/Madame [nom du client],"
            
            Créé un message de prospection qui pose une question intéressante sur l'eau.
            """,
            
            "sophie": f"""
            Tu es Sophie, experte en vente consultative et appels commerciaux.
            
            Client: {client_info['name']}
            Contexte: Appel commercial - qualification et closing
            
            Structure ton discours en 3 points logiques et convaincants.
            Pour un appel vocal, message de 30-45 secondes maximum.
            Professionnel, persuasif mais respectueux.
            COMMENCE TOUJOURS par "Bonjour Monsieur/Madame [nom du client],"
            
            Créé un discours d'appel qui présente 3 bénéfices clairs des purificateurs d'eau.
            """,
            
            "marie": f"""
            Tu es Marie, spécialiste en relation client et suivi personnalisé.
            
            Client: {client_info['name']}
            Contexte: Suivi relationnel par SMS
            
            Message court, chaleureux, avec emojis appropriés.
            Maximum 140 caractères pour SMS.
            Crée une connexion personnelle et professionnelle.
            COMMENCE TOUJOURS par "Bonjour Monsieur/Madame [nom du client],"
            
            Créé un SMS de suivi qui montre de l'intérêt pour le bien-être du client.
            """,
            
            "julien": f"""
            Tu es Julien, expert en récupération commerciale et gestion d'abandons.
            
            Client: {client_info['name']}
            Contexte: Panier abandonné - rappel bienveillant
            
            Crée une approche chaleureuse sans pression aggressive.
            Message qui réveille l'intérêt avec un bénéfice tangible.
            Maximum 140 caractères pour SMS.
            COMMENCE TOUJOURS par "Bonjour Monsieur/Madame [nom du client],"
            
            Créé un message qui donne envie de finaliser l'achat abandonné.
            """,
            
            "caroline": f"""
            Tu es Caroline, analyste performance et insights clients.
            
            Client: {client_info['name']}
            Contexte: Partage d'informations utiles et conseils
            
            Message informatif avec des données intéressantes.
            Présente des statistiques ou conseils utiles.
            Maximum 140 caractères.
            COMMENCE TOUJOURS par "Bonjour Monsieur/Madame [nom du client],"
            
            Créé un message avec un conseil sur la qualité de l'eau qui apporte de la valeur.
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
        """Envoie un SMS de test sans mention Twilio"""
        try:
            # Message propre sans préfixe de test
            clean_message = message
            
            sms = self.twilio_client.messages.create(
                body=clean_message,  # Message direct sans préfixe
                from_=TWILIO_PHONE_NUMBER,
                to=TEST_CLIENT_NUMBER
            )
            
            self.log_result(
                agent=f"{agent_name.title()} 💬", 
                action="SMS",
                success=True,
                message="SMS envoyé avec succès",
                details=f"SID: {sms.sid}, Longueur: {len(message)} caractères"
            )
            return True
            
        except Exception as e:
            self.log_result(
                agent=f"{agent_name.title()} 💬",
                action="SMS", 
                success=False,
                message="Erreur envoi SMS",
                details=str(e)
            )
            return False

    def make_call_test(self, agent_name, message):
        """Effectue un appel interactif avec conversation possible"""
        try:
            # URL de webhook pour gérer l'interaction (à implémenter)
            webhook_url = "https://handler.twilio.com/twiml/EH4a9a64c1aa7c6b0f45b7e92bdcf2b24b"  # Webhook par défaut
            
            # TwiML pour conversation interactive
            twiml_content = f"""
            <Response>
                <Say voice="Polly.Celine" language="fr-FR">
                    {message}
                    
                    Si vous souhaitez en savoir plus, appuyez sur 1.
                    Pour être rappelé plus tard, appuyez sur 2.
                    Pour parler à un conseiller, appuyez sur 3.
                </Say>
                
                <Gather numDigits="1" timeout="10" action="{webhook_url}">
                    <Say voice="Polly.Celine" language="fr-FR">
                        Votre choix s'il vous plaît.
                    </Say>
                </Gather>
                
                <Say voice="Polly.Celine" language="fr-FR">
                    Merci pour votre attention. Un conseiller vous recontactera très prochainement. 
                    Bonne journée !
                </Say>
            </Response>
            """
            
            call = self.twilio_client.calls.create(
                twiml=twiml_content,
                to=TEST_CLIENT_NUMBER,
                from_=TWILIO_PHONE_NUMBER,
                record=False,
                timeout=30  # Timeout pour réponse
            )
            
            self.log_result(
                agent=f"{agent_name.title()} 📞",
                action="APPEL INTERACTIF",
                success=True,
                message="Appel interactif lancé avec succès",
                details=f"Call SID: {call.sid}, Conversation possible avec options"
            )
            return True
            
        except Exception as e:
            self.log_result(
                agent=f"{agent_name.title()} 📞",
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
            "name": "Monsieur Dubois",  # Nom plus réaliste
            "phone": TEST_CLIENT_NUMBER,
            "personality": "ANALYTIQUE"  # Pour le test
        }
        
        # Nouveaux agents avec prénoms professionnels
        agents_to_test = [
            ("thomas", "👨‍💼", "sms"),      # Ex-Socrate: Prospection  
            ("marie", "👩‍💼", "sms"),        # Ex-Cicéron: Relation client
            ("julien", "👨‍💼", "sms"),      # Ex-Démosthène: Paniers abandonnés
            ("sophie", "👩‍💼", "call")       # Ex-Aristote: Appels commerciaux
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
        
        # Test final Caroline (Analytics) 
        print(f"\n--- Test CAROLINE 📊 (Analytics & Conseils) ---")
        caroline_insights = self.generate_agent_message("caroline", client_info, "sms")
        print(f"💭 Conseils générés: {caroline_insights}")
        self.send_sms_test("caroline", caroline_insights)
        
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