#!/usr/bin/env python3
"""
Script de correction urgente des images produits
Remplace les images cassées et incorrectes par des images appropriées d'osmoseurs
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging

# Configuration
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'josmoze_production')

# Nouvelles images appropriées pour osmoseurs
CORRECT_IMAGES = {
    # Osmoseurs BlueMountain - Images professionnelles d'équipements de filtration
    "osmoseur-essentiel": "https://images.unsplash.com/photo-1617155093703-b10e7e1b6f42?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2Njl8MHwxfHNlYXJjaHwxfHx3YXRlciUyMGZpbHRyYXRpb24lMjBzeXN0ZW18ZW58MHx8fHwxNzU4MjM1NTUxfDA&ixlib=rb-4.1.0&q=85",
    
    "osmoseur-premium": "https://images.unsplash.com/photo-1656082352918-75e24cb6d06c?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzF8MHwxfHNlYXJjaHwxfHxyZXZlcnNlJTIwb3Ntb3Npc3xlbnwwfHx8fDE3NTgyMzU1NTZ8MA&ixlib=rb-4.1.0&q=85",
    
    "osmoseur-prestige": "https://images.unsplash.com/photo-1662647343354-5a03bbbd1d45?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzF8MHwxfHNlYXJjaHw0fHxyZXZlcnNlJTIwb3Ntb3Npc3xlbnwwfHx8fDE3NTgyMzU1NTZ8MA&ixlib=rb-4.1.0&q=85",
    
    "osmoseur-pro": "https://images.unsplash.com/photo-1616996691973-0560486764f7?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2Njl8MHwxfHNlYXJjaHwzfHx3YXRlciUyMGZpbHRyYXRpb24lMjBzeXN0ZW18ZW58MHx8fHwxNzU4MjM1NTUxfDA&ixlib=rb-4.1.0&q=85",
    
    # Filtres - Image d'équipement de filtration industriel
    "filtres-rechange": "https://images.pexels.com/photos/12726229/pexels-photo-12726229.jpeg",
    "filtres-pro": "https://images.pexels.com/photos/12726229/pexels-photo-12726229.jpeg",
}

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def fix_product_images():
    """Corrige toutes les images produits défaillantes"""
    try:
        client = AsyncIOMotorClient(MONGO_URL)
        db = client[DB_NAME]
        
        logger.info("🚨 CORRECTION URGENTE DES IMAGES PRODUITS...")
        
        fixed_count = 0
        
        for product_id, new_image_url in CORRECT_IMAGES.items():
            # Vérifier si le produit existe
            product = await db.products.find_one({"id": product_id})
            
            if product:
                old_image = product.get("image", "N/A")
                
                # Mettre à jour l'image
                result = await db.products.update_one(
                    {"id": product_id},
                    {"$set": {"image": new_image_url}}
                )
                
                if result.modified_count > 0:
                    logger.info(f"✅ {product.get('name', product_id)}")
                    logger.info(f"   Ancienne: {old_image}")
                    logger.info(f"   Nouvelle: {new_image_url}")
                    fixed_count += 1
                else:
                    logger.warning(f"⚠️ Échec mise à jour: {product_id}")
            else:
                logger.warning(f"❌ Produit non trouvé: {product_id}")
        
        logger.info(f"🎉 CORRECTION TERMINÉE: {fixed_count} images mises à jour")
        
        # Vérification finale
        logger.info("\n🔍 VÉRIFICATION FINALE:")
        products = await db.products.find({}).to_list(100)
        
        for product in products:
            name = product.get("name", "N/A")
            image = product.get("image", "N/A")
            logger.info(f"📦 {name}")
            logger.info(f"   Image: {image}")
        
        client.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ Erreur correction images: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(fix_product_images())
    if success:
        print("✅ CORRECTION DES IMAGES RÉUSSIE")
    else:
        print("❌ ÉCHEC CORRECTION DES IMAGES")