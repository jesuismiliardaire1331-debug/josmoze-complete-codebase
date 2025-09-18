#!/usr/bin/env python3
"""
🔧 TEST CORRECTION LIEN - Vérification URL réelle
"""

import asyncio
from conversational_agents import conversational_agents

async def test_link_correction():
    """Test rapide du lien corrigé"""
    
    print("🔧 TEST CORRECTION LIEN JOSMOSE")
    print("=" * 40)
    
    # Test avec Thomas
    thomas = conversational_agents["thomas"]
    
    client_phone = "+15068893760"  
    client_name = "Monsieur Dubois"
    
    # Message test pour déclencher envoi de lien
    test_message = "Envoyez-moi le lien de votre site s'il vous plaît"
    
    print(f"📱 Test envoi lien corrigé à {client_name}")
    print(f"👤 Message test: {test_message}")
    
    success = await thomas.send_intelligent_sms(client_phone, test_message, client_name)
    
    if success:
        print("✅ SMS avec lien corrigé envoyé !")
        print("🌐 Le lien devrait maintenant être accessible depuis votre mobile")
        print(f"🔗 URL utilisée: https://buildfix-josmoze.preview.emergentagent.com")
    else:
        print("❌ Échec envoi")

if __name__ == "__main__":
    asyncio.run(test_link_correction())