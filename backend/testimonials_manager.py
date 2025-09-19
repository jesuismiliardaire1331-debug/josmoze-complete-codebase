"""
⭐ GESTIONNAIRE TÉMOIGNAGES - JOSMOZE.COM
Système d'avis clients avec notation 5 étoiles et modération
"""

import os
import uuid
import logging
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from enum import Enum

from fastapi import HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field, validator

# Configuration
MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.environ.get("DB_NAME", "josmoze_production")

class TestimonialStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class CustomerTestimonial(BaseModel):
    """Modèle de témoignage client"""
    id: Optional[str] = None
    customer_name: str = Field(..., min_length=2, max_length=100)
    customer_email: str = Field(..., pattern=r'^[^@]+@[^@]+\.[^@]+$')
    customer_city: Optional[str] = Field(None, max_length=100)
    product_id: str = Field(..., min_length=1)
    product_name: Optional[str] = None
    rating: int = Field(..., ge=1, le=5)
    title: str = Field(..., min_length=5, max_length=150)
    content: str = Field(..., min_length=10, max_length=2000)
    pros: List[str] = Field(default=[])
    cons: List[str] = Field(default=[])
    purchase_date: Optional[datetime] = None
    usage_duration: Optional[str] = None  # "6 mois", "1 an", etc.
    would_recommend: bool = Field(default=True)
    installation_photo: Optional[str] = None
    status: TestimonialStatus = Field(default=TestimonialStatus.PENDING)
    admin_notes: Optional[str] = None
    created_date: Optional[datetime] = None
    approved_date: Optional[datetime] = None
    helpful_votes: int = Field(default=0)
    total_votes: int = Field(default=0)

