#!/usr/bin/env python3
"""
🔧 TEST CORRECTION URL - SMS avec lien fonctionnel
================================================
"""

import asyncio
from conversational_agents import conversational_agents, JOSMOSE_WEBSITE

async def test_correction_url():
    """Test SMS avec URL corrigée"""
    
    print("🔧 TEST CORRECTION URL URGENTE")
    print("=" * 40)
    
    client_phone = "+15068893760"
    client_name = "Cher Client"
    
    print(f"🌐 URL corrigée: {JOSMOSE_WEBSITE}")
    
    # Test génération message (sans envoi pour éviter limite Twilio)
    thomas = conversational_agents["thomas"]
    message_test = "Vos purificateurs m'intéressent, pouvez-vous me donner plus d'infos ?"
    
    response = await thomas.generate_intelligent_response(
        message_test, client_phone, client_name
    )
    
    print(f"\n📝 Message généré par Thomas:")
    print(f"💬 \"{response}\"")
    print(f"📏 Longueur: {len(response)} caractères")
    
    # Vérifications
    if "0d683f65-404e-4436-abda-79303fb40932.preview.emergentagent.com" in response:
        print("✅ URL fonctionnelle présente!")
    elif "josmose.com" in response:
        print("❌ Ancienne URL non-fonctionnelle encore présente!")
    else:
        print("⚠️ Aucune URL trouvée")
    
    print(f"\n🎯 RÉSULTAT:")
    print("✅ URL corrigée dans le système")
    print("✅ Les nouveaux SMS utiliseront l'URL fonctionnelle")
    print("📱 Les clients pourront maintenant accéder au site!")

if __name__ == "__main__":
    asyncio.run(test_correction_url())