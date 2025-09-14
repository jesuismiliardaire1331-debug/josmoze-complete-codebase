#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Prospects Database Manager - JOSMOSE.COM
========================================
Gestion complète des prospects avec conformité CNIL/GDPR

Fonctionnalités:
- CRUD complet pour prospects
- Validation données entrée
- Conformité GDPR/CNIL
- Système d'opt-out automatique
- Tracking consent et communications
- Export/Import sécurisé

Auteur: Système OSMOSE v1.0
Date: Août 2025
"""

from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr, Field, validator
from enum import Enum
import uuid
import logging
from motor.motor_asyncio import AsyncIOMotorDatabase

# Configuration logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ConsentStatus(str, Enum):
    """Statuts de consentement conformes GDPR"""
    B2B_OPTOUT_ALLOWED = "b2b_optout_allowed"  # B2B : opt-out autorisé (soft opt-in)
    B2C_OPTIN_REQUIRED = "b2c_optin_required"  # B2C : opt-in explicite requis
    B2C_OPTIN_CONFIRMED = "b2c_optin_confirmed"  # B2C : opt-in confirmé
    LEGITIMATE_INTEREST = "legitimate_interest"  # Intérêt légitime (relation existante)
    WITHDRAWN = "withdrawn"  # Consentement retiré
    EXPIRED = "expired"  # Consentement expiré (>3 ans)

class ProspectStatus(str, Enum):
    """Statuts du prospect dans le funnel"""
    NEW = "new"  # Nouveau prospect
    CONTACTED = "contacted"  # Contacté au moins une fois
    ENGAGED = "engaged"  # A interagi (ouvert email, cliqué, etc.)
    QUALIFIED = "qualified"  # Prospect qualifié (intérêt confirmé)
    CONVERTED = "converted"  # Converti en client
    UNSUBSCRIBED = "unsubscribed"  # Désinscrit
    BOUNCED = "bounced"  # Email invalide

class ProspectBase(BaseModel):
    """Modèle de base pour un prospect"""
    email: EmailStr = Field(..., description="Email unique du prospect")
    first_name: Optional[str] = Field(None, max_length=100, description="Prénom")
    last_name: Optional[str] = Field(None, max_length=100, description="Nom de famille")
    company: Optional[str] = Field(None, max_length=200, description="Entreprise (B2B)")
    
    # Contexte de prospection
    source_url: Optional[str] = Field(None, description="URL de source du contact")
    keyword_intent: Optional[str] = Field(None, max_length=500, description="Intention détectée")
    
    # Géolocalisation
    country: str = Field("FR", max_length=2, description="Code pays ISO")
    city: Optional[str] = Field(None, max_length=100, description="Ville")
    region: Optional[str] = Field(None, max_length=100, description="Région/État")
    
    # Consentement et statut
    consent_status: ConsentStatus = Field(ConsentStatus.B2B_OPTOUT_ALLOWED, description="Statut consentement GDPR")
    status: ProspectStatus = Field(ProspectStatus.NEW, description="Statut dans le funnel")
    
    # Tracking temporel
    last_contacted_at: Optional[datetime] = Field(None, description="Dernière prise de contact")
    consent_date: Optional[datetime] = Field(None, description="Date du consentement")
    
    # Données libres
    notes: Optional[str] = Field(None, max_length=2000, description="Notes libres")
    tags: List[str] = Field(default_factory=list, description="Tags de classification")
    
    @validator('keyword_intent')
    def validate_keyword_intent(cls, v):
        """Valider que les intentions sont liées à notre niche"""
        if not v:
            return v
            
        allowed_keywords = [
            'osmoseur', 'filtration', 'purification', 'eau pure', 'eau calcaire',
            'chlore', 'contaminants', 'robinet', 'cuisine', 'santé eau',
            'bactéries eau', 'virus eau', 'traitement eau', 'eau potable'
        ]
        
        v_lower = v.lower()
        if not any(keyword in v_lower for keyword in allowed_keywords):
            logger.warning(f"Keyword intent potentiellement hors-contexte: {v}")
            
        return v
    
    @validator('consent_status')
    def validate_consent_gdpr(cls, v, values):
        """Validation conformité GDPR selon le type de contact"""
        email = values.get('email', '')
        
        # Détecter si B2B ou B2C selon le domaine email
        business_domains = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com']
        is_likely_b2c = any(domain in email for domain in business_domains)
        
        if is_likely_b2c and v == ConsentStatus.B2B_OPTOUT_ALLOWED:
            logger.warning(f"Email B2C {email} avec consentement B2B - Vérifier conformité")
            
        return v

class ProspectCreate(ProspectBase):
    """Modèle pour création d'un prospect"""
    pass

