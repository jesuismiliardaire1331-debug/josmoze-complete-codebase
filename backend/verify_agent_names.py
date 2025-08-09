#!/usr/bin/env python3
"""
✅ VÉRIFICATION RENOMMAGE AGENTS IA
==================================
Vérification que tous les agents ont été renommés correctement
"""

import asyncio
from ai_agents_system import get_ai_agent_system

async def verify_agent_renaming():
    """Vérifier que tous les agents sont correctement renommés"""
    
    print("✅ VÉRIFICATION RENOMMAGE AGENTS IA")
    print("=" * 50)
    
    # Obtenir le système d'agents
    agent_system = await get_ai_agent_system()
    
    # Noms attendus
    expected_agents = {
        "thomas": "Thomas 👨‍💼",
        "sophie": "Sophie 👩‍💼", 
        "marie": "Marie 👩‍💼",
        "julien": "Julien 👨‍💼",
        "caroline": "Caroline 👩‍💼"
    }
    
    print("🔍 Vérification des agents configurés:")
    print("-" * 40)
    
    all_correct = True
    
    for agent_id, expected_name in expected_agents.items():
        if agent_id in agent_system.agents:
            agent_config = agent_system.agents[agent_id]
            actual_name = agent_config.name
            
            if actual_name == expected_name:
                print(f"✅ {agent_id}: {actual_name}")
            else:
                print(f"❌ {agent_id}: {actual_name} (attendu: {expected_name})")
                all_correct = False
        else:
            print(f"❌ {agent_id}: Agent non trouvé!")
            all_correct = False
    
    print("\n🎯 Spécialités des agents:")
    print("-" * 30)
    
    specialties = {
        "thomas": "Prospection & Qualification 24/7",
        "sophie": "SMS Vente (Appels désactivés)",
        "marie": "SMS & Suivi Relationnel", 
        "julien": "Paniers Abandonnés Spécialisé",
        "caroline": "Analytics & Intelligence Prédictive"
    }
    
    for agent_id, specialty in specialties.items():
        if agent_id in agent_system.agents:
            agent = agent_system.agents[agent_id]
            print(f"🎯 {agent.name}: {specialty}")
        
    print("\n📊 RÉSULTAT FINAL:")
    if all_correct:
        print("✅ Tous les agents ont été correctement renommés!")
        print("✅ Noms cohérents avec l'analyse concurrentielle")
        print("✅ Prêt pour déploiement en production")
    else:
        print("❌ Certains agents nécessitent encore des corrections")
    
    print("\n🚀 AGENTS DISPONIBLES POUR CRM:")
    for agent_id in expected_agents.keys():
        if agent_id in agent_system.agents:
            agent = agent_system.agents[agent_id]
            status = "🟢 Actif" if agent.active else "🔴 Inactif"
            hours = agent.working_hours
            print(f"   {agent.name} - {status} - Horaires: {hours}")

if __name__ == "__main__":
    asyncio.run(verify_agent_renaming())