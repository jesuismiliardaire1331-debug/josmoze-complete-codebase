#!/usr/bin/env python3
"""
🧪 TEST CONVERSATION MANUELLE - Simule vos réponses SMS
"""

import asyncio
from conversational_agents import conversational_agents

async def test_conversation_avec_vos_reponses():
    """Test avec vos vraies réponses SMS du screenshot"""
    
    print("🧪 TEST CONVERSATION RÉALISTE")
    print("=" * 40)
    
    # Vos vraies réponses du screenshot
    conversations_reelles = [
        {
            "message_initial": "Bonjour Monsieur Dubois, avez-vous déjà réfléchi à l'impact de la qualité de l'eau sur votre santé au quotidien ?",
            "agent": "thomas",
            "reponse_client": "Bonjour oui un peu"
        },
        {
            "message_initial": "Merci de votre intérêt pour nos solutions ! Pour mieux vous guider, avez-vous des besoins spécifiques en tête ?", 
            "agent": "sophie",
            "reponse_client": "Oui"
        }
    ]
    
    client_phone = "+15068893760"
    client_name = "Monsieur Dubois" 
    
    for i, conv in enumerate(conversations_reelles, 1):
        print(f"\n--- CONVERSATION {i} avec {conv['agent'].upper()} ---")
        
        agent = conversational_agents[conv["agent"]]
        
        print(f"🤖 {agent.name} (message initial): {conv['message_initial']}")
        print(f"👤 Votre réponse: {conv['reponse_client']}")
        
        # Réponse intelligente à votre message
        response = await agent.generate_intelligent_response(
            conv["reponse_client"], client_phone, client_name
        )
        
        print(f"🤖 {agent.name} (réponse intelligente): {response}")
        
        # Envoi SMS réel
        success = await agent.send_intelligent_sms(
            client_phone, conv["reponse_client"], client_name
        )
        
        if success:
            print("✅ SMS de suivi envoyé sur votre mobile!")
        else:
            print("❌ Échec envoi")
        
        print("-" * 50)
        await asyncio.sleep(2)
    
    print("\n📱 Vérifiez votre téléphone pour les réponses intelligentes !")

if __name__ == "__main__":
    asyncio.run(test_conversation_avec_vos_reponses())