"""
Josmose.com - Social Media Marketing Automation System
Système d'automatisation marketing Facebook, Instagram, TikTok
Génération automatique de contenu, campagnes et leads
"""

import os
import uuid
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from motor.motor_asyncio import AsyncIOMotorDatabase
import httpx
import json
import base64
from io import BytesIO

# Configuration pour tests sans API keys
DEMO_MODE = True  # Changera à False quand les vraies clés seront disponibles

# ========== MODELS ==========

class SocialMediaAccount(BaseModel):
    """Modèle pour gérer les comptes de réseaux sociaux"""
    platform: str  # facebook, instagram, tiktok
    account_id: str
    account_name: str
    access_token: Optional[str] = None
    account_type: str = "business"  # business, personal
    status: str = "active"  # active, inactive, suspended
    country_target: str = "FR"  # FR, ES, EU
    language: str = "fr"  # fr, es, en
    daily_budget: float = 10.0  # Budget quotidien en EUR
    total_spent: float = 0.0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class Campaign(BaseModel):
    """Modèle pour les campagnes publicitaires"""
    campaign_id: str = Field(default_factory=lambda: f"CAMP-{str(uuid.uuid4())[:8].upper()}")
    name: str
    platform: str  # facebook, instagram, tiktok
    objective: str  # awareness, traffic, conversions, lead_generation
    status: str = "draft"  # draft, active, paused, completed
    budget_total: float = 50.0
    budget_spent: float = 0.0
    target_country: str = "FR"
    target_language: str = "fr"
    start_date: datetime = Field(default_factory=datetime.utcnow)
    end_date: Optional[datetime] = None
    target_audience: Dict[str, Any] = {}
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class AdCreative(BaseModel):
    """Modèle pour les créatifs publicitaires"""
    creative_id: str = Field(default_factory=lambda: f"CRE-{str(uuid.uuid4())[:8].upper()}")
    campaign_id: str
    name: str
    type: str  # image, video, carousel, story
    platform: str  # facebook, instagram, tiktok
    content: Dict[str, Any] = {}  # headline, description, cta, media_urls
    performance_score: float = 0.0
    language: str = "fr"
    status: str = "active"  # active, paused, rejected
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class ContentTemplate(BaseModel):
    """Modèle pour les templates de contenu"""
    template_id: str = Field(default_factory=lambda: f"TPL-{str(uuid.uuid4())[:8].upper()}")
    name: str
    platform: str
    content_type: str  # post, story, video, ad
    template_data: Dict[str, Any] = {}
    language: str = "fr"
    tags: List[str] = []
    usage_count: int = 0
    performance_rating: float = 0.0
    created_at: datetime = Field(default_factory=datetime.utcnow)

class SocialMediaMetrics(BaseModel):
    """Modèle pour les métriques des réseaux sociaux"""
    metric_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    campaign_id: Optional[str] = None
    platform: str
    date: datetime = Field(default_factory=datetime.utcnow)
    impressions: int = 0
    clicks: int = 0
    conversions: int = 0
    cost: float = 0.0
    cpc: float = 0.0  # Cost per click
    cpm: float = 0.0  # Cost per mille
    cpa: float = 0.0  # Cost per acquisition
    roas: float = 0.0  # Return on ad spend


# ========== SOCIAL MEDIA AUTOMATION CLASS ==========

