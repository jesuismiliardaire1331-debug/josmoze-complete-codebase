#!/usr/bin/env python3
"""
📱 TEST SMS ULTRA-OPTIMISÉS - Conversations parfaites
"""

import asyncio
from conversational_agents import conversational_agents

async def test_sms_scenarios_reels():
    """Test avec scénarios réels clients variés"""
    
    print("📱 TEST SMS ULTRA-OPTIMISÉS")
    print("=" * 40)
    
    client_phone = "+15068893760"
    client_name = "Monsieur Dubois"
    
    # Scénarios réels complets de conversations
    scenarios = [
        # Scénario 1: Recherche prix
        {
            "conversation": [
                ("Bonjour, combien coûte un purificateur ?", "sophie"),
                ("C'est dans mon budget, quels sont les modèles ?", "thomas"),
                ("Le modèle à 399€ m'intéresse", "sophie")
            ]
        },
        
        # Scénario 2: Hésitation puis conviction
        {
            "conversation": [
                ("Je ne sais pas si j'en ai vraiment besoin", "thomas"),
                ("Oui mais c'est un investissement important", "marie"),
                ("D'accord, je veux voir vos produits", "sophie")
            ]
        },
        
        # Scénario 3: Client pressé
        {
            "conversation": [
                ("J'ai besoin rapidement d'un purificateur", "julien"),
                ("Oui aujourd'hui si possible", "sophie"),
                ("Parfait, comment commander ?", "julien")
            ]
        }
    ]
    
    for scenario_num, scenario in enumerate(scenarios, 1):
        print(f"\n🎭 SCÉNARIO {scenario_num}")
        print("-" * 25)
        
        for step_num, (message, agent_name) in enumerate(scenario["conversation"], 1):
            print(f"\n--- Étape {step_num} ---")
            print(f"👤 {client_name}: {message}")
            
            agent = conversational_agents[agent_name]
            print(f"🤖 Agent: {agent.name}")
            
            success = await agent.send_intelligent_sms(client_phone, message, client_name)
            
            if success:
                print("✅ SMS optimisé envoyé")
            else:
                print("❌ Échec")
            
            await asyncio.sleep(2)
        
        print(f"\n✅ Scénario {scenario_num} terminé")
        await asyncio.sleep(3)
    
    # Test questions spécifiques
    print(f"\n🎯 TESTS SPÉCIFIQUES")
    print("-" * 25)
    
    questions_specifiques = [
        ("Quelle est la différence entre vos modèles ?", "caroline"),
        ("Avez-vous des promotions en cours ?", "julien"),
        ("L'installation est-elle comprise ?", "marie"),
        ("Puis-je avoir une démonstration ?", "thomas"),
        ("Vos filtres durent combien de temps ?", "caroline")
    ]
    
    for question, agent_name in questions_specifiques:
        print(f"\n❓ Question: {question}")
        agent = conversational_agents[agent_name]
        
        success = await agent.send_intelligent_sms(client_phone, question, client_name)
        if success:
            print("✅ Réponse experte envoyée")
        
        await asyncio.sleep(2)
    
    print(f"\n🌊 TESTS TERMINÉS !")
    print(f"📱 Vérifiez {client_phone} pour tous les SMS optimisés")
    print("🔗 Chaque SMS pertinent contient le lien du site")
    print("💬 Conversations naturelles et personnalisées")

async def test_agent_specialises():
    """Test des spécialisations d'agents"""
    
    print(f"\n🎯 TEST SPÉCIALISATIONS AGENTS")
    print("=" * 35)
    
    client_phone = "+15068893760"
    client_name = "Monsieur Dubois"
    
    tests_specialises = [
        ("Thomas - Questions eau", "L'eau de ma ville a un goût bizarre, que faire ?", "thomas"),
        ("Sophie - Closing commercial", "Je veux acheter mais j'hésite entre 2 modèles", "sophie"),
        ("Marie - Service client", "J'ai un problème avec ma commande", "marie"),
        ("Julien - Récupération", "J'avais mis un produit dans mon panier hier", "julien"),
        ("Caroline - Technique", "Vos filtres éliminent-ils les nitrates ?", "caroline")
    ]
    
    for test_name, question, agent_name in tests_specialises:
        print(f"\n🧪 {test_name}")
        agent = conversational_agents[agent_name]
        
        success = await agent.send_intelligent_sms(client_phone, question, client_name)
        if success:
            print(f"✅ {agent.name} - Réponse spécialisée envoyée")
        
        await asyncio.sleep(2)

if __name__ == "__main__":
    # Lancement des tests
    asyncio.run(test_sms_scenarios_reels())
    
    # Tests spécialisés supplémentaires
    # asyncio.run(test_agent_specialises())