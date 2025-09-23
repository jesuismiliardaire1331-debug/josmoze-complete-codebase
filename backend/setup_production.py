#!/usr/bin/env python3
"""
⚙️ CONFIGURATION PRODUCTION
===========================
Configure le système pour la production
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os

async def setup_production_config():
    """Configure le système pour production"""
    
    print("⚙️ CONFIGURATION PRODUCTION")
    print("=" * 40)
    
    # Connexion MongoDB
    mongo_url = os.environ.get('MONGO_URI', os.environ.get('MONGO_URL', ''))
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.environ.get('DB_NAME', 'josmoze_production')]
    
    # Configuration production
    production_config = {
        "environment": "production",
        "domain": "josmoze.com",  # À configurer avec le vrai domaine
        "company": {
            "name": "Josmose",
            "countries": ["FR", "ES", "BE"],  # France, Espagne, Belgique
            "languages": ["fr", "es", "nl"],
            "currencies": ["EUR"],
            "stock": {
                "osmoseurs": 50,
                "filtres": 200
            }
        },
        "team": {
            "managers": [
                {
                    "email": "aziza@josmoze.com",
                    "name": "Aziza",
                    "role": "manager",
                    "status": "active"
                },
                {
                    "email": "naima@josmoze.com", 
                    "name": "Naima",
                    "role": "manager",
                    "status": "active"
                },
                {
                    "email": "antonio@josmoze.com",
                    "name": "Antonio", 
                    "role": "manager",
                    "status": "active"
                }
            ]
        },
        "ai_agents": {
            "sophie": {
                "active": True,
                "type": "sms_only",  # Pas d'appels pour Sophie
                "specialty": "Vente & Closing",
                "working_hours": "9h-18h"
            },
            "thomas": {
                "active": True,
                "type": "sms_calls",
                "specialty": "Conseil & Information", 
                "working_hours": "9h-18h"
            },
            "marie": {
                "active": True,
                "type": "sms_calls",
                "specialty": "Relation Client & SAV",
                "working_hours": "9h-18h" 
            },
            "julien": {
                "active": True,
                "type": "sms_only",
                "specialty": "Récupération Paniers",
                "working_hours": "9h-20h"
            },
            "caroline": {
                "active": True, 
                "type": "sms_only",
                "specialty": "Analytics & Technique",
                "working_hours": "24/7"
            }
        },
        "integrations": {
            "openai": {"status": "configured"},
            "twilio": {"status": "configured"},
            "stripe": {"status": "to_configure"},
            "paypal": {"status": "to_configure"},
            "meta_business": {"status": "to_configure"}
        },
        "features": {
            "auto_lead_response": True,
            "sms_marketing": True, 
            "abandoned_cart_recovery": True,
            "auto_invoicing": True,
            "delivery_labels": True,
            "stock_alerts": True,
            "brand_monitoring": True,
            "security_audit": True
        }
    }
    
    # Sauvegarder config
    try:
        settings = db.settings
        await settings.update_one(
            {"type": "production_config"}, 
            {"$set": production_config},
            upsert=True
        )
        print("✅ Configuration production sauvegardée")
    except Exception as e:
        print(f"❌ Erreur config: {str(e)}")
    
    print(f"\n📋 CONFIGURATION APPLIQUÉE:")
    print(f"🌍 Pays cibles: France, Espagne, Belgique")
    print(f"👥 3 Managers: Aziza, Naima, Antonio")
    print(f"🤖 5 Agents IA configurés")
    print(f"📦 Stock: 50 osmoseurs, 200 filtres")
    print(f"✅ Toutes fonctionnalités activées")

if __name__ == "__main__":
    asyncio.run(setup_production_config())
