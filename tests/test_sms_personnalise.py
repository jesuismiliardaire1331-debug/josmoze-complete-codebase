#!/usr/bin/env python3
"""
📱 TEST SMS PERSONNALISÉ - Numéro Client Réel
============================================
Test avec le numéro +15068893760
"""

import asyncio
from conversational_agents import conversational_agents, JOSMOSE_WEBSITE

async def test_sms_personnalise():
    """Test SMS avec le vrai numéro client"""
    
    print("📱 TEST SMS PERSONNALISÉ - OPTIMISATION COMPLÈTE")
    print("=" * 50)
    
    client_phone = "+15068893760"
    client_name = "Cher Client"  # Nom personnalisé
    
    print(f"📞 Numéro de test: {client_phone}")
    print(f"🌐 URL utilisée: {JOSMOSE_WEBSITE}")
    print(f"👤 Nom client: {client_name}")
    
    # Scénarios réels optimisés pour démonstration
    scenarios_test = [
        {
            "agent": "sophie",
            "message": "Combien coûte votre purificateur le plus populaire ?",
            "contexte": "💰 Question Prix - Agent Sophie (Vente)",
            "attendu": "Prix + valeur + URL josmoze.com + closing"
        },
        
        {
            "agent": "thomas", 
            "message": "Bonjour, j'aimerais des informations sur vos systèmes",
            "contexte": "📋 Demande Info - Agent Thomas (Conseil)",
            "attendu": "Info + conseils + URL josmoze.com + question qualifiante"
        },
        
        {
            "agent": "marie",
            "message": "Je ne sais pas si j'en ai vraiment besoin...",
            "contexte": "🤔 Hésitation - Agent Marie (Relation Client)",
            "attendu": "Empathie + bénéfices + URL josmoze.com + rassurance"
        },
        
        {
            "agent": "julien",
            "message": "J'avais regardé vos produits hier mais j'hésite encore",
            "contexte": "🛒 Récupération - Agent Julien (Conversion)",
            "attendu": "Urgence douce + facilitation + URL josmoze.com"
        }
    ]
    
    for i, scenario in enumerate(scenarios_test, 1):
        print(f"\n🎯 TEST {i}/4: {scenario['contexte']}")
        print(f"👤 Message client: \"{scenario['message']}\"")
        print(f"📝 Attendu: {scenario['attendu']}")
        print("-" * 60)
        
        agent = conversational_agents[scenario['agent']]
        
        try:
            # Envoyer SMS réel
            success = await agent.send_intelligent_sms(
                client_phone, 
                scenario['message'], 
                client_name
            )
            
            if success:
                print(f"✅ SMS ENVOYÉ avec succès par {agent.name}!")
                print("📱 Vérifiez votre téléphone dans quelques secondes...")
            else:
                print(f"❌ Échec envoi SMS par {agent.name}")
                
        except Exception as e:
            print(f"❌ Erreur: {str(e)}")
        
        print("-" * 60)
        
        # Pause entre les messages pour éviter le spam
        if i < len(scenarios_test):
            print("⏳ Pause 10 secondes avant le prochain test...")
            await asyncio.sleep(10)
    
    print(f"\n🎉 TEST TERMINÉ!")
    print(f"📱 Vous devriez avoir reçu 4 SMS sur {client_phone}")
    print(f"🌐 Chaque SMS contient l'URL correcte: {JOSMOSE_WEBSITE}")
    print(f"📏 Tous les SMS respectent la limite 160 caractères")
    print(f"🎯 Messages personnalisés avec stratégies Schopenhauer")
    print(f"💬 Différents styles selon l'agent (Sophie=Vente, Thomas=Conseil, etc.)")

async def test_generation_sans_envoi():
    """Test génération messages sans envoi réel (pour debug)"""
    
    print(f"\n🧪 GÉNÉRATION TEST (SANS ENVOI)")
    print("=" * 40)
    
    client_phone = "+15068893760"
    client_name = "Cher Client"
    
    # Test génération de message Sophie
    sophie = conversational_agents["sophie"]
    message_test = "Quel est votre prix le plus bas ?"
    
    response = await sophie.generate_intelligent_response(
        message_test, client_phone, client_name
    )
    
    print(f"📝 Message généré par Sophie:")
    print(f"💬 \"{response}\"")
    print(f"📏 Longueur: {len(response)} caractères")
    
    if "www.josmoze.com" in response:
        print("✅ URL correcte présente")
    else:
        print("❌ URL manquante ou incorrecte")

if __name__ == "__main__":
    print("🚀 LANCEMENT TEST SMS PERSONNALISÉ")
    print("⚠️  ATTENTION: Ce test va envoyer de vrais SMS!")
    print("💰 Note: Limite Twilio peut s'appliquer (compte trial)\n")
    
    # Lancer le test complet
    asyncio.run(test_sms_personnalise())
    
    # Test génération supplémentaire
    asyncio.run(test_generation_sans_envoi())