class TestimonialsManager:
    def __init__(self):
        self.client = None
        self.db = None
        
    async def initialize(self):
        """Initialiser la connexion MongoDB"""
        if not self.client:
            self.client = AsyncIOMotorClient(MONGO_URL)
            self.db = self.client[DB_NAME]
            
    async def submit_testimonial(self, testimonial_data: CustomerTestimonial) -> dict:
        """
        ⭐ Soumettre un nouveau témoignage client
        
        Args:
            testimonial_data: Données du témoignage
            
        Returns:
            Dict avec informations du témoignage créé
        """
        await self.initialize()
        
        # Générer ID unique
        testimonial_data.id = str(uuid.uuid4())
        testimonial_data.created_date = datetime.now(timezone.utc)
        
        # Récupérer nom du produit si pas fourni
        if not testimonial_data.product_name:
            product = await self.db.products.find_one({"id": testimonial_data.product_id})
            if product:
                testimonial_data.product_name = product.get("name", "Produit Josmoze")
        
        # Sauvegarde
        await self.db.testimonials.insert_one(testimonial_data.dict())
        
        logging.info(f"✅ Témoignage soumis: {testimonial_data.customer_name} - {testimonial_data.rating}⭐")
        
        return {
            "success": True,
            "testimonial_id": testimonial_data.id,
            "message": "Témoignage soumis avec succès ! Il sera publié après modération."
        }
        
    async def get_testimonials(
        self, 
        status: Optional[TestimonialStatus] = TestimonialStatus.APPROVED,
        product_id: Optional[str] = None,
        limit: int = 10,
        skip: int = 0,
        min_rating: Optional[int] = None
    ) -> List[dict]:
        """⭐ Récupérer liste des témoignages"""
        await self.initialize()
        
        query = {}
        if status:
            query["status"] = status
        if product_id:
            query["product_id"] = product_id
        if min_rating:
            query["rating"] = {"$gte": min_rating}
            
        cursor = self.db.testimonials.find(query).sort("approved_date", -1).skip(skip).limit(limit)
        testimonials = await cursor.to_list(length=None)
        
        return testimonials
        
    async def get_testimonial_stats(self, product_id: Optional[str] = None) -> dict:
        """📊 Statistiques des témoignages"""
        await self.initialize()
        
        match_stage = {"status": "approved"}
        if product_id:
            match_stage["product_id"] = product_id
            
        pipeline = [
            {"$match": match_stage},
            {"$group": {
                "_id": None,
                "total_reviews": {"$sum": 1},
                "average_rating": {"$avg": "$rating"},
                "rating_distribution": {
                    "$push": {
                        "$switch": {
                            "branches": [
                                {"case": {"$eq": ["$rating", 5]}, "then": "5_stars"},
                                {"case": {"$eq": ["$rating", 4]}, "then": "4_stars"},
                                {"case": {"$eq": ["$rating", 3]}, "then": "3_stars"},
                                {"case": {"$eq": ["$rating", 2]}, "then": "2_stars"},
                                {"case": {"$eq": ["$rating", 1]}, "then": "1_star"}
                            ],
                            "default": "unknown"
                        }
                    }
                }
            }}
        ]
        
        cursor = self.db.testimonials.aggregate(pipeline)
        results = await cursor.to_list(length=None)
        
        if not results:
            return {
                "total_reviews": 0,
                "average_rating": 0,
                "rating_distribution": {"5": 0, "4": 0, "3": 0, "2": 0, "1": 0}
            }
            
        stats = results[0]
        
        # Calculer distribution des notes
        distribution = {"5": 0, "4": 0, "3": 0, "2": 0, "1": 0}
        for rating in stats.get("rating_distribution", []):
            if rating == "5_stars":
                distribution["5"] += 1
            elif rating == "4_stars":
                distribution["4"] += 1
            elif rating == "3_stars":
                distribution["3"] += 1
            elif rating == "2_stars":
                distribution["2"] += 1
            elif rating == "1_star":
                distribution["1"] += 1
                
        return {
            "total_reviews": stats.get("total_reviews", 0),
            "average_rating": round(stats.get("average_rating", 0), 1),
            "rating_distribution": distribution
        }
        
    async def moderate_testimonial(self, testimonial_id: str, action: TestimonialStatus, admin_notes: Optional[str] = None) -> dict:
        """🛡️ Modérer un témoignage (admin)"""
        await self.initialize()
        
        update_data = {
            "status": action,
            "admin_notes": admin_notes
        }
        
        if action == TestimonialStatus.APPROVED:
            update_data["approved_date"] = datetime.now(timezone.utc)
            
        result = await self.db.testimonials.update_one(
            {"id": testimonial_id},
            {"$set": update_data}
        )
        
        if result.modified_count == 0:
            raise HTTPException(404, "Témoignage non trouvé")
            
        return {"success": True, "message": f"Témoignage {action}"}
        
    async def vote_helpful(self, testimonial_id: str, helpful: bool = True) -> dict:
        """👍 Voter pour l'utilité d'un témoignage"""
        await self.initialize()
        
        increment = {"total_votes": 1}
        if helpful:
            increment["helpful_votes"] = 1
            
        result = await self.db.testimonials.update_one(
            {"id": testimonial_id, "status": "approved"},
            {"$inc": increment}
        )
        
        if result.modified_count == 0:
            raise HTTPException(404, "Témoignage non trouvé ou non approuvé")
            
        return {"success": True, "message": "Vote enregistré"}
        
    async def get_featured_testimonials(self) -> List[dict]:
        """🌟 Témoignages vedettes (pour homepage)"""
        await self.initialize()
        
        # Récupérer les meilleurs témoignages (5 étoiles, plus de votes positifs)
        pipeline = [
            {"$match": {"status": "approved", "rating": 5}},
            {"$addFields": {
                "helpfulness_ratio": {
                    "$cond": {
                        "if": {"$gt": ["$total_votes", 0]},
                        "then": {"$divide": ["$helpful_votes", "$total_votes"]},
                        "else": 0
                    }
                }
            }},
            {"$sort": {"helpfulness_ratio": -1, "helpful_votes": -1}},
            {"$limit": 6}
        ]
        
        cursor = self.db.testimonials.aggregate(pipeline)
        testimonials = await cursor.to_list(length=None)
        
        return testimonials

