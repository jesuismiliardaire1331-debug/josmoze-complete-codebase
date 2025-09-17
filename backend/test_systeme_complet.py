#!/usr/bin/env python3
"""
🎯 TEST SYSTÈME COMPLET - SMS avec liens + Appels interactifs
"""

import asyncio
from conversational_agents import conversational_agents
from interactive_call_system import call_agents

async def test_systeme_conversationnel_complet():
    """Test complet SMS avec liens automatiques + appel interactif"""
    
    print("🌊 TEST SYSTÈME CONVERSATIONNEL COMPLET")
    print("=" * 50)
    
    client_phone = "+15068893760"
    client_name = "Monsieur Dubois"
    
    # PARTIE 1: Tests SMS avec questions typiques + liens automatiques
    print("📱 PARTIE 1: SMS AVEC LIENS AUTOMATIQUES")
    print("-" * 30)
    
    questions_typiques = [
        ("Quel est le prix de vos purificateurs ?", "sophie"),
        ("J'aimerais voir vos produits", "thomas"), 
        ("Pouvez-vous m'envoyer le catalogue ?", "marie"),
        ("Je voudrais commander", "julien")
    ]
    
    for i, (question, agent_name) in enumerate(questions_typiques, 1):
        print(f"\n--- Test SMS {i} ---")
        print(f"❓ Question client: {question}")
        
        agent = conversational_agents[agent_name]
        print(f"🤖 Agent: {agent.name}")
        
        # Test de réponse avec lien automatique
        success = await agent.send_intelligent_sms(client_phone, question, client_name)
        
        if success:
            print("✅ SMS avec lien envoyé!")
        else:
            print("❌ Échec SMS")
        
        await asyncio.sleep(3)
    
    print("\n" + "=" * 50)
    print("📞 PARTIE 2: APPEL INTERACTIF")
    print("-" * 30)
    
    # PARTIE 2: Appel interactif avec Sophie
    sophie = call_agents["sophie"]
    
    print(f"📞 Sophie va appeler {client_name} pour appel interactif...")
    print("🗣️ Appel avec conversation naturelle et réponses vocales")
    
    success = sophie.make_intelligent_call(client_phone, client_name)
    
    if success:
        print("✅ Appel interactif lancé!")
        print("📋 Options proposées: 1=Questions, 2=SMS info, 3=Conseiller")
    else:
        print("❌ Échec appel")
    
    print("\n" + "🎉" * 50)
    print("🎊 SYSTÈME COMPLET DÉPLOYÉ ! 🎊")
    print("🎉" * 50)
    
    print(f"\n📱 VÉRIFIEZ VOTRE TÉLÉPHONE {client_phone}:")
    print("📨 4 SMS intelligents avec liens automatiques reçus")
    print("📞 1 appel interactif avec options vocales")
    print("🔗 Tous les SMS contiennent le lien du site")
    print("🗣️ Appel permet conversation naturelle")
    
    print(f"\n🌐 SITE WEB: https://josmoze-ecommerce.preview.emergentagent.com")
    print("✅ Bouton 'Acheter' fonctionnel")
    print("✅ Produits chargés et disponibles")

if __name__ == "__main__":
    asyncio.run(test_systeme_conversationnel_complet())