#!/usr/bin/env python3
"""
🤖 SYSTÈME CONVERSATIONNEL OSMOSE AVANCÉ
===========================================
Agents IA vraiment interactifs avec conversations naturelles
- SMS bidirectionnels intelligents
- IA conversationnelle avec mémoire
- Stratégies commerciales adaptatives
"""

import openai
from openai import OpenAI
from twilio.rest import Client
import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import asyncio

# Configuration
client = OpenAI(api_key="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")
TWILIO_ACCOUNT_SID = "AC5d37fc46401a27a84540203820d680ca"
TWILIO_AUTH_TOKEN = "ead5696cac732121a4f448942845517c"
TWILIO_PHONE_NUMBER = "+16592518805"
JOSMOSE_WEBSITE = "https://38ebfc62-3cd2-4bbe-be3b-666002d5e6cd.preview.emergentagent.com"  # URL de base fonctionnelle

class ConversationalAgent:
    def __init__(self, name: str, role: str, personality: str):
        self.name = name
        self.role = role 
        self.personality = personality
        self.twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        self.conversation_memory = {}  # Stockage des conversations
        
    def get_conversation_context(self, client_phone: str) -> str:
        """Récupère le contexte de conversation précédent"""
        if client_phone in self.conversation_memory:
            history = self.conversation_memory[client_phone]
            # Formatage de l'historique pour l'IA
            context = "Historique conversation précédente:\n"
            for msg in history[-5:]:  # Derniers 5 messages
                timestamp = msg.get('timestamp', 'Inconnu')
                sender = msg.get('sender', 'Inconnu')
                text = msg.get('text', '')
                context += f"[{timestamp}] {sender}: {text}\n"
            return context
        return "Première conversation avec ce client."
    
    def save_message(self, client_phone: str, sender: str, message: str):
        """Sauvegarde un message dans l'historique"""
        if client_phone not in self.conversation_memory:
            self.conversation_memory[client_phone] = []
        
        self.conversation_memory[client_phone].append({
            'timestamp': datetime.now().strftime("%H:%M:%S"),
            'sender': sender,
            'text': message
        })
        
        # Limiter à 20 messages max par conversation
        if len(self.conversation_memory[client_phone]) > 20:
            self.conversation_memory[client_phone] = self.conversation_memory[client_phone][-20:]
    
    async def generate_intelligent_response(self, client_message: str, client_phone: str, client_name: str = "Client") -> str:
        """Génère une réponse intelligente basée sur le message client"""
        
        # Contexte de conversation
        conversation_context = self.get_conversation_context(client_phone)
        
        # Détection des mots-clés pour inclure automatiquement le lien
        message_lower = client_message.lower()
        keywords_need_link = ["prix", "coût", "tarif", "acheter", "commander", "info", "information", "site", "voir", "produit", "catalogue"]
        needs_link = any(keyword in message_lower for keyword in keywords_need_link)
        
        # Construction du prompt système avec directive lien
        link_directive = f"IMPORTANT: Si approprié (surtout si le client demande prix, infos, produits), TOUJOURS inclure le lien {JOSMOSE_WEBSITE} de façon naturelle dans ta réponse." if needs_link else f"Inclus le lien {JOSMOSE_WEBSITE} si c'est pertinent pour aider le client."
        
        base_directive = f"""
        Tu es {self.name}, {self.role} chez Josmose (purificateurs d'eau).
        
        Personnalité: {self.personality}
        
        DIRECTIVES STRICTES:
        1. Réponds de manière naturelle et conversationnelle
        2. Poses des questions pour qualifier le besoin si approprié
        3. Utilise les stratégies de Schopenhauer subtilement et éthiquement
        4. {link_directive}
        5. Maximum 140 caractères pour SMS (important!)
        6. Sois empathique et professionnel
        7. Mémorise et utilise l'historique de conversation
        8. Adapte ta réponse au contexte et aux besoins exprimés
        9. Si client demande prix/tarif, donne info rapide ET lien pour détails
        10. Guide toujours vers une action concrète (visite site, appel, rdv)
        
        HISTORIQUE CONVERSATION:
        {conversation_context}
        
        MESSAGE DU CLIENT: "{client_message}"
        
        Réponds intelligemment et de manière personnalisée à {client_name}.
        INCLUS le lien {JOSMOSE_WEBSITE} naturellement si approprié.
        """
        
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",  # Plus rapide et moins cher pour SMS
                messages=[
                    {"role": "system", "content": base_directive},
                    {"role": "user", "content": f"Client {client_name}: {client_message}"}
                ],
                max_tokens=120,  # Plus court pour SMS avec lien
                temperature=0.7
            )
            
            intelligent_response = response.choices[0].message.content.strip()
            
            # Force l'inclusion du lien si mots-clés critiques détectés
            if needs_link and JOSMOSE_WEBSITE not in intelligent_response:
                # Ajout automatique du lien si l'IA l'a oublié
                if len(intelligent_response) < 80:  # Assez de place
                    intelligent_response += f" Voir: {JOSMOSE_WEBSITE}"
                else:
                    # Remplacer une partie pour faire de la place
                    intelligent_response = intelligent_response[:60] + f"... Détails: {JOSMOSE_WEBSITE}"
            
            # Sauvegarder la conversation
            self.save_message(client_phone, f"Client ({client_name})", client_message)
            self.save_message(client_phone, f"{self.name}", intelligent_response)
            
            return intelligent_response
            
        except Exception as e:
            print(f"❌ Erreur IA: {str(e)}")
            
            # Réponses de secours avec lien automatique
            fallback_responses = {
                "Thomas": f"Merci {client_name} ! Questions sur l'eau importantes. Détails: {JOSMOSE_WEBSITE} ou appelez-nous ! 💧",
                "Sophie": f"Parfait {client_name} ! Prix et devis personnalisés: {JOSMOSE_WEBSITE} 📞",
                "Marie": f"Bonjour {client_name} 😊 Toutes nos infos: {JOSMOSE_WEBSITE} ✨",
                "Julien": f"{client_name}, finalisez rapidement: {JOSMOSE_WEBSITE} 🛒",
                "Caroline": f"Analyses complètes {client_name}: {JOSMOSE_WEBSITE} 📊"
            }
            return fallback_responses.get(self.name, f"Merci {client_name} ! Infos: {JOSMOSE_WEBSITE}")
    
    async def send_intelligent_sms(self, to_number: str, client_message: str, client_name: str = "Client") -> bool:
        """Envoie une réponse SMS intelligente"""
        try:
            # Génération réponse IA
            response = await self.generate_intelligent_response(client_message, to_number, client_name)
            
            # Envoi SMS propre (sans préfixe)
            sms = self.twilio_client.messages.create(
                body=response,
                from_=TWILIO_PHONE_NUMBER,
                to=to_number
            )
            
            print(f"✅ {self.name} → SMS intelligent: {response}")
            print(f"📋 SID: {sms.sid}")
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur envoi SMS: {str(e)}")
            return False