# Témoignages par défaut pour la démo
DEFAULT_TESTIMONIALS = [
    {
        "customer_name": "Marie Dubois",
        "customer_email": "marie.dubois@example.com",
        "customer_city": "Lyon",
        "product_id": "osmoseur-premium",
        "product_name": "Osmoseur Premium - BlueMountain Avancé",
        "rating": 5,
        "title": "Une eau parfaitement pure, enfin !",
        "content": "Après 8 mois d'utilisation, je ne peux que recommander cet osmoseur. L'eau a un goût incroyable, mes enfants boivent enfin de l'eau avec plaisir ! L'installation a été rapide et le service client est excellent. Plus besoin d'acheter des packs d'eau, c'est un vrai soulagement pour le dos et le portefeuille.",
        "pros": ["Goût excellent", "Installation rapide", "Économies importantes", "Service client réactif"],
        "cons": ["Un peu encombrant sous l'évier"],
        "usage_duration": "8 mois",
        "would_recommend": True,
        "status": "approved",
        "helpful_votes": 24,
        "total_votes": 27
    },
    {
        "customer_name": "Jean-Pierre Martin",
        "customer_email": "jp.martin@example.com", 
        "customer_city": "Marseille",
        "product_id": "osmoseur-essentiel",
        "product_name": "Osmoseur Essentiel - BlueMountain Compact",
        "rating": 5,
        "title": "Parfait pour notre famille de 4 !",
        "content": "L'eau de Marseille étant très calcaire, nous cherchions une solution efficace. Cet osmoseur a dépassé nos attentes ! Plus de traces blanches sur les verres, l'eau est délicieuse et nos appareils électroménagers nous remercient. Le rapport qualité-prix est imbattable.",
        "pros": ["Eau sans calcaire", "Prix abordable", "Facile d'entretien", "Résultats immédiats"],
        "cons": [],
        "usage_duration": "1 an",
        "would_recommend": True,
        "status": "approved",
        "helpful_votes": 31,
        "total_votes": 33
    },
    {
        "customer_name": "Sophie Leroy",
        "customer_email": "sophie.leroy@example.com",
        "customer_city": "Nantes", 
        "product_id": "osmoseur-prestige",
        "product_name": "Osmoseur Prestige - BlueMountain De Comptoir",
        "rating": 5,
        "title": "Le top du top pour notre bébé",
        "content": "Avec l'arrivée de notre premier enfant, nous voulions le meilleur pour sa santé. Cet osmoseur haut de gamme nous donne une tranquillité d'esprit totale. L'écran tactile est très pratique, la qualité de filtration est exceptionnelle. Notre bébé grandit sereinement avec une eau 100% pure.",
        "pros": ["Qualité exceptionnelle", "Écran tactile moderne", "Tranquillité d'esprit", "Parfait pour bébé"],
        "cons": ["Prix élevé mais justifié"],
        "usage_duration": "6 mois",
        "would_recommend": True,
        "status": "approved",
        "helpful_votes": 18,
        "total_votes": 19
    },
    {
        "customer_name": "Claude Moreau",
        "customer_email": "claude.moreau@example.com",
        "customer_city": "Toulouse",
        "product_id": "purificateur-portable-hydrogene",
        "product_name": "Purificateur Portable à Hydrogène H2-Pro",
        "rating": 4,
        "title": "Pratique et efficace en déplacement",
        "content": "Je voyage beaucoup pour le travail et cette bouteille purificatrice est devenue indispensable. L'eau du robinet des hôtels est transformée en eau pure en quelques minutes. Compact, élégant et très efficace. Petit bémol sur l'autonomie de la batterie qui pourrait être meilleure.",
        "pros": ["Ultra portable", "Design élégant", "Efficacité prouvée", "Parfait en voyage"],
        "cons": ["Autonomie batterie limitée"],
        "usage_duration": "4 mois",
        "would_recommend": True,
        "status": "approved",
        "helpful_votes": 12,
        "total_votes": 15
    },
    {
        "customer_name": "Isabelle Petit",
        "customer_email": "isabelle.petit@example.com",
        "customer_city": "Bordeaux",
        "product_id": "fontaine-eau-animaux", 
        "product_name": "Fontaine à Eau pour Animaux AquaPet Premium",
        "rating": 5,
        "title": "Mes chats adorent leur nouvelle fontaine !",
        "content": "Mes deux chats boudaient leur gamelle d'eau. Depuis l'installation de cette fontaine, ils boivent beaucoup plus ! L'eau est toujours fraîche et filtrée. La fontaine est silencieuse et très facile à nettoyer. Un excellent investissement pour la santé de nos compagnons.",
        "pros": ["Chats boivent plus", "Eau toujours fraîche", "Très silencieuse", "Facile à nettoyer"],
        "cons": [],
        "usage_duration": "3 mois",
        "would_recommend": True,
        "status": "approved",
        "helpful_votes": 9,
        "total_votes": 10
    }
]

# Instance globale
testimonials_manager = TestimonialsManager()

async def get_testimonials_manager():
    """Factory pour récupérer le gestionnaire de témoignages"""
    return testimonials_manager

async def initialize_default_testimonials():
    """Initialiser les témoignages par défaut"""
    manager = await get_testimonials_manager()
    await manager.initialize()
    
    for testimonial_data in DEFAULT_TESTIMONIALS:
        # Vérifier si le témoignage existe déjà
        existing = await manager.db.testimonials.find_one({
            "customer_email": testimonial_data["customer_email"],
            "product_id": testimonial_data["product_id"]
        })
        
        if not existing:
            testimonial = CustomerTestimonial(**testimonial_data)
            testimonial.id = str(uuid.uuid4())
            testimonial.created_date = datetime.now(timezone.utc)
            testimonial.approved_date = datetime.now(timezone.utc)
            
            await manager.db.testimonials.insert_one(testimonial.dict())
            logging.info(f"✅ Témoignage par défaut créé: {testimonial.customer_name} - {testimonial.rating}⭐")