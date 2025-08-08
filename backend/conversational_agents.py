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
JOSMOSE_WEBSITE = "https://www.josmose.com"  # URL officielle du site

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
        """Génère une réponse SMS ultra-optimisée avec intelligence conversationnelle maximale"""
        
        # Contexte de conversation
        conversation_context = self.get_conversation_context(client_phone)
        
        # Analyse poussée des intentions client
        message_lower = client_message.lower()
        
        # Catégories d'intentions avec mots-clés étendus
        intentions = {
            "prix_tarif": ["prix", "coût", "tarif", "combien", "€", "euros", "cher", "budget", "coûte"],
            "info_produit": ["info", "information", "produit", "catalogue", "voir", "montre", "détails", "caractéristiques"],
            "achat_commande": ["acheter", "commander", "commande", "veux", "voudrais", "prendre", "intéressé"],
            "comparaison": ["comparai", "différence", "mieux", "quel", "lequel", "choisir", "conseil"],
            "technique": ["technique", "fonctionne", "installation", "entretien", "filtre", "garantie"],
            "urgence": ["urgent", "rapidement", "vite", "immédiat", "maintenant", "aujourd'hui"],
            "hésitation": ["hésite", "réfléchis", "pas sûr", "doute", "peut-être", "voir"],
            "positif": ["oui", "ok", "d'accord", "intéresse", "parfait", "bien", "merci"],
            "négatif": ["non", "pas intéressé", "cher", "plus tard", "réfléchir"]
        }
        
        # Détection de l'intention principale
        detected_intention = "general"
        max_score = 0
        for intention, keywords in intentions.items():
            score = sum(1 for keyword in keywords if keyword in message_lower)
            if score > max_score:
                max_score = score
                detected_intention = intention
        
        # Génération du prompt ultra-personnalisé selon l'agent ET l'intention
        prompt_templates = {
            "Thomas": {
                "prix_tarif": f"Client demande les prix. Donne fourchette rapide (199€-599€) + lien {JOSMOSE_WEBSITE} pour devis personnalisé + question qualifiante sur besoins.",
                "info_produit": f"Client veut des infos produits. Donne 2-3 avantages clés + lien {JOSMOSE_WEBSITE} pour catalogue + question sur usage prévu.",
                "achat_commande": f"Client veut acheter. Félicite + guide vers {JOSMOSE_WEBSITE} pour choisir + question sur priorités (santé/goût/économie).",
                "comparaison": f"Client compare. Donne notre différenciation unique + lien {JOSMOSE_WEBSITE} + question sur critères importants.",
                "technique": f"Client question technique. Donne réponse experte concise + lien {JOSMOSE_WEBSITE} pour détails + propose échange téléphonique.",
                "hésitation": f"Client hésite. Empathie + rassurance + petit bénéfice concret + lien {JOSMOSE_WEBSITE} + question ouverte.",
                "positif": f"Client positif. Enthousiasme + prochaine étape concrète + lien {JOSMOSE_WEBSITE} + question progression.",
                "général": f"Réponse empathique + question qualifiante + lien {JOSMOSE_WEBSITE} si approprié."
            },
            
            "Sophie": {
                "prix_tarif": f"Client demande prix. Fourchette + valeur/prix + lien {JOSMOSE_WEBSITE} pour configurateur + ROI/économies.",
                "info_produit": f"Client infos. 3 bénéfices commerciaux + lien {JOSMOSE_WEBSITE} + question besoin urgent/prévu.",
                "achat_commande": f"Client acheter. Closing doux + guide {JOSMOSE_WEBSITE} + urgence douce (stock/promo) + facilitation.",
                "comparaison": f"Client compare. Avantages concurrentiels + preuve sociale + lien {JOSMOSE_WEBSITE} + question décision.",
                "hésitation": f"Client hésite. Objection handling + rassurance + petit plus + lien {JOSMOSE_WEBSITE} + closing alternatif.",
                "positif": f"Client positif. Momentum + action immédiate + lien {JOSMOSE_WEBSITE} + facilitation achat.",
                "négatif": f"Client négatif. Empathie + reframe + bénéfice inattendu + lien {JOSMOSE_WEBSITE} + porte ouverte.",
                "général": f"Approche consultative + qualification besoin + lien {JOSMOSE_WEBSITE} + question closing."
            },
            
            "Marie": {
                "prix_tarif": f"Client prix. Transparence + options financement + lien {JOSMOSE_WEBSITE} pour simulateur + accompagnement.",
                "info_produit": f"Client infos. Service personnalisé + lien {JOSMOSE_WEBSITE} + proposition accompagnement choix.",
                "achat_commande": f"Client commande. Accompagnement complet + lien {JOSMOSE_WEBSITE} + rassurance SAV.",
                "technique": f"Client technique. Expertise + lien {JOSMOSE_WEBSITE} pour guides + support personnalisé.",
                "hésitation": f"Client hésite. Écoute + compréhension + solutions personnalisées + lien {JOSMOSE_WEBSITE}.",
                "général": f"Approche relationnelle + écoute + lien {JOSMOSE_WEBSITE} + proposition d'aide."
            },
            
            "Julien": {
                "prix_tarif": f"Client prix. Prix juste + économies long terme + lien {JOSMOSE_WEBSITE} + urgence stock/promo.",
                "achat_commande": f"Client commande. Félicitations + facilitation maximum + lien {JOSMOSE_WEBSITE} + bonus/urgence.",
                "hésitation": f"Client hésite. Levée objections + offre spéciale + lien {JOSMOSE_WEBSITE} + scarcité.",
                "négatif": f"Client négatif. Dernière chance + offre exceptionnelle + lien {JOSMOSE_WEBSITE} + urgence.",
                "général": f"Récupération + motivation + lien {JOSMOSE_WEBSITE} + incitation action."
            },
            
            "Caroline": {
                "technique": f"Client technique. Données précises + études/tests + lien {JOSMOSE_WEBSITE} pour documentation + expertise.",
                "comparaison": f"Client compare. Analyses objectives + tableaux comparatifs + lien {JOSMOSE_WEBSITE} + recommandation data-driven.",
                "info_produit": f"Client infos. Spécifications détaillées + performances + lien {JOSMOSE_WEBSITE} + tests personnalisés.",
                "général": f"Approche analytique + données concrètes + lien {JOSMOSE_WEBSITE} + insights personnalisés."
            }
        }
        
        # Sélection du template approprié
        agent_templates = prompt_templates.get(self.name, prompt_templates["Thomas"])
        template = agent_templates.get(detected_intention, agent_templates.get("général", ""))
        
        # Construction du prompt ultra-optimisé
        base_directive = f"""
        Tu es {self.name}, {self.role} chez Josmose (purificateurs d'eau).
        Personnalité: {self.personality}
        
        CLIENT: {client_name}
        INTENTION DÉTECTÉE: {detected_intention}
        MESSAGE CLIENT: "{client_message}"
        
        CONTEXT PRÉCÉDENT:
        {conversation_context}
        
        DIRECTIVE SPÉCIALISÉE:
        {template}
        
        RÈGLES SMS ULTRA-OPTIMALES:
        1. Maximum 160 caractères (limite SMS standard)
        2. Ton personnalisé selon ton rôle
        3. TOUJOURS inclure lien {JOSMOSE_WEBSITE} si approprié à l'intention
        4. Question engageante pour continuer conversation
        5. Action concrète suggérée
        6. Urgence douce si approprié
        7. Personnalisation avec nom client
        8. Éviter répétitions avec historique
        9. Utiliser émojis avec parcimonie (maximum 1-2)
        10. Appel à l'action clair et direct
        
        Génère la réponse SMS PARFAITE pour cette intention et ce contexte.
        """
        
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": base_directive},
                    {"role": "user", "content": f"Génère le SMS parfait pour {client_name}"}
                ],
                max_tokens=100,  # Augmenté pour messages plus complets mais dans la limite SMS
                temperature=0.7  # Réduit pour plus de cohérence
            )
            
            intelligent_response = response.choices[0].message.content.strip()
            
            # Post-traitement pour optimisation finale
            # Définir les intentions critiques
            critical_intentions = ["prix_tarif", "info_produit", "achat_commande", "comparaison", "technique"]
            
            # Forcer respect limite 160 caractères SMS
            if len(intelligent_response) > 160:
                # Compresser automatiquement
                parts = intelligent_response.split(' ')
                compressed = ""
                for part in parts:
                    if len(compressed + " " + part) <= 155:  # 5 chars de marge
                        compressed = compressed + " " + part if compressed else part
                    else:
                        break
                # S'assurer qu'on a l'URL si critique
                if JOSMOSE_WEBSITE not in compressed and detected_intention in critical_intentions:
                    # Sacrifier du texte pour garder l'URL
                    url_space = len(JOSMOSE_WEBSITE) + 1
                    available_space = 155 - url_space
                    if available_space > 20:  # Minimum viable
                        text_part = intelligent_response[:available_space].rsplit(' ', 1)[0]
                        intelligent_response = f"{text_part} {JOSMOSE_WEBSITE}"
                    else:
                        intelligent_response = compressed
                else:
                    intelligent_response = compressed
                    
            # Forcer inclusion lien si intention critique et pas présent
            if detected_intention in critical_intentions and JOSMOSE_WEBSITE not in intelligent_response:
                if len(intelligent_response) < 120:  # Assez de place
                    intelligent_response += f" {JOSMOSE_WEBSITE}"
                else:
                    # Compresser pour faire de la place
                    available = 155 - len(JOSMOSE_WEBSITE)
                    text_part = intelligent_response[:available].rsplit(' ', 1)[0]
                    intelligent_response = f"{text_part} {JOSMOSE_WEBSITE}"
            
            # Sauvegarder conversation avec métadonnées
            self.save_message(client_phone, f"Client ({client_name})", client_message)
            self.save_message(client_phone, f"{self.name} [{detected_intention}]", intelligent_response)
            
            return intelligent_response
            
        except Exception as e:
            print(f"❌ Erreur IA: {str(e)}")
            
            # Réponses de secours ultra-optimisées par intention
            emergency_responses = {
                "prix_tarif": f"{client_name}, nos purificateurs 199-599€ selon besoins. Devis: {JOSMOSE_WEBSITE} Votre budget ?",
                "info_produit": f"{client_name}, découvrez notre gamme: {JOSMOSE_WEBSITE} Quelle eau purifiez-vous ?",
                "achat_commande": f"Parfait {client_name} ! Choisissez votre modèle: {JOSMOSE_WEBSITE} Installation quand ?",
                "hésitation": f"Je comprends {client_name}. Essai gratuit 30j: {JOSMOSE_WEBSITE} Questions ?",
                "général": f"Merci {client_name} ! Toutes nos solutions: {JOSMOSE_WEBSITE} Puis-je vous aider ?"
            }
            
            return emergency_responses.get(detected_intention, f"Merci {client_name} ! Infos: {JOSMOSE_WEBSITE}")
    
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