# Agents conversationnels pré-configurés
conversational_agents = {
    "thomas": ConversationalAgent(
        name="Thomas",
        role="conseiller expert en qualité de l'eau",
        personality="Empathique, curieux, poseur de bonnes questions, jamais insistant"
    ),
    
    "sophie": ConversationalAgent(
        name="Sophie", 
        role="experte en vente consultative",
        personality="Professionnelle, persuasive, gestion fine des objections, adaptable"
    ),
    
    "marie": ConversationalAgent(
        name="Marie",
        role="spécialiste relation client",
        personality="Chaleureuse, empathique, solutionniste, fidélisatrice"
    ),
    
    "julien": ConversationalAgent(
        name="Julien", 
        role="expert en récupération commerciale",
        personality="Bienveillant, créateur d'urgence douce, facilitateur de décisions"
    ),
    
    "caroline": ConversationalAgent(
        name="Caroline",
        role="analyste performance et conseils techniques", 
        personality="Analytique, pédagogue, apporteuse de valeur, basée données"
    )
}

def detect_appropriate_agent(message: str) -> str:
    """Détecte l'agent le plus approprié selon le message"""
    
    message_lower = message.lower()
    
    # Mots-clés pour chaque agent
    keywords = {
        "thomas": ["info", "question", "qualité", "eau", "conseil", "aide", "bonjour", "comment"],
        "sophie": ["prix", "achat", "commander", "intéressé", "closing", "vendre", "coût", "tarif"],
        "marie": ["problème", "service", "support", "aide", "réclamation", "assistance", "merci"],
        "julien": ["panier", "commande", "abandonné", "hésité", "réfléchir", "décision", "hésitation"],
        "caroline": ["analyse", "donnée", "statistique", "technique", "comparaison", "étude", "test"]
    }
    
    # Score par agent
    scores = {}
    for agent, words in keywords.items():
        scores[agent] = sum(1 for word in words if word in message_lower)
    
    # Agent avec le meilleur score
    best_agent = max(scores.items(), key=lambda x: x[1])
    
    # Si aucun match, Thomas par défaut
    return best_agent[0] if best_agent[1] > 0 else "thomas"

