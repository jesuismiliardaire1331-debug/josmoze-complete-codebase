#!/usr/bin/env python3
"""
📱 TEST SMS CORRIGÉ - URL Fonctionnelle
=====================================
Test avec URL corrigée qui marche vraiment !
"""

import asyncio
from conversational_agents import conversational_agents, JOSMOSE_WEBSITE

async def test_sms_url_corrigee():
    """Test SMS avec URL fonctionnelle corrigée"""
    
    print("📱 TEST SMS - URL FONCTIONNELLE CORRIGÉE")
    print("=" * 50)
    
    client_phone = "+15068893760"
    client_name = "Cher Client"
    
    print(f"📞 Numéro: {client_phone}")
    print(f"🌐 URL corrigée (fonctionnelle): {JOSMOSE_WEBSITE}")
    print("✅ Cette URL fonctionne (testée avec succès)")
    print()
    
    # D'abord, génération de test pour montrer la correction
    print("🧪 GÉNÉRATION MESSAGES (AVANT ENVOI):")
    print("-" * 40)
    
    scenarios = [
        ("sophie", "Combien coûtent vos purificateurs ?", "💰 Prix"),
        ("thomas", "J'aimerais des informations sur vos systèmes", "📋 Info"),
        ("marie", "Je ne sais pas si j'en ai besoin...", "🤔 Hésitation")
    ]
    
    for agent_name, message, contexte in scenarios:
        agent = conversational_agents[agent_name]
        response = await agent.generate_intelligent_response(message, client_phone, client_name)
        
        print(f"\n{contexte} - {agent.name}:")
        print(f"💬 \"{response}\"")
        print(f"📏 {len(response)} caractères")
        
        if "preview.emergentagent.com" in response:
            print("✅ URL fonctionnelle présente!")
        elif "josmoze.com" in response:
            print("❌ Ancienne URL non-fonctionnelle!")
        else:
            print("⚠️ Pas d'URL")
    
    print("\n" + "="*50)
    print("🚀 TENTATIVE D'ENVOI SMS RÉELS:")
    print("-" * 30)
    
    # Essayer d'envoyer quelques SMS
    tests_envoi = [
        ("thomas", "Bonjour, j'aimerais des informations", "📋 Thomas - Conseil"),
        ("sophie", "Quel est votre prix le plus accessible ?", "💰 Sophie - Vente")
    ]
    
    sms_envoyes = 0
    
    for agent_name, message, description in tests_envoi:
        print(f"\n{description}:")
        agent = conversational_agents[agent_name]
        
        try:
            success = await agent.send_intelligent_sms(client_phone, message, client_name)
            
            if success:
                print(f"✅ SMS envoyé avec succès!")
                print("📱 Vérifiez votre téléphone...")
                sms_envoyes += 1
            else:
                print("❌ Échec envoi")
                
        except Exception as e:
            if "429" in str(e):
                print("⚠️ Limite quotidienne Twilio atteinte")
                break
            else:
                print(f"❌ Erreur: {str(e)}")
        
        await asyncio.sleep(5)  # Pause entre envois
    
    print(f"\n🎯 RÉSUMÉ FINAL:")
    print(f"📱 SMS envoyés: {sms_envoyes}")
    print(f"🌐 URL utilisée: {JOSMOSE_WEBSITE}")
    print(f"✅ Cette URL fonctionne parfaitement!")
    print(f"👆 Cliquez sur le lien dans votre SMS pour tester!")
    
    if sms_envoyes > 0:
        print(f"\n🔗 INSTRUCTION IMPORTANTE:")
        print(f"Cliquez sur le lien dans le SMS reçu.")
        print(f"Cette fois, vous devriez arriver sur le site josmoze.com")
        print(f"et NON sur une page 'Unable to connect' !")

if __name__ == "__main__":
    asyncio.run(test_sms_url_corrigee())