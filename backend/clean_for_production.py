#!/usr/bin/env python3
"""
🧹 SCRIPT DE NETTOYAGE - PRÉPARATION PRODUCTION
===============================================
Vide toutes les données test, garde la structure
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os

async def clean_for_production():
    """Nettoie toutes les données test pour production"""
    
    print("🧹 PRÉPARATION PRODUCTION - NETTOYAGE DONNÉES")
    print("=" * 50)
    
    # Connexion MongoDB
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    client = AsyncIOMotorClient(mongo_url)
    db = client.josmose_db
    
    print("🔌 Connexion MongoDB établie")
    
    # Collections à nettoyer (garder structure, vider données)
    collections_to_clean = [
        "leads",           # Leads de démonstration
        "orders",          # Commandes test  
        "abandoned_carts", # Paniers test
        "conversations",   # Historiques SMS test
        "analytics_events", # Événements de test
        "email_campaigns", # Campagnes test
        "notifications"    # Notifications test
    ]
    
    # Collections à garder intactes
    collections_to_keep = [
        "users",           # Naima, Aziza, Antonio (managers)
        "products",        # Vos 6 produits actuels
        "ai_agents_config", # Configuration des 5 agents IA
        "settings"         # Paramètres système
    ]
    
    print("\n🗑️ NETTOYAGE EN COURS...")
    
    for collection_name in collections_to_clean:
        try:
            collection = db[collection_name]
            result = await collection.delete_many({})
            print(f"✅ {collection_name}: {result.deleted_count} documents supprimés")
        except Exception as e:
            print(f"⚠️ {collection_name}: {str(e)}")
    
    print("\n📊 COLLECTIONS CONSERVÉES:")
    for collection_name in collections_to_keep:
        try:
            collection = db[collection_name]
            count = await collection.count_documents({})
            print(f"✅ {collection_name}: {count} documents conservés")
        except Exception as e:
            print(f"⚠️ {collection_name}: {str(e)}")
    
    # Réinitialiser les compteurs
    try:
        settings = db.settings
        await settings.update_one(
            {"type": "counters"}, 
            {"$set": {
                "leads_count": 0,
                "orders_count": 0,
                "revenue_total": 0,
                "last_reset": "2025-08-08"
            }},
            upsert=True
        )
        print("✅ Compteurs réinitialisés")
    except Exception as e:
        print(f"⚠️ Compteurs: {str(e)}")
    
    print(f"\n🎯 NETTOYAGE TERMINÉ!")
    print("✅ Système prêt pour production")
    print("✅ CRM + Agents IA conservés")
    print("✅ Structure complète intacte")
    print("❌ Toutes données test supprimées")

if __name__ == "__main__":
    asyncio.run(clean_for_production())