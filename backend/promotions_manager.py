#!/usr/bin/env python3
"""
Gestionnaire des promotions et du système de parrainage pour Josmoze.com
"""

import secrets
import string
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pydantic import BaseModel
import logging

# Configuration
logger = logging.getLogger(__name__)

class ReferralCode(BaseModel):
    """Modèle pour les codes de parrainage"""
    user_id: str
    code: str
    created_at: datetime
    uses_count: int = 0
    is_active: bool = True

class ReferralReward(BaseModel):
    """Modèle pour les récompenses de parrainage"""
    referrer_id: str  # Parrain
    referee_id: str   # Filleul
    referral_code: str
    order_id: str
    bonus_amount: float
    discount_applied: float
    created_at: datetime
    status: str = "pending"  # pending, completed, cancelled

class LaunchOfferCart(BaseModel):
    """Modèle pour l'offre de lancement"""
    eligible_product_id: str
    selected_gift_id: str
    customer_email: str
    applied_at: datetime

class PromotionsManager:
    """Gestionnaire des promotions et parrainage"""
    
    def __init__(self, db):
        self.db = db
        
    async def generate_referral_code(self, user_id: str) -> str:
        """Génère un code de parrainage unique pour un utilisateur"""
        try:
            # Vérifier si l'utilisateur a déjà un code actif
            existing_code = await self.db.referral_codes.find_one({
                "user_id": user_id,
                "is_active": True
            })
            
            if existing_code:
                return existing_code["code"]
            
            # Générer un nouveau code unique
            while True:
                code = self._generate_unique_code()
                
                # Vérifier l'unicité
                existing = await self.db.referral_codes.find_one({"code": code})
                if not existing:
                    break
            
            # Créer le nouveau code
            referral_code = ReferralCode(
                user_id=user_id,
                code=code,
                created_at=datetime.utcnow()
            )
            
            await self.db.referral_codes.insert_one(referral_code.dict())
            
            logger.info(f"Code de parrainage généré pour utilisateur {user_id}: {code}")
            return code
            
        except Exception as e:
            logger.error(f"Erreur génération code parrainage: {e}")
            raise
    
    def _generate_unique_code(self) -> str:
        """Génère un code unique de 8 caractères"""
        # Format: JOSM + 4 caractères aléatoires
        random_part = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(4))
        return f"JOSM{random_part}"
    
    async def validate_referral_code(self, code: str) -> Optional[Dict]:
        """Valide un code de parrainage"""
        try:
            referral_code = await self.db.referral_codes.find_one({
                "code": code,
                "is_active": True
            })
            
            if not referral_code:
                return None
                
            return {
                "valid": True,
                "user_id": referral_code["user_id"],
                "discount_percentage": 10,
                "description": "10% de réduction sur votre première commande d'osmoseur"
            }
            
        except Exception as e:
            logger.error(f"Erreur validation code parrainage: {e}")
            return None
    
    async def apply_referral_discount(self, code: str, order_data: Dict) -> Dict:
        """Applique la réduction de parrainage à une commande"""
        try:
            # Valider le code
            validation = await self.validate_referral_code(code)
            if not validation:
                return {"success": False, "message": "Code de parrainage invalide"}
            
            # Vérifier que la commande contient un osmoseur éligible
            eligible_products = ["osmoseur-essentiel", "osmoseur-premium", "osmoseur-prestige"]
            has_eligible_product = False
            discount_amount = 0
            
            for item in order_data.get("items", []):
                if item.get("product_id") in eligible_products:
                    has_eligible_product = True
                    discount_amount += item.get("price", 0) * item.get("quantity", 1) * 0.10
            
            if not has_eligible_product:
                return {
                    "success": False, 
                    "message": "Le code de parrainage s'applique uniquement aux osmoseurs"
                }
            
            # Appliquer la réduction
            return {
                "success": True,
                "discount_percentage": 10,
                "discount_amount": round(discount_amount, 2),
                "referrer_id": validation["user_id"],
                "message": f"Réduction de 10% appliquée (-{discount_amount:.2f}€)"
            }
            
        except Exception as e:
            logger.error(f"Erreur application réduction parrainage: {e}")
            return {"success": False, "message": "Erreur lors de l'application de la réduction"}
    
    async def process_referral_reward(self, referrer_id: str, referee_order: Dict) -> bool:
        """Traite la récompense du parrain après commande validée du filleul"""
        try:
            # Créer la récompense
            reward = ReferralReward(
                referrer_id=referrer_id,
                referee_id=referee_order.get("customer_email", ""),
                referral_code=referee_order.get("referral_code", ""),
                order_id=referee_order.get("order_id", ""),
                bonus_amount=50.0,
                discount_applied=referee_order.get("referral_discount", 0),
                created_at=datetime.utcnow()
            )
            
            await self.db.referral_rewards.insert_one(reward.dict())
            
            # Mettre à jour le compteur du code de parrainage
            await self.db.referral_codes.update_one(
                {"user_id": referrer_id, "is_active": True},
                {"$inc": {"uses_count": 1}}
            )
            
            # Créer le bon d'achat pour le parrain
            voucher = {
                "user_id": referrer_id,
                "amount": 50.0,
                "code": f"BONUS{self._generate_unique_code()}",
                "created_at": datetime.utcnow(),
                "expires_at": datetime.utcnow() + timedelta(days=365),
                "used": False,
                "source": "referral_bonus"
            }
            
            await self.db.vouchers.insert_one(voucher)
            
            logger.info(f"Récompense parrainage créée pour {referrer_id}: 50€")
            return True
            
        except Exception as e:
            logger.error(f"Erreur traitement récompense parrainage: {e}")
            return False
    
    async def check_launch_offer_eligibility(self, cart_items: List[Dict]) -> Dict:
        """Vérifie si le panier est éligible à l'offre de lancement"""
        try:
            eligible_products = ["osmoseur-premium", "osmoseur-prestige"]
            eligible_items = []
            
            for item in cart_items:
                if item.get("product_id") in eligible_products:
                    eligible_items.append(item)
            
            if not eligible_items:
                return {"eligible": False, "message": "Aucun produit éligible à l'offre de lancement"}
            
            return {
                "eligible": True,
                "eligible_products": eligible_items,
                "gift_options": [
                    {
                        "id": "purificateur-portable-hydrogene",
                        "name": "Purificateur Portable à Hydrogène H2-Pro",
                        "value": "79€"
                    },
                    {
                        "id": "fontaine-eau-animaux",
                        "name": "Fontaine à Eau pour Animaux AquaPet Premium",
                        "value": "49€"
                    }
                ],
                "message": "Choisissez votre produit gratuit !"
            }
            
        except Exception as e:
            logger.error(f"Erreur vérification offre de lancement: {e}")
            return {"eligible": False, "message": "Erreur lors de la vérification"}
    
    async def apply_launch_offer(self, cart_items: List[Dict], selected_gift_id: str, customer_email: str) -> Dict:
        """Applique l'offre de lancement au panier"""
        try:
            # Vérifier l'éligibilité
            eligibility = await self.check_launch_offer_eligibility(cart_items)
            if not eligibility["eligible"]:
                return {"success": False, "message": eligibility["message"]}
            
            # Vérifier que le cadeau sélectionné est valide
            valid_gifts = ["purificateur-portable-hydrogene", "fontaine-eau-animaux"]
            if selected_gift_id not in valid_gifts:
                return {"success": False, "message": "Produit cadeau non valide"}
            
            # Ajouter le produit gratuit au panier
            gift_product = {
                "product_id": selected_gift_id,
                "quantity": 1,
                "price": 0.0,  # Gratuit
                "is_gift": True,
                "gift_reason": "Offre de Lancement Josmoze"
            }
            
            # Enregistrer l'application de l'offre
            launch_offer = LaunchOfferCart(
                eligible_product_id=eligibility["eligible_products"][0]["product_id"],
                selected_gift_id=selected_gift_id,
                customer_email=customer_email,
                applied_at=datetime.utcnow()
            )
            
            await self.db.launch_offers.insert_one(launch_offer.dict())
            
            return {
                "success": True,
                "gift_product": gift_product,
                "message": f"Produit gratuit ajouté à votre commande !"
            }
            
        except Exception as e:
            logger.error(f"Erreur application offre de lancement: {e}")
            return {"success": False, "message": "Erreur lors de l'application de l'offre"}
    
    async def get_user_referral_stats(self, user_id: str) -> Dict:
        """Récupère les statistiques de parrainage d'un utilisateur"""
        try:
            # Code de parrainage
            referral_code = await self.db.referral_codes.find_one({
                "user_id": user_id,
                "is_active": True
            })
            
            # Récompenses gagnées
            rewards = await self.db.referral_rewards.find({
                "referrer_id": user_id
            }).to_list(100)
            
            # Bons d'achat disponibles
            vouchers = await self.db.vouchers.find({
                "user_id": user_id,
                "used": False,
                "expires_at": {"$gt": datetime.utcnow()}
            }).to_list(100)
            
            total_bonus = sum(reward.get("bonus_amount", 0) for reward in rewards)
            available_vouchers = sum(voucher.get("amount", 0) for voucher in vouchers)
            
            return {
                "referral_code": referral_code.get("code") if referral_code else None,
                "total_referrals": len(rewards),
                "total_bonus_earned": total_bonus,
                "available_vouchers_amount": available_vouchers,
                "vouchers": vouchers
            }
            
        except Exception as e:
            logger.error(f"Erreur récupération stats parrainage: {e}")
            return {}

# Instance globale (sera initialisée dans server.py)
promotions_manager = None

def init_promotions_manager(db):
    """Initialise l'instance du gestionnaire de promotions"""
    global promotions_manager
    promotions_manager = PromotionsManager(db)
    return promotions_manager

def get_promotions_manager():
    """Récupère l'instance du gestionnaire de promotions"""
    global promotions_manager
    if not promotions_manager:
        raise RuntimeError("PromotionsManager non initialisé - appelez init_promotions_manager() d'abord")
    return promotions_manager