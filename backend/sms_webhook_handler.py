#!/usr/bin/env python3
"""
📱 SMS WEBHOOK HANDLER - Vraies Conversations Bidirectionnelles
================================================================
Traite les réponses SMS clients et génère des réponses intelligentes
"""

from fastapi import FastAPI, Request, Form
from fastapi.responses import Response
from twilio.twiml.messaging_response import MessagingResponse
from conversational_agents import conversational_agents, detect_appropriate_agent
import asyncio
import logging

# Configuration logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

sms_app = FastAPI()

@sms_app.post("/sms-webhook")
async def handle_sms_webhook(
    From: str = Form(...),
    Body: str = Form(...),
    To: str = Form(...)
):
    """Traite les SMS entrants et génère des réponses intelligentes"""
    
    logger.info(f"📨 SMS reçu de {From}: {Body}")
    
    try:
        # Détection automatique de l'agent approprié
        agent_name = detect_appropriate_agent(Body)
        agent = conversational_agents.get(agent_name, conversational_agents["thomas"])
        
        logger.info(f"🤖 Agent sélectionné: {agent.name}")
        
        # Génération réponse intelligente
        client_name = extract_client_name(From) # Sera amélioré
        intelligent_response = await agent.generate_intelligent_response(
            Body, From, client_name
        )
        
        # Création réponse TwiML
        twiml = MessagingResponse()
        twiml.message(intelligent_response)
        
        logger.info(f"✅ Réponse envoyée par {agent.name}: {intelligent_response[:50]}...")
        
        return Response(
            content=str(twiml),
            media_type="application/xml"
        )
        
    except Exception as e:
        logger.error(f"❌ Erreur webhook SMS: {str(e)}")
        
        # Réponse de secours
        twiml = MessagingResponse()
        twiml.message("Merci pour votre message ! Un conseiller vous répond rapidement. 😊")
        
        return Response(
            content=str(twiml),
            media_type="application/xml"
        )

def extract_client_name(phone_number: str) -> str:
    """Extrait le nom du client depuis le numéro (à améliorer avec DB)"""
    
    # Base simple pour les tests
    name_mapping = {
        "+15068893760": "Monsieur Dubois",
        # Ajouter d'autres clients ici
    }
    
    return name_mapping.get(phone_number, "Client")

@sms_app.get("/sms-webhook-status")
async def webhook_status():
    """Status du webhook pour debug"""
    return {
        "status": "active",
        "agents_available": list(conversational_agents.keys()),
        "webhook_url": "https://votre-ngrok-url.ngrok.io/sms-webhook"
    }

# Pour tester localement
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(sms_app, host="0.0.0.0", port=8002)