async def test_conversational_system():
    """Test du système conversationnel complet"""
    
    print("🤖 TEST SYSTÈME CONVERSATIONNEL AVANCÉ")
    print("=" * 50)
    
    client_phone = "+15068893760"  
    client_name = "Monsieur Dubois"
    
    # Simulation conversation progressive
    conversations = [
        ("Bonjour, je voudrais des infos sur vos purificateurs", "thomas"),
        ("Combien ça coûte exactement ?", "sophie"), 
        ("Est-ce que c'est vraiment efficace contre le calcaire ?", "caroline"),
        ("J'hésite encore... c'est cher quand même", "julien")
    ]
    
    print(f"🧪 Test conversation intelligente avec {client_name}")
    
    for i, (message, preferred_agent) in enumerate(conversations, 1):
        print(f"\n--- Échange {i} ---")
        print(f"👤 {client_name}: {message}")
        
        # Détection automatique ou agent préféré
        agent_name = preferred_agent
        agent = conversational_agents[agent_name]
        
        print(f"🤖 Agent sélectionné: {agent.name}")
        
        # Réponse intelligente
        success = await agent.send_intelligent_sms(client_phone, message, client_name)
        
        if success:
            print(f"✅ SMS intelligent envoyé")
        else:
            print(f"❌ Échec envoi")
        
        # Pause réaliste entre messages
        await asyncio.sleep(3)
    
    # Afficher l'historique de conversation de Thomas (premier agent)
    thomas = conversational_agents["thomas"]
    print(f"\n📋 HISTORIQUE CONVERSATION THOMAS:")
    if client_phone in thomas.conversation_memory:
        for msg in thomas.conversation_memory[client_phone]:
            print(f"[{msg['timestamp']}] {msg['sender']}: {msg['text']}")
    
    print(f"\n🌊 Test terminé ! Vérifiez vos SMS sur {client_phone}")

async def simulate_client_response(agent_name: str, client_message: str):
    """Simule une réponse client spécifique à un agent"""
    
    client_phone = "+15068893760"  
    client_name = "Monsieur Dubois"
    
    agent = conversational_agents.get(agent_name, conversational_agents["thomas"])
    
    print(f"\n🧪 TEST RÉPONSE SPÉCIFIQUE - Agent: {agent.name}")
    print(f"👤 Message client: {client_message}")
    
    success = await agent.send_intelligent_sms(client_phone, client_message, client_name)
    
    if success:
        print(f"✅ Réponse intelligente envoyée par {agent.name}")
    else:
        print(f"❌ Échec")

if __name__ == "__main__":
    # Test du système complet
    asyncio.run(test_conversational_system())
    
    # Tests spécifiques supplémentaires
    # asyncio.run(simulate_client_response("sophie", "Votre prix de 1500€ est trop élevé"))
    # asyncio.run(simulate_client_response("marie", "J'ai un problème avec ma commande"))