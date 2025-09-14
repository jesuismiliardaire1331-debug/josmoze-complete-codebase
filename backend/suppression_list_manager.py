"""
Suppression List Manager - Opt-out Guardian GDPR/CNIL
Module complet de gestion des désinscriptions et exclusions
Conformité RGPD pour les campagnes email
"""

import os
import csv
import hmac
import hashlib
import base64
import uuid
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from motor.motor_asyncio import AsyncIOMotorClient
import pandas as pd
from email_validator import validate_email, EmailNotValidError

class SuppressionListManager:
    def __init__(self, db):
        self.db = db
        self.collection = db.suppression_list
        self.gdpr_journal = db.gdpr_journal
        self.secret_key = os.environ.get('UNSUBSCRIBE_SECRET_KEY', 'josmoze_unsubscribe_secret_2024!')
        
    async def create_indexes(self):
        """Créer les index pour optimiser les performances"""
        try:
            # Index unique sur email
            await self.collection.create_index([("email", 1)], unique=True)
            await self.collection.create_index([("reason", 1)])
            await self.collection.create_index([("source", 1)])
            await self.collection.create_index([("unsubscribed_at", -1)])
            
            # Index pour le journal GDPR
            await self.gdpr_journal.create_index([("timestamp", -1)])
            await self.gdpr_journal.create_index([("action_type", 1)])
            await self.gdpr_journal.create_index([("email", 1)])
            
            print("✅ Index suppression_list et gdpr_journal créés")
            
        except Exception as e:
            print(f"⚠️ Erreur lors de la création des index: {e}")
        """Initialiser les collections avec les index appropriés"""
        try:
            # Index unique sur email
            await self.collection.create_index([("email", 1)], unique=True)
            await self.collection.create_index([("reason", 1)])
            await self.collection.create_index([("source", 1)])
            await self.collection.create_index([("unsubscribed_at", -1)])
            
            # Index pour le journal GDPR
            await self.gdpr_journal.create_index([("timestamp", -1)])
            await self.gdpr_journal.create_index([("action_type", 1)])
            await self.gdpr_journal.create_index([("email", 1)])
            
            print("✅ Collections suppression_list et gdpr_journal initialisées")
            
        except Exception as e:
            print(f"⚠️ Erreur lors de l'initialisation des collections: {e}")
    
    async def add_email_to_suppression_list(
        self, 
        email: str, 
        reason: str = "manual", 
        source: str = "crm_manual",
        notes: str = "",
        agent_email: str = "system"
    ) -> Dict[str, Any]:
        """Ajouter un email à la liste de suppression"""
        try:
            # Valider l'email (format seulement pour les tests)
            try:
                validated_email = validate_email(email, check_deliverability=False)
                email = validated_email.email
            except EmailNotValidError as e:
                return {"success": False, "error": f"Format email invalide: {str(e)}"}
            
            # Vérifier si l'email existe déjà
            existing = await self.collection.find_one({"email": email})
            if existing:
                return {"success": False, "error": "Email déjà dans la liste d'exclusion"}
            
            # Créer l'entrée
            suppression_entry = {
                "email": email,
                "reason": reason,
                "unsubscribed_at": datetime.now(timezone.utc),
                "source": source,
                "notes": notes
            }
            
            # Insérer dans la collection
            await self.collection.insert_one(suppression_entry)
            
            # Journaliser l'action GDPR
            await self.log_gdpr_action(
                action_type="add_suppression",
                email=email,
                details=f"Reason: {reason}, Source: {source}",
                agent_email=agent_email
            )
            
            return {
                "success": True, 
                "message": f"Email {email} ajouté à la liste d'exclusion",
                "entry": suppression_entry
            }
            
        except Exception as e:
            return {"success": False, "error": f"Erreur lors de l'ajout: {str(e)}"}
    
    async def remove_email_from_suppression_list(
        self, 
        email: str, 
        agent_email: str = "system"
    ) -> Dict[str, Any]:
        """Retirer un email de la liste de suppression"""
        try:
            result = await self.collection.delete_one({"email": email})
            
            if result.deleted_count > 0:
                # Journaliser l'action GDPR
                await self.log_gdpr_action(
                    action_type="remove_suppression",
                    email=email,
                    details="Removed from suppression list",
                    agent_email=agent_email
                )
                
                return {"success": True, "message": f"Email {email} retiré de la liste d'exclusion"}
            else:
                return {"success": False, "error": "Email non trouvé dans la liste d'exclusion"}
                
        except Exception as e:
            return {"success": False, "error": f"Erreur lors de la suppression: {str(e)}"}
    
    async def is_email_suppressed(self, email: str) -> bool:
        """Vérifier si un email est dans la liste de suppression"""
        try:
            result = await self.collection.find_one({"email": email})
            return result is not None
        except Exception as e:
            print(f"Erreur lors de la vérification de suppression: {e}")
            return False
    
    async def get_suppression_list(
        self, 
        skip: int = 0, 
        limit: int = 100,
        reason_filter: str = None,
        source_filter: str = None,
        search_email: str = None,
        date_from: datetime = None,
        date_to: datetime = None
    ) -> Dict[str, Any]:
        """Récupérer la liste de suppression avec filtres"""
        try:
            # Construire le filtre
            filter_query = {}
            
            if reason_filter:
                filter_query["reason"] = reason_filter
            
            if source_filter:
                filter_query["source"] = source_filter
            
            if search_email:
                filter_query["email"] = {"$regex": search_email, "$options": "i"}
            
            if date_from or date_to:
                date_filter = {}
                if date_from:
                    date_filter["$gte"] = date_from
                if date_to:
                    date_filter["$lte"] = date_to
                filter_query["unsubscribed_at"] = date_filter
            
            # Compter le total
            total_count = await self.collection.count_documents(filter_query)
            
            # Récupérer les documents
            cursor = self.collection.find(filter_query).sort("unsubscribed_at", -1).skip(skip).limit(limit)
            suppression_list = await cursor.to_list(length=None)
            
            # Formater les dates pour JSON et retirer les ObjectId
            for item in suppression_list:
                if '_id' in item:
                    del item['_id']  # Supprimer l'ObjectId MongoDB
                if 'unsubscribed_at' in item:
                    item['unsubscribed_at'] = item['unsubscribed_at'].isoformat()
            
            return {
                "success": True,
                "data": suppression_list,
                "total_count": total_count,
                "page_size": limit,
                "current_page": skip // limit + 1
            }
            
        except Exception as e:
            return {"success": False, "error": f"Erreur lors de la récupération: {str(e)}"}
    
    async def get_suppression_stats(self) -> Dict[str, Any]:
        """Obtenir les statistiques de la liste de suppression"""
        try:
            # Total des suppressions
            total_suppressed = await self.collection.count_documents({})
            
            # Suppressions des 30 derniers jours
            from datetime import timedelta
            thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
            recent_suppressed = await self.collection.count_documents({
                "unsubscribed_at": {"$gte": thirty_days_ago}
            })
            
            # Suppressions par motif
            pipeline = [
                {"$group": {"_id": "$reason", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}}
            ]
            reason_stats = await self.collection.aggregate(pipeline).to_list(length=None)
            
            # Suppressions par source
            pipeline = [
                {"$group": {"_id": "$source", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}}
            ]
            source_stats = await self.collection.aggregate(pipeline).to_list(length=None)
            
            return {
                "success": True,
                "stats": {
                    "total_suppressed": total_suppressed,
                    "recent_suppressed_30d": recent_suppressed,
                    "by_reason": reason_stats,
                    "by_source": source_stats
                }
            }
            
        except Exception as e:
            return {"success": False, "error": f"Erreur lors du calcul des statistiques: {str(e)}"}
    
    async def import_csv_suppression_list(
        self, 
        csv_content: str, 
        agent_email: str = "system"
    ) -> Dict[str, Any]:
        """Importer une liste de suppression depuis un CSV"""
        try:
            # Parser le CSV
            lines = csv_content.strip().split('\n')
            if len(lines) < 2:
                return {"success": False, "error": "CSV vide ou format invalide"}
            
            # Lire l'en-tête
            headers = [h.strip().lower() for h in lines[0].split(',')]
            if 'email' not in headers:
                return {"success": False, "error": "Colonne 'email' obligatoire manquante"}
            
            imported_count = 0
            errors = []
            
            for line_num, line in enumerate(lines[1:], 2):
                try:
                    values = [v.strip() for v in line.split(',')]
                    if len(values) != len(headers):
                        errors.append(f"Ligne {line_num}: Nombre de colonnes incorrect")
                        continue
                    
                    # Créer le dictionnaire des données
                    row_data = dict(zip(headers, values))
                    
                    email = row_data.get('email', '').strip()
                    if not email:
                        errors.append(f"Ligne {line_num}: Email vide")
                        continue
                    
                    reason = row_data.get('reason', 'import_csv')
                    source = row_data.get('source', 'csv_import')
                    notes = row_data.get('notes', f'Imported via CSV by {agent_email}')
                    
                    # Ajouter l'email
                    result = await self.add_email_to_suppression_list(
                        email=email,
                        reason=reason,
                        source=source,
                        notes=notes,
                        agent_email=agent_email
                    )
                    
                    if result["success"]:
                        imported_count += 1
                    else:
                        errors.append(f"Ligne {line_num} ({email}): {result['error']}")
                        
                except Exception as e:
                    errors.append(f"Ligne {line_num}: Erreur de traitement - {str(e)}")
            
            # Journaliser l'import
            await self.log_gdpr_action(
                action_type="csv_import",
                email="",
                details=f"Imported {imported_count} emails, {len(errors)} errors",
                agent_email=agent_email
            )
            
            return {
                "success": True,
                "imported_count": imported_count,
                "errors": errors,
                "message": f"Import terminé: {imported_count} emails ajoutés, {len(errors)} erreurs"
            }
            
        except Exception as e:
            return {"success": False, "error": f"Erreur lors de l'import CSV: {str(e)}"}
    
    async def export_csv_suppression_list(self, agent_email: str = "system") -> Dict[str, Any]:
        """Exporter la liste de suppression en CSV"""
        try:
            # Récupérer toutes les suppressions
            cursor = self.collection.find({}).sort("unsubscribed_at", -1)
            suppression_list = await cursor.to_list(length=None)
            
            if not suppression_list:
                return {"success": False, "error": "Aucune donnée à exporter"}
            
            # Créer le CSV
            csv_content = "email,reason,source,unsubscribed_at,notes\n"
            
            for item in suppression_list:
                email = item.get('email', '')
                reason = item.get('reason', '')
                source = item.get('source', '')
                unsubscribed_at = item.get('unsubscribed_at', '').isoformat() if item.get('unsubscribed_at') else ''
                notes = item.get('notes', '').replace('\n', ' ').replace(',', ';')
                
                csv_content += f'"{email}","{reason}","{source}","{unsubscribed_at}","{notes}"\n'
            
            # Journaliser l'export
            await self.log_gdpr_action(
                action_type="csv_export",
                email="",
                details=f"Exported {len(suppression_list)} suppression records",
                agent_email=agent_email
            )
            
            return {
                "success": True,
                "csv_content": csv_content,
                "record_count": len(suppression_list)
            }
            
        except Exception as e:
            return {"success": False, "error": f"Erreur lors de l'export CSV: {str(e)}"}
    
    def generate_unsubscribe_token(self, email: str) -> str:
        """Générer un token sécurisé pour la désinscription"""
        try:
            # Créer le payload avec timestamp pour expiration optionnelle
            payload = f"{email}:{int(datetime.now(timezone.utc).timestamp())}"
            
            # Créer la signature HMAC
            signature = hmac.new(
                self.secret_key.encode('utf-8'),
                payload.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            
            # Encoder en base64 pour l'URL
            token_data = f"{payload}:{signature}"
            token = base64.urlsafe_b64encode(token_data.encode('utf-8')).decode('utf-8')
            
            return token
            
        except Exception as e:
            print(f"Erreur lors de la génération du token: {e}")
            return ""
    
    def verify_unsubscribe_token(self, token: str) -> Optional[str]:
        """Vérifier et décoder un token de désinscription"""
        try:
            # Décoder le token
            token_data = base64.urlsafe_b64decode(token.encode('utf-8')).decode('utf-8')
            parts = token_data.split(':')
            
            if len(parts) != 3:
                return None
            
            email, timestamp, signature = parts
            payload = f"{email}:{timestamp}"
            
            # Vérifier la signature HMAC
            expected_signature = hmac.new(
                self.secret_key.encode('utf-8'),
                payload.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            
            if not hmac.compare_digest(signature, expected_signature):
                return None
            
            # Optionnel: vérifier l'expiration (ex: 30 jours)
            token_timestamp = int(timestamp)
            current_timestamp = int(datetime.now(timezone.utc).timestamp())
            
            # Token valide pendant 30 jours (2592000 secondes)
            if current_timestamp - token_timestamp > 2592000:
                return None
            
            return email
            
        except Exception as e:
            print(f"Erreur lors de la vérification du token: {e}")
            return None
    
    def build_unsubscribe_link(self, email: str, base_url: str = "https://josmoze.com") -> str:
        """Construire un lien de désinscription sécurisé"""
        token = self.generate_unsubscribe_token(email)
        # Utiliser la route /api/public/unsubscribe qui est correctement routée
        return f"{base_url}/api/public/unsubscribe?token={token}"
    
    async def process_unsubscribe(self, token: str, user_agent: str = "", ip_address: str = "") -> Dict[str, Any]:
        """Traiter une demande de désinscription via token"""
        try:
            # Vérifier et décoder le token
            email = self.verify_unsubscribe_token(token)
            if not email:
                return {"success": False, "error": "Token invalide ou expiré"}
            
            # Ajouter l'email à la liste de suppression
            result = await self.add_email_to_suppression_list(
                email=email,
                reason="unsubscribe",
                source="footer_link",
                notes=f"Unsubscribed via public link. IP: {ip_address}, UA: {user_agent}",
                agent_email="public_unsubscribe"
            )
            
            return {
                "success": True,
                "email": email,
                "message": "Désinscription effectuée avec succès"
            }
            
        except Exception as e:
            return {"success": False, "error": f"Erreur lors de la désinscription: {str(e)}"}
    
    async def log_gdpr_action(
        self, 
        action_type: str, 
        email: str, 
        details: str, 
        agent_email: str = "system"
    ):
        """Journaliser une action GDPR"""
        try:
            journal_entry = {
                "id": str(uuid.uuid4()),
                "timestamp": datetime.now(timezone.utc),
                "action_type": action_type,
                "email": email,
                "details": details,
                "agent_email": agent_email
            }
            
            await self.gdpr_journal.insert_one(journal_entry)
            
        except Exception as e:
            print(f"Erreur lors de l'écriture du journal GDPR: {e}")
    
    async def get_gdpr_journal(
        self, 
        skip: int = 0, 
        limit: int = 100,
        action_type_filter: str = None,
        date_from: datetime = None,
        date_to: datetime = None
    ) -> Dict[str, Any]:
        """Récupérer le journal GDPR"""
        try:
            # Construire le filtre
            filter_query = {}
            
            if action_type_filter:
                filter_query["action_type"] = action_type_filter
            
            if date_from or date_to:
                date_filter = {}
                if date_from:
                    date_filter["$gte"] = date_from
                if date_to:
                    date_filter["$lte"] = date_to
                filter_query["timestamp"] = date_filter
            
            # Compter le total
            total_count = await self.gdpr_journal.count_documents(filter_query)
            
            # Récupérer les documents
            cursor = self.gdpr_journal.find(filter_query).sort("timestamp", -1).skip(skip).limit(limit)
            journal_entries = await cursor.to_list(length=None)
            
            # Formater les dates pour JSON
            for entry in journal_entries:
                if 'timestamp' in entry:
                    entry['timestamp'] = entry['timestamp'].isoformat()
            
            return {
                "success": True,
                "data": journal_entries,
                "total_count": total_count,
                "page_size": limit,
                "current_page": skip // limit + 1
            }
            
        except Exception as e:
            return {"success": False, "error": f"Erreur lors de la récupération du journal: {str(e)}"}
    
    async def check_email_before_send(self, email: str, campaign_id: str = "", agent_email: str = "system") -> Dict[str, Any]:
        """Vérifier un email avant envoi et journaliser si supprimé"""
        try:
            is_suppressed = await self.is_email_suppressed(email)
            
            if is_suppressed:
                # Journaliser l'envoi bloqué
                await self.log_gdpr_action(
                    action_type="skip_send",
                    email=email,
                    details=f"Email skipped (suppressed) for campaign: {campaign_id}",
                    agent_email=agent_email
                )
                
                return {
                    "can_send": False,
                    "reason": "Email in suppression list",
                    "message": "Envoi bloqué - Email dans la liste d'exclusion"
                }
            
            return {
                "can_send": True,
                "reason": "Email not suppressed",
                "message": "Envoi autorisé"
            }
            
        except Exception as e:
            return {
                "can_send": False,
                "reason": "Error checking suppression",
                "message": f"Erreur lors de la vérification: {str(e)}"
            }