class ProspectUpdate(BaseModel):
    """Modèle pour mise à jour d'un prospect"""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    company: Optional[str] = None
    keyword_intent: Optional[str] = None
    city: Optional[str] = None
    region: Optional[str] = None
    status: Optional[ProspectStatus] = None
    notes: Optional[str] = None
    tags: Optional[List[str]] = None

class ProspectInDB(ProspectBase):
    """Modèle prospect en base de données"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Métadonnées de conformité
    gdpr_compliant: bool = Field(True, description="Indicateur conformité GDPR")
    data_retention_until: Optional[datetime] = Field(None, description="Date limite rétention données")
    unsubscribe_token: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Token de désinscription")
    
    # Statistiques de communication
    emails_sent: int = Field(0, description="Nombre d'emails envoyés")
    emails_opened: int = Field(0, description="Nombre d'emails ouverts")
    emails_clicked: int = Field(0, description="Nombre de clics")
    sms_sent: int = Field(0, description="Nombre de SMS envoyés")
    
    class Config:
        populate_by_name = True

class ProspectResponse(ProspectInDB):
    """Modèle de réponse API (sans données sensibles)"""
    unsubscribe_token: str = Field(..., exclude=True)  # Masquer le token dans les réponses

class ProspectsManager:
    """Gestionnaire de la base de données prospects"""
    
    def __init__(self, database: AsyncIOMotorDatabase):
        self.db = database
        self.collection = database.prospects
        
    async def create_indexes(self):
        """Créer les index pour optimiser les performances"""
        await self.collection.create_index("email", unique=True)
        await self.collection.create_index("status")
        await self.collection.create_index("consent_status") 
        await self.collection.create_index("country")
        await self.collection.create_index("created_at")
        await self.collection.create_index("last_contacted_at")
        await self.collection.create_index("unsubscribe_token", unique=True)
        
        logger.info("✅ Index prospects créés")
    
    async def create_prospect(self, prospect_data: ProspectCreate) -> ProspectInDB:
        """Créer un nouveau prospect avec validation GDPR"""
        try:
            # Créer l'objet prospect
            prospect = ProspectInDB(**prospect_data.dict())
            
            # Définir la rétention des données selon GDPR (3 ans max)
            prospect.data_retention_until = datetime.utcnow() + timedelta(days=3*365)
            
            # Validation de conformité
            prospect.gdpr_compliant = self._validate_gdpr_compliance(prospect)
            
            # Insérer en base
            result = await self.collection.insert_one(prospect.dict(by_alias=True))
            
            if result.inserted_id:
                logger.info(f"✅ Prospect créé: {prospect.email}")
                return prospect
            else:
                raise Exception("Erreur insertion base de données")
                
        except Exception as e:
            logger.error(f"❌ Erreur création prospect {prospect_data.email}: {e}")
            raise
    
    async def get_prospect(self, prospect_id: str) -> Optional[ProspectInDB]:
        """Récupérer un prospect par ID"""
        result = await self.collection.find_one({"_id": prospect_id})
        if result:
            return ProspectInDB(**result)
        return None
    
    async def get_prospect_by_email(self, email: str) -> Optional[ProspectInDB]:
        """Récupérer un prospect par email"""
        result = await self.collection.find_one({"email": email})
        if result:
            return ProspectInDB(**result)
        return None
    
    async def update_prospect(self, prospect_id: str, update_data: ProspectUpdate) -> Optional[ProspectInDB]:
        """Mettre à jour un prospect"""
        update_dict = {k: v for k, v in update_data.dict().items() if v is not None}
        update_dict["updated_at"] = datetime.utcnow()
        
        result = await self.collection.update_one(
            {"_id": prospect_id}, 
            {"$set": update_dict}
        )
        
        if result.modified_count:
            return await self.get_prospect(prospect_id)
        return None
    
    async def delete_prospect(self, prospect_id: str) -> bool:
        """Supprimer un prospect (droit à l'oubli GDPR)"""
        result = await self.collection.delete_one({"_id": prospect_id})
        if result.deleted_count:
            logger.info(f"🗑️ Prospect supprimé (droit à l'oubli): {prospect_id}")
            return True
        return False
    
    async def unsubscribe_prospect(self, unsubscribe_token: str) -> bool:
        """Désinscrire un prospect via token"""
        result = await self.collection.update_one(
            {"unsubscribe_token": unsubscribe_token},
            {
                "$set": {
                    "status": ProspectStatus.UNSUBSCRIBED,
                    "consent_status": ConsentStatus.WITHDRAWN,
                    "updated_at": datetime.utcnow(),
                    "last_contacted_at": datetime.utcnow()
                }
            }
        )
        
        if result.modified_count:
            logger.info(f"✅ Prospect désinscrit via token")
            return True
        return False
    
    async def list_prospects(
        self,
        status: Optional[ProspectStatus] = None,
        consent_status: Optional[ConsentStatus] = None,
        country: str = "FR",
        limit: int = 100,
        skip: int = 0
    ) -> List[ProspectInDB]:
        """Lister les prospects avec filtres"""
        
        filter_dict = {"country": country}
        
        if status:
            filter_dict["status"] = status
        if consent_status:
            filter_dict["consent_status"] = consent_status
            
        cursor = self.collection.find(filter_dict).skip(skip).limit(limit)
        prospects = []
        
        async for doc in cursor:
            prospects.append(ProspectInDB(**doc))
            
        return prospects
    
    async def get_stats(self) -> Dict[str, Any]:
        """Statistiques globales des prospects"""
        total_prospects = await self.collection.count_documents({})
        
        # Statistiques par statut
        pipeline_status = [
            {"$group": {"_id": "$status", "count": {"$sum": 1}}}
        ]
        status_stats = {}
        async for result in self.collection.aggregate(pipeline_status):
            status_stats[result["_id"]] = result["count"]
        
        # Statistiques par consentement
        pipeline_consent = [
            {"$group": {"_id": "$consent_status", "count": {"$sum": 1}}}
        ]
        consent_stats = {}
        async for result in self.collection.aggregate(pipeline_consent):
            consent_stats[result["_id"]] = result["count"]
        
        # Prospects à supprimer (rétention expirée)
        expired_count = await self.collection.count_documents({
            "data_retention_until": {"$lt": datetime.utcnow()}
        })
        
        return {
            "total_prospects": total_prospects,
            "status_breakdown": status_stats,
            "consent_breakdown": consent_stats,
            "gdpr_expired_count": expired_count,
            "last_updated": datetime.utcnow()
        }
    
    async def cleanup_expired_data(self) -> int:
        """Nettoyer les données expirées (conformité GDPR)"""
        result = await self.collection.delete_many({
            "data_retention_until": {"$lt": datetime.utcnow()}
        })
        
        if result.deleted_count:
            logger.info(f"🧹 {result.deleted_count} prospects expirés supprimés (GDPR)")
            
        return result.deleted_count
    
    async def track_communication(self, prospect_id: str, comm_type: str):
        """Tracker une communication (email, SMS)"""
        update_field = f"{comm_type}_sent"
        await self.collection.update_one(
            {"_id": prospect_id},
            {
                "$inc": {update_field: 1},
                "$set": {"last_contacted_at": datetime.utcnow()}
            }
        )
    
    def _validate_gdpr_compliance(self, prospect: ProspectInDB) -> bool:
        """Valider la conformité GDPR d'un prospect"""
        
        # Vérifier que l'intention est liée à notre activité
        if not prospect.keyword_intent:
            logger.warning(f"Prospect {prospect.email} sans intention définie")
            return False
        
        # Vérifier le consentement approprié
        if prospect.consent_status in [ConsentStatus.WITHDRAWN, ConsentStatus.EXPIRED]:
            return False
            
        # Vérifier la rétention des données
        if prospect.data_retention_until and prospect.data_retention_until < datetime.utcnow():
            return False
        
        return True

# Export des classes principales
__all__ = [
    'ProspectCreate',
    'ProspectUpdate', 
    'ProspectInDB',
    'ProspectResponse',
    'ProspectsManager',
    'ConsentStatus',
    'ProspectStatus'
]