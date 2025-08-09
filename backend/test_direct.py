#!/usr/bin/env python3
"""
🎯 TEST DIRECT - URL dans SMS
============================
Test simple et direct
"""

import asyncio
from conversational_agents import conversational_agents, JOSMOSE_WEBSITE

async def test_direct_url():
    """Test direct simple"""
    
    print("🎯 TEST DIRECT URL SMS")
    print("=" * 30)
    
    client_phone = "+15068893760"
    client_name = "Client Test"
    
    print(f"🌐 URL système: {JOSMOSE_WEBSITE}")
    
    # Test Sophie avec message prix (intention critique)
    sophie = conversational_agents["sophie"]
    
    messages_test = [
        "Combien coûte votre purificateur ?",
        "Quel est le prix ?",
        "Je veux acheter",
        "Montrez-moi vos produits"
    ]
    
    for i, message in enumerate(messages_test, 1):
        print(f"\n📋 TEST {i}: \"{message}\"")
        
        response = await sophie.generate_intelligent_response(
            message, client_phone, client_name
        )
        
        print(f"💬 Réponse: \"{response}\"")
        print(f"📏 {len(response)} chars")
        
        if "0d683f65" in response:
            print("✅ URL preview présente")
        elif "josmoze.com" in response:
            print("⚠️ URL josmoze.com présente")
        else:
            print("❌ AUCUNE URL!")
        
        print("-" * 30)

if __name__ == "__main__":
    asyncio.run(test_direct_url())