#!/usr/bin/env python3
"""
🚀 PHASE 9 - SYSTÈME DE PROMOTIONS ET PARRAINAGE
Backend pour Josmoze.com - Gestion complète codes promo et parrainage

FONCTIONNALITÉS :
1. **Codes Promotionnels** : Création, validation, application
2. **Système Parrainage** : Génération codes, rewards, suivi
3. **Interface Admin** : CRUD promotions via AdminDashboard
4. **Intégration Checkout** : Application codes en temps réel

COLLECTIONS MONGODB :
- promotions : codes promo avec paramètres
- referrals : système parrainage complet
- users : comptes clients pour espace client
"""

import logging
import secrets
import string
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel, Field
import uuid
import hashlib

logger = logging.getLogger(__name__)

# ========== MODELS PYDANTIC ==========

class Promotion(BaseModel):
    """Modèle code promotionnel"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    code: str  # Ex: BIENVENUE10, LIVRAISONGRATUITE
    name: str  # Nom descriptif pour admin
    description: str  # Description pour utilisateurs
    type: str  # "percentage" ou "fixed_amount" ou "free_shipping"
    value: float  # Pourcentage (ex: 10.0) ou montant fixe (ex: 20.0)
    min_order_amount: float = 0.0  # Montant minimum commande
    max_discount_amount: Optional[float] = None  # Plafond réduction
    usage_limit: Optional[int] = None  # Limite utilisation (None = illimité)
    usage_limit_per_customer: int = 1  # Limite par client
    used_count: int = 0  # Nombre utilisations
    expires_at: Optional[datetime] = None  # Date expiration
    active: bool = True  # Statut actif/inactif
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: str  # Email admin créateur
    target_customer_type: str = "both"  # "B2C", "B2B", "both"

class PromotionUsage(BaseModel):
    """Historique utilisation promotion"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    promotion_id: str
    promotion_code: str
    user_email: str
    order_id: Optional[str] = None
    discount_amount: float
    original_amount: float
    final_amount: float
    used_at: datetime = Field(default_factory=datetime.utcnow)
    ip_address: Optional[str] = None

class Referral(BaseModel):
    """Modèle système parrainage"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    referrer_email: str  # Email du parrain
    referrer_code: str  # Code unique du parrain
    referee_email: Optional[str] = None  # Email du filleul (None avant utilisation)
    referee_order_id: Optional[str] = None  # Commande du filleul
    status: str = "pending"  # pending, completed, expired, cancelled
    referee_discount_percent: float = 15.0  # Réduction filleul (%)
    referrer_reward_amount: float = 20.0  # Bon parrain (€)
    referee_order_amount: Optional[float] = None  # Montant commande filleul
    referee_discount_applied: Optional[float] = None  # Réduction appliquée
    referrer_reward_issued: bool = False  # Bon parrain émis
    referrer_reward_code: Optional[str] = None  # Code bon parrain
    created_at: datetime = Field(default_factory=datetime.utcnow)
    used_at: Optional[datetime] = None  # Date utilisation par filleul
    completed_at: Optional[datetime] = None  # Date finalisation
    expires_at: datetime = Field(default_factory=lambda: datetime.utcnow() + timedelta(days=90))

class User(BaseModel):
    """Modèle utilisateur pour espace client"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: str
    password_hash: str  # Hash sécurisé
    first_name: str
    last_name: str
    phone: Optional[str] = None
    customer_type: str = "B2C"  # B2C ou B2B
    company: Optional[str] = None  # Pour B2B
    address: Optional[Dict[str, str]] = None
    is_active: bool = True
    email_verified: bool = False
    total_orders: int = 0
    total_spent: float = 0.0
    referral_code: Optional[str] = None  # Code parrainage personnel
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None

# ========== SYSTÈME PROMOTIONS ==========

