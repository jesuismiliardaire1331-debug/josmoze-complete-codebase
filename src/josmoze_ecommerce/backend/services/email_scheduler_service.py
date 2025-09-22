#!/usr/bin/env python3
"""
Email Scheduler Service - Traitement automatique des emails programmés
Service autonome qui traite les emails de séquences selon leur programmation
"""

import asyncio
import logging
import os
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient
from email_sequencer_manager import EmailSequencerManager
from suppression_list_manager import SuppressionListManager

# Configuration logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def process_scheduled_emails():
    """Traiter les emails programmés"""
    try:
        # Connexion MongoDB
        mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/josmoze_crm')
        client = AsyncIOMotorClient(mongo_url)
        db = client.josmoze_crm
        
        # Initialiser les managers
        suppression_manager = SuppressionListManager(db)
        await suppression_manager.create_indexes()
        
        email_sequencer = EmailSequencerManager(db, suppression_manager)
        await email_sequencer.create_indexes()
        
        logger.info("🚀 Démarrage du traitement des emails programmés")
        
        # Traiter les emails programmés
        result = await email_sequencer.process_scheduled_emails()
        
        if result["success"]:
            logger.info(f"✅ Traitement terminé - Traités: {result['processed']}, Envoyés: {result['sent']}, Erreurs: {result['errors']}")
        else:
            logger.error(f"❌ Erreur lors du traitement: {result['error']}")
        
        # Fermer la connexion
        client.close()
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Erreur critique dans le scheduler: {e}")
        return {"success": False, "error": str(e)}

async def scheduler_loop():
    """Boucle principale du scheduler (toutes les 15 minutes)"""
    logger.info("📧 Email Scheduler Service démarré")
    
    while True:
        try:
            # Traiter les emails programmés
            await process_scheduled_emails()
            
            # Attendre 15 minutes avant le prochain traitement
            logger.info("⏰ Prochaine vérification dans 15 minutes")
            await asyncio.sleep(900)  # 15 minutes = 900 secondes
            
        except KeyboardInterrupt:
            logger.info("🛑 Arrêt du scheduler demandé")
            break
        except Exception as e:
            logger.error(f"❌ Erreur dans la boucle scheduler: {e}")
            # Attendre 5 minutes en cas d'erreur avant de reprendre
            await asyncio.sleep(300)

if __name__ == "__main__":
    try:
        # Lancer le scheduler
        asyncio.run(scheduler_loop())
    except KeyboardInterrupt:
        logger.info("🛑 Email Scheduler Service arrêté")
    except Exception as e:
        logger.error(f"❌ Erreur fatale: {e}")