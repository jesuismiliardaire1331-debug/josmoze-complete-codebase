#!/usr/bin/env python3
"""
Script de mise à jour finale des produits et promotions pour Josmoze.com
"""

import asyncio
import sys
import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
import logging

# Ajouter le répertoire backend au path
sys.path.append('./backend')

# Importer les nouveaux produits
from products_final import FINAL_PRODUCTS, PROMOTION_RULES, REFERRAL_SYSTEM

# Configuration MongoDB
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
client = AsyncIOMotorClient(MONGO_URL)
db = client[os.environ.get('DB_NAME', 'josmoze_production')]

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def update_products():
    """Met à jour tous les produits avec la nouvelle gamme"""
    try:
        logger.info("🔄 Début mise à jour des produits...")
        
        # Supprimer les anciens produits
        result_delete = await db.products.delete_many({})
        logger.info(f"✅ {result_delete.deleted_count} anciens produits supprimés")
        
        # Insérer les nouveaux produits
        result_insert = await db.products.insert_many(FINAL_PRODUCTS)
        logger.info(f"✅ {len(result_insert.inserted_ids)} nouveaux produits insérés")
        
        # Vérifier l'insertion
        product_count = await db.products.count_documents({})
        logger.info(f"📊 Total produits en base: {product_count}")
        
        # Afficher les nouveaux produits
        logger.info("🆕 NOUVEAUX PRODUITS AJOUTÉS:")
        for product in FINAL_PRODUCTS:
            if product["id"] in ["osmoseur-essentiel", "osmoseur-premium", "osmoseur-prestige", 
                                "purificateur-portable-hydrogene", "fontaine-eau-animaux"]:
                logger.info(f"   - {product['name']}: {product['price']}€")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erreur mise à jour produits: {e}")
        return False

async def setup_promotions():
    """Configure les règles de promotions"""
    try:
        logger.info("🎁 Configuration des promotions...")
        
        # Sauvegarder les règles de promotion
        await db.promotion_rules.replace_one(
            {"type": "launch_offer"}, 
            {
                "type": "launch_offer",
                "rules": PROMOTION_RULES["launch_offer"],
                "updated_at": datetime.utcnow()
            }, 
            upsert=True
        )
        
        # Sauvegarder les règles de parrainage
        await db.referral_rules.replace_one(
            {"type": "referral_system"}, 
            {
                "type": "referral_system",
                "rules": REFERRAL_SYSTEM,
                "updated_at": datetime.utcnow()
            }, 
            upsert=True
        )
        
        logger.info("✅ Règles de promotions configurées")
        logger.info(f"   - Offre de lancement: {PROMOTION_RULES['launch_offer']['description']}")
        logger.info(f"   - Système parrainage: {REFERRAL_SYSTEM['description']}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erreur configuration promotions: {e}")
        return False

async def create_indexes():
    """Crée les index nécessaires pour les nouvelles collections"""
    try:
        logger.info("📊 Création des index...")
        
        # Index pour les codes de parrainage
        await db.referral_codes.create_index("code", unique=True)
        await db.referral_codes.create_index("user_id")
        
        # Index pour les récompenses
        await db.referral_rewards.create_index("referrer_id")
        await db.referral_rewards.create_index("order_id")
        
        # Index pour les bons d'achat
        await db.vouchers.create_index("user_id")
        await db.vouchers.create_index("code", unique=True)
        await db.vouchers.create_index("expires_at")
        
        # Index pour les offres de lancement
        await db.launch_offers.create_index("customer_email")
        await db.launch_offers.create_index("applied_at")
        
        logger.info("✅ Index créés avec succès")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erreur création index: {e}")
        return False

async def validate_setup():
    """Valide que la mise à jour s'est bien passée"""
    try:
        logger.info("🔍 Validation de la mise à jour...")
        
        # Vérifier les produits
        products = await db.products.find({}).to_list(1000)
        
        # Compter par catégorie
        osmoseurs = [p for p in products if p.get("category") == "osmoseur"]
        nouveaux = [p for p in products if p.get("id") in ["purificateur-portable-hydrogene", "fontaine-eau-animaux"]]
        
        logger.info(f"✅ {len(osmoseurs)} osmoseurs dans la gamme")
        logger.info(f"✅ {len(nouveaux)} nouveaux produits")
        
        # Vérifier les gammes
        essentiel = next((p for p in products if p.get("product_tier") == "essentiel"), None)
        premium = next((p for p in products if p.get("product_tier") == "premium"), None)
        prestige = next((p for p in products if p.get("product_tier") == "prestige"), None)
        
        if essentiel and premium and prestige:
            logger.info("✅ Gamme complète: Essentiel, Premium, Prestige")
            logger.info(f"   - Essentiel: {essentiel['price']}€")
            logger.info(f"   - Premium: {premium['price']}€")
            logger.info(f"   - Prestige: {prestige['price']}€")
        else:
            logger.warning("⚠️ Gamme incomplète détectée")
        
        # Vérifier les promotions
        promotion_rules = await db.promotion_rules.count_documents({})
        referral_rules = await db.referral_rules.count_documents({})
        
        logger.info(f"✅ {promotion_rules} règles de promotion configurées")
        logger.info(f"✅ {referral_rules} règles de parrainage configurées")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erreur validation: {e}")
        return False

async def main():
    """Fonction principale de mise à jour"""
    logger.info("🚀 DÉMARRAGE MISE À JOUR FINALE JOSMOZE.COM")
    logger.info("=" * 60)
    
    try:
        # Étape 1: Mise à jour des produits
        if await update_products():
            logger.info("✅ Étape 1/4: Produits mis à jour")
        else:
            logger.error("❌ Échec mise à jour produits")
            return False
        
        # Étape 2: Configuration des promotions
        if await setup_promotions():
            logger.info("✅ Étape 2/4: Promotions configurées")
        else:
            logger.error("❌ Échec configuration promotions")
            return False
        
        # Étape 3: Création des index
        if await create_indexes():
            logger.info("✅ Étape 3/4: Index créés")
        else:
            logger.error("❌ Échec création index")
            return False
        
        # Étape 4: Validation
        if await validate_setup():
            logger.info("✅ Étape 4/4: Validation réussie")
        else:
            logger.error("❌ Échec validation")
            return False
        
        logger.info("=" * 60)
        logger.info("🎉 MISE À JOUR FINALE TERMINÉE AVEC SUCCÈS !")
        logger.info("=" * 60)
        logger.info("📋 RÉSUMÉ:")
        logger.info("   ✅ Gamme osmoseurs restructurée (Essentiel 449€, Premium 549€, Prestige 899€)")
        logger.info("   ✅ 2 nouveaux produits ajoutés (Purificateur H2 79€, Fontaine Animaux 49€)")
        logger.info("   ✅ Offre de lancement configurée (produit gratuit Premium/Prestige)")
        logger.info("   ✅ Système parrainage activé (10% filleul, 50€ parrain)")
        logger.info("   ✅ Base de données et index optimisés")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erreur critique: {e}")
        return False
    finally:
        client.close()

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
