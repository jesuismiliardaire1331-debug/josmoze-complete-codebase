#!/usr/bin/env python3
"""
🔧 DEBUG URL MOBILE - Test toutes les variantes d'URL
===================================================
"""

import asyncio
from conversational_agents import conversational_agents, JOSMOSE_WEBSITE

async def test_debug_url():
    """Debug complet des URLs disponibles"""
    
    print("🔧 DEBUG URL MOBILE - TEST COMPLET")
    print("=" * 50)
    
    client_phone = "+15068893760"
    client_name = "Cher Client"
    
    # URLs à tester
    urls_test = [
        "https://chatbot-debug-2.preview.emergentagent.com",
        "http://0d683f65-404e-4436-abda-79303fb40932.preview.emergentagent.com",
        "0d683f65-404e-4436-abda-79303fb40932.preview.emergentagent.com",
    ]
    
    print("🌐 URLs à tester pour mobile:")
    for i, url in enumerate(urls_test, 1):
        print(f"{i}. {url}")
    
    # Modifier temporairement l'URL pour test
    original_url = JOSMOSE_WEBSITE
    
    for i, test_url in enumerate(urls_test, 1):
        print(f"\n📱 TEST {i}: {test_url}")
        print("-" * 40)
        
        # Modifier temporairement l'URL globale
        import conversational_agents
        conversational_agents.JOSMOSE_WEBSITE = test_url
        
        # Générer un message de test
        thomas = conversational_agents.conversational_agents["thomas"]
        
        response = await thomas.generate_intelligent_response(
            "Test de lien mobile", 
            client_phone, 
            client_name
        )
        
        print(f"💬 Message généré: \"{response}\"")
        print(f"📏 Longueur: {len(response)} chars")
        
        if test_url in response:
            print(f"✅ URL présente dans le message")
        else:
            print(f"❌ URL manquante")
    
    # Restaurer URL originale
    import conversational_agents
    conversational_agents.JOSMOSE_WEBSITE = original_url
    
    print(f"\n🎯 SOLUTIONS ALTERNATIVES MOBILE:")
    print("=" * 40)
    print("1️⃣ Testez MANUELLEMENT ces URLs depuis votre mobile:")
    for url in urls_test:
        print(f"   👆 {url}")
    
    print(f"\n2️⃣ Si aucune ne marche, le problème peut être:")
    print("   - Restriction réseau mobile")
    print("   - DNS mobile différent")
    print("   - Certificat SSL non reconnu")
    print("   - Firewall opérateur")
    
    print(f"\n3️⃣ SOLUTION D'URGENCE - URL courte:")
    print("   Utiliser un raccourcisseur d'URL (bit.ly, tinyurl)")
    print("   ou configurer un vrai domaine")

if __name__ == "__main__":
    asyncio.run(test_debug_url())