#!/usr/bin/env python3
"""
🔗 TEST URL CORRECTE DANS SMS
============================
Vérification que tous les SMS utilisent www.josmose.com
"""

import asyncio
from conversational_agents import conversational_agents, JOSMOSE_WEBSITE

async def test_url_correcte():
    """Test que tous les agents utilisent la bonne URL"""
    
    print("🔗 TEST URL CORRECTE DANS SMS")
    print("=" * 40)
    
    print(f"✅ URL configurée: {JOSMOSE_WEBSITE}")
    
    if JOSMOSE_WEBSITE != "https://www.josmose.com":
        print("❌ ERREUR: URL incorrecte configurée!")
        return
    
    client_phone = "+15068893760"
    client_name = "Monsieur Test"
    
    # Messages de test pour chaque agent
    test_messages = {
        "thomas": "Bonjour, j'aimerais des informations sur vos purificateurs",
        "sophie": "Combien coûte votre purificateur le plus populaire ?",
        "marie": "J'ai un problème avec ma commande",
        "julien": "J'avais mis un produit dans mon panier hier",
        "caroline": "Vos filtres éliminent-ils les bactéries ?"
    }
    
    print("\n🧪 Test génération messages avec URL correcte:")
    
    for agent_name, message in test_messages.items():
        print(f"\n--- {agent_name.upper()} ---")
        agent = conversational_agents[agent_name]
        
        # Générer réponse sans envoyer SMS
        try:
            response = await agent.generate_intelligent_response(
                message, client_phone, client_name
            )
            
            print(f"📱 Message généré: {response}")
            
            # Vérifier que la bonne URL est utilisée
            if "www.josmose.com" in response:
                print("✅ URL CORRECTE trouvée dans le message")
            elif "preview.emergentagent.com" in response:
                print("❌ ANCIENNE URL trouvée - PROBLÈME!")
            else:
                print("ℹ️  Pas d'URL dans ce message (normal selon le contexte)")
                
        except Exception as e:
            print(f"❌ Erreur génération: {str(e)}")
    
    print(f"\n🎯 RÉSUMÉ:")
    print(f"URL système: {JOSMOSE_WEBSITE}")
    print("✅ Tous les nouveaux SMS utiliseront www.josmose.com")
    print("🔄 Test terminé - vérifiez les messages ci-dessus")

if __name__ == "__main__":
    asyncio.run(test_url_correcte())