"""
Gestionnaire de Paiements Stripe pour Josmoze.com
Implémente le flux de paiement complet selon le cahier des charges
"""

import os
import logging
import asyncio
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from uuid import uuid4

from fastapi import HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from emergentintegrations.payments.stripe.checkout import (
    StripeCheckout, 
    CheckoutSessionResponse, 
    CheckoutStatusResponse, 
    CheckoutSessionRequest
)

# Configuration
STRIPE_API_KEY = os.environ.get("STRIPE_API_KEY")
MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.environ.get("DB_NAME", "josmoze_production")

# Packages de produits Josmoze (prix fixes pour sécurité)
JOSMOZE_PACKAGES = {
    "osmoseur_particulier": {
        "name": "Osmoseur Particulier", 
        "price": 499.0,
        "currency": "eur",
        "description": "Système d'osmose inverse pour particuliers"
    },
    "osmoseur_professionnel": {
        "name": "Osmoseur Professionnel", 
        "price": 899.0,
        "currency": "eur",
        "description": "Système d'osmose inverse haute capacité pour professionnels"
    },
    "fontaine_animaux": {
        "name": "Fontaine à Eau pour Animaux", 
        "price": 49.0,
        "currency": "eur",
        "description": "Fontaine automatique pour animaux domestiques"
    },
    "sac_transport": {
        "name": "Sac de Transport pour Animaux", 
        "price": 29.0,
        "currency": "eur",
        "description": "Sac de transport confortable pour animaux"
    },
    "distributeur_nourriture": {
        "name": "Distributeur de Nourriture Automatique", 
        "price": 39.0,
        "currency": "eur",
        "description": "Distributeur automatique de nourriture pour animaux"
    }
}

