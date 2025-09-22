"""
CRM-related API endpoints
Extracted from monolithic server.py for better organization
"""
from fastapi import APIRouter, HTTPException, Request, Depends
from typing import List, Optional, Dict, Any
import logging
import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime

router = APIRouter(prefix="/crm", tags=["crm"])

MONGO_URL = os.environ.get("MONGO_URI", os.environ.get("MONGO_URL", "mongodb://localhost:27017"))
DB_NAME = os.environ.get("DB_NAME", "josmoze_production")

async def get_database():
    """Get database connection"""
    client = AsyncIOMotorClient(MONGO_URL)
    return client[DB_NAME]

@router.get("/leads")
async def get_leads():
    """Get all leads for CRM dashboard"""
    try:
        return {
            "leads": [],
            "message": "CRM leads endpoint - implementation pending refactor"
        }
    except Exception as e:
        logging.error(f"Error getting leads: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/leads")
async def create_lead(lead_data: dict):
    """Create new lead"""
    try:
        return {
            "message": "Create lead endpoint - implementation pending refactor",
            "lead_data": lead_data
        }
    except Exception as e:
        logging.error(f"Error creating lead: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/leads/{lead_id}")
async def update_lead(lead_id: str, lead_data: dict):
    """Update existing lead"""
    try:
        return {
            "message": "Update lead endpoint - implementation pending refactor",
            "lead_id": lead_id,
            "lead_data": lead_data
        }
    except Exception as e:
        logging.error(f"Error updating lead: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dashboard")
async def get_crm_dashboard():
    """Get CRM dashboard data"""
    try:
        return {
            "dashboard": {},
            "message": "CRM dashboard endpoint - implementation pending refactor"
        }
    except Exception as e:
        logging.error(f"Error getting dashboard: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/orders")
async def get_orders():
    """Get all orders"""
    try:
        return {
            "orders": [],
            "message": "CRM orders endpoint - implementation pending refactor"
        }
    except Exception as e:
        logging.error(f"Error getting orders: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/contact-forms")
async def get_contact_forms():
    """Get all contact form submissions"""
    try:
        return {
            "contact_forms": [],
            "message": "Contact forms endpoint - implementation pending refactor"
        }
    except Exception as e:
        logging.error(f"Error getting contact forms: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/admin/populate-blog")