class PromotionsSystem:
    """Gestionnaire système promotions et parrainage"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.promotions_collection = db.promotions  
        self.promotion_usage_collection = db.promotion_usage
        self.referrals_collection = db.referrals
        self.users_collection = db.users
        
    async def initialize(self):
        """Initialiser collections et index"""
        try:
            # Index pour performance
            await self.promotions_collection.create_index("code", unique=True)
            await self.promotions_collection.create_index("active")
            await self.promotions_collection.create_index("expires_at")
            
            await self.referrals_collection.create_index("referrer_code", unique=True)
            await self.referrals_collection.create_index("referrer_email")
            await self.referrals_collection.create_index("status")
            
            await self.users_collection.create_index("email", unique=True)
            await self.users_collection.create_index("referral_code", unique=True, sparse=True)
            
            # Créer promotions par défaut si aucune
            existing_promos = await self.promotions_collection.count_documents({})
            if existing_promos == 0:
                await self._create_default_promotions()
                
            logger.info("✅ PromotionsSystem initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing PromotionsSystem: {e}")
            raise
    
    async def _create_default_promotions(self):
        """Créer promotions par défaut"""
        default_promotions = [
            {
                "code": "BIENVENUE10",
                "name": "Bienvenue - 10% de réduction", 
                "description": "10% de réduction pour les nouveaux clients",
                "type": "percentage",
                "value": 10.0,
                "min_order_amount": 200.0,
                "usage_limit": 1000,
                "usage_limit_per_customer": 1,
                "expires_at": datetime.utcnow() + timedelta(days=365),
                "created_by": "system",
                "target_customer_type": "both"
            },
            {
                "code": "LIVRAISONGRATUITE",
                "name": "Livraison gratuite",
                "description": "Livraison gratuite sans minimum",
                "type": "free_shipping", 
                "value": 0.0,
                "min_order_amount": 0.0,
                "usage_limit": None,
                "usage_limit_per_customer": 5,
                "created_by": "system",
                "target_customer_type": "both"
            },
            {
                "code": "FAMILLE20",
                "name": "Réduction famille - 20€",
                "description": "20€ de réduction pour les familles",
                "type": "fixed_amount",
                "value": 20.0,
                "min_order_amount": 300.0,
                "max_discount_amount": 20.0,
                "usage_limit": 500,
                "usage_limit_per_customer": 2,
                "expires_at": datetime.utcnow() + timedelta(days=180),
                "created_by": "system",
                "target_customer_type": "B2C"
            }
        ]
        
        for promo_data in default_promotions:
            promo = Promotion(**promo_data)
            await self.promotions_collection.insert_one(promo.dict())
            
        logger.info("✅ Default promotions created")
    
    # ========== GESTION PROMOTIONS ==========
    
    async def create_promotion(self, promotion_data: Dict[str, Any], created_by: str) -> Promotion:
        """Créer nouvelle promotion"""
        try:
            # Vérifier unicité du code
            existing = await self.promotions_collection.find_one({"code": promotion_data["code"]})
            if existing:
                raise ValueError(f"Code promotion '{promotion_data['code']}' déjà existant")
            
            promotion_data["created_by"] = created_by
            promotion = Promotion(**promotion_data)
            
            await self.promotions_collection.insert_one(promotion.dict())
            logger.info(f"✅ Promotion créée: {promotion.code}")
            
            return promotion
            
        except Exception as e:
            logger.error(f"Error creating promotion: {e}")
            raise
    
    async def get_promotions(self, active_only: bool = False) -> List[Dict[str, Any]]:
        """Récupérer liste promotions"""
        try:
            query = {"active": True} if active_only else {}
            promotions = await self.promotions_collection.find(query).sort("created_at", -1).to_list(100)
            
            # Supprimer ObjectId pour sérialisation
            for promo in promotions:
                if "_id" in promo:
                    del promo["_id"]
                    
            return promotions
            
        except Exception as e:
            logger.error(f"Error getting promotions: {e}")
            return []
    
    async def validate_promotion_code(self, code: str, user_email: str, order_amount: float, customer_type: str = "B2C") -> Dict[str, Any]:
        """Valider et calculer réduction code promo"""
        try:
            # Récupérer promotion
            promo = await self.promotions_collection.find_one({
                "code": code.upper(),
                "active": True
            })
            
            if not promo:
                return {"valid": False, "error": "Code promotionnel invalide"}
            
            promotion = Promotion(**promo)
            
            # Vérifier expiration
            if promotion.expires_at and datetime.utcnow() > promotion.expires_at:
                return {"valid": False, "error": "Code promotionnel expiré"}
            
            # Vérifier limite utilisation globale
            if promotion.usage_limit and promotion.used_count >= promotion.usage_limit:
                return {"valid": False, "error": "Code promotionnel épuisé"}
            
            # Vérifier type client
            if promotion.target_customer_type != "both" and promotion.target_customer_type != customer_type:
                return {"valid": False, "error": "Code non applicable à votre type de compte"}
            
            # Vérifier montant minimum
            if order_amount < promotion.min_order_amount:
                return {"valid": False, "error": f"Commande minimum {promotion.min_order_amount}€ requise"}
            
            # Vérifier limite par client
            usage_count = await self.promotion_usage_collection.count_documents({
                "promotion_code": code.upper(),
                "user_email": user_email
            })
            
            if usage_count >= promotion.usage_limit_per_customer:
                return {"valid": False, "error": "Limite d'utilisation atteinte pour ce code"}
            
            # Calculer réduction
            discount_amount = 0.0
            
            if promotion.type == "percentage":
                discount_amount = order_amount * (promotion.value / 100)
                if promotion.max_discount_amount:
                    discount_amount = min(discount_amount, promotion.max_discount_amount)
                    
            elif promotion.type == "fixed_amount":
                discount_amount = min(promotion.value, order_amount)
                
            elif promotion.type == "free_shipping":
                # Pour livraison gratuite, la réduction sera gérée différemment
                discount_amount = 0.0  # Sera calculé selon coût livraison
            
            return {
                "valid": True,
                "promotion": {
                    "id": promotion.id,
                    "code": promotion.code,
                    "name": promotion.name,
                    "description": promotion.description,
                    "type": promotion.type,
                    "value": promotion.value
                },
                "discount_amount": discount_amount,
                "final_amount": max(0, order_amount - discount_amount)
            }
            
        except Exception as e:
            logger.error(f"Error validating promotion code: {e}")
            return {"valid": False, "error": "Erreur lors de la validation"}
    
    async def apply_promotion(self, code: str, user_email: str, order_amount: float, order_id: str = None, ip_address: str = None) -> Dict[str, Any]:
        """Appliquer promotion et enregistrer utilisation"""
        try:
            # Valider d'abord
            validation = await self.validate_promotion_code(code, user_email, order_amount)
            if not validation["valid"]:
                return validation
            
            # Enregistrer utilisation
            usage = PromotionUsage(
                promotion_id=validation["promotion"]["id"],
                promotion_code=code.upper(),
                user_email=user_email,
                order_id=order_id,
                discount_amount=validation["discount_amount"],
                original_amount=order_amount,
                final_amount=validation["final_amount"],
                ip_address=ip_address
            )
            
            await self.promotion_usage_collection.insert_one(usage.dict())
            
            # Incrémenter compteur utilisation
            await self.promotions_collection.update_one(
                {"code": code.upper()},
                {"$inc": {"used_count": 1}}
            )
            
            logger.info(f"✅ Promotion appliquée: {code} pour {user_email}")
            return validation
            
        except Exception as e:
            logger.error(f"Error applying promotion: {e}")
            return {"valid": False, "error": "Erreur lors de l'application"}
    
    # ========== SYSTÈME PARRAINAGE ==========
    
    def _generate_referral_code(self, email: str) -> str:
        """Générer code parrainage unique"""
        # Utiliser partie email + random pour unicité
        email_part = email.split('@')[0][:4].upper()
        random_part = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(4))
        return f"{email_part}{random_part}"
    
    async def generate_referral_code(self, referrer_email: str) -> Dict[str, Any]:
        """Générer code parrainage pour utilisateur"""
        try:
            # Vérifier si code existe déjà
            existing = await self.referrals_collection.find_one({"referrer_email": referrer_email})
            if existing:
                return {
                    "success": True,
                    "referral_code": existing["referrer_code"],
                    "message": "Code parrainage existant récupéré"
                }
            
            # Générer nouveau code unique
            attempts = 0
            max_attempts = 10
            
            while attempts < max_attempts:
                code = self._generate_referral_code(referrer_email)
                existing_code = await self.referrals_collection.find_one({"referrer_code": code})
                
                if not existing_code:
                    # Code unique trouvé
                    referral = Referral(
                        referrer_email=referrer_email,
                        referrer_code=code
                    )
                    
                    await self.referrals_collection.insert_one(referral.dict())
                    
                    # Mettre à jour profil utilisateur
                    await self.users_collection.update_one(
                        {"email": referrer_email},
                        {"$set": {"referral_code": code}},
                        upsert=True
                    )
                    
                    logger.info(f"✅ Code parrainage généré: {code} pour {referrer_email}")
                    
                    return {
                        "success": True,
                        "referral_code": code,
                        "message": "Code parrainage généré avec succès"
                    }
                
                attempts += 1
            
            return {"success": False, "error": "Impossible de générer un code unique"}
            
        except Exception as e:
            logger.error(f"Error generating referral code: {e}")
            return {"success": False, "error": "Erreur lors de la génération"}
    
    async def validate_referral_code(self, code: str, referee_email: str) -> Dict[str, Any]:
        """Valider code parrainage"""
        try:
            # Récupérer parrainage
            referral = await self.referrals_collection.find_one({
                "referrer_code": code.upper(),
                "status": "pending"
            })
            
            if not referral:
                return {"valid": False, "error": "Code parrainage invalide ou déjà utilisé"}
            
            # Vérifier que le filleul n'est pas le parrain
            if referral["referrer_email"].lower() == referee_email.lower():
                return {"valid": False, "error": "Vous ne pouvez pas utiliser votre propre code"}
            
            # Vérifier expiration
            if datetime.utcnow() > referral["expires_at"]:
                return {"valid": False, "error": "Code parrainage expiré"}
            
            # Vérifier que l'email n'a pas déjà été parrainé
            existing_referral = await self.referrals_collection.find_one({
                "referee_email": referee_email,
                "status": {"$in": ["completed", "pending"]}
            })
            
            if existing_referral:
                return {"valid": False, "error": "Vous avez déjà bénéficié du parrainage"}
            
            return {
                "valid": True,
                "referral": {
                    "id": referral["id"],
                    "referrer_email": referral["referrer_email"],
                    "referrer_code": referral["referrer_code"],
                    "discount_percent": referral["referee_discount_percent"],
                    "reward_amount": referral["referrer_reward_amount"]
                }
            }
            
        except Exception as e:
            logger.error(f"Error validating referral code: {e}")
            return {"valid": False, "error": "Erreur lors de la validation"}
    
    async def apply_referral_discount(self, code: str, referee_email: str, order_amount: float, order_id: str) -> Dict[str, Any]:
        """Appliquer réduction parrainage"""
        try:
            # Valider code
            validation = await self.validate_referral_code(code, referee_email)
            if not validation["valid"]:
                return validation
            
            referral_data = validation["referral"]
            discount_percent = referral_data["discount_percent"]
            discount_amount = order_amount * (discount_percent / 100)
            final_amount = order_amount - discount_amount
            
            # Mettre à jour parrainage
            await self.referrals_collection.update_one(
                {"referrer_code": code.upper(), "status": "pending"},
                {
                    "$set": {
                        "referee_email": referee_email,
                        "referee_order_id": order_id,
                        "referee_order_amount": order_amount,
                        "referee_discount_applied": discount_amount,
                        "used_at": datetime.utcnow(),
                        "status": "completed"  # Sera completed après validation commande
                    }
                }
            )
            
            logger.info(f"✅ Parrainage appliqué: {code} pour {referee_email}")
            
            return {
                "valid": True,
                "discount_amount": discount_amount,
                "discount_percent": discount_percent,
                "final_amount": final_amount,
                "referrer_email": referral_data["referrer_email"]
            }
            
        except Exception as e:
            logger.error(f"Error applying referral discount: {e}")
            return {"valid": False, "error": "Erreur lors de l'application"}
    
    async def complete_referral_reward(self, order_id: str) -> Dict[str, Any]:
        """Finaliser parrainage et émettre bon parrain"""
        try:
            # Trouver parrainage lié à cette commande
            referral = await self.referrals_collection.find_one({
                "referee_order_id": order_id,
                "status": "completed",
                "referrer_reward_issued": False
            })
            
            if not referral:
                return {"success": False, "message": "Aucun parrainage à finaliser"}
            
            # Générer code bon parrain
            reward_code = f"PARRAIN{secrets.token_hex(4).upper()}"
            
            # Créer promotion pour le parrain
            reward_promotion = Promotion(
                code=reward_code,
                name=f"Bon parrainage - {referral['referrer_reward_amount']}€",
                description=f"Bon de {referral['referrer_reward_amount']}€ pour parrainage réussi",
                type="fixed_amount",
                value=referral['referrer_reward_amount'],
                min_order_amount=0.0,
                usage_limit=1,
                usage_limit_per_customer=1,
                expires_at=datetime.utcnow() + timedelta(days=365),
                created_by="referral_system",
                target_customer_type="both"
            )
            
            await self.promotions_collection.insert_one(reward_promotion.dict())
            
            # Mettre à jour parrainage
            await self.referrals_collection.update_one(
                {"id": referral["id"]},
                {
                    "$set": {
                        "referrer_reward_issued": True,
                        "referrer_reward_code": reward_code,
                        "completed_at": datetime.utcnow()
                    }
                }
            )
            
            logger.info(f"✅ Récompense parrainage émise: {reward_code} pour {referral['referrer_email']}")
            
            return {
                "success": True,
                "reward_code": reward_code,
                "reward_amount": referral['referrer_reward_amount'],
                "referrer_email": referral['referrer_email']
            }
            
        except Exception as e:
            logger.error(f"Error completing referral reward: {e}")
            return {"success": False, "error": "Erreur lors de la finalisation"}
    
    async def get_user_referral_stats(self, user_email: str) -> Dict[str, Any]:
        """Statistiques parrainage utilisateur"""
        try:
            # Récupérer code parrainage
            user_referral = await self.referrals_collection.find_one({"referrer_email": user_email})
            
            if not user_referral:
                return {"referral_code": None, "stats": {}}
            
            # Compter parrainages
            total_referrals = await self.referrals_collection.count_documents({
                "referrer_email": user_email,
                "status": "completed"
            })
            
            pending_referrals = await self.referrals_collection.count_documents({
                "referrer_email": user_email,
                "status": "pending",
                "referee_email": {"$ne": None}
            })
            
            # Calculer gains
            completed_referrals = await self.referrals_collection.find({
                "referrer_email": user_email,
                "status": "completed"
            }).to_list(100)
            
            total_earnings = sum(r.get("referrer_reward_amount", 0) for r in completed_referrals if r.get("referrer_reward_issued"))
            pending_earnings = sum(r.get("referrer_reward_amount", 0) for r in completed_referrals if not r.get("referrer_reward_issued"))
            
            return {
                "referral_code": user_referral["referrer_code"],
                "stats": {
                    "total_referrals": total_referrals,
                    "pending_referrals": pending_referrals,
                    "total_earnings": total_earnings,
                    "pending_earnings": pending_earnings,
                    "active_codes": [r.get("referrer_reward_code") for r in completed_referrals if r.get("referrer_reward_code")]
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting referral stats: {e}")
            return {"referral_code": None, "stats": {}}

# ========== INSTANCE GLOBALE ==========

promotions_system = None

async def get_promotions_system(db: AsyncIOMotorDatabase) -> PromotionsSystem:
    """Obtenir instance système promotions"""
    global promotions_system
    if promotions_system is None:
        promotions_system = PromotionsSystem(db)
        await promotions_system.initialize()
    return promotions_system

async def init_promotions_system(db: AsyncIOMotorDatabase):
    """Initialiser système promotions"""
    global promotions_system
    promotions_system = PromotionsSystem(db)
    await promotions_system.initialize()
    return promotions_system