class PaymentManager:
    """Gestionnaire de paiements Stripe pour Josmoze"""
    
    def __init__(self):
        self.stripe_api_key = STRIPE_API_KEY
        self.db_client = None
        self.db = None
        self.stripe_checkout = None
        
        if not self.stripe_api_key:
            logging.warning("STRIPE_API_KEY non configurée - paiements désactivés")
    
    async def initialize(self):
        """Initialiser les connexions DB et Stripe"""
        try:
            # Connexion MongoDB
            self.db_client = AsyncIOMotorClient(MONGO_URL)
            self.db = self.db_client[DB_NAME]
            
            # Test connexion
            await self.db_client.admin.command('ping')
            logging.info("✅ PaymentManager: Connexion MongoDB établie")
            
            # Initialiser Stripe si clé disponible
            if self.stripe_api_key:
                # On initialisera stripe_checkout lors de chaque appel avec l'URL dynamique
                logging.info("✅ PaymentManager: Stripe configuré")
            
        except Exception as e:
            logging.error(f"❌ Erreur initialisation PaymentManager: {e}")
            raise
    
    def _get_stripe_checkout(self, host_url: str) -> StripeCheckout:
        """Créer instance StripeCheckout avec URL webhook dynamique"""
        if not self.stripe_api_key:
            raise HTTPException(500, "Stripe non configuré")
        
        webhook_url = f"{host_url}/api/webhook/stripe"
        return StripeCheckout(api_key=self.stripe_api_key, webhook_url=webhook_url)
    
    async def create_checkout_session(
        self,
        package_id: str,
        quantity: int,
        host_url: str,
        customer_info: Dict[str, Any],
        metadata: Optional[Dict[str, str]] = None
    ) -> CheckoutSessionResponse:
        """
        Créer une session de paiement Stripe
        
        Args:
            package_id: ID du package Josmoze (osmoseur_particulier, etc.)
            quantity: Quantité
            host_url: URL du frontend (pour success/cancel URLs)
            customer_info: Informations client
            metadata: Métadonnées additionnelles
        """
        try:
            # Validation package
            if package_id not in JOSMOZE_PACKAGES:
                raise HTTPException(400, f"Package invalide: {package_id}")
            
            package = JOSMOZE_PACKAGES[package_id]
            total_amount = package["price"] * quantity
            
            # Construire URLs dynamiques
            success_url = f"{host_url}/payment-success?session_id={{CHECKOUT_SESSION_ID}}"
            cancel_url = f"{host_url}/payment-cancelled"
            
            # Métadonnées par défaut + custom
            session_metadata = {
                "package_id": package_id,
                "package_name": package["name"],
                "quantity": str(quantity),
                "customer_email": customer_info.get("email", ""),
                "customer_name": customer_info.get("name", ""),
                "source": "josmoze_checkout"
            }
            if metadata:
                session_metadata.update(metadata)
            
            # Créer session Stripe
            stripe_checkout = self._get_stripe_checkout(host_url)
            
            checkout_request = CheckoutSessionRequest(
                amount=total_amount,
                currency=package["currency"],
                success_url=success_url,
                cancel_url=cancel_url,
                metadata=session_metadata
            )
            
            session_response = await stripe_checkout.create_checkout_session(checkout_request)
            
            # Créer transaction dans DB
            transaction_id = str(uuid4())
            transaction_data = {
                "transaction_id": transaction_id,
                "session_id": session_response.session_id,
                "package_id": package_id,
                "package_name": package["name"],
                "amount": total_amount,
                "currency": package["currency"],
                "quantity": quantity,
                "payment_status": "initiated",
                "status": "pending",
                "customer_info": customer_info,
                "metadata": session_metadata,
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc)
            }
            
            await self.db.payment_transactions.insert_one(transaction_data)
            
            logging.info(f"✅ Session paiement créée: {session_response.session_id} - {total_amount}€")
            
            return session_response
            
        except HTTPException:
            raise
        except Exception as e:
            logging.error(f"❌ Erreur création session paiement: {e}")
            raise HTTPException(500, f"Erreur paiement: {str(e)}")
    
    async def get_payment_status(self, session_id: str, host_url: str) -> Dict[str, Any]:
        """
        Vérifier le statut d'un paiement et mettre à jour la DB
        
        Args:
            session_id: ID de la session Stripe
            host_url: URL pour webhook
        """
        try:
            # Récupérer transaction existante
            transaction = await self.db.payment_transactions.find_one({"session_id": session_id})
            if not transaction:
                raise HTTPException(404, "Transaction non trouvée")
            
            # Éviter traitement multiple du même paiement réussi
            if transaction.get("payment_status") == "paid":
                logging.info(f"ℹ️ Paiement déjà traité: {session_id}")
                return {
                    "status": transaction.get("status", "complete"),
                    "payment_status": "paid",
                    "amount_total": int(transaction.get("amount", 0) * 100), # centimes
                    "currency": transaction.get("currency", "eur"),
                    "metadata": transaction.get("metadata", {}),
                    "already_processed": True
                }
            
            # Vérifier statut auprès de Stripe
            stripe_checkout = self._get_stripe_checkout(host_url)
            status_response = await stripe_checkout.get_checkout_status(session_id)
            
            # Mettre à jour transaction si statut changé
            if status_response.payment_status != transaction.get("payment_status"):
                update_data = {
                    "status": status_response.status,
                    "payment_status": status_response.payment_status,
                    "updated_at": datetime.now(timezone.utc)
                }
                
                # Ajouter infos de succès si paiement réussi
                if status_response.payment_status == "paid":
                    update_data["completed_at"] = datetime.now(timezone.utc)
                    update_data["stripe_amount"] = status_response.amount_total
                    update_data["stripe_currency"] = status_response.currency
                
                await self.db.payment_transactions.update_one(
                    {"session_id": session_id},
                    {"$set": update_data}
                )
                
                logging.info(f"✅ Transaction mise à jour: {session_id} - {status_response.payment_status}")
            
            return {
                "status": status_response.status,
                "payment_status": status_response.payment_status,
                "amount_total": status_response.amount_total,
                "currency": status_response.currency,
                "metadata": status_response.metadata
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logging.error(f"❌ Erreur vérification statut paiement: {e}")
            raise HTTPException(500, f"Erreur vérification paiement: {str(e)}")
    
    async def handle_stripe_webhook(self, webhook_body: bytes, stripe_signature: str, host_url: str) -> Dict[str, Any]:
        """
        Traiter les webhooks Stripe
        
        Args:
            webhook_body: Corps de la requête webhook
            stripe_signature: Signature Stripe
            host_url: URL pour webhook
        """
        try:
            stripe_checkout = self._get_stripe_checkout(host_url)
            webhook_response = await stripe_checkout.handle_webhook(webhook_body, stripe_signature)
            
            # Mettre à jour transaction si événement de paiement
            if webhook_response.event_type in ["checkout.session.completed", "payment_intent.succeeded"]:
                transaction = await self.db.payment_transactions.find_one({"session_id": webhook_response.session_id})
                
                if transaction and transaction.get("payment_status") != "paid":
                    update_data = {
                        "payment_status": webhook_response.payment_status,
                        "status": "complete",
                        "webhook_received_at": datetime.now(timezone.utc),
                        "updated_at": datetime.now(timezone.utc)
                    }
                    
                    await self.db.payment_transactions.update_one(
                        {"session_id": webhook_response.session_id},
                        {"$set": update_data}
                    )
                    
                    logging.info(f"✅ Webhook traité: {webhook_response.event_type} - {webhook_response.session_id}")
            
            return {
                "event_type": webhook_response.event_type,
                "event_id": webhook_response.event_id,
                "session_id": webhook_response.session_id,
                "payment_status": webhook_response.payment_status,
                "processed": True
            }
            
        except Exception as e:
            logging.error(f"❌ Erreur traitement webhook: {e}")
            raise HTTPException(500, f"Erreur webhook: {str(e)}")
    
    async def get_packages(self) -> Dict[str, Any]:
        """Retourner la liste des packages disponibles"""
        return {
            "packages": JOSMOZE_PACKAGES,
            "currency": "eur"
        }
    
    async def close(self):
        """Fermer les connexions"""
        if self.db_client:
            self.db_client.close()
            logging.info("✅ PaymentManager: Connexions fermées")

# Instance globale
payment_manager = PaymentManager()

async def get_payment_manager() -> PaymentManager:
    """Obtenir l'instance du gestionnaire de paiements"""
    if payment_manager.db is None:
        await payment_manager.initialize()
    return payment_manager