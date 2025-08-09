"""
Josmoze.com - Smart Loyalty Program System
Programme de fidélité intelligent pour augmenter la rétention
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorDatabase
from enum import Enum
import uuid

logger = logging.getLogger(__name__)

class LoyaltyTier(str, Enum):
    BRONZE = "bronze"
    SILVER = "silver" 
    GOLD = "gold"
    PLATINUM = "platinum"

class RewardType(str, Enum):
    DISCOUNT_PERCENTAGE = "discount_percentage"
    DISCOUNT_AMOUNT = "discount_amount"
    FREE_SHIPPING = "free_shipping"
    FREE_PRODUCT = "free_product"
    EARLY_ACCESS = "early_access"

class LoyaltyCustomer(BaseModel):
    customer_id: str
    email: str
    name: str
    tier: LoyaltyTier = LoyaltyTier.BRONZE
    points: int = 0
    total_spent: float = 0
    orders_count: int = 0
    created_at: datetime = datetime.now()
    last_activity: datetime = datetime.now()
    tier_upgrade_date: Optional[datetime] = None

class LoyaltyReward(BaseModel):
    id: str = uuid.uuid4().hex
    name: str
    description: str
    reward_type: RewardType
    points_cost: int
    value: float  # Amount or percentage
    valid_until: Optional[datetime] = None
    max_uses: Optional[int] = None
    current_uses: int = 0
    min_tier: LoyaltyTier = LoyaltyTier.BRONZE
    is_active: bool = True

class LoyaltyTransaction(BaseModel):
    id: str = uuid.uuid4().hex
    customer_id: str
    transaction_type: str  # "earned", "redeemed", "expired"
    points_change: int  # Positive for earned, negative for redeemed/expired
    description: str
    order_id: Optional[str] = None
    reward_id: Optional[str] = None
    created_at: datetime = datetime.now()

class LoyaltyProgramManager:
    """Gestionnaire du programme de fidélité intelligent"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        
        # Configuration du programme
        self.config = {
            "points_per_euro": 10,  # 10 points par euro dépensé
            "tier_thresholds": {
                LoyaltyTier.BRONZE: 0,
                LoyaltyTier.SILVER: 500,    # 50€ dépensés
                LoyaltyTier.GOLD: 1500,     # 150€ dépensés
                LoyaltyTier.PLATINUM: 3000  # 300€ dépensés
            },
            "tier_multipliers": {
                LoyaltyTier.BRONZE: 1.0,
                LoyaltyTier.SILVER: 1.2,
                LoyaltyTier.GOLD: 1.5,
                LoyaltyTier.PLATINUM: 2.0
            },
            "birthday_bonus_points": 100,
            "referral_bonus_points": 200,
            "review_bonus_points": 50,
            "points_expiry_days": 365
        }
        
        # Récompenses par défaut
        self.default_rewards = [
            LoyaltyReward(
                name="Réduction 5€",
                description="5€ de réduction sur votre prochaine commande",
                reward_type=RewardType.DISCOUNT_AMOUNT,
                points_cost=100,
                value=5.0,
                min_tier=LoyaltyTier.BRONZE
            ),
            LoyaltyReward(
                name="Réduction 10%",
                description="10% de réduction sur votre prochaine commande", 
                reward_type=RewardType.DISCOUNT_PERCENTAGE,
                points_cost=200,
                value=10.0,
                min_tier=LoyaltyTier.SILVER
            ),
            LoyaltyReward(
                name="Livraison Gratuite",
                description="Livraison gratuite sur votre prochaine commande",
                reward_type=RewardType.FREE_SHIPPING,
                points_cost=150,
                value=9.90,
                min_tier=LoyaltyTier.BRONZE
            ),
            LoyaltyReward(
                name="Kit Filtres Gratuit",
                description="Kit de filtres de rechange offert",
                reward_type=RewardType.FREE_PRODUCT,
                points_cost=500,
                value=49.0,
                min_tier=LoyaltyTier.GOLD
            ),
            LoyaltyReward(
                name="Accès Prioritaire",
                description="Accès en avant-première aux nouveaux produits",
                reward_type=RewardType.EARLY_ACCESS,
                points_cost=300,
                value=0.0,
                min_tier=LoyaltyTier.GOLD
            )
        ]
    
    async def initialize_loyalty_program(self):
        """Initialiser le programme de fidélité avec les récompenses par défaut"""
        try:
            # Vérifier si les récompenses existent déjà
            existing_rewards = await self.db.loyalty_rewards.count_documents({})
            
            if existing_rewards == 0:
                # Insérer les récompenses par défaut
                rewards_data = [reward.dict() for reward in self.default_rewards]
                await self.db.loyalty_rewards.insert_many(rewards_data)
                logger.info(f"Initialized {len(rewards_data)} default loyalty rewards")
            
            return True
        except Exception as e:
            logger.error(f"Loyalty program initialization error: {e}")
            return False
    
    async def get_or_create_customer(self, customer_id: str, email: str, name: str) -> LoyaltyCustomer:
        """Récupérer ou créer un client fidélité"""
        try:
            # Rechercher le client existant
            existing = await self.db.loyalty_customers.find_one({"customer_id": customer_id})
            
            if existing:
                return LoyaltyCustomer(**existing)
            
            # Créer un nouveau client
            new_customer = LoyaltyCustomer(
                customer_id=customer_id,
                email=email,
                name=name
            )
            
            await self.db.loyalty_customers.insert_one(new_customer.dict())
            
            # Bonus de bienvenue
            await self.award_points(
                customer_id,
                50,
                "Bonus de bienvenue - Merci de rejoindre notre programme de fidélité !"
            )
            
            logger.info(f"Created new loyalty customer: {email}")
            return new_customer
            
        except Exception as e:
            logger.error(f"Get/create loyalty customer error: {e}")
            # Retourner un client par défaut en cas d'erreur
            return LoyaltyCustomer(customer_id=customer_id, email=email, name=name)
    
    async def award_points(
        self, 
        customer_id: str, 
        points: int, 
        description: str,
        order_id: Optional[str] = None
    ) -> bool:
        """Attribuer des points à un client"""
        try:
            # Récupérer le client
            customer = await self.db.loyalty_customers.find_one({"customer_id": customer_id})
            if not customer:
                logger.warning(f"Customer not found for points award: {customer_id}")
                return False
            
            loyalty_customer = LoyaltyCustomer(**customer)
            
            # Appliquer le multiplicateur de niveau
            tier_multiplier = self.config["tier_multipliers"][loyalty_customer.tier]
            final_points = int(points * tier_multiplier)
            
            # Mettre à jour les points du client
            new_points = loyalty_customer.points + final_points
            await self.db.loyalty_customers.update_one(
                {"customer_id": customer_id},
                {
                    "$set": {
                        "points": new_points,
                        "last_activity": datetime.now()
                    }
                }
            )
            
            # Enregistrer la transaction
            transaction = LoyaltyTransaction(
                customer_id=customer_id,
                transaction_type="earned",
                points_change=final_points,
                description=description,
                order_id=order_id
            )
            
            await self.db.loyalty_transactions.insert_one(transaction.dict())
            
            # Vérifier une éventuelle promotion de niveau
            await self._check_tier_upgrade(customer_id)
            
            logger.info(f"Awarded {final_points} points to {customer_id}: {description}")
            return True
            
        except Exception as e:
            logger.error(f"Award points error: {e}")
            return False
    
    async def process_order_points(self, order_data: Dict) -> bool:
        """Traiter les points pour une commande"""
        try:
            customer_email = order_data.get("customer_email")
            customer_name = order_data.get("customer_name", "Client")
            order_total = order_data.get("total_amount", 0)
            order_id = order_data.get("id", str(uuid.uuid4()))
            
            if not customer_email or order_total <= 0:
                return False
            
            # Créer ou récupérer le client
            customer = await self.get_or_create_customer(customer_email, customer_email, customer_name)
            
            # Calculer les points basés sur le montant
            base_points = int(order_total * self.config["points_per_euro"])
            
            # Bonus pour les gros achats (>200€)
            bonus_points = 0
            if order_total >= 200:
                bonus_points = 50
            elif order_total >= 500:
                bonus_points = 150
            
            total_points = base_points + bonus_points
            
            # Attribuer les points
            description = f"Commande #{order_id} - {order_total}€"
            if bonus_points > 0:
                description += f" (bonus {bonus_points} pts)"
            
            await self.award_points(customer_email, total_points, description, order_id)
            
            # Mettre à jour les statistiques du client
            await self.db.loyalty_customers.update_one(
                {"customer_id": customer_email},
                {
                    "$inc": {
                        "total_spent": order_total,
                        "orders_count": 1
                    }
                }
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Process order points error: {e}")
            return False
    
    async def redeem_reward(self, customer_id: str, reward_id: str) -> Dict[str, Any]:
        """Échanger des points contre une récompense"""
        try:
            # Récupérer le client et la récompense
            customer = await self.db.loyalty_customers.find_one({"customer_id": customer_id})
            reward = await self.db.loyalty_rewards.find_one({"id": reward_id})
            
            if not customer or not reward:
                return {"success": False, "error": "Client ou récompense introuvable"}
            
            loyalty_customer = LoyaltyCustomer(**customer)
            loyalty_reward = LoyaltyReward(**reward)
            
            # Vérifications
            if not loyalty_reward.is_active:
                return {"success": False, "error": "Cette récompense n'est plus disponible"}
            
            if loyalty_customer.points < loyalty_reward.points_cost:
                return {"success": False, "error": "Points insuffisants"}
            
            if loyalty_customer.tier.value < loyalty_reward.min_tier.value:
                return {"success": False, "error": f"Niveau {loyalty_reward.min_tier.value} requis"}
            
            if loyalty_reward.valid_until and datetime.now() > loyalty_reward.valid_until:
                return {"success": False, "error": "Cette récompense a expiré"}
            
            if loyalty_reward.max_uses and loyalty_reward.current_uses >= loyalty_reward.max_uses:
                return {"success": False, "error": "Limite d'utilisation atteinte"}
            
            # Déduire les points
            new_points = loyalty_customer.points - loyalty_reward.points_cost
            await self.db.loyalty_customers.update_one(
                {"customer_id": customer_id},
                {"$set": {"points": new_points, "last_activity": datetime.now()}}
            )
            
            # Enregistrer la transaction
            transaction = LoyaltyTransaction(
                customer_id=customer_id,
                transaction_type="redeemed",
                points_change=-loyalty_reward.points_cost,
                description=f"Échange: {loyalty_reward.name}",
                reward_id=reward_id
            )
            
            await self.db.loyalty_transactions.insert_one(transaction.dict())
            
            # Mettre à jour l'utilisation de la récompense
            await self.db.loyalty_rewards.update_one(
                {"id": reward_id},
                {"$inc": {"current_uses": 1}}
            )
            
            # Générer le code de récompense
            reward_code = f"LOYAL-{reward_id[:8]}-{customer_id[:8]}".upper()
            
            logger.info(f"Reward redeemed: {customer_id} - {loyalty_reward.name}")
            
            return {
                "success": True,
                "reward_code": reward_code,
                "reward": loyalty_reward.dict(),
                "remaining_points": new_points,
                "message": f"Félicitations ! Votre récompense '{loyalty_reward.name}' est prête à utiliser."
            }
            
        except Exception as e:
            logger.error(f"Redeem reward error: {e}")
            return {"success": False, "error": "Erreur lors de l'échange"}
    
    async def get_customer_status(self, customer_id: str) -> Dict[str, Any]:
        """Obtenir le statut complet d'un client fidélité"""
        try:
            customer = await self.db.loyalty_customers.find_one({"customer_id": customer_id})
            
            if not customer:
                return {"success": False, "error": "Client non trouvé"}
            
            loyalty_customer = LoyaltyCustomer(**customer)
            
            # Récupérer les transactions récentes
            recent_transactions = await self.db.loyalty_transactions.find({
                "customer_id": customer_id
            }).sort("created_at", -1).limit(10).to_list(10)
            
            # Calculer les points jusqu'au prochain niveau
            current_tier_value = self.config["tier_thresholds"][loyalty_customer.tier]
            next_tier = self._get_next_tier(loyalty_customer.tier)
            points_to_next_tier = 0
            
            if next_tier:
                next_tier_value = self.config["tier_thresholds"][next_tier]
                points_to_next_tier = max(0, next_tier_value - loyalty_customer.points)
            
            # Récompenses disponibles
            available_rewards = await self.db.loyalty_rewards.find({
                "is_active": True,
                "points_cost": {"$lte": loyalty_customer.points},
                "min_tier": {"$lte": loyalty_customer.tier.value}
            }).to_list(None)
            
            return {
                "success": True,
                "customer": loyalty_customer.dict(),
                "tier_info": {
                    "current_tier": loyalty_customer.tier.value,
                    "next_tier": next_tier.value if next_tier else None,
                    "points_to_next_tier": points_to_next_tier,
                    "tier_benefits": self._get_tier_benefits(loyalty_customer.tier)
                },
                "available_rewards": available_rewards,
                "recent_transactions": recent_transactions,
                "statistics": {
                    "member_since": loyalty_customer.created_at.isoformat(),
                    "total_points_earned": await self._get_total_points_earned(customer_id),
                    "rewards_redeemed": await self._get_rewards_count(customer_id)
                }
            }
            
        except Exception as e:
            logger.error(f"Get customer status error: {e}")
            return {"success": False, "error": "Erreur lors de la récupération du statut"}
    
    async def _check_tier_upgrade(self, customer_id: str):
        """Vérifier et effectuer une promotion de niveau si nécessaire"""
        try:
            customer = await self.db.loyalty_customers.find_one({"customer_id": customer_id})
            if not customer:
                return
            
            loyalty_customer = LoyaltyCustomer(**customer)
            current_tier = loyalty_customer.tier
            new_tier = self._calculate_tier(loyalty_customer.points)
            
            if new_tier != current_tier:
                # Promotion de niveau
                await self.db.loyalty_customers.update_one(
                    {"customer_id": customer_id},
                    {
                        "$set": {
                            "tier": new_tier.value,
                            "tier_upgrade_date": datetime.now()
                        }
                    }
                )
                
                # Bonus de promotion
                bonus_points = self._get_tier_upgrade_bonus(new_tier)
                if bonus_points > 0:
                    await self.award_points(
                        customer_id,
                        bonus_points,
                        f"Bonus promotion niveau {new_tier.value.upper()}"
                    )
                
                logger.info(f"Tier upgraded: {customer_id} from {current_tier.value} to {new_tier.value}")
                
        except Exception as e:
            logger.error(f"Tier upgrade check error: {e}")
    
    def _calculate_tier(self, points: int) -> LoyaltyTier:
        """Calculer le niveau basé sur les points"""
        if points >= self.config["tier_thresholds"][LoyaltyTier.PLATINUM]:
            return LoyaltyTier.PLATINUM
        elif points >= self.config["tier_thresholds"][LoyaltyTier.GOLD]:
            return LoyaltyTier.GOLD
        elif points >= self.config["tier_thresholds"][LoyaltyTier.SILVER]:
            return LoyaltyTier.SILVER
        else:
            return LoyaltyTier.BRONZE
    
    def _get_next_tier(self, current_tier: LoyaltyTier) -> Optional[LoyaltyTier]:
        """Obtenir le niveau suivant"""
        tiers = [LoyaltyTier.BRONZE, LoyaltyTier.SILVER, LoyaltyTier.GOLD, LoyaltyTier.PLATINUM]
        current_index = tiers.index(current_tier)
        
        if current_index < len(tiers) - 1:
            return tiers[current_index + 1]
        return None
    
    def _get_tier_benefits(self, tier: LoyaltyTier) -> List[str]:
        """Obtenir les avantages d'un niveau"""
        benefits = {
            LoyaltyTier.BRONZE: [
                "Points sur chaque achat",
                "Réductions exclusives",
                "Support client prioritaire"
            ],
            LoyaltyTier.SILVER: [
                "20% de points bonus",
                "Livraison gratuite dès 50€",
                "Offres spéciales mensuelles"
            ],
            LoyaltyTier.GOLD: [
                "50% de points bonus",
                "Accès aux ventes privées", 
                "Retour gratuit 60 jours"
            ],
            LoyaltyTier.PLATINUM: [
                "Points doubles sur tous les achats",
                "Conseiller personnel dédié",
                "Cadeaux d'anniversaire exclusifs"
            ]
        }
        return benefits.get(tier, [])
    
    def _get_tier_upgrade_bonus(self, new_tier: LoyaltyTier) -> int:
        """Obtenir le bonus de promotion de niveau"""
        bonuses = {
            LoyaltyTier.SILVER: 100,
            LoyaltyTier.GOLD: 200,
            LoyaltyTier.PLATINUM: 500
        }
        return bonuses.get(new_tier, 0)
    
    async def _get_total_points_earned(self, customer_id: str) -> int:
        """Calculer le total des points gagnés"""
        try:
            pipeline = [
                {"$match": {"customer_id": customer_id, "transaction_type": "earned"}},
                {"$group": {"_id": None, "total": {"$sum": "$points_change"}}}
            ]
            
            result = await self.db.loyalty_transactions.aggregate(pipeline).to_list(1)
            return result[0]["total"] if result else 0
        except:
            return 0
    
    async def _get_rewards_count(self, customer_id: str) -> int:
        """Compter les récompenses échangées"""
        try:
            return await self.db.loyalty_transactions.count_documents({
                "customer_id": customer_id,
                "transaction_type": "redeemed"
            })
        except:
            return 0

# Fonctions utilitaires
async def process_order_loyalty_points(db: AsyncIOMotorDatabase, order_data: Dict) -> bool:
    """Traiter les points de fidélité pour une commande"""
    manager = LoyaltyProgramManager(db)
    return await manager.process_order_points(order_data)

async def get_customer_loyalty_status(db: AsyncIOMotorDatabase, customer_id: str) -> Dict[str, Any]:
    """Obtenir le statut fidélité d'un client"""
    manager = LoyaltyProgramManager(db)
    return await manager.get_customer_status(customer_id)