async def populate_blog_articles():
    """Admin endpoint to populate blog articles"""
    try:
        import sys
        sys.path.append('.')
        
        TOUS_LES_ARTICLES = [
            {
                "title": "Pourquoi l'eau du robinet peut être dangereuse pour votre santé",
                "slug": "pourquoi-l-eau-du-robinet-peut-etre-dangereuse-pour-votre-sante",
                "excerpt": "Découvrez les risques cachés de l'eau du robinet : chlore, métaux lourds, pesticides et micro-organismes qui menacent votre santé au quotidien.",
                "category": "Santé",
                "content": "L'eau du robinet, bien qu'elle soit traitée et considérée comme potable dans la plupart des pays développés, peut contenir des substances potentiellement dangereuses pour votre santé...",
                "image": "/images/blog/eau-robinet-danger.jpg",
                "author": "Dr. Marie Dubois",
                "published_date": datetime(2024, 1, 15),
                "tags": ["santé", "eau", "pollution", "prévention"],
                "reading_time": 8,
                "featured": True,
                "related_products": ["osmoseur-essentiel", "osmoseur-premium"]
            },
            {
                "title": "Les 7 signes que votre eau est contaminée",
                "slug": "les-7-signes-que-votre-eau-est-contaminee",
                "excerpt": "Apprenez à identifier les signaux d'alarme qui indiquent que votre eau de consommation pourrait être contaminée et nécessiter une filtration.",
                "category": "Prévention",
                "content": "Votre eau a-t-elle un goût étrange ? Une odeur particulière ? Ces signes peuvent indiquer une contamination...",
                "image": "/images/blog/signes-eau-contaminee.jpg",
                "author": "Thomas Martin",
                "published_date": datetime(2024, 1, 22),
                "tags": ["contamination", "détection", "qualité eau"],
                "reading_time": 6,
                "featured": False,
                "related_products": ["purificateur-portable-hydrogene"]
            },
            {
                "title": "Osmose inverse vs filtration classique : le guide complet",
                "slug": "osmose-inverse-vs-filtration-classique-guide-complet",
                "excerpt": "Comparaison détaillée entre les systèmes d'osmose inverse et la filtration traditionnelle pour vous aider à faire le bon choix.",
                "category": "Technologie",
                "content": "Choisir le bon système de filtration d'eau peut sembler complexe. Voici un guide complet pour comprendre les différences...",
                "image": "/images/blog/osmose-vs-filtration.jpg",
                "author": "Ingénieur Paul Leclerc",
                "published_date": datetime(2024, 2, 5),
                "tags": ["osmose inverse", "filtration", "comparaison", "technologie"],
                "reading_time": 12,
                "featured": True,
                "related_products": ["osmoseur-premium", "osmoseur-prestige"]
            },
            {
                "title": "Comment installer votre système d'osmose inverse en 30 minutes",
                "slug": "comment-installer-systeme-osmose-inverse-30-minutes",
                "excerpt": "Guide d'installation étape par étape pour installer facilement votre système d'osmose inverse sans faire appel à un plombier.",
                "category": "Installation",
                "content": "L'installation d'un système d'osmose inverse peut sembler intimidante, mais avec ce guide détaillé...",
                "image": "/images/blog/installation-osmose.jpg",
                "author": "Marc Dubois",
                "published_date": datetime(2024, 2, 12),
                "tags": ["installation", "DIY", "tutoriel"],
                "reading_time": 10,
                "featured": False,
                "related_products": ["osmoseur-essentiel"]
            },
            {
                "title": "L'eau hydrogénée : révolution ou simple tendance ?",
                "slug": "eau-hydrogenee-revolution-ou-simple-tendance",
                "excerpt": "Analyse scientifique des bienfaits supposés de l'eau hydrogénée et de son impact réel sur la santé humaine.",
                "category": "Science",
                "content": "L'eau hydrogénée fait beaucoup parler d'elle ces dernières années. Mais que dit vraiment la science ?",
                "image": "/images/blog/eau-hydrogenee.jpg",
                "author": "Dr. Sophie Laurent",
                "published_date": datetime(2024, 2, 20),
                "tags": ["hydrogène", "science", "santé", "innovation"],
                "reading_time": 9,
                "featured": True,
                "related_products": ["purificateur-portable-hydrogene"]
            },
            {
                "title": "Économisez 1200€ par an en arrêtant l'eau en bouteille",
                "slug": "economisez-1200-euros-par-an-arretant-eau-bouteille",
                "excerpt": "Calcul détaillé des économies réalisables en passant de l'eau en bouteille à un système de filtration domestique.",
                "category": "Économie",
                "content": "Saviez-vous qu'une famille française moyenne dépense plus de 1200€ par an en eau en bouteille ?",
                "image": "/images/blog/economies-eau-bouteille.jpg",
                "author": "Économiste Julie Moreau",
                "published_date": datetime(2024, 3, 1),
                "tags": ["économies", "budget", "écologie"],
                "reading_time": 7,
                "featured": False,
                "related_products": ["osmoseur-premium", "fontaine-eau-animaux"]
            },
            {
                "title": "Maintenance de votre osmoseur : le guide annuel",
                "slug": "maintenance-osmoseur-guide-annuel",
                "excerpt": "Calendrier de maintenance et conseils d'entretien pour optimiser la durée de vie et l'efficacité de votre système d'osmose inverse.",
                "category": "Maintenance",
                "content": "Un système d'osmose inverse bien entretenu peut durer plus de 10 ans. Voici comment en prendre soin...",
                "image": "/images/blog/maintenance-osmoseur.jpg",
                "author": "Technicien Expert Jean Dupont",
                "published_date": datetime(2024, 3, 10),
                "tags": ["maintenance", "entretien", "durabilité"],
                "reading_time": 11,
                "featured": False,
                "related_products": ["filtres-rechange", "filtres-pro"]
            },
            {
                "title": "Eau pour animaux : pourquoi la qualité compte",
                "slug": "eau-pour-animaux-pourquoi-qualite-compte",
                "excerpt": "L'importance de fournir une eau pure à vos animaux de compagnie et l'impact sur leur santé et leur bien-être.",
                "category": "Animaux",
                "content": "Nos animaux de compagnie méritent la même qualité d'eau que nous. Découvrez pourquoi c'est crucial...",
                "image": "/images/blog/eau-animaux.jpg",
                "author": "Vétérinaire Dr. Claire Rousseau",
                "published_date": datetime(2024, 3, 18),
                "tags": ["animaux", "santé animale", "qualité eau"],
                "reading_time": 6,
                "featured": False,
                "related_products": ["fontaine-eau-animaux"]
            },
            {
                "title": "Impact environnemental : osmose inverse vs eau en bouteille",
                "slug": "impact-environnemental-osmose-inverse-vs-eau-bouteille",
                "excerpt": "Analyse comparative de l'empreinte carbone et de l'impact écologique entre les systèmes de filtration et l'eau embouteillée.",
                "category": "Écologie",
                "content": "Dans un monde où l'écologie devient prioritaire, quel est le choix le plus responsable pour notre consommation d'eau ?",
                "image": "/images/blog/impact-environnemental.jpg",
                "author": "Écologiste Pierre Vert",
                "published_date": datetime(2024, 3, 25),
                "tags": ["écologie", "environnement", "durabilité"],
                "reading_time": 8,
                "featured": True,
                "related_products": ["osmoseur-prestige", "osmoseur-pro"]
            }
        ]
        
        db = await get_database()
        
        await db.blog_articles.delete_many({})
        
        if TOUS_LES_ARTICLES:
            result = await db.blog_articles.insert_many(TOUS_LES_ARTICLES)
            inserted_count = len(result.inserted_ids)
        else:
            inserted_count = 0
        
        return {
            "success": True,
            "message": f"Successfully populated {inserted_count} blog articles",
            "inserted_count": inserted_count
        }
    except Exception as e:
        logging.error(f"Error populating blog articles: {e}")
        raise HTTPException(status_code=500, detail=str(e))
