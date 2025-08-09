"""
Service de Gestion des Paniers Abandonnés - Josmoze.com
Système intelligent pour récupérer les ventes perdues avec emails automatiques
et liens de recommande rapide
"""

import os
import uuid
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from motor.motor_asyncio import AsyncIOMotorDatabase
import json
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from io import BytesIO
import base64

# Configuration des emails de récupération
RECOVERY_CONFIG = {
    "immediate_delay_minutes": 30,    # Email immédiat après 30 minutes
    "reminder_delay_hours": 24,       # Rappel après 24h
    "final_reminder_delay_hours": 72, # Dernier rappel après 72h
    "discount_codes": {
        "immediate": "RETOUR10",      # 10% de remise immédiate
        "reminder": "RETOUR15",       # 15% après 24h
        "final": "RETOUR20"           # 20% en dernière chance
    },
    "link_expiry_days": 7            # Liens valides 7 jours
}

class AbandonedCart(BaseModel):
    """Modèle pour les paniers abandonnés"""
    cart_id: str = Field(default_factory=lambda: f"CART-{str(uuid.uuid4())[:8].upper()}")
    customer_email: str
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    customer_address: Optional[Dict[str, str]] = None
    items: List[Dict[str, Any]] = []
    total_value: float = 0.0
    currency: str = "EUR"
    abandoned_at: datetime = Field(default_factory=datetime.utcnow)
    last_activity: datetime = Field(default_factory=datetime.utcnow)
    recovery_emails_sent: List[Dict[str, Any]] = []
    recovery_link: Optional[str] = None
    recovery_token: str = Field(default_factory=lambda: str(uuid.uuid4()))
    status: str = "abandoned"  # abandoned, recovered, expired
    source_page: str = "/checkout"
    browser_info: Optional[Dict] = None
    recovery_attempts: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class DeliveryNote(BaseModel):
    """Modèle pour les bons de livraison"""
    delivery_id: str = Field(default_factory=lambda: f"BL-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:6].upper()}")
    order_id: str
    cart_id: Optional[str] = None
    customer_name: str
    customer_email: str
    delivery_address: Dict[str, str]
    items: List[Dict[str, Any]] = []
    total_weight: float = 0.0
    delivery_method: str = "standard"  # standard, express, pickup
    delivery_date: Optional[datetime] = None
    tracking_number: Optional[str] = None
    carrier: str = "Transporteur Standard"
    special_instructions: str = ""
    pdf_generated: bool = False
    pdf_base64: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class AbandonedCartService:
    """Service de gestion des paniers abandonnés"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.logger = logging.getLogger(__name__)
        
        # Templates d'emails de récupération
        self.email_templates = {
            "immediate": {
                "subject": "🛒 Votre panier vous attend - Josmose (10% offert)",
                "template": """
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                    <div style="background: linear-gradient(135deg, #1E40AF, #3B82F6); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
                        <h1 style="margin: 0; font-size: 28px;">🌊 Josmose</h1>
                        <p style="margin: 10px 0 0 0; font-size: 16px;">Votre eau pure vous attend</p>
                    </div>
                    
                    <div style="background: white; padding: 30px; border: 1px solid #e5e7eb; border-radius: 0 0 10px 10px;">
                        <h2 style="color: #1F2937; margin-top: 0;">Bonjour {customer_name},</h2>
                        
                        <p style="color: #374151; font-size: 16px; line-height: 1.6;">
                            Vous avez ajouté des produits à votre panier mais n'avez pas finalisé votre commande. 
                            Ne perdez pas cette opportunité d'avoir une eau pure pour votre famille !
                        </p>
                        
                        <div style="background: #F3F4F6; padding: 20px; border-radius: 8px; margin: 25px 0;">
                            <h3 style="color: #1F2937; margin-top: 0;">📦 Récapitulatif de votre panier :</h3>
                            {cart_items}
                            <div style="border-top: 2px solid #1E40AF; padding-top: 15px; margin-top: 15px;">
                                <p style="font-size: 18px; font-weight: bold; color: #1E40AF; margin: 0;">
                                    Total : {total_value}€
                                </p>
                            </div>
                        </div>
                        
                        <div style="background: #FEF2F2; border: 2px dashed #EF4444; padding: 20px; border-radius: 8px; margin: 25px 0; text-align: center;">
                            <h3 style="color: #DC2626; margin-top: 0;">🎁 OFFRE SPÉCIALE - 10% DE REMISE !</h3>
                            <p style="color: #7F1D1D; font-size: 16px; margin: 10px 0;">
                                Code promo : <strong>RETOUR10</strong><br>
                                <small>Valable 48h seulement</small>
                            </p>
                        </div>
                        
                        <div style="text-align: center; margin: 30px 0;">
                            <a href="{recovery_link}" style="background: #1E40AF; color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px; font-size: 16px; font-weight: bold; display: inline-block;">
                                ✅ Finaliser ma commande maintenant
                            </a>
                        </div>
                        
                        <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #E5E7EB;">
                            <p style="color: #6B7280; font-size: 14px;">
                                ✅ Installation gratuite comprise<br>
                                ✅ Garantie 2 ans incluse<br>
                                ✅ Support technique dédié<br>
                                ✅ Livraison rapide en Europe
                            </p>
                        </div>
                        
                        <p style="color: #6B7280; font-size: 12px; margin-top: 25px;">
                            Ceci est un email automatique. Si vous ne souhaitez plus recevoir ces rappels, 
                            <a href="{unsubscribe_link}" style="color: #6B7280;">cliquez ici</a>.
                        </p>
                    </div>
                </div>
                """
            },
            "reminder": {
                "subject": "⏰ Dernière chance - 15% sur votre panier Josmose",
                "template": """
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                    <div style="background: linear-gradient(135deg, #DC2626, #EF4444); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
                        <h1 style="margin: 0; font-size: 28px;">⏰ DERNIÈRE CHANCE</h1>
                        <p style="margin: 10px 0 0 0; font-size: 16px;">Votre panier expire bientôt</p>
                    </div>
                    
                    <div style="background: white; padding: 30px; border: 1px solid #e5e7eb; border-radius: 0 0 10px 10px;">
                        <h2 style="color: #1F2937; margin-top: 0;">Bonjour {customer_name},</h2>
                        
                        <p style="color: #374151; font-size: 16px; line-height: 1.6;">
                            Il ne vous reste que <strong>48 heures</strong> pour récupérer votre panier Josmose 
                            avec une remise exceptionnelle de <strong>15%</strong> !
                        </p>
                        
                        <div style="background: #FEF2F2; border-left: 4px solid #EF4444; padding: 20px; margin: 25px 0;">
                            <h3 style="color: #DC2626; margin-top: 0;">🚨 OFFRE LIMITÉE - 15% DE REMISE</h3>
                            <p style="color: #7F1D1D; font-size: 18px; margin: 10px 0;">
                                Code promo : <strong style="font-size: 22px;">RETOUR15</strong><br>
                                <small>Expire dans 48h !</small>
                            </p>
                        </div>
                        
                        <div style="background: #F3F4F6; padding: 20px; border-radius: 8px; margin: 25px 0;">
                            <h3 style="color: #1F2937; margin-top: 0;">📦 Votre panier :</h3>
                            {cart_items}
                            <div style="border-top: 2px solid #DC2626; padding-top: 15px; margin-top: 15px;">
                                <p style="font-size: 16px; color: #6B7280; margin: 0; text-decoration: line-through;">
                                    Total : {total_value}€
                                </p>
                                <p style="font-size: 20px; font-weight: bold; color: #DC2626; margin: 5px 0 0 0;">
                                    Avec remise : {discounted_total}€ (-15%)
                                </p>
                            </div>
                        </div>
                        
                        <div style="text-align: center; margin: 30px 0;">
                            <a href="{recovery_link}" style="background: #DC2626; color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px; font-size: 16px; font-weight: bold; display: inline-block;">
                                🔥 RÉCUPÉRER MAINTENANT - 15% DE REMISE
                            </a>
                        </div>
                        
                        <p style="color: #6B7280; font-size: 12px; margin-top: 25px; text-align: center;">
                            Cette offre expire le {expiry_date}
                        </p>
                    </div>
                </div>
                """
            },
            "final": {
                "subject": "💔 Au revoir - Dernière offre 20% avant suppression",
                "template": """
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                    <div style="background: linear-gradient(135deg, #7C3AED, #A855F7); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
                        <h1 style="margin: 0; font-size: 28px;">💔 Au revoir {customer_name}</h1>
                        <p style="margin: 10px 0 0 0; font-size: 16px;">Dernière chance avant suppression</p>
                    </div>
                    
                    <div style="background: white; padding: 30px; border: 1px solid #e5e7eb; border-radius: 0 0 10px 10px;">
                        <p style="color: #374151; font-size: 16px; line-height: 1.6;">
                            Nous sommes désolés de vous voir partir. Votre panier sera définitivement supprimé dans 24h.
                        </p>
                        
                        <p style="color: #374151; font-size: 16px; line-height: 1.6;">
                            En dernière chance, nous vous offrons notre <strong>meilleure remise : 20%</strong> 
                            sur votre commande Josmose.
                        </p>
                        
                        <div style="background: #F3E8FF; border: 2px solid #A855F7; padding: 25px; border-radius: 8px; margin: 25px 0; text-align: center;">
                            <h3 style="color: #7C3AED; margin-top: 0;">🎁 OFFRE FINALE - 20% DE REMISE</h3>
                            <p style="color: #581C87; font-size: 20px; margin: 10px 0;">
                                Code promo : <strong style="font-size: 24px;">RETOUR20</strong><br>
                                <small>Notre meilleure offre - 24h seulement</small>
                            </p>
                        </div>
                        
                        <div style="text-align: center; margin: 30px 0;">
                            <a href="{recovery_link}" style="background: #7C3AED; color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px; font-size: 16px; font-weight: bold; display: inline-block;">
                                💜 DERNIÈRE CHANCE - 20% DE REMISE
                            </a>
                        </div>
                        
                        <div style="background: #F3F4F6; padding: 20px; border-radius: 8px; margin: 25px 0;">
                            <h3 style="color: #1F2937; margin-top: 0;">📦 Ce que vous perdez :</h3>
                            {cart_items}
                            <div style="border-top: 2px solid #7C3AED; padding-top: 15px; margin-top: 15px;">
                                <p style="font-size: 16px; color: #6B7280; margin: 0; text-decoration: line-through;">
                                    Total : {total_value}€
                                </p>
                                <p style="font-size: 22px; font-weight: bold; color: #7C3AED; margin: 5px 0 0 0;">
                                    Prix final : {discounted_total}€ (-20%)
                                </p>
                            </div>
                        </div>
                        
                        <p style="color: #EF4444; font-size: 14px; text-align: center; margin-top: 25px;">
                            ⚠️ Votre panier sera supprimé le {deletion_date}
                        </p>
                    </div>
                </div>
                """
            }
        }
    
    async def track_abandoned_cart(self, cart_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enregistrer un panier abandonné"""
        try:
            # Vérifier si un panier existe déjà pour ce client
            existing_cart = await self.db.abandoned_carts.find_one({
                "customer_email": cart_data["customer_email"],
                "status": "abandoned"
            })
            
            if existing_cart:
                # Mettre à jour le panier existant
                update_data = {
                    "items": cart_data["items"],
                    "total_value": cart_data["total_value"],
                    "last_activity": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
                
                await self.db.abandoned_carts.update_one(
                    {"cart_id": existing_cart["cart_id"]},
                    {"$set": update_data}
                )
                
                cart_id = existing_cart["cart_id"]
                
            else:
                # Créer un nouveau panier abandonné
                abandoned_cart = AbandonedCart(
                    customer_email=cart_data["customer_email"],
                    customer_name=cart_data.get("customer_name"),
                    customer_phone=cart_data.get("customer_phone"),
                    customer_address=cart_data.get("customer_address"),
                    items=cart_data["items"],
                    total_value=cart_data["total_value"],
                    currency=cart_data.get("currency", "EUR"),
                    source_page=cart_data.get("source_page", "/checkout"),
                    browser_info=cart_data.get("browser_info")
                )
                
                # Générer le lien de récupération
                abandoned_cart.recovery_link = f"https://www.josmoze.com/recovery?token={abandoned_cart.recovery_token}"
                
                await self.db.abandoned_carts.insert_one(abandoned_cart.dict())
                cart_id = abandoned_cart.cart_id
            
            # Programmer l'envoi des emails de récupération
            await self._schedule_recovery_emails(cart_id)
            
            self.logger.info(f"Abandoned cart tracked: {cart_id}")
            
            return {
                "success": True,
                "cart_id": cart_id,
                "recovery_emails_scheduled": True
            }
            
        except Exception as e:
            self.logger.error(f"Error tracking abandoned cart: {e}")
            return {"success": False, "error": str(e)}
    
    async def _schedule_recovery_emails(self, cart_id: str):
        """Programmer les emails de récupération"""
        try:
            now = datetime.utcnow()
            
            # Email immédiat (30 minutes)
            immediate_time = now + timedelta(minutes=RECOVERY_CONFIG["immediate_delay_minutes"])
            await self.db.scheduled_emails.insert_one({
                "cart_id": cart_id,
                "email_type": "immediate",
                "scheduled_for": immediate_time,
                "status": "pending",
                "discount_code": RECOVERY_CONFIG["discount_codes"]["immediate"],
                "created_at": now
            })
            
            # Email de rappel (24h)
            reminder_time = now + timedelta(hours=RECOVERY_CONFIG["reminder_delay_hours"])
            await self.db.scheduled_emails.insert_one({
                "cart_id": cart_id,
                "email_type": "reminder",
                "scheduled_for": reminder_time,
                "status": "pending",
                "discount_code": RECOVERY_CONFIG["discount_codes"]["reminder"],
                "created_at": now
            })
            
            # Email final (72h)
            final_time = now + timedelta(hours=RECOVERY_CONFIG["final_reminder_delay_hours"])
            await self.db.scheduled_emails.insert_one({
                "cart_id": cart_id,
                "email_type": "final",
                "scheduled_for": final_time,
                "status": "pending",
                "discount_code": RECOVERY_CONFIG["discount_codes"]["final"],
                "created_at": now
            })
            
            self.logger.info(f"Recovery emails scheduled for cart: {cart_id}")
            
        except Exception as e:
            self.logger.error(f"Error scheduling recovery emails: {e}")
    
    async def process_scheduled_emails(self):
        """Traiter les emails programmés (à appeler périodiquement)"""
        try:
            # Récupérer les emails à envoyer
            pending_emails = await self.db.scheduled_emails.find({
                "scheduled_for": {"$lte": datetime.utcnow()},
                "status": "pending"
            }).to_list(100)
            
            for email_schedule in pending_emails:
                cart_id = email_schedule["cart_id"]
                email_type = email_schedule["email_type"]
                discount_code = email_schedule["discount_code"]
                
                # Récupérer le panier
                cart = await self.db.abandoned_carts.find_one({"cart_id": cart_id})
                if not cart or cart["status"] != "abandoned":
                    # Marquer comme annulé si le panier n'est plus abandonné
                    await self.db.scheduled_emails.update_one(
                        {"_id": email_schedule["_id"]},
                        {"$set": {"status": "cancelled", "updated_at": datetime.utcnow()}}
                    )
                    continue
                
                # Envoyer l'email de récupération
                email_sent = await self._send_recovery_email(cart, email_type, discount_code)
                
                if email_sent:
                    # Marquer comme envoyé
                    await self.db.scheduled_emails.update_one(
                        {"_id": email_schedule["_id"]},
                        {"$set": {"status": "sent", "sent_at": datetime.utcnow()}}
                    )
                    
                    # Mettre à jour le panier
                    await self.db.abandoned_carts.update_one(
                        {"cart_id": cart_id},
                        {
                            "$push": {
                                "recovery_emails_sent": {
                                    "type": email_type,
                                    "sent_at": datetime.utcnow(),
                                    "discount_code": discount_code
                                }
                            },
                            "$inc": {"recovery_attempts": 1}
                        }
                    )
                    
                    self.logger.info(f"Recovery email sent: {email_type} for cart {cart_id}")
                
                else:
                    # Marquer comme échoué
                    await self.db.scheduled_emails.update_one(
                        {"_id": email_schedule["_id"]},
                        {"$set": {"status": "failed", "updated_at": datetime.utcnow()}}
                    )
            
        except Exception as e:
            self.logger.error(f"Error processing scheduled emails: {e}")
    
    async def _send_recovery_email(self, cart: Dict, email_type: str, discount_code: str) -> bool:
        """Envoyer un email de récupération"""
        try:
            # Préparer les données pour le template
            customer_name = cart.get("customer_name", "Cher client")
            total_value = cart["total_value"]
            discounted_total = round(total_value * (0.9 if email_type == "immediate" 
                                                  else 0.85 if email_type == "reminder" 
                                                  else 0.8), 2)
            
            # Générer le HTML des articles du panier
            cart_items_html = ""
            for item in cart["items"]:
                cart_items_html += f"""
                <div style="display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid #E5E7EB;">
                    <span>{item.get('name', 'Produit')}</span>
                    <span>{item.get('quantity', 1)}x {item.get('price', 0)}€</span>
                </div>
                """
            
            # Récupérer le template
            template_data = self.email_templates[email_type]
            
            # Remplacer les variables dans le template
            email_html = template_data["template"].format(
                customer_name=customer_name,
                cart_items=cart_items_html,
                total_value=total_value,
                discounted_total=discounted_total,
                recovery_link=cart["recovery_link"],
                unsubscribe_link=f"https://www.josmoze.com/unsubscribe?token={cart['recovery_token']}",
                expiry_date=(datetime.utcnow() + timedelta(days=2)).strftime("%d/%m/%Y"),
                deletion_date=(datetime.utcnow() + timedelta(days=1)).strftime("%d/%m/%Y")
            )
            
            # Importer et utiliser le service email
            from email_service import email_service
            
            result = await email_service.send_email(
                from_email="commercial@josmoze.com",
                to_email=cart["customer_email"],
                subject=template_data["subject"],
                body=email_html
            )
            
            return result.get("success", False)
            
        except Exception as e:
            self.logger.error(f"Error sending recovery email: {e}")
            return False
    
    async def get_abandoned_carts_dashboard(self) -> Dict[str, Any]:
        """Récupérer les données du dashboard des paniers abandonnés"""
        try:
            # Statistiques générales
            total_abandoned = await self.db.abandoned_carts.count_documents({"status": "abandoned"})
            total_recovered = await self.db.abandoned_carts.count_documents({"status": "recovered"})
            
            # Paniers récents (dernières 24h)
            recent_cutoff = datetime.utcnow() - timedelta(hours=24)
            recent_abandoned = await self.db.abandoned_carts.count_documents({
                "abandoned_at": {"$gte": recent_cutoff},
                "status": "abandoned"
            })
            
            # Valeur totale des paniers abandonnés
            pipeline = [
                {"$match": {"status": "abandoned"}},
                {"$group": {"_id": None, "total_value": {"$sum": "$total_value"}}}
            ]
            
            total_value_result = await self.db.abandoned_carts.aggregate(pipeline).to_list(1)
            total_abandoned_value = total_value_result[0]["total_value"] if total_value_result else 0
            
            # Taux de récupération
            total_carts = total_abandoned + total_recovered
            recovery_rate = (total_recovered / total_carts * 100) if total_carts > 0 else 0
            
            # Paniers abandonnés récents avec détails
            recent_carts = await self.db.abandoned_carts.find({
                "status": "abandoned"
            }).sort("abandoned_at", -1).limit(20).to_list(20)
            
            # Convertir ObjectId en string pour JSON
            for cart in recent_carts:
                cart["_id"] = str(cart["_id"])
            
            # Emails programmés en attente
            pending_emails = await self.db.scheduled_emails.count_documents({"status": "pending"})
            
            return {
                "statistics": {
                    "total_abandoned": total_abandoned,
                    "total_recovered": total_recovered,
                    "recent_abandoned_24h": recent_abandoned,
                    "total_abandoned_value": round(total_abandoned_value, 2),
                    "recovery_rate": round(recovery_rate, 1),
                    "pending_recovery_emails": pending_emails
                },
                "recent_carts": recent_carts,
                "last_updated": datetime.utcnow()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting abandoned carts dashboard: {e}")
            return {"error": str(e)}
    
    async def recover_cart_by_token(self, recovery_token: str, apply_discount: bool = True) -> Dict[str, Any]:
        """Récupérer un panier via son token de récupération"""
        try:
            cart = await self.db.abandoned_carts.find_one({
                "recovery_token": recovery_token,
                "status": "abandoned"
            })
            
            if not cart:
                return {"success": False, "error": "Token de récupération invalide ou expiré"}
            
            # Vérifier si le lien n'a pas expiré
            link_expiry = cart["abandoned_at"] + timedelta(days=RECOVERY_CONFIG["link_expiry_days"])
            if datetime.utcnow() > link_expiry:
                return {"success": False, "error": "Lien de récupération expiré"}
            
            # Déterminer la remise à appliquer
            discount_code = None
            discount_percent = 0
            
            if apply_discount:
                # Récupérer le dernier email envoyé pour déterminer la remise
                emails_sent = cart.get("recovery_emails_sent", [])
                if emails_sent:
                    last_email = max(emails_sent, key=lambda x: x["sent_at"])
                    discount_code = last_email["discount_code"]
                    
                    if discount_code == "RETOUR10":
                        discount_percent = 10
                    elif discount_code == "RETOUR15":
                        discount_percent = 15
                    elif discount_code == "RETOUR20":
                        discount_percent = 20
            
            # Préparer les données du panier pour la commande
            cart_data = {
                "items": cart["items"],
                "total_value": cart["total_value"],
                "discount_code": discount_code,
                "discount_percent": discount_percent,
                "discounted_total": round(cart["total_value"] * (1 - discount_percent/100), 2),
                "customer_info": {
                    "email": cart["customer_email"],
                    "name": cart.get("customer_name"),
                    "phone": cart.get("customer_phone"),
                    "address": cart.get("customer_address")
                }
            }
            
            return {
                "success": True,
                "cart_data": cart_data,
                "cart_id": cart["cart_id"]
            }
            
        except Exception as e:
            self.logger.error(f"Error recovering cart by token: {e}")
            return {"success": False, "error": str(e)}
    
    async def mark_cart_recovered(self, cart_id: str, order_id: str) -> Dict[str, Any]:
        """Marquer un panier comme récupéré"""
        try:
            result = await self.db.abandoned_carts.update_one(
                {"cart_id": cart_id},
                {
                    "$set": {
                        "status": "recovered",
                        "recovered_at": datetime.utcnow(),
                        "recovery_order_id": order_id,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            if result.modified_count > 0:
                # Annuler les emails programmés restants
                await self.db.scheduled_emails.update_many(
                    {"cart_id": cart_id, "status": "pending"},
                    {"$set": {"status": "cancelled", "updated_at": datetime.utcnow()}}
                )
                
                self.logger.info(f"Cart {cart_id} marked as recovered with order {order_id}")
                return {"success": True}
            else:
                return {"success": False, "error": "Panier non trouvé"}
                
        except Exception as e:
            self.logger.error(f"Error marking cart as recovered: {e}")
            return {"success": False, "error": str(e)}
    
    async def generate_delivery_note_pdf(self, delivery_data: Dict[str, Any]) -> str:
        """Générer un bon de livraison PDF"""
        try:
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
            styles = getSampleStyleSheet()
            story = []
            
            # Style personnalisé pour le titre
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=18,
                textColor=colors.HexColor('#1E40AF'),
                alignment=TA_CENTER,
                spaceAfter=20
            )
            
            # En-tête du bon de livraison
            story.append(Paragraph("🌊 JOSMOZE.COM", title_style))
            story.append(Paragraph("BON DE LIVRAISON", title_style))
            story.append(Spacer(1, 20))
            
            # Informations du bon de livraison
            delivery_info = [
                ['N° Bon de Livraison:', delivery_data.get('delivery_id', 'BL-XXX')],
                ['Date:', datetime.now().strftime('%d/%m/%Y')],
                ['Commande N°:', delivery_data.get('order_id', 'N/A')],
                ['Méthode de livraison:', delivery_data.get('delivery_method', 'Standard')],
            ]
            
            if delivery_data.get('tracking_number'):
                delivery_info.append(['N° Suivi:', delivery_data['tracking_number']])
            
            info_table = Table(delivery_info, colWidths=[5*cm, 8*cm])
            info_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F3F4F6')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            
            story.append(info_table)
            story.append(Spacer(1, 25))
            
            # Adresse de livraison
            story.append(Paragraph("ADRESSE DE LIVRAISON:", styles['Heading3']))
            
            address = delivery_data.get('delivery_address', {})
            address_text = f"""
            {delivery_data.get('customer_name', '')}<br/>
            {address.get('street', '')}<br/>
            {address.get('postal_code', '')} {address.get('city', '')}<br/>
            {address.get('country', 'France')}
            """
            
            if delivery_data.get('customer_phone'):
                address_text += f"<br/>Tél: {delivery_data['customer_phone']}"
            
            story.append(Paragraph(address_text, styles['Normal']))
            story.append(Spacer(1, 25))
            
            # Articles à livrer
            story.append(Paragraph("ARTICLES À LIVRER:", styles['Heading3']))
            
            items_data = [['Article', 'Quantité', 'Prix unitaire', 'Total']]
            
            total_weight = 0
            for item in delivery_data.get('items', []):
                items_data.append([
                    item.get('name', 'Article'),
                    str(item.get('quantity', 1)),
                    f"{item.get('price', 0)}€",
                    f"{item.get('price', 0) * item.get('quantity', 1)}€"
                ])
                # Estimation du poids (à adapter selon vos produits)
                total_weight += item.get('quantity', 1) * 15  # 15kg par unité estimé
            
            # Ajouter le total
            items_data.append(['', '', 'TOTAL:', f"{sum(item.get('price', 0) * item.get('quantity', 1) for item in delivery_data.get('items', []))}€"])
            
            items_table = Table(items_data, colWidths=[8*cm, 2*cm, 3*cm, 3*cm])
            items_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E40AF')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#F3F4F6')),
                ('FONTNAME', (2, -1), (-1, -1), 'Helvetica-Bold'),
            ]))
            
            story.append(items_table)
            story.append(Spacer(1, 25))
            
            # Informations supplémentaires
            additional_info = f"""
            <b>Informations de transport:</b><br/>
            • Transporteur: {delivery_data.get('carrier', 'Transporteur Standard')}<br/>
            • Poids total estimé: {total_weight} kg<br/>
            """
            
            if delivery_data.get('special_instructions'):
                additional_info += f"• Instructions spéciales: {delivery_data['special_instructions']}<br/>"
            
            additional_info += f"""
            • Livraison prévue: {delivery_data.get('delivery_date', 'À définir')}<br/><br/>
            
            <b>Signature du destinataire:</b><br/><br/>
            Date: ________________   Signature: ________________________________<br/><br/>
            
            <b>Signature du livreur:</b><br/><br/>
            Date: ________________   Signature: ________________________________
            """
            
            story.append(Paragraph(additional_info, styles['Normal']))
            
            # Pied de page
            story.append(Spacer(1, 30))
            footer_text = """
            <font size="8">
            Josmoze.com - Spécialiste des systèmes d'osmose inverse<br/>
            Support client: support@josmoze.com | Service commercial: commercial@josmoze.com
            </font>
            """
            story.append(Paragraph(footer_text, styles['Normal']))
            
            # Construire le PDF
            doc.build(story)
            buffer.seek(0)
            
            # Convertir en base64
            pdf_base64 = base64.b64encode(buffer.read()).decode('utf-8')
            buffer.close()
            
            self.logger.info(f"Delivery note PDF generated for order {delivery_data.get('order_id')}")
            
            return pdf_base64
            
        except Exception as e:
            self.logger.error(f"Error generating delivery note PDF: {e}")
            return None

# Instance globale du service
abandoned_cart_service = AbandonedCartService