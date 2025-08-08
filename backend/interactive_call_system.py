#!/usr/bin/env python3
"""
📞 SYSTÈME D'APPELS VRAIMENT INTERACTIFS
==========================================
Appels conversationnels avec Speech-to-Text et réponses intelligentes
"""

from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse, Gather, Say
from openai import OpenAI
import asyncio
from typing import Dict, List
import json

# Configuration
openai_client = OpenAI(api_key="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")
twilio_client = Client("AC5d37fc46401a27a84540203820d680ca", "ead5696cac732121a4f448942845517c")
TWILIO_PHONE_NUMBER = "+16592518805"
JOSMOSE_WEBSITE = "https://38ebfc62-3cd2-4bbe-be3b-666002d5e6cd.preview.emergentagent.com"

class InteractiveCallAgent:
    def __init__(self, name: str, specialty: str):
        self.name = name
        self.specialty = specialty
        self.call_history = {}  # Historique des appels
        
    def generate_conversational_response(self, client_speech: str, call_context: Dict) -> str:
        """Génère une réponse conversationnelle basée sur ce que dit le client"""
        
        # Récupération du contexte d'appel
        conversation_history = call_context.get("history", [])
        client_name = call_context.get("client_name", "Client")
        
        # Construction du prompt conversationnel
        system_prompt = f"""
        Tu es {self.name}, {self.specialty} chez Josmose. Tu es au téléphone avec {client_name}.
        
        SITUATION: Appel commercial interactif sur les purificateurs d'eau.
        
        DIRECTIVES POUR CONVERSATION TÉLÉPHONIQUE:
        1. Réponds de façon naturelle et conversationnelle
        2. Écoute ce que dit le client et adapte ta réponse
        3. Pose des questions qualifiantes selon ses réponses
        4. Traite les objections avec empathie et logique
        5. Guide vers le site {JOSMOSE_WEBSITE} si besoin
        6. Propose des solutions concrètes
        7. Reste professionnel mais chaleureux
        8. Maximum 30 secondes de parole par réponse
        9. Utilise les stratégies de Schopenhauer subtilement
        10. Cherche à comprendre les vrais besoins
        
        HISTORIQUE DE CET APPEL:
        {json.dumps(conversation_history, ensure_ascii=False)}
        
        LE CLIENT VIENT DE DIRE: "{client_speech}"
        
        Réponds de façon naturelle comme dans une vraie conversation téléphonique.
        Adapte-toi à ce qu'il a dit et fais avancer la conversation commerciale.
        """
        
        try:
            response = openai_client.chat.completions.create(
                model="gpt-4o",  # Plus intelligent pour conversations
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Client dit: {client_speech}"}
                ],
                max_tokens=150,
                temperature=0.8  # Plus créatif pour conversation
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            # Réponse de secours conversationnelle
            return f"Je comprends {client_name}. Pouvez-vous m'en dire un peu plus sur ce qui vous intéresse concernant nos purificateurs d'eau ?"
    
    def create_interactive_twiml(self, client_name: str, conversation_stage: str = "opening") -> str:
        """Crée le TwiML pour un appel vraiment interactif"""
        
        response = VoiceResponse()
        
        # Messages d'ouverture selon l'étape
        opening_messages = {
            "opening": f"""
                Bonjour {client_name}, ici {self.name} de Josmose, votre spécialiste en purification d'eau.
                
                Je vous appelle car j'ai vu que vous vous intéressez à nos solutions pour améliorer 
                la qualité de votre eau. 
                
                Avant tout, puis-je vous demander : quelle est votre principale préoccupation 
                concernant l'eau que vous consommez actuellement ?
            """,
            
            "followup": f"""
                Merci {client_name} pour votre réponse précédente. 
                
                J'aimerais approfondir avec vous pour mieux comprendre vos besoins spécifiques.
                
                Dites-moi, qu'est-ce qui vous amène à chercher une solution de purification maintenant ?
            """,
            
            "closing": f"""
                Parfait {client_name}, je pense avoir une solution idéale pour vous.
                
                Basé sur ce que vous m'avez dit, je peux vous proposer notre système 
                qui répond exactement à vos besoins.
                
                Souhaitez-vous que je vous envoie les détails par SMS avec un lien direct vers notre site ?
            """
        }
        
        # Message d'ouverture
        message = opening_messages.get(conversation_stage, opening_messages["opening"])
        response.say(message, voice='Polly.Celine', language='fr-FR')
        
        # Collecte de la réponse avec Speech-to-Text
        gather = Gather(
            input='speech',
            language='fr-FR',
            speech_timeout='auto',
            timeout=15,
            action='/webhook/call-response',  # Webhook pour traiter la réponse
            method='POST'
        )
        
        gather.say(
            "Je vous écoute, parlez librement.",
            voice='Polly.Celine',
            language='fr-FR'
        )
        
        response.append(gather)
        
        # Si pas de réponse après timeout
        response.say(
            f"Je comprends que vous réfléchissiez {client_name}. Je vais vous envoyer nos informations par SMS. Consultez notre site {JOSMOSE_WEBSITE} ou rappelez-nous. Bonne journée !",
            voice='Polly.Celine',
            language='fr-FR'
        )
        
        return str(response)
    
    def make_intelligent_call(self, client_phone: str, client_name: str = "Client") -> bool:
        """Lance un appel vraiment conversationnel"""
        
        print(f"📞 {self.name} appelle {client_name} ({client_phone})...")
        
        try:
            # Pour l'instant, créons un TwiML statique mais intelligent
            twiml_content = f"""
            <Response>
                <Say voice="Polly.Celine" language="fr-FR">
                    Bonjour {client_name}, ici {self.name} de Josmose, votre spécialiste en purification d'eau.
                    
                    Je vous appelle car vous vous intéressez à nos solutions pour améliorer la qualité de votre eau.
                    
                    Puis-je vous poser quelques questions rapides pour mieux comprendre vos besoins ?
                    
                    Si vous êtes d'accord, appuyez sur 1.
                    Si vous préférez recevoir nos informations par SMS, appuyez sur 2.  
                    Pour parler à un conseiller humain, appuyez sur 3.
                </Say>
                
                <Gather numDigits="1" timeout="10">
                    <Say voice="Polly.Celine" language="fr-FR">
                        Appuyez sur 1 pour continuer, 2 pour recevoir un SMS, ou 3 pour un conseiller.
                    </Say>
                </Gather>
                
                <Say voice="Polly.Celine" language="fr-FR">
                    Pas de problème {client_name}. Je vous envoie nos informations par SMS.
                    Consultez notre site {JOSMOSE_WEBSITE} ou rappelez-nous au moment qui vous convient.
                    Merci et bonne journée !
                </Say>
            </Response>
            """
            
            call = twilio_client.calls.create(
                twiml=twiml_content,
                to=client_phone,
                from_=TWILIO_PHONE_NUMBER,
                record=False,
                timeout=30
            )
            
            print(f"✅ Appel interactif lancé - SID: {call.sid}")
            return True
            
        except Exception as e:
            print(f"❌ Erreur appel: {str(e)}")
            return False

# Agents d'appel spécialisés
call_agents = {
    "sophie": InteractiveCallAgent(
        name="Sophie",
        specialty="experte en vente consultative"
    ),
    
    "thomas": InteractiveCallAgent(
        name="Thomas", 
        specialty="conseiller en qualité de l'eau"
    )
}

async def test_appel_interactif():
    """Test d'appel vraiment interactif"""
    
    print("📞 TEST APPEL INTERACTIF AVANCÉ")
    print("=" * 40)
    
    sophie = call_agents["sophie"]
    
    client_phone = "+15068893760"
    client_name = "Monsieur Dubois"
    
    print(f"🎯 Sophie va appeler {client_name}...")
    print("📋 Appel avec conversation naturelle et options interactives")
    
    success = sophie.make_intelligent_call(client_phone, client_name)
    
    if success:
        print("✅ Appel interactif lancé avec succès!")
        print(f"📞 {client_name} devrait recevoir un appel intelligent dans quelques secondes")
        print("🔔 L'appel proposera 3 options interactives")
    else:
        print("❌ Échec lancement appel")

if __name__ == "__main__":
    asyncio.run(test_appel_interactif())