class SocialMediaAutomation:
    """Gestionnaire d'automatisation des réseaux sociaux pour Josmose.com"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.logger = logging.getLogger(__name__)
        
        # Configuration initiale des comptes
        self.accounts_config = [
            {
                "platform": "facebook",
                "account_name": "Josmose France",
                "country_target": "FR",
                "language": "fr",
                "daily_budget": 15.0
            },
            {
                "platform": "facebook", 
                "account_name": "Josmose España",
                "country_target": "ES",
                "language": "es",
                "daily_budget": 12.0
            },
            {
                "platform": "instagram",
                "account_name": "josmose_france",
                "country_target": "FR", 
                "language": "fr",
                "daily_budget": 10.0
            },
            {
                "platform": "instagram",
                "account_name": "josmose_espana",
                "country_target": "ES",
                "language": "es",
                "daily_budget": 8.0
            },
            {
                "platform": "tiktok",
                "account_name": "josmose_eu",
                "country_target": "EU",
                "language": "fr",
                "daily_budget": 5.0
            }
        ]
        
        # Templates de contenu par défaut
        self.content_templates = {
            "facebook": {
                "fr": {
                    "post_template": "🌊 Découvrez l'eau pure avec Josmose ! \n\n✅ Élimine 99% des contaminants\n💧 Goût exceptionnel\n🏠 Installation facile\n💰 Prix spécial Europe: €{price}\n\n👉 Commandez maintenant sur josmose.com\n#EauPure #Santé #Josmose #France",
                    "ad_headlines": [
                        "Eau Pure pour Toute la Famille 💧",
                        "Technologie d'Osmose Inverse Avancée",
                        "Installation Gratuite - Prix Spécial €499"
                    ]
                },
                "es": {
                    "post_template": "🌊 ¡Descubre agua pura con Josmose! \n\n✅ Elimina 99% de contaminantes\n💧 Sabor excepcional\n🏠 Instalación fácil\n💰 Precio especial Europa: €{price}\n\n👉 Pide ahora en josmose.com\n#AguaPura #Salud #Josmose #España",
                    "ad_headlines": [
                        "Agua Pura para Toda la Familia 💧",
                        "Tecnología de Ósmosis Inversa Avanzada", 
                        "Instalación Gratuita - Precio Especial €499"
                    ]
                }
            },
            "instagram": {
                "fr": {
                    "story_template": "💧 EAU PURE JOSMOSE 💧\n\n🏠 Pour votre famille\n✅ 99% de pureté\n💰 €499 seulement\n\n⬆️ Swipe up pour commander",
                    "post_captions": [
                        "L'eau pure, c'est la santé de votre famille 💧✨ #Josmose #EauPure #Santé",
                        "Technologie française, qualité européenne 🇫🇷💧 #Innovation #EauPure",
                        "Installation en 24h, satisfaction garantie ⚡🔧 #Service #Qualité"
                    ]
                },
                "es": {
                    "story_template": "💧 AGUA PURA JOSMOSE 💧\n\n🏠 Para tu familia\n✅ 99% pureza\n💰 Solo €499\n\n⬆️ Swipe up para pedir",
                    "post_captions": [
                        "Agua pura es salud para tu familia 💧✨ #Josmose #AguaPura #Salud",
                        "Tecnología francesa, calidad europea 🇪🇸💧 #Innovación #AguaPura",
                        "Instalación en 24h, satisfacción garantizada ⚡🔧 #Servicio #Calidad"
                    ]
                }
            },
            "tiktok": {
                "fr": {
                    "video_scripts": [
                        "POV: Tu découvres que ton eau du robinet n'est pas si pure... 😱 \n\nMais avec Josmose, fini les soucis ! 💧✨\n\n99% de contaminants éliminés ✅\n#EauPure #Santé #Josmose #WaterTok",
                        "Test de goût : Eau du robinet VS Eau Josmose 🥛\n\nLa différence est incroyable ! 😍\n\nCommande ton système sur josmose.com 👆\n#TestEau #Josmose #EauPure",
                        "Installation Josmose en 60 secondes chrono ⏱️\n\nC'est vraiment si facile ? OUI ! 💪\n\n#DIY #Installation #Josmose #EauPure"
                    ]
                }
            }
        }
    
    async def initialize_accounts(self):
        """Initialiser les comptes de réseaux sociaux par défaut"""
        try:
            for account_config in self.accounts_config:
                existing = await self.db.social_media_accounts.find_one({
                    "platform": account_config["platform"],
                    "account_name": account_config["account_name"]
                })
                
                if not existing:
                    account = SocialMediaAccount(
                        platform=account_config["platform"],
                        account_id=f"{account_config['platform']}-{str(uuid.uuid4())[:8]}",
                        account_name=account_config["account_name"],
                        country_target=account_config["country_target"],
                        language=account_config["language"],
                        daily_budget=account_config["daily_budget"]
                    )
                    
                    await self.db.social_media_accounts.insert_one(account.dict())
            
            self.logger.info("Social media accounts initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Social media accounts initialization failed: {e}")
    
    async def generate_content_ai(self, 
                                  content_type: str, 
                                  platform: str, 
                                  language: str = "fr",
                                  product_focus: str = "osmoseur") -> Dict[str, Any]:
        """Générer du contenu avec AI (mode démo pour l'instant)"""
        try:
            if DEMO_MODE:
                # Mode démo - contenu pré-généré
                templates = self.content_templates.get(platform, {}).get(language, {})
                
                if content_type == "post":
                    content = {
                        "headline": f"💧 Eau Pure Josmose - Technologie Avancée",
                        "description": templates.get("post_template", "").format(price="499"),
                        "cta": "Découvrir maintenant",
                        "hashtags": ["#EauPure", "#Josmose", "#Santé", f"#{language.upper()}"],
                        "media_type": "image",
                        "generated_at": datetime.utcnow(),
                        "estimated_reach": 5000,
                        "estimated_engagement": 250
                    }
                
                elif content_type == "video":
                    scripts = templates.get("video_scripts", [])
                    content = {
                        "script": scripts[0] if scripts else "Découvrez Josmose, votre solution eau pure !",
                        "duration": 30,
                        "style": "trending",
                        "music_genre": "upbeat",
                        "hashtags": ["#EauPure", "#Josmose", "#WaterTok"],
                        "cta": "Commander maintenant",
                        "estimated_reach": 8000,
                        "estimated_engagement": 600
                    }
                
                elif content_type == "story":
                    content = {
                        "text": templates.get("story_template", "💧 Josmose - Eau Pure 💧"),
                        "background_color": "#1E40AF",
                        "cta": "Swipe Up",
                        "duration": 15,
                        "stickers": ["water_drop", "sparkles", "heart"],
                        "estimated_reach": 2000,
                        "estimated_engagement": 150
                    }
                
                else:
                    content = {
                        "headline": "Josmose - Eau Pure",
                        "description": "Découvrez notre technologie d'osmose inverse",
                        "cta": "En savoir plus"
                    }
                
                # Sauvegarder le contenu généré
                creative = AdCreative(
                    campaign_id="demo",
                    name=f"{content_type}_{platform}_{language}",
                    type=content_type,
                    platform=platform,
                    content=content,
                    language=language
                )
                
                await self.db.ad_creatives.insert_one(creative.dict())
                
                self.logger.info(f"AI content generated for {platform} {content_type} in {language}")
                return content
            
            else:
                # Mode production avec vraie API OpenAI
                # TODO: Intégrer OpenAI API quand les clés seront disponibles
                pass
                
        except Exception as e:
            self.logger.error(f"Error generating AI content: {e}")
            return {"error": str(e)}
    
    async def create_campaign(self, 
                              name: str,
                              platform: str,
                              objective: str,
                              budget: float,
                              target_country: str = "FR",
                              target_language: str = "fr") -> Dict[str, Any]:
        """Créer une nouvelle campagne publicitaire"""
        try:
            campaign = Campaign(
                name=name,
                platform=platform,
                objective=objective,
                budget_total=budget,
                target_country=target_country,
                target_language=target_language,
                target_audience={
                    "age_min": 25,
                    "age_max": 55,
                    "interests": ["home improvement", "health", "water quality", "family"],
                    "behaviors": ["home owners", "online shoppers"],
                    "location": target_country,
                    "language": target_language
                }
            )
            
            if DEMO_MODE:
                campaign.status = "active"
                
                # Simuler la création de publicités
                for i in range(3):  # 3 créatifs par campagne
                    content = await self.generate_content_ai(
                        content_type=["post", "video", "story"][i % 3],
                        platform=platform,
                        language=target_language
                    )
                    
                    creative = AdCreative(
                        campaign_id=campaign.campaign_id,
                        name=f"{name} - Creative {i+1}",
                        type=["post", "video", "story"][i % 3],
                        platform=platform,
                        content=content,
                        language=target_language
                    )
                    
                    await self.db.ad_creatives.insert_one(creative.dict())
            
            # Sauvegarder la campagne
            await self.db.campaigns.insert_one(campaign.dict())
            
            self.logger.info(f"Campaign created: {campaign.campaign_id} for {platform}")
            
            return {
                "success": True,
                "campaign_id": campaign.campaign_id,
                "campaign": campaign.dict(),
                "creatives_generated": 3 if DEMO_MODE else 0
            }
            
        except Exception as e:
            self.logger.error(f"Error creating campaign: {e}")
            return {"success": False, "error": str(e)}
    
    async def setup_abandoned_cart_retargeting(self, 
                                               customer_email: str,
                                               cart_items: List[Dict],
                                               platform: str = "facebook") -> Dict[str, Any]:
        """Configurer le retargeting pour panier abandonné"""
        try:
            # Créer une campagne de retargeting spécifique
            campaign_name = f"Retargeting - Panier Abandonné - {customer_email[:10]}"
            
            campaign_result = await self.create_campaign(
                name=campaign_name,
                platform=platform,
                objective="conversions",
                budget=20.0,  # Budget plus faible pour retargeting
                target_country="FR"  # À adapter selon la détection de localisation
            )
            
            if campaign_result.get("success"):
                # Créer du contenu spécifique au panier abandonné
                abandoned_content = await self.generate_content_ai(
                    content_type="post",
                    platform=platform,
                    language="fr"
                )
                
                # Personnaliser le contenu avec les produits du panier
                product_names = [item.get("product_id", "osmoseur") for item in cart_items]
                total_value = sum([item.get("price", 499) * item.get("quantity", 1) for item in cart_items])
                
                abandoned_content.update({
                    "personalized_message": f"🛒 N'oubliez pas vos {', '.join(product_names)} ! \n\n💰 Valeur du panier: €{total_value:.2f}\n🎁 Offre spéciale: -10% avec le code RETOUR10\n\n⏰ Offre limitée - 24h seulement !",
                    "discount_code": "RETOUR10",
                    "urgency": "24h",
                    "cart_value": total_value
                })
                
                # Enregistrer la campagne de retargeting
                await self.db.abandoned_cart_campaigns.insert_one({
                    "customer_email": customer_email,
                    "campaign_id": campaign_result["campaign_id"],
                    "cart_items": cart_items,
                    "cart_value": total_value,
                    "platform": platform,
                    "created_at": datetime.utcnow(),
                    "status": "active",
                    "content": abandoned_content
                })
                
                self.logger.info(f"Abandoned cart retargeting setup for {customer_email}")
                
                return {
                    "success": True,
                    "campaign_id": campaign_result["campaign_id"],
                    "retargeting_active": True,
                    "estimated_reach": 500,
                    "discount_offered": "10%"
                }
            
            return {"success": False, "error": "Failed to create retargeting campaign"}
            
        except Exception as e:
            self.logger.error(f"Error setting up abandoned cart retargeting: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_campaign_performance(self, campaign_id: str = None) -> List[Dict[str, Any]]:
        """Obtenir les performances des campagnes"""
        try:
            if campaign_id:
                campaigns = await self.db.campaigns.find({"campaign_id": campaign_id}).to_list(1)
            else:
                campaigns = await self.db.campaigns.find().to_list(100)
            
            performance_data = []
            
            for campaign in campaigns:
                if DEMO_MODE:
                    # Simuler des données de performance
                    days_running = (datetime.utcnow() - campaign["created_at"]).days or 1
                    
                    # Générer des métriques réalistes
                    impressions = days_running * (2000 + hash(campaign["campaign_id"]) % 3000)
                    clicks = int(impressions * (0.01 + hash(campaign["campaign_id"]) % 100 / 10000))  # CTR 1-2%
                    conversions = int(clicks * (0.02 + hash(campaign["campaign_id"]) % 50 / 1000))  # CVR 2-5%
                    cost = days_running * campaign.get("budget_total", 50) / 30  # Coût quotidien estimé
                    
                    performance = {
                        "campaign_id": campaign["campaign_id"],
                        "campaign_name": campaign["name"],
                        "platform": campaign["platform"],
                        "status": campaign["status"],
                        "impressions": impressions,
                        "clicks": clicks,
                        "conversions": conversions,
                        "cost": round(cost, 2),
                        "cpc": round(cost / clicks if clicks > 0 else 0, 2),
                        "cpm": round(cost * 1000 / impressions if impressions > 0 else 0, 2),
                        "cpa": round(cost / conversions if conversions > 0 else 0, 2),
                        "roas": round(conversions * 499 / cost if cost > 0 else 0, 2),  # ROAS assumant €499 par conversion
                        "ctr": round(clicks / impressions * 100 if impressions > 0 else 0, 2),
                        "cvr": round(conversions / clicks * 100 if clicks > 0 else 0, 2),
                        "days_running": days_running,
                        "target_country": campaign.get("target_country", "FR"),
                        "budget_utilization": round(cost / campaign.get("budget_total", 50) * 100, 1)
                    }
                    
                    performance_data.append(performance)
                
                else:
                    # En mode production, récupérer les vraies métriques des API
                    pass
            
            self.logger.info(f"Performance data retrieved for {len(performance_data)} campaigns")
            return performance_data
            
        except Exception as e:
            self.logger.error(f"Error getting campaign performance: {e}")
            return []
    
    async def optimize_budget_allocation(self) -> Dict[str, Any]:
        """Optimiser automatiquement l'allocation du budget"""
        try:
            performance_data = await self.get_campaign_performance()
            
            if not performance_data:
                return {"success": False, "error": "No performance data available"}
            
            # Calculer les scores de performance
            for campaign in performance_data:
                # Score basé sur ROAS, CTR, et CVR
                roas_score = min(campaign["roas"] / 3.0, 1.0)  # Normaliser ROAS optimal à 3.0
                ctr_score = min(campaign["ctr"] / 2.0, 1.0)   # Normaliser CTR optimal à 2%
                cvr_score = min(campaign["cvr"] / 3.0, 1.0)   # Normaliser CVR optimal à 3%
                
                campaign["performance_score"] = (roas_score * 0.5 + ctr_score * 0.3 + cvr_score * 0.2)
            
            # Trier par performance
            performance_data.sort(key=lambda x: x["performance_score"], reverse=True)
            
            # Réallouer le budget (simulation)
            total_budget = 500.0  # Budget mensuel
            allocated_budget = 0
            optimization_actions = []
            
            for i, campaign in enumerate(performance_data):
                if campaign["performance_score"] > 0.7:  # Haute performance
                    new_budget = total_budget * 0.4 / max(1, len([c for c in performance_data if c["performance_score"] > 0.7]))
                    action = "increase_budget"
                elif campaign["performance_score"] > 0.4:  # Performance moyenne
                    new_budget = total_budget * 0.4 / max(1, len([c for c in performance_data if 0.4 < c["performance_score"] <= 0.7]))
                    action = "maintain_budget"
                else:  # Faible performance
                    new_budget = total_budget * 0.2 / max(1, len([c for c in performance_data if c["performance_score"] <= 0.4]))
                    action = "decrease_budget"
                
                optimization_actions.append({
                    "campaign_id": campaign["campaign_id"],
                    "current_performance_score": round(campaign["performance_score"], 3),
                    "recommended_action": action,
                    "current_budget": campaign.get("budget_total", 50),
                    "recommended_budget": round(new_budget, 2),
                    "reason": f"ROAS: {campaign['roas']}, CTR: {campaign['ctr']}%, CVR: {campaign['cvr']}%"
                })
                
                allocated_budget += new_budget
            
            self.logger.info(f"Budget optimization completed for {len(optimization_actions)} campaigns")
            
            return {
                "success": True,
                "total_budget": total_budget,
                "allocated_budget": round(allocated_budget, 2),
                "optimization_actions": optimization_actions,
                "high_performers": len([c for c in performance_data if c["performance_score"] > 0.7]),
                "avg_performers": len([c for c in performance_data if 0.4 < c["performance_score"] <= 0.7]),
                "low_performers": len([c for c in performance_data if c["performance_score"] <= 0.4])
            }
            
        except Exception as e:
            self.logger.error(f"Error optimizing budget allocation: {e}")
            return {"success": False, "error": str(e)}
    
    async def create_landing_page(self, 
                                  campaign_id: str, 
                                  target_audience: Dict[str, Any],
                                  language: str = "fr") -> Dict[str, Any]:
        """Créer une landing page personnalisée pour une campagne"""
        try:
            # Templates de landing page par langue
            landing_templates = {
                "fr": {
                    "title": "🌊 Josmose - Eau Pure pour Votre Famille",
                    "subtitle": "Technologie d'Osmose Inverse Avancée - Installation Gratuite",
                    "benefits": [
                        "✅ Élimine 99% des contaminants",
                        "💧 Goût exceptionnel garanti",
                        "🔧 Installation professionnelle incluse",
                        "🛡️ Garantie 5 ans",
                        "🚚 Livraison gratuite en France"
                    ],
                    "cta_primary": "Commander Maintenant - €499",
                    "cta_secondary": "Demander un Devis Gratuit",
                    "urgency": "⏰ Offre limitée - Stock restant: 15 unités",
                    "testimonials": [
                        {
                            "name": "Marie D., Lyon",
                            "text": "L'eau n'a plus le même goût ! Ma famille adore.",
                            "rating": 5
                        },
                        {
                            "name": "Pierre M., Paris", 
                            "text": "Installation rapide, service parfait. Je recommande !",
                            "rating": 5
                        }
                    ]
                },
                "es": {
                    "title": "🌊 Josmose - Agua Pura para Tu Familia",
                    "subtitle": "Tecnología de Ósmosis Inversa Avanzada - Instalación Gratuita",
                    "benefits": [
                        "✅ Elimina 99% de contaminantes",
                        "💧 Sabor excepcional garantizado",
                        "🔧 Instalación profesional incluida",
                        "🛡️ Garantía 5 años",
                        "🚚 Envío gratuito en España"
                    ],
                    "cta_primary": "Pedir Ahora - €499",
                    "cta_secondary": "Solicitar Presupuesto Gratis",
                    "urgency": "⏰ Oferta limitada - Stock restante: 15 unidades",
                    "testimonials": [
                        {
                            "name": "Carmen R., Madrid",
                            "text": "¡El agua sabe increíble! Toda la familia está contenta.",
                            "rating": 5
                        },
                        {
                            "name": "Carlos L., Barcelona",
                            "text": "Instalación rápida, servicio perfecto. ¡Recomendado!",
                            "rating": 5
                        }
                    ]
                }
            }
            
            template = landing_templates.get(language, landing_templates["fr"])
            
            # Personnaliser selon l'audience cible
            if target_audience.get("interests"):
                if "family" in str(target_audience.get("interests")):
                    template["title"] = template["title"].replace("Votre Famille", "Vos Enfants")
                if "health" in str(target_audience.get("interests")):
                    template["benefits"].insert(1, "🏥 Recommandé par les professionnels de santé")
            
            # Créer la landing page
            landing_page = {
                "landing_id": f"LP-{str(uuid.uuid4())[:8].upper()}",
                "campaign_id": campaign_id,
                "language": language,
                "template_data": template,
                "url": f"https://josmose.com/lp/{campaign_id}",
                "conversion_tracking": True,
                "a_b_testing": {
                    "variant_a": "Original",
                    "variant_b": "High Urgency",
                    "traffic_split": 50
                },
                "seo_data": {
                    "meta_title": template["title"],
                    "meta_description": template["subtitle"],
                    "keywords": ["osmoseur", "eau pure", "osmose inverse", language]
                },
                "performance_tracking": {
                    "visitors": 0,
                    "conversions": 0,
                    "bounce_rate": 0.0,
                    "avg_time_on_page": 0
                },
                "created_at": datetime.utcnow()
            }
            
            # Sauvegarder la landing page
            await self.db.landing_pages.insert_one(landing_page)
            
            self.logger.info(f"Landing page created for campaign {campaign_id}")
            
            return {
                "success": True,
                "landing_id": landing_page["landing_id"],
                "landing_url": landing_page["url"],
                "landing_page": landing_page
            }
            
        except Exception as e:
            self.logger.error(f"Error creating landing page: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_social_media_dashboard(self) -> Dict[str, Any]:
        """Obtenir les données du dashboard marketing automation"""
        try:
            # Compter les comptes actifs
            accounts = await self.db.social_media_accounts.find({"status": "active"}).to_list(100)
            
            # Compter les campagnes par statut
            campaigns_active = await self.db.campaigns.count_documents({"status": "active"})
            campaigns_draft = await self.db.campaigns.count_documents({"status": "draft"})
            campaigns_total = await self.db.campaigns.count_documents({})
            
            # Obtenir les performances
            performance_data = await self.get_campaign_performance()
            
            # Calculer les totaux
            total_impressions = sum([p["impressions"] for p in performance_data])
            total_clicks = sum([p["clicks"] for p in performance_data])
            total_conversions = sum([p["conversions"] for p in performance_data])
            total_cost = sum([p["cost"] for p in performance_data])
            
            # Métriques par plateforme
            platform_metrics = {}
            for performance in performance_data:
                platform = performance["platform"]
                if platform not in platform_metrics:
                    platform_metrics[platform] = {
                        "impressions": 0,
                        "clicks": 0,
                        "conversions": 0,
                        "cost": 0,
                        "campaigns": 0
                    }
                
                platform_metrics[platform]["impressions"] += performance["impressions"]
                platform_metrics[platform]["clicks"] += performance["clicks"]
                platform_metrics[platform]["conversions"] += performance["conversions"]
                platform_metrics[platform]["cost"] += performance["cost"]
                platform_metrics[platform]["campaigns"] += 1
            
            # Calculer les moyennes
            avg_ctr = round(total_clicks / total_impressions * 100 if total_impressions > 0 else 0, 2)
            avg_cvr = round(total_conversions / total_clicks * 100 if total_clicks > 0 else 0, 2)
            avg_cpa = round(total_cost / total_conversions if total_conversions > 0 else 0, 2)
            total_roas = round(total_conversions * 499 / total_cost if total_cost > 0 else 0, 2)
            
            dashboard_data = {
                "accounts": {
                    "total": len(accounts),
                    "by_platform": {
                        "facebook": len([a for a in accounts if a["platform"] == "facebook"]),
                        "instagram": len([a for a in accounts if a["platform"] == "instagram"]),
                        "tiktok": len([a for a in accounts if a["platform"] == "tiktok"])
                    }
                },
                "campaigns": {
                    "total": campaigns_total,
                    "active": campaigns_active,
                    "draft": campaigns_draft,
                    "paused": campaigns_total - campaigns_active - campaigns_draft
                },
                "performance": {
                    "total_impressions": total_impressions,
                    "total_clicks": total_clicks,
                    "total_conversions": total_conversions,
                    "total_cost": round(total_cost, 2),
                    "avg_ctr": avg_ctr,
                    "avg_cvr": avg_cvr,
                    "avg_cpa": avg_cpa,
                    "total_roas": total_roas,
                    "budget_used": round(total_cost, 2),
                    "budget_remaining": round(500 - total_cost, 2)  # Budget mensuel €500
                },
                "platforms": platform_metrics,
                "top_campaigns": sorted(performance_data, key=lambda x: x["performance_score"] if "performance_score" in x else x["roas"], reverse=True)[:5],
                "recent_activity": [],  # À implémenter
                "automated_actions": {
                    "abandoned_carts_targeted": await self.db.abandoned_cart_campaigns.count_documents({"status": "active"}),
                    "content_pieces_generated": await self.db.ad_creatives.count_documents({}),
                    "landing_pages_created": await self.db.landing_pages.count_documents({})
                },
                "last_updated": datetime.utcnow()
            }
            
            self.logger.info("Social media dashboard data retrieved successfully")
            return dashboard_data
            
        except Exception as e:
            self.logger.error(f"Error getting social media dashboard: {e}")
            return {"error": str(e)}


# ========== HELPER FUNCTIONS ==========

def get_social_media_automation(db: AsyncIOMotorDatabase) -> SocialMediaAutomation:
    """Factory function pour créer une instance de SocialMediaAutomation"""
    return SocialMediaAutomation(db)