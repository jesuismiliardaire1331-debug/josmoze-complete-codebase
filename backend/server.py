from fastapi import FastAPI, APIRouter, HTTPException, Request, Depends, status
from fastapi.responses import StreamingResponse
from fastapi.security import HTTPBearer
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timedelta
import httpx
import re
from emergentintegrations.payments.stripe.checkout import StripeCheckout, CheckoutSessionResponse, CheckoutStatusResponse, CheckoutSessionRequest

# Import security and performance middleware
from security_middleware import SecurityMiddleware, CacheMiddleware, get_security_stats, clear_cache
from analytics_dashboard import AnalyticsEngine, export_analytics_csv
from recommendation_engine import get_smart_recommendations
from loyalty_program import LoyaltyProgramManager, process_order_loyalty_points, get_customer_loyalty_status

# Import translation service
from translation_service import translation_service

# Import email service
from email_service import email_service

# Import authentication and AI agents
from auth import User, UserAuth, Token, authenticate_user, create_access_token, get_current_user, require_role, get_company_info, get_user_permissions
from ai_agents import get_marketing_automation, MarketingAutomation

# Import new inventory management and social media automation systems
from inventory_manager import get_inventory_manager, StockItem, CustomerProfile, OrderTracking, Invoice
from social_media_automation import get_social_media_automation, SocialMediaAutomation, Campaign, AdCreative


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Initialize marketing automation, inventory manager, and social media automation as global variables
marketing_automation = None
inventory_manager = None
social_media_automation = None

# Create the main app
app = FastAPI(title="Josmose CRM & Marketing Automation", version="2.0.0")

# Add Security and Performance Middleware (Critical for Production)
# app.add_middleware(SecurityMiddleware)
# app.add_middleware(CacheMiddleware)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://josmose.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create routers
api_router = APIRouter(prefix="/api")
crm_router = APIRouter()  # No prefix since it will be included in api_router with /crm prefix

# Security
security = HTTPBearer()


# ========== MODELS ==========

class Product(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    price: float
    original_price: Optional[float] = None
    image: str
    category: str
    specifications: Dict[str, str] = {}
    features: List[str] = []
    in_stock: bool = True
    target_audience: str = "B2C"  # B2C or B2B
    created_at: datetime = Field(default_factory=datetime.utcnow)

class CartItem(BaseModel):
    product_id: str
    quantity: int
    price: float

class Order(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    customer_email: str
    customer_name: str
    customer_phone: str
    customer_address: Dict[str, str]
    customer_type: str = "B2C"  # B2C or B2B
    items: List[CartItem]
    subtotal: float
    shipping_cost: float
    total: float
    currency: str
    status: str = "pending"
    payment_method: Optional[str] = None
    lead_source: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Lead(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: str
    name: str
    phone: Optional[str] = None
    company: Optional[str] = None
    lead_type: str = "contact"  # contact, quote, consultation, abandoned_cart
    customer_type: str = "B2C"  # B2C or B2B
    source: str = "website"  # website, facebook, google, etc.
    status: str = "new"  # new, contacted, qualified, converted, lost
    score: int = 0  # Lead scoring 0-100
    country_code: Optional[str] = None
    message: Optional[str] = None
    consultation_requested: bool = False
    preferred_contact_time: Optional[str] = None
    last_activity: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    follow_up_date: Optional[datetime] = None
    notes: List[str] = []

class ContactForm(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    company: Optional[str] = None
    message: str
    request_type: str = "quote"  # quote, support, general, consultation
    customer_type: str = "B2C"  # B2C or B2B
    consultation_requested: bool = False
    preferred_contact_time: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class CountryDetection(BaseModel):
    country_code: str
    country_name: str
    currency: str
    language: str
    shipping_cost: float

class TranslationRequest(BaseModel):
    text: str
    target_language: str
    source_language: str = "FR"

class TranslationResponse(BaseModel):
    original_text: str
    translated_text: str
    source_language: str
    target_language: str

class LanguageDetectionResponse(BaseModel):
    detected_language: str
    detected_country: str
    currency: Dict[str, str]
    available_languages: Dict[str, Dict[str, str]]
    ip_address: str

class LocalizationSettings(BaseModel):
    language: str
    country: str
    currency: Dict[str, str]

class PaymentTransaction(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    amount: float
    currency: str
    metadata: Dict[str, str] = {}
    payment_status: str = "pending"  # pending, paid, failed, expired
    status: str = "initiated"  # initiated, completed, failed
    customer_email: Optional[str] = None
    products: List[Dict[str, Any]] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class CheckoutRequest(BaseModel):
    cart_items: List[CartItem]
    customer_info: Dict[str, str]
    origin_url: str

class EmailCampaign(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    subject: str
    content: str
    recipient_emails: List[str]
    status: str = "draft"  # draft, scheduled, sent, failed
    scheduled_at: Optional[datetime] = None
    sent_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ConsultationRequest(BaseModel):
    lead_id: str
    consultation_type: str = "diagnostic"  # diagnostic, installation, maintenance
    preferred_date: Optional[str] = None
    preferred_time: str
    notes: Optional[str] = None
    status: str = "requested"  # requested, scheduled, completed, cancelled


# ========== STRIPE INTEGRATION ==========

stripe_api_key = os.environ.get('STRIPE_API_KEY')
if not stripe_api_key:
    logging.error("STRIPE_API_KEY not found in environment variables")

# Product packages with fixed pricing (security)
PRODUCT_PACKAGES = {
    "osmoseur-principal": 499.0,
    "osmoseur-pro": 899.0,  # B2B version
    "filtres-rechange": 49.0,
    "filtres-pro": 89.0,  # B2B version
    "garantie-2ans": 39.0,
    "garantie-5ans": 59.0,
    "installation-service": 150.0,
    "consultation-expert": 0.0  # Free consultation
}

def get_stripe_checkout(request: Request) -> StripeCheckout:
    """Initialize Stripe checkout with webhook URL"""
    host_url = str(request.base_url).rstrip('/')
    webhook_url = f"{host_url}/api/webhook/stripe"
    return StripeCheckout(api_key=stripe_api_key, webhook_url=webhook_url)


# ========== LEAD SCORING SYSTEM ==========

def calculate_lead_score(lead_data: Dict) -> int:
    """Calculate lead score based on various factors"""
    score = 0
    
    # Base score for having contact info
    score += 10
    
    # Email provided
    if lead_data.get("email"):
        score += 15
    
    # Phone provided
    if lead_data.get("phone"):
        score += 20
    
    # Company (B2B leads are more valuable)
    if lead_data.get("company"):
        score += 25
    
    # Lead type scoring
    lead_type = lead_data.get("lead_type", "contact")
    if lead_type == "quote":
        score += 30
    elif lead_type == "consultation":
        score += 40
    elif lead_type == "abandoned_cart":
        score += 35
    
    # Consultation requested
    if lead_data.get("consultation_requested"):
        score += 20
    
    return min(score, 100)  # Cap at 100


# ========== EMAIL AUTOMATION SYSTEM ==========

async def send_welcome_email(lead_email: str, lead_name: str, lead_type: str):
    """Send welcome email based on lead type"""
    try:
        email_templates = {
            "contact": "Merci pour votre intérêt ! Un expert vous contactera sous 24h.",
            "quote": "Votre demande de devis a été reçue. Calcul en cours...",
            "consultation": "Consultation gratuite confirmée ! Un expert vous appellera.",
            "abandoned_cart": "Votre osmoseur vous attend ! -10% avec le code RETOUR10"
        }
        
        subject = f"Josmose.com - {email_templates.get(lead_type, 'Bienvenue')}"
        content = f"Bonjour {lead_name},\n\n{email_templates.get(lead_type)}\n\nÀ bientôt,\nL'équipe Josmose"
        
        # Store email in database for tracking
        email_record = {
            "recipient": lead_email,
            "subject": subject,
            "content": content,
            "type": "welcome",
            "status": "sent",
            "sent_at": datetime.utcnow()
        }
        
        await db.email_logs.insert_one(email_record)
        logging.info(f"Welcome email sent to {lead_email}")
        
    except Exception as e:
        logging.error(f"Failed to send welcome email to {lead_email}: {e}")

async def process_abandoned_cart(customer_email: str, cart_items: List[Dict]):
    """Process abandoned cart and create lead"""
    try:
        # Create abandoned cart lead
        lead_data = {
            "email": customer_email,
            "name": "Prospect Panier",
            "lead_type": "abandoned_cart",
            "status": "new",
            "score": calculate_lead_score({"email": customer_email, "lead_type": "abandoned_cart"}),
            "message": f"Panier abandonné: {len(cart_items)} articles",
            "last_activity": datetime.utcnow(),
            "follow_up_date": datetime.utcnow() + timedelta(hours=2)  # Follow up in 2 hours
        }
        
        # Check if lead already exists
        existing_lead = await db.leads.find_one({"email": customer_email})
        if existing_lead:
            await db.leads.update_one(
                {"email": customer_email},
                {"$set": {
                    "lead_type": "abandoned_cart",
                    "last_activity": datetime.utcnow(),
                    "score": lead_data["score"]
                }}
            )
        else:
            lead = Lead(**lead_data)
            await db.leads.insert_one(lead.dict())
        
        # Send abandoned cart email
        await send_welcome_email(customer_email, "Prospect", "abandoned_cart")
        
    except Exception as e:
        logging.error(f"Failed to process abandoned cart for {customer_email}: {e}")


# ========== COUNTRY/CURRENCY/LANGUAGE DETECTION ==========

COUNTRY_CONFIG = {
    "FR": {"name": "France", "currency": "EUR", "language": "fr", "shipping": 19.0},
    "ES": {"name": "España", "currency": "EUR", "language": "es", "shipping": 29.0},
    "DE": {"name": "Deutschland", "currency": "EUR", "language": "de", "shipping": 29.0},
    "IT": {"name": "Italia", "currency": "EUR", "language": "it", "shipping": 29.0},
    "GB": {"name": "United Kingdom", "currency": "GBP", "language": "en", "shipping": 35.0},
    "BE": {"name": "Belgique", "currency": "EUR", "language": "fr", "shipping": 29.0},
    "NL": {"name": "Nederland", "currency": "EUR", "language": "en", "shipping": 29.0},
    "AT": {"name": "Österreich", "currency": "EUR", "language": "de", "shipping": 29.0},
    "CH": {"name": "Switzerland", "currency": "CHF", "language": "de", "shipping": 35.0},
    "PT": {"name": "Portugal", "currency": "EUR", "language": "es", "shipping": 29.0}
}

async def detect_country_from_ip(ip_address: str) -> Optional[str]:
    """Detect country from IP address using ipapi.co"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"http://ipapi.co/{ip_address}/country/")
            if response.status_code == 200:
                country_code = response.text.strip()
                return country_code if country_code in COUNTRY_CONFIG else None
    except Exception as e:
        logging.warning(f"IP detection failed: {e}")
    return None

def get_client_ip(request: Request) -> str:
    """Extract client IP from request"""
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    
    real_ip = request.headers.get("x-real-ip")
    if real_ip:
        return real_ip
    
    return request.client.host if request.client else "127.0.0.1"

def detect_language_from_header(accept_language: str) -> str:
    """Parse Accept-Language header"""
    if not accept_language:
        return "en"
    
    # Extract first language preference
    lang_match = re.match(r'^([a-z]{2})', accept_language.lower())
    if lang_match:
        lang = lang_match.group(1)
        lang_map = {"fr": "fr", "es": "es", "de": "de", "it": "it"}
        return lang_map.get(lang, "en")
    
    return "en"


# ========== API ROUTES ==========

@api_router.get("/")
async def root():
    return {"message": "Josmose.com API - Système d'Osmose Inverse avec CRM"}

@api_router.get("/detect-location")
async def detect_location(request: Request):
    """Detect user location, currency, and language using enhanced IP detection"""
    try:
        # Utiliser le nouveau service de traduction pour la détection
        client_ip = translation_service.get_client_ip(request)
        
        # Détecter le pays via le service de traduction
        country_code = translation_service.detect_country_from_ip(client_ip)
        
        # Obtenir la devise via le service de traduction
        currency_info = translation_service.get_user_currency_from_ip(client_ip)
        
        # Obtenir la langue via le service de traduction
        language_code = translation_service.get_user_language_from_ip(client_ip)
        
        # Mapping pour compatibilité avec l'ancien format
        config = COUNTRY_CONFIG.get(country_code, COUNTRY_CONFIG["FR"])
        
        return CountryDetection(
            country_code=country_code,
            country_name=config["name"],
            currency=currency_info["code"],
            language=language_code,
            shipping_cost=config["shipping"]
        )
        
    except Exception as e:
        logging.error(f"Location detection error: {str(e)}")
        # Fallback vers la configuration par défaut
        config = COUNTRY_CONFIG["FR"]
        return CountryDetection(
            country_code="FR",
            country_name=config["name"],
            currency="EUR",
            language="FR",
            shipping_cost=config["shipping"]
        )

@api_router.get("/products")
async def get_products(customer_type: str = "B2C"):
    """Get products filtered by customer type (B2C/B2B) with stock info"""
    products_data = await db.products.find({"target_audience": {"$in": [customer_type, "both"]}}).to_list(1000)
    if not products_data:
        # Initialize with default products if empty
        await initialize_products()
        products_data = await db.products.find({"target_audience": {"$in": [customer_type, "both"]}}).to_list(1000)
    
    # Enrichir avec les informations de stock
    enriched_products = []
    for product in products_data:
        product_obj = Product(**product)
        
        # Obtenir le statut du stock
        stock_status = await inventory_manager.get_stock_status(product["id"])
        
        # Ajouter les infos de stock au produit
        product_dict = product_obj.dict()
        product_dict["stock_info"] = {
            "in_stock": stock_status.get("available_stock", 0) > 0,
            "show_stock_warning": stock_status.get("show_stock_warning", False),
            "stock_warning_text": stock_status.get("stock_warning_text"),
            "available_stock": stock_status.get("available_stock", 0) if stock_status.get("available_stock", 0) > 5 else "Quelques unités disponibles"
        }
        
        enriched_products.append(product_dict)
    
    return enriched_products

@api_router.get("/products/translated")
async def get_translated_products(
    customer_type: str = "B2C", 
    language: str = "FR",
    request: Request = None
):
    """
    Récupère les produits traduits automatiquement
    Si pas de langue spécifiée, détecte automatiquement via IP
    """
    try:
        # Si pas de langue spécifiée, détecter automatiquement
        if language == "FR" and request:
            client_ip = translation_service.get_client_ip(request)
            language = translation_service.get_user_language_from_ip(client_ip)
        
        # Récupérer les produits originaux
        products_data = await db.products.find({"target_audience": {"$in": [customer_type, "both"]}}).to_list(1000)
        if not products_data:
            await initialize_products()
            products_data = await db.products.find({"target_audience": {"$in": [customer_type, "both"]}}).to_list(1000)
        
        # Traduire chaque produit si nécessaire
        translated_products = []
        for product in products_data:
            if language != "FR":
                # Traduire le produit
                translated_product = await translation_service.translate_object(product, language)
            else:
                translated_product = product
            
            # Ajouter les informations de stock
            product_obj = Product(**translated_product)
            stock_status = await inventory_manager.get_stock_status(product["id"])
            
            product_dict = product_obj.dict()
            product_dict["stock_info"] = {
                "in_stock": stock_status.get("available_stock", 0) > 0,
                "show_stock_warning": stock_status.get("show_stock_warning", False),
                "stock_warning_text": stock_status.get("stock_warning_text"),
                "available_stock": stock_status.get("available_stock", 0) if stock_status.get("available_stock", 0) > 5 else "Quelques unités disponibles"
            }
            
            translated_products.append(product_dict)
        
        return {
            "products": translated_products,
            "language": language,
            "customer_type": customer_type
        }
        
    except Exception as e:
        logging.error(f"Error in translated products: {str(e)}")
        # Fallback vers les produits originaux
        return await get_products(customer_type)

@api_router.get("/products/{product_id}")
async def get_product(product_id: str):
    """Get single product"""
    product_data = await db.products.find_one({"id": product_id})
    if not product_data:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return Product(**product_data)


# ========== TRANSLATION AND LOCALIZATION ENDPOINTS ==========

@api_router.get("/localization/detect")
async def detect_user_localization(request: Request) -> LanguageDetectionResponse:
    """
    Détecte automatiquement la langue et la devise de l'utilisateur basé sur l'IP
    """
    try:
        # Obtenir l'IP du client
        client_ip = translation_service.get_client_ip(request)
        
        # Détecter la langue basée sur l'IP
        detected_language = translation_service.get_user_language_from_ip(client_ip)
        
        # Détecter la devise basée sur l'IP
        currency = translation_service.get_user_currency_from_ip(client_ip)
        
        # Détecter le pays
        detected_country = translation_service.detect_country_from_ip(client_ip)
        
        # Obtenir les langues disponibles
        available_languages = translation_service.get_available_languages()
        
        return LanguageDetectionResponse(
            detected_language=detected_language,
            detected_country=detected_country,
            currency=currency,
            available_languages=available_languages,
            ip_address=client_ip
        )
        
    except Exception as e:
        logging.error(f"Error in localization detection: {str(e)}")
        # Fallback vers les valeurs par défaut
        return LanguageDetectionResponse(
            detected_language="FR",
            detected_country="FR", 
            currency={"code": "EUR", "symbol": "€", "name": "Euro"},
            available_languages=translation_service.get_available_languages(),
            ip_address="unknown"
        )

@api_router.post("/localization/translate")
async def translate_text(translation_request: TranslationRequest) -> TranslationResponse:
    """
    Traduit un texte vers la langue cible
    """
    try:
        translated_text = await translation_service.translate_text(
            text=translation_request.text,
            target_language=translation_request.target_language,
            source_language=translation_request.source_language
        )
        
        return TranslationResponse(
            original_text=translation_request.text,
            translated_text=translated_text,
            source_language=translation_request.source_language,
            target_language=translation_request.target_language
        )
        
    except Exception as e:
        logging.error(f"Translation error: {str(e)}")
        raise HTTPException(status_code=500, detail="Translation failed")

@api_router.get("/localization/languages")
async def get_available_languages():
    """
    Retourne toutes les langues disponibles avec leurs métadonnées
    """
    return translation_service.get_available_languages()

@api_router.post("/localization/translate-bulk")
async def translate_bulk_content(
    content: Dict[str, Any],
    target_language: str,
    source_language: str = "FR"
):
    """
    Traduit un objet complexe (dictionnaire) récursivement
    Utile pour traduire plusieurs éléments à la fois
    """
    try:
        translated_content = await translation_service.translate_object(
            content, target_language, source_language
        )
        
        return {
            "original": content,
            "translated": translated_content,
            "source_language": source_language,
            "target_language": target_language
        }
        
    except Exception as e:
        logging.error(f"Bulk translation error: {str(e)}")
        raise HTTPException(status_code=500, detail="Bulk translation failed")

@api_router.post("/leads")
async def create_lead(lead: Lead, request: Request):
    """Create new lead and trigger automation"""
    # Detect country for lead
    location = await detect_location(request)
    lead.country_code = location.country_code
    
    # Calculate lead score
    lead.score = calculate_lead_score(lead.dict())
    
    # Set follow-up date based on lead type
    if lead.lead_type == "consultation":
        lead.follow_up_date = datetime.utcnow() + timedelta(hours=1)
    elif lead.lead_type == "quote":
        lead.follow_up_date = datetime.utcnow() + timedelta(hours=4)
    else:
        lead.follow_up_date = datetime.utcnow() + timedelta(days=1)
    
    # Store lead in database
    await db.leads.insert_one(lead.dict())
    
    # Trigger welcome automation
    await marketing_automation.trigger_welcome_sequence(lead.dict())
    
    logging.info(f"New lead created: {lead.email} (score: {lead.score})")
    
    return {"message": "Lead créé avec succès!", "lead_id": lead.id, "score": lead.score}

@api_router.post("/consultation/request")
async def request_consultation(consultation: ConsultationRequest):
    """Request consultation with expert"""
    try:
        # Store consultation request
        await db.consultations.insert_one(consultation.dict())
        
        # Update lead status
        await db.leads.update_one(
            {"id": consultation.lead_id},
            {"$set": {
                "consultation_requested": True,
                "status": "qualified",
                "last_activity": datetime.utcnow()
            }}
        )
        
        logging.info(f"Consultation requested for lead: {consultation.lead_id}")
        
        return {"message": "Consultation programmée ! Un expert vous contactera dans les prochaines heures."}
        
    except Exception as e:
        logging.error(f"Consultation request failed: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la programmation")

@api_router.post("/orders")
async def create_order(order: Order):
    """Create new order"""
    order_dict = order.dict()
    await db.orders.insert_one(order_dict)
    
    # Create lead from order if not exists
    existing_lead = await db.leads.find_one({"email": order.customer_email})
    if not existing_lead:
        lead_data = {
            "email": order.customer_email,
            "name": order.customer_name,
            "phone": order.customer_phone,
            "lead_type": "converted",
            "customer_type": order.customer_type,
            "status": "converted",
            "score": 100,
            "source": order.lead_source or "website"
        }
        lead = Lead(**lead_data)
        await db.leads.insert_one(lead.dict())
    else:
        # Update existing lead
        await db.leads.update_one(
            {"email": order.customer_email},
            {"$set": {"status": "converted", "score": 100}}
        )
    
    logging.info(f"New order created: {order.id} for {order.customer_email}")
    
    return order

@api_router.post("/contact")
async def submit_contact_form(form: ContactForm, request: Request):
    """Submit contact form and create lead"""
    try:
        # Store contact form
        form_dict = form.dict()
        await db.contact_forms.insert_one(form_dict)
        
        # Create lead from contact form
        location = await detect_location(request)
        lead_data = {
            "email": form.email,
            "name": form.name,
            "phone": form.phone,
            "company": form.company,
            "lead_type": form.request_type,
            "customer_type": form.customer_type,
            "message": form.message,
            "consultation_requested": form.consultation_requested,
            "preferred_contact_time": form.preferred_contact_time,
            "country_code": location.country_code,
            "source": "contact_form"
        }
        
        lead = Lead(**lead_data)
        lead.score = calculate_lead_score(lead_data)
        
        await db.leads.insert_one(lead.dict())
        
        # Trigger welcome automation
        await marketing_automation.trigger_welcome_sequence({"email": form.email, "name": form.name, "customer_type": form.customer_type})
        
        logging.info(f"Contact form submitted: {form.email} - {form.request_type}")
        
        return {"message": "Votre demande a été envoyée avec succès!", "lead_score": lead.score}
        
    except Exception as e:
        logging.error(f"Contact form submission failed: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de l'envoi")

# ========== CRM ENDPOINTS ==========

@api_router.get("/crm/leads")
async def get_leads(status: Optional[str] = None, customer_type: Optional[str] = None):
    """Get all leads with optional filtering"""
    query = {}
    if status:
        query["status"] = status
    if customer_type:
        query["customer_type"] = customer_type
    
    leads_data = await db.leads.find(query).sort("created_at", -1).limit(500).to_list(500)
    return [Lead(**lead) for lead in leads_data]

@api_router.get("/crm/dashboard")
async def get_crm_dashboard():
    """Get CRM dashboard statistics"""
    try:
        # Count leads by status
        leads_by_status = {}
        for status in ["new", "contacted", "qualified", "converted", "lost"]:
            count = await db.leads.count_documents({"status": status})
            leads_by_status[status] = count
        
        # Count leads by type
        leads_by_type = {}
        for lead_type in ["contact", "quote", "consultation", "abandoned_cart"]:
            count = await db.leads.count_documents({"lead_type": lead_type})
            leads_by_type[lead_type] = count
        
        # Recent activity
        recent_leads = await db.leads.find().sort("created_at", -1).limit(10).to_list(10)
        recent_orders = await db.orders.find().sort("created_at", -1).limit(10).to_list(10)
        
        # Revenue stats
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        week_ago = today - timedelta(days=7)
        
        daily_orders = await db.orders.count_documents({"created_at": {"$gte": today}})
        weekly_orders = await db.orders.count_documents({"created_at": {"$gte": week_ago}})
        
        # Calculate revenue
        weekly_revenue_pipeline = [
            {"$match": {"created_at": {"$gte": week_ago}, "status": "paid"}},
            {"$group": {"_id": None, "total": {"$sum": "$total"}}}
        ]
        
        revenue_result = await db.orders.aggregate(weekly_revenue_pipeline).to_list(1)
        weekly_revenue = revenue_result[0]["total"] if revenue_result else 0
        
        return {
            "leads_by_status": leads_by_status,
            "leads_by_type": leads_by_type,
            "total_leads": sum(leads_by_status.values()),
            "recent_leads": [Lead(**lead) for lead in recent_leads],
            "recent_orders": [Order(**order) for order in recent_orders],
            "daily_orders": daily_orders,
            "weekly_orders": weekly_orders,
            "weekly_revenue": weekly_revenue,
            "conversion_rate": round((leads_by_status.get("converted", 0) / max(sum(leads_by_status.values()), 1)) * 100, 2)
        }
        
    except Exception as e:
        logging.error(f"Dashboard query failed: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors du chargement du dashboard")

@api_router.put("/crm/leads/{lead_id}")
async def update_lead(lead_id: str, update_data: Dict[str, Any]):
    """Update lead information"""
    try:
        update_data["last_activity"] = datetime.utcnow()
        
        await db.leads.update_one(
            {"id": lead_id},
            {"$set": update_data}
        )
        
        return {"message": "Lead mis à jour avec succès"}
        
    except Exception as e:
        logging.error(f"Lead update failed: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la mise à jour")

@api_router.get("/orders")
async def get_orders():
    """Get all orders (for admin/CRM)"""
    orders_data = await db.orders.find().sort("created_at", -1).to_list(1000)
    return [Order(**order) for order in orders_data]

@api_router.get("/contact-forms")
async def get_contact_forms():
    """Get all contact forms (for admin/CRM)"""
    forms_data = await db.contact_forms.find().sort("created_at", -1).to_list(1000)
    return [ContactForm(**form) for form in forms_data]


@api_router.get("/crm/user-permissions")
async def get_crm_user_permissions(current_user: User = Depends(get_current_user)):
    """Get current user CRM permissions (detailed permissions for CRM interface)"""
    try:
        # Import the detailed permissions function from auth.py
        from auth import get_user_permissions as get_detailed_permissions
        permissions = get_detailed_permissions(current_user.role)
        
        return {
            "success": True,
            "user": {
                "id": current_user.id,
                "username": current_user.username,
                "email": current_user.email,
                "full_name": current_user.full_name,
                "role": current_user.role,
                "is_active": current_user.is_active
            },
            "permissions": permissions
        }
    except Exception as e:
        logging.error(f"Error getting CRM user permissions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user permissions"
        )

@api_router.get("/auth/user-info")
async def get_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information and permissions"""
    try:
        permissions = get_user_permissions(current_user.role)
        
        return {
            "success": True,
            "user": {
                "id": current_user.id,
                "username": current_user.username,
                "email": current_user.email,
                "full_name": current_user.full_name,
                "role": current_user.role,
                "is_active": current_user.is_active
            },
            "permissions": permissions
        }
    except Exception as e:
        logging.error(f"Error getting user info: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user information"
        )

async def get_all_products():
    """Get all products from the initialized products list"""
    # This function returns the same products as initialized in initialize_products()
    products = [
        {
            "id": "osmoseur-principal",
            "name": "Fontaine à Eau Osmosée BlueMountain",
            "description": "Système d'osmose inverse professionnel BlueMountain. Production 380L/jour (16L/h). Eau chaude, froide et tempérée. Membrane 100GPD encapsulée. Prix spécial : 499€ au lieu de 599€.",
            "price": 499.0,
            "original_price": 599.0,
            "image": "https://www.josmose.fr/2570-large_default/fontaine-osmoseur-minibluesea.jpg",
            "category": "osmoseur",
            "target_audience": "both",
            "in_stock": True,
            "created_at": datetime.now()
        },
        {
            "id": "fontaine-ultrafiltration",
            "name": "Fontaine Intelligente H₂O",
            "description": "Fontaine d'eau intelligente avec contrôle digital du bout des doigts. Température réglable en 3 secondes, installation plug & play, sécurité enfant intégrée.",
            "price": 399.0,
            "original_price": 499.0,
            "image": "https://static.wixstatic.com/media/6af6bd_d5ec79a577694414b12e794e8a30e3bb~mv2.png/v1/fill/w_558,h_684,al_c,q_90,usm_0.66_1.00_0.01,enc_avif,quality_auto/Hf8e72e690708417d8f7fae61845a5e804_png_720x720q50.png",
            "category": "osmoseur", 
            "target_audience": "both",
            "in_stock": True,
            "created_at": datetime.now()
        },
        {
            "id": "osmoseur-pro",
            "name": "Système Osmose Inverse Professionnel BlueMountain Grand Format",
            "description": "Solution professionnelle BlueMountain grand format pour restaurants, bureaux et commerces. Dimensions 1040×330×300mm avec même performance 15L/h.",
            "price": 899.0,
            "original_price": 1199.0,
            "image": "https://www.josmose.fr/img/cms/fontaine_a_eau_entreprise%20-%20copie.jpg",
            "category": "osmoseur",
            "target_audience": "B2B",
            "in_stock": True,
            "created_at": datetime.now()
        },
        {
            "id": "filtres-rechange",
            "name": "Kit Filtres de Rechange - 4 Étapes",
            "description": "Lot complet de filtres de rechange selon CDC. Kit 4 étapes : PP + GAC + CTO + Membrane UF. À partir du 6ème mois - 49€.",
            "price": 49.0,
            "image": "https://static.wixstatic.com/media/6af6bd_1b0ed5e9b180466baeee7436019f6fef~mv2.png/v1/fill/w_520,h_692,al_c,lg_1,q_85,enc_avif,quality_auto/H10e839a4d05e44ab881e05d9aeb3e0d80_jpg_720x720q50-removebg-preview.png",
            "category": "accessoire",
            "target_audience": "both",
            "in_stock": True,
            "created_at": datetime.now()
        },
        {
            "id": "garantie-2ans", 
            "name": "Extension Garantie 2 ans - 39€",
            "description": "Étendez votre garantie à 2 ans selon tarif CDC. Tranquillité d'esprit totale avec support technique.",
            "price": 39.0,
            "image": "https://images.unsplash.com/photo-1556740749-887f6717d7e4?w=400&h=300&fit=crop&auto=format",
            "category": "service",
            "target_audience": "both",
            "in_stock": True,
            "created_at": datetime.now()
        }
    ]
    return products

# ========== LOYALTY PROGRAM ENDPOINTS ==========

@api_router.get("/loyalty/status/{customer_id}")
async def get_loyalty_status(customer_id: str):
    """Get customer loyalty program status"""
    try:
        status = await get_customer_loyalty_status(db, customer_id)
        return status
    except Exception as e:
        logging.error(f"Get loyalty status error: {str(e)}")
        return {
            "success": False,
            "error": "Failed to retrieve loyalty status"
        }

class RedeemRewardRequest(BaseModel):
    customer_id: str
    reward_id: str

@api_router.post("/loyalty/redeem")
async def redeem_loyalty_reward(request: RedeemRewardRequest):
    """Redeem a loyalty reward"""
    try:
        loyalty_manager = LoyaltyProgramManager(db)
        result = await loyalty_manager.redeem_reward(
            request.customer_id, 
            request.reward_id
        )
        return result
    except Exception as e:
        logging.error(f"Redeem loyalty reward error: {str(e)}")
        return {
            "success": False,
            "error": "Failed to redeem reward"
        }

@api_router.post("/loyalty/award-points")
async def award_loyalty_points(
    customer_id: str,
    points: int,
    description: str,
    order_id: Optional[str] = None,
    current_user: User = Depends(require_role(["manager", "agent"]))
):
    """Award points to a customer (CRM only)"""
    try:
        loyalty_manager = LoyaltyProgramManager(db)
        result = await loyalty_manager.award_points(
            customer_id, points, description, order_id
        )
        
        return {
            "success": result,
            "message": f"Points awarded to {customer_id}" if result else "Failed to award points"
        }
    except Exception as e:
        logging.error(f"Award loyalty points error: {str(e)}")
        return {
            "success": False,
            "error": "Failed to award points"
        }

# ========== SMART PRODUCT RECOMMENDATIONS ==========

class RecommendationRequest(BaseModel):
    customer_id: Optional[str] = None
    current_cart: List[Dict] = []
    customer_type: str = "B2C"
    context: Dict = {}
    max_recommendations: int = 4

@api_router.post("/recommendations/smart")
async def get_product_recommendations(request: RecommendationRequest):
    """Get intelligent product recommendations"""
    try:
        recommendations = await get_smart_recommendations(
            db=db,
            customer_id=request.customer_id,
            current_cart=request.current_cart,
            customer_type=request.customer_type,
            context=request.context
        )
        
        # Limit results
        limited_recommendations = recommendations[:request.max_recommendations]
        
        return {
            "success": True,
            "recommendations": limited_recommendations,
            "total_available": len(recommendations),
            "algorithm_version": "1.0",
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logging.error(f"Product recommendations error: {str(e)}")
        return {
            "success": False,
            "error": "Failed to generate recommendations",
            "recommendations": []
        }

# ========== ADVANCED ANALYTICS & BI ENDPOINTS ==========

@crm_router.get("/analytics/dashboard")
async def get_comprehensive_analytics(
    date_range: int = 30,
    current_user: User = Depends(require_role(["manager", "agent"]))
):
    """Get comprehensive business intelligence dashboard"""
    try:
        analytics_engine = AnalyticsEngine(db)
        dashboard_data = await analytics_engine.get_comprehensive_dashboard(date_range)
        
        return {
            "success": True,
            "data": dashboard_data
        }
    except Exception as e:
        logging.error(f"Analytics dashboard error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate analytics dashboard"
        )

@crm_router.get("/analytics/export/csv")
async def export_analytics_data(
    date_range: int = 30,
    current_user: User = Depends(require_role(["manager"]))
):
    """Export analytics data as CSV (Manager only)"""
    try:
        csv_data = await export_analytics_csv(db, date_range)
        
        from io import StringIO
        csv_io = StringIO(csv_data)
        
        response = StreamingResponse(
            iter([csv_data]),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=josmose_analytics.csv"}
        )
        
        return response
        
    except Exception as e:
        logging.error(f"CSV export error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to export analytics data"
        )

@crm_router.get("/security/stats")
async def get_security_statistics(
    current_user: User = Depends(require_role(["manager", "technique"]))
):
    """Get security and performance statistics"""
    try:
        security_stats = get_security_stats()
        
        return {
            "success": True,
            "security_stats": security_stats,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logging.error(f"Security stats error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve security statistics"
        )

@crm_router.post("/cache/clear")
async def clear_system_cache(
    pattern: str = "*",
    current_user: User = Depends(require_role(["manager"]))
):
    """Clear system cache (Manager only)"""
    try:
        result = await clear_cache(pattern)
        
        return {
            "success": True,
            "result": result
        }
        
    except Exception as e:
        logging.error(f"Cache clear error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to clear cache"
        )

@api_router.get("/crm/team-contacts")
async def get_team_contacts():
    """
    Récupère les adresses email professionnelles de l'équipe pour les clients et prospects
    """
    team_contacts = {
        "managers": [
            {
                "name": "Antonio",
                "position": "Directeur Général", 
                "email": "antonio@josmose.com",
                "department": "Direction Générale",
                "speciality": "Direction stratégique et développement"
            },
            {
                "name": "Aziza",
                "position": "Directrice Adjointe",
                "email": "aziza@josmose.com", 
                "department": "Direction Adjointe",
                "speciality": "Gestion opérationnelle et coordination"
            },
            {
                "name": "Naima", 
                "position": "Directrice Commerciale",
                "email": "naima@josmose.com",
                "department": "Direction Commerciale", 
                "speciality": "Développement commercial et relations clients"
            }
        ],
        "services": [
            {
                "name": "Service Commercial",
                "position": "Équipe Commerciale",
                "email": "commercial@josmose.com",
                "department": "Service Commercial",
                "speciality": "Prospection et ventes, devis personnalisés"
            },
            {
                "name": "Support Technique",
                "position": "Technicien Support", 
                "email": "support@josmose.com",
                "department": "Support Technique",
                "speciality": "Installation, maintenance et support technique"
            }
        ],
        "contact_general": {
            "website": "josmose.com",
            "domain": "@josmose.com",
            "headquarters": "France",
            "business_hours": "Lundi-Vendredi 9h-18h"
        }
    }
    
    return team_contacts

# ========== EMAIL SYSTEM ENDPOINTS ==========

class EmailSendRequest(BaseModel):
    to_email: str
    subject: str
    body: str
    attachments: Optional[List[Dict]] = None

class EmailSimulationRequest(BaseModel):
    from_email: str
    subject: str
    body: str

@api_router.post("/crm/emails/send")
async def send_email(email_data: EmailSendRequest, current_user: dict = Depends(require_role(["manager", "commercial", "technique"]))):
    """
    Envoie un email depuis l'adresse professionnelle de l'utilisateur
    """
    try:
        user_email = current_user.get("email")
        
        result = await email_service.send_email(
            from_email=user_email,
            to_email=email_data.to_email,
            subject=email_data.subject,
            body=email_data.body,
            attachments=email_data.attachments,
            email_password="demo_password"  # En production, utiliser les vrais mots de passe
        )
        
        return result
        
    except Exception as e:
        logging.error(f"Erreur envoi email: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur lors de l'envoi de l'email")

@api_router.get("/crm/emails/inbox")
async def get_inbox(current_user: dict = Depends(require_role(["manager", "commercial", "technique"]))):
    """
    Récupère les emails de la boîte mail de l'utilisateur
    """
    try:
        user_email = current_user.get("email")
        emails = await email_service.receive_emails(user_email, "demo_password")
        
        return {
            "emails": emails,
            "user_email": user_email
        }
        
    except Exception as e:
        logging.error(f"Erreur récupération inbox: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur lors de la récupération des emails")

@api_router.get("/crm/emails/stats")
async def get_inbox_stats(current_user: dict = Depends(require_role(["manager", "commercial", "technique"]))):
    """
    Récupère les statistiques de la boîte mail
    """
    try:
        user_email = current_user.get("email")
        stats = await email_service.get_inbox_stats(user_email)
        
        return stats
        
    except Exception as e:
        logging.error(f"Erreur stats inbox: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur lors de la récupération des statistiques")

@api_router.post("/crm/emails/{email_id}/read")
async def mark_email_read(email_id: str, current_user: dict = Depends(require_role(["manager", "commercial", "technique"]))):
    """
    Marque un email comme lu
    """
    try:
        result = await email_service.mark_email_as_read(email_id)
        return result
        
    except Exception as e:
        logging.error(f"Erreur marquage email lu: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur lors du marquage de l'email")

@api_router.post("/crm/emails/simulate-incoming")
@require_role(["manager"])  # Seulement pour les managers (démo)
async def simulate_incoming_email(email_data: EmailSimulationRequest, current_user: dict = Depends(get_current_user)):
    """
    Simule la réception d'un email (pour démonstration)
    Déclenche automatiquement un accusé de réception
    """
    try:
        user_email = current_user.get("email")
        
        result = await email_service.simulate_incoming_email(
            to_email=user_email,
            from_email=email_data.from_email,
            subject=email_data.subject,
            body=email_data.body
        )
        
        return result
        
    except Exception as e:
        logging.error(f"Erreur simulation email: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur lors de la simulation")

# ========== COMPANY LEGAL INFO ENDPOINT ==========

@api_router.get("/company/legal-info")
async def get_legal_info():
    """Get company legal information for payment compliance"""
    try:
        return {
            "success": True,
            "company_info": get_company_info()
        }
    except Exception as e:
        logging.error(f"Error getting company legal info: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve company information"
        )

# ========== STRIPE PAYMENT ENDPOINTS ==========

@api_router.post("/checkout/session")
async def create_checkout_session(checkout: CheckoutRequest, request: Request):
    """Create Stripe checkout session"""
    try:
        # Initialize Stripe
        stripe_checkout = get_stripe_checkout(request)
        
        # Calculate total from cart items (server-side security)
        total_amount = 0.0
        products = []
        
        for item in checkout.cart_items:
            # Validate product exists and get server-side price
            if item.product_id not in PRODUCT_PACKAGES:
                raise HTTPException(status_code=400, detail=f"Invalid product: {item.product_id}")
            
            server_price = PRODUCT_PACKAGES[item.product_id]
            item_total = server_price * item.quantity
            total_amount += item_total
            
            products.append({
                "product_id": item.product_id,
                "quantity": item.quantity,
                "unit_price": server_price,
                "total": item_total
            })
        
        # Add shipping cost based on detected location
        location_data = await detect_location(request)
        shipping_cost = location_data.shipping_cost
        total_amount += shipping_cost
        currency = location_data.currency.lower()
        
        # Build success and cancel URLs
        origin_url = checkout.origin_url.rstrip('/')
        success_url = f"{origin_url}/payment-success?session_id={{CHECKOUT_SESSION_ID}}"
        cancel_url = f"{origin_url}/payment-cancelled"
        
        # Create checkout session
        checkout_request = CheckoutSessionRequest(
            amount=total_amount,
            currency=currency,
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={
                "customer_email": checkout.customer_info.get("email", ""),
                "customer_name": checkout.customer_info.get("name", ""),
                "source": "josmose_checkout",
                "products_count": str(len(checkout.cart_items))
            }
        )
        
        session: CheckoutSessionResponse = await stripe_checkout.create_checkout_session(checkout_request)
        
        # Create payment transaction record
        transaction = PaymentTransaction(
            session_id=session.session_id,
            amount=total_amount,
            currency=currency,
            metadata=checkout_request.metadata,
            customer_email=checkout.customer_info.get("email"),
            products=products,
            payment_status="pending",
            status="initiated"
        )
        
        await db.payment_transactions.insert_one(transaction.dict())
        
        logging.info(f"Checkout session created: {session.session_id} for {total_amount} {currency}")
        
        return {"url": session.url, "session_id": session.session_id}
        
    except Exception as e:
        logging.error(f"Checkout session creation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/checkout/status/{session_id}")
async def get_checkout_status(session_id: str, request: Request):
    """Get checkout session status"""
    try:
        # Initialize Stripe
        stripe_checkout = get_stripe_checkout(request)
        
        # Get status from Stripe
        status_response: CheckoutStatusResponse = await stripe_checkout.get_checkout_status(session_id)
        
        # Update database record
        existing_transaction = await db.payment_transactions.find_one({"session_id": session_id})
        if existing_transaction:
            update_data = {
                "payment_status": status_response.payment_status,
                "status": status_response.status,
                "updated_at": datetime.utcnow()
            }
            
            await db.payment_transactions.update_one(
                {"session_id": session_id},
                {"$set": update_data}
            )
            
            # If payment is successful, create order
            if status_response.payment_status == "paid" and existing_transaction.get("status") != "completed":
                await create_order_from_payment(existing_transaction, status_response)
                
                # Mark as completed to avoid duplicate processing
                await db.payment_transactions.update_one(
                    {"session_id": session_id},
                    {"$set": {"status": "completed"}}
                )
        
        return {
            "session_id": session_id,
            "status": status_response.status,
            "payment_status": status_response.payment_status,
            "amount_total": status_response.amount_total,
            "currency": status_response.currency,
            "metadata": status_response.metadata
        }
        
    except Exception as e:
        logging.error(f"Status check failed for session {session_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/webhook/stripe")
async def stripe_webhook(request: Request):
    """Handle Stripe webhook events"""
    try:
        # Get raw request body
        body = await request.body()
        stripe_signature = request.headers.get("Stripe-Signature")
        
        # Initialize Stripe
        stripe_checkout = get_stripe_checkout(request)
        
        # Process webhook
        webhook_response = await stripe_checkout.handle_webhook(body, stripe_signature)
        
        # Handle the webhook event
        if webhook_response.event_type == "checkout.session.completed":
            session_id = webhook_response.session_id
            
            # Update transaction status
            await db.payment_transactions.update_one(
                {"session_id": session_id},
                {"$set": {
                    "payment_status": webhook_response.payment_status,
                    "updated_at": datetime.utcnow()
                }}
            )
            
            logging.info(f"Webhook processed: {webhook_response.event_type} for session {session_id}")
        
        return {"status": "success"}
        
    except Exception as e:
        logging.error(f"Webhook processing failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))

async def create_order_from_payment(transaction_data: Dict, payment_status: CheckoutStatusResponse):
    """Create order from successful payment"""
    try:
        # Extract order data from transaction
        order = Order(
            customer_email=transaction_data.get("customer_email", ""),
            customer_name=payment_status.metadata.get("customer_name", ""),
            customer_phone="",  # Would be collected in checkout form
            customer_address={},  # Would be collected in checkout form
            items=[
                CartItem(
                    product_id=product["product_id"],
                    quantity=product["quantity"],
                    price=product["unit_price"]
                ) for product in transaction_data.get("products", [])
            ],
            subtotal=transaction_data.get("amount", 0.0),
            shipping_cost=0.0,  # Already included in amount
            total=transaction_data.get("amount", 0.0),
            currency=transaction_data.get("currency", "eur"),
            status="paid",
            payment_method="stripe",
            lead_source="website"
        )
        
        # Sauvegarder la commande
        await db.orders.insert_one(order.dict())
        
        # 🔥 NOUVELLES FONCTIONNALITÉS AUTOMATIQUES 🔥
        
        # 1. Confirmer l'utilisation du stock pour chaque produit
        for item in order.items:
            if item.product_id not in ["garantie-2ans", "garantie-5ans", "installation-service"]:  # Services illimités
                await inventory_manager.confirm_stock_usage(item.product_id, item.quantity)
        
        # 2. Générer automatiquement la facture PDF
        try:
            invoice_result = await inventory_manager.create_invoice_for_order(order.dict())
            if invoice_result.get("success"):
                logging.info(f"✅ Invoice created for order {order.id}: {invoice_result.get('invoice_id')}")
        except Exception as e:
            logging.error(f"❌ Failed to create invoice for order {order.id}: {e}")
        
        # 3. Créer le suivi de commande automatiquement
        try:
            tracking_result = await inventory_manager.create_order_tracking(order.dict())
            if tracking_result.get("success"):
                logging.info(f"✅ Tracking created for order {order.id}: {tracking_result.get('tracking_number')}")
        except Exception as e:
            logging.error(f"❌ Failed to create tracking for order {order.id}: {e}")
        
        logging.info(f"🎉 Order created with all automation: {order.id} for {order.customer_email}")
        
    except Exception as e:
        logging.error(f"Failed to create order from payment: {e}")


# ========== INITIALIZATION ==========

async def initialize_products():
    """Initialize products with real data from CDC"""
    products = [
        {
            "id": "osmoseur-principal",
            "name": "Fontaine à Eau Osmosée BlueMountain",
            "description": "Système d'osmose inverse professionnel BlueMountain. Production 380L/jour (16L/h). Eau chaude, froide et tempérée. Membrane 100GPD encapsulée. Prix spécial : 499€ au lieu de 599€.",
            "price": 499.0,
            "original_price": 599.0,
            "image": "https://www.josmose.fr/2570-large_default/fontaine-osmoseur-minibluesea.jpg",
            "category": "osmoseur",
            "target_audience": "both",
            "specifications": {
                "Production d'eau": "Jusqu'à 380 litres/jour (16L/h)",
                "Membrane": "100GPD encapsulée",
                "Filtration": "PP et CTO pré-filtres",
                "Type": "Osmose Inverse (RO)",
                "Installation": "Raccordement et évacuation réseau",
                "Garantie": "1 à 5 ans selon option",
                "Températures": "Eau chaude, froide et tempérée"
            },
            "features": [
                "Production jusqu'à 380 litres/jour (16 litres/heure)",
                "Membrane 100GPD encapsulée haute performance",
                "Pré-filtres PP et CTO inclus",
                "Eau chaude, froide et tempérée disponible",
                "Installation avec raccordement réseau",
                "Dimensions compactes: 56×41×30 cm",
                "Technologie BlueMountain avancée",
                "Service après-vente professionnel",
                "Compatible usage domestique et bureau"
            ],
            "images_gallery": [
                "https://www.josmose.fr/2570-large_default/fontaine-osmoseur-minibluesea.jpg",
                "https://www.josmose.fr/2566-small_default/fontaine-osmoseur-minibluesea.jpg",
                "https://www.josmose.fr/img/cms/BlueSea/BlueMountain/Sch%C3%A9ma_Blue_Mountain-removebg-preview.png",
                "https://www.josmose.fr/img/cms/fontaine_a_eau_entreprise%20-%20copie.jpg"
            ],
            "in_stock": True
        },
        {
            "id": "fontaine-ultrafiltration",
            "name": "Fontaine Intelligente H₂O",
            "description": "Fontaine d'eau intelligente avec contrôle digital du bout des doigts. Température réglable en 3 secondes, installation plug & play, sécurité enfant intégrée.",
            "price": 399.0,
            "original_price": 499.0,
            "image": "https://static.wixstatic.com/media/6af6bd_d5ec79a577694414b12e794e8a30e3bb~mv2.png/v1/fill/w_558,h_684,al_c,q_90,usm_0.66_1.00_0.01,enc_avif,quality_auto/Hf8e72e690708417d8f7fae61845a5e804_png_720x720q50.png",
            "category": "osmoseur", 
            "target_audience": "both",
            "specifications": {
                "Type": "Fontaine intelligente",
                "Contrôle": "Digital tactile",
                "Réglage température": "3 secondes",
                "Installation": "Plug & Play - simple branchement",
                "Sécurité": "Protection enfant intégrée",
                "Design": "Minimaliste et élégant"
            },
            "features": [
                "Contrôlez l'eau du bout des doigts grâce au filtre H20",
                "Température réglable en 3 secondes seulement",
                "Installation ultra-simple - brancher c'est l'installer",
                "L'essayer c'est l'adopter - satisfaction garantie",
                "Stérilisation avancée - adieu pollution, gardez minéraux",
                "Contrôle précis quantité et température",
                "Sécurité enfant activable en un clic",
                "Design minimaliste qui s'adapte à votre cuisine",
                "Technologie française innovante"
            ],
            "images_gallery": [
                "https://static.wixstatic.com/media/6af6bd_d5ec79a577694414b12e794e8a30e3bb~mv2.png/v1/fill/w_558,h_684,al_c,q_90,usm_0.66_1.00_0.01,enc_avif,quality_auto/Hf8e72e690708417d8f7fae61845a5e804_png_720x720q50.png",
                "https://static.wixstatic.com/media/6af6bd_1b0ed5e9b180466baeee7436019f6fef~mv2.png/v1/fill/w_520,h_692,al_c,lg_1,q_85,enc_avif,quality_auto/H10e839a4d05e44ab881e05d9aeb3e0d80_jpg_720x720q50-removebg-preview.png",
                "https://static.wixstatic.com/media/6af6bd_16baeaf62afc42009cf6ece2f46c767a~mv2.png/v1/fill/w_797,h_487,al_c,q_90,usm_0.66_1.00_0.01,enc_avif,quality_auto/Les%20b%C3%A9b%C3%A9s%20pleurent%20quand%20ils%20ont%20faim%2C%20ne%20peuvent%20pas%20attendre__%20c'est%20touj_20250220_19362.png"
            ],
            "in_stock": True
        },
        {
            "id": "osmoseur-pro",
            "name": "Système Osmose Inverse Professionnel BlueMountain Grand Format",
            "description": "Solution professionnelle BlueMountain grand format pour restaurants, bureaux et commerces. Dimensions 1040×330×300mm avec même performance 15L/h.",
            "price": 899.0,
            "original_price": 1199.0,
            "image": "https://www.josmose.fr/img/cms/fontaine_a_eau_entreprise%20-%20copie.jpg",
            "category": "osmoseur",
            "target_audience": "B2B",
            "specifications": {
                "Type": "BlueMountain Grand Format",
                "Dimensions": "1040×330×300mm",
                "Production": "15 litres/heure identique",
                "Installation": "Professionnelle incluse", 
                "Garantie": "5 ans pièces et main-d'œuvre",
                "Support": "Technique dédié professionnel"
            },
            "features": [
                "Système BlueMountain grand format pour entreprises",
                "Même performance que petit format: 15L/h",
                "Production eau froide <10° - 4 litres/heure",
                "Production eau chaude >90° - 5 litres/heure",
                "Dimensions optimisées: 1040×330×300mm",
                "Installation professionnelle par technicien certifié",
                "Maintenance préventive incluse",
                "Formation du personnel à l'utilisation",
                "Support technique prioritaire B2B",
                "Certification sanitaire entreprise"
            ],
            "images_gallery": [
                "https://www.josmose.fr/img/cms/fontaine_a_eau_entreprise%20-%20copie.jpg",
                "https://www.josmose.fr/2570-large_default/fontaine-osmoseur-minibluesea.jpg",
                "https://www.josmose.fr/img/cms/BlueSea/BlueMountain/Sch%C3%A9ma_Blue_Mountain-removebg-preview.png"
            ],
            "in_stock": True
        },
        {
            "id": "filtres-rechange",
            "name": "Kit Filtres de Rechange - 4 Étapes",
            "description": "Lot complet de filtres de rechange selon CDC. Kit 4 étapes : PP + GAC + CTO + Membrane UF. À partir du 6ème mois - 49€.",
            "price": 49.0,
            "image": "https://static.wixstatic.com/media/6af6bd_1b0ed5e9b180466baeee7436019f6fef~mv2.png/v1/fill/w_520,h_692,al_c,lg_1,q_85,enc_avif,quality_auto/H10e839a4d05e44ab881e05d9aeb3e0d80_jpg_720x720q50-removebg-preview.png",
            "category": "accessoire",
            "target_audience": "both",
            "specifications": {
                "Contenu": "4 cartouches complètes",
                "Compatibilité": "Tous systèmes Josmose", 
                "Fréquence": "Changement tous les 6 mois",
                "Qualité": "Filtres certifiés d'origine"
            },
            "features": [
                "Filtre PP - Polypropylène (grosses particules >5 microns)",
                "Filtre GAC - Charbon actif granulés (chlore + organiques)", 
                "Filtre CTO - Charbon actif bloc (reste chlore)",
                "Membrane Ultrafiltration (virus, bactéries, 0.01 micron)",
                "Compatible avec système principal",
                "Installation facile avec instructions",
                "Maintient efficacité optimale",
                "Cartouches à baïonnette"
            ],
            "in_stock": True
        },
        {
            "id": "filtres-pro",
            "name": "Filtres Professionnels - Pack Annuel",
            "description": "Pack de filtres professionnels pour systèmes industriels. Qualité supérieure avec suivi de maintenance.",
            "price": 89.0,
            "image": "https://www.josmose.fr/img/cms/BlueSea/BlueMountain/Sch%C3%A9ma_Blue_Mountain-removebg-preview.png",
            "category": "accessoire",
            "target_audience": "B2B",
            "specifications": {
                "Compatibilité": "Systèmes professionnels BlueMountain",
                "Durée de vie": "12 mois",
                "Contenu": "8 cartouches premium + indicateurs"
            },
            "features": [
                "Filtres industriels haute performance",
                "Indicateurs de remplacement intelligent",
                "Maintenance programmée incluse",
                "Certification qualité professionnelle"
            ],
            "in_stock": True
        },
        {
            "id": "garantie-2ans", 
            "name": "Extension Garantie 2 ans - 39€",
            "description": "Étendez votre garantie à 2 ans selon tarif CDC. Tranquillité d'esprit totale avec support technique.",
            "price": 39.0,
            "image": "https://images.unsplash.com/photo-1556740749-887f6717d7e4?w=400&h=300&fit=crop&auto=format",
            "category": "service",
            "target_audience": "both",
            "specifications": {
                "Durée": "2 ans à partir de l'achat",
                "Couverture": "Pièces et main d'œuvre",
                "Service": "Support technique inclus"
            },
            "features": [
                "Support téléphonique prioritaire",
                "Remplacement gratuit des pièces défectueuses", 
                "Service après-vente dédié"
            ],
            "in_stock": True
        },
        {
            "id": "garantie-5ans", 
            "name": "Extension Garantie 5 ans - 59€",
            "description": "Protection maximale avec garantie étendue à 5 ans selon tarif CDC. Couverture complète premium.",
            "price": 59.0,
            "image": "https://images.unsplash.com/photo-1621905251189-08b45d6a269e?w=400&h=300&fit=crop&auto=format",
            "category": "service",
            "target_audience": "both",
            "specifications": {
                "Durée": "5 ans à partir de l'achat",
                "Couverture": "Pièces et main d'œuvre",
                "Service": "Support technique premium"
            },
            "features": [
                "Support téléphonique prioritaire",
                "Remplacement gratuit des pièces",
                "Maintenance préventive incluse",
                "Service après-vente premium"
            ],
            "in_stock": True
        },
        {
            "id": "installation-service",
            "name": "Service d'Installation Professionnel",
            "description": "Installation complète par nos techniciens certifiés. Mise en service et formation incluses. Service après-vente garanti.",
            "price": 150.0,
            "image": "https://images.unsplash.com/photo-1589652717406-1c69efaf1ff8?w=400&h=300&fit=crop&auto=format",
            "category": "service",
            "target_audience": "both",
            "specifications": {
                "Durée": "2-3 heures",
                "Inclus": "Installation, test, formation",
                "Zone": "France et Espagne"
            },
            "features": [
                "Technicien certifié à domicile",
                "Installation simple sans électricité",
                "Test complet du système 4 étapes",
                "Formation complète à l'utilisation", 
                "Garantie installation 2 ans",
                "Support technique post-installation"
            ],
            "in_stock": True
        }
    ]
    
    for product in products:
        await db.products.replace_one({"id": product["id"]}, product, upsert=True)
    
    logging.info("Products initialized with real CDC images and specifications")

# Router inclusion moved to end of file after all routes are defined

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("startup")
async def startup_db():
    await initialize_products()
    
    # Initialize marketing automation
    global marketing_automation
    marketing_automation = get_marketing_automation(db)
    
    # Initialize inventory management
    global inventory_manager
    inventory_manager = get_inventory_manager(db)
    await inventory_manager.initialize_stock()
    
    # Initialize social media automation
    global social_media_automation
    social_media_automation = get_social_media_automation(db)
    await social_media_automation.initialize_accounts()

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()


# ========== AUTHENTICATION ENDPOINTS ==========

@api_router.post("/auth/login")
async def login(user_auth: UserAuth) -> Token:
    """Login endpoint for CRM access"""
    # Authenticate user (now supports email login)
    user_data = authenticate_user(user_auth.username, user_auth.password)
    
    if not user_data:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"  # Updated message for email login
        )
    
    # Create JWT token
    access_token = create_access_token(data={"sub": user_data["username"]})
    
    # Update last login
    user_data["last_login"] = datetime.utcnow()
    
    user = User(
        id=user_data["id"],
        username=user_data["username"],
        email=user_data["email"],
        full_name=user_data["full_name"],
        role=user_data["role"],
        is_active=user_data["is_active"],
        created_at=datetime.utcnow(),
        last_login=datetime.utcnow()
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=user
    )

@api_router.get("/auth/me")
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return current_user


# ========== NEW INVENTORY & STOCK MANAGEMENT ENDPOINTS ==========

@api_router.get("/products/{product_id}/stock")
async def get_product_stock(product_id: str):
    """Obtenir le statut du stock d'un produit (pour affichage public)"""
    try:
        stock_status = await inventory_manager.get_stock_status(product_id)
        
        # Retourner seulement les infos nécessaires pour le public
        return {
            "product_id": product_id,
            "in_stock": stock_status.get("available_stock", 0) > 0,
            "show_stock_warning": stock_status.get("show_stock_warning", False),
            "stock_warning_text": stock_status.get("stock_warning_text"),
            "available_stock": stock_status.get("available_stock", 0) if stock_status.get("available_stock", 0) > 5 else "Quelques unités"
        }
        
    except Exception as e:
        logging.error(f"Error getting product stock: {e}")
        return {"in_stock": True, "show_stock_warning": False}

@crm_router.get("/inventory/dashboard")
async def get_inventory_dashboard(
    current_user: User = Depends(require_role(["manager", "agent"]))
):
    """Dashboard de gestion des stocks pour le CRM"""
    try:
        all_stock = await inventory_manager.get_all_stock_status()
        
        # Compter les alertes par niveau
        alert_counts = {"critical": 0, "warning": 0, "normal": 0, "optimal": 0}
        for item in all_stock:
            level = item.get("alert_level", "normal")
            alert_counts[level] = alert_counts.get(level, 0) + 1
        
        # Produits nécessitant un réapprovisionnement
        restock_needed = [item for item in all_stock if item.get("reorder_needed")]
        
        return {
            "stock_items": all_stock,
            "alert_summary": alert_counts,
            "critical_items": [item for item in all_stock if item.get("alert_level") == "critical"],
            "restock_needed": restock_needed,
            "total_products": len(all_stock),
            "last_updated": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logging.error(f"Error getting inventory dashboard: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors du chargement du dashboard stock")

@crm_router.post("/inventory/restock/{product_id}")
async def restock_product(
    product_id: str, 
    quantity: int,
    current_user: User = Depends(require_role(["manager"]))
):
    """Réapprovisionner un produit"""
    try:
        # Mettre à jour le stock
        await db.stock_items.update_one(
            {"product_id": product_id},
            {
                "$inc": {
                    "current_stock": quantity,
                    "available_stock": quantity
                },
                "$set": {
                    "last_restocked": datetime.utcnow(),
                    "next_restock_due": datetime.utcnow() + timedelta(days=90),  # 3 mois
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        # Log de l'opération
        await db.stock_operations.insert_one({
            "operation_type": "restock",
            "product_id": product_id,
            "quantity": quantity,
            "performed_by": current_user.username,
            "timestamp": datetime.utcnow(),
            "notes": f"Réapprovisionnement de {quantity} unités"
        })
        
        return {"message": f"Stock mis à jour: +{quantity} unités", "success": True}
        
    except Exception as e:
        logging.error(f"Error restocking product: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors du réapprovisionnement")

@crm_router.get("/invoices")
async def get_all_invoices(
    limit: int = 100,
    current_user: User = Depends(require_role(["manager", "agent"]))
):
    """Obtenir toutes les factures"""
    try:
        invoices = await db.invoices.find().sort("created_at", -1).limit(limit).to_list(limit)
        return invoices
        
    except Exception as e:
        logging.error(f"Error getting invoices: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors du chargement des factures")

@crm_router.get("/invoices/{invoice_id}")
async def get_invoice(
    invoice_id: str,
    current_user: User = Depends(require_role(["manager", "agent"]))
):
    """Obtenir une facture spécifique"""
    try:
        invoice = await db.invoices.find_one({"invoice_id": invoice_id})
        if not invoice:
            raise HTTPException(status_code=404, detail="Facture non trouvée")
        
        return invoice
        
    except Exception as e:
        logging.error(f"Error getting invoice: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors du chargement de la facture")

@crm_router.get("/orders/{order_id}/tracking")
async def get_order_tracking(
    order_id: str,
    current_user: User = Depends(require_role(["manager", "agent"]))
):
    """Obtenir le suivi d'une commande"""
    try:
        tracking = await db.order_tracking.find_one({"order_id": order_id})
        if not tracking:
            raise HTTPException(status_code=404, detail="Suivi non trouvé")
        
        return tracking
        
    except Exception as e:
        logging.error(f"Error getting order tracking: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors du chargement du suivi")

@crm_router.put("/orders/{order_id}/status")
async def update_order_status(
    order_id: str,
    status_data: Dict[str, Any],
    current_user: User = Depends(require_role(["manager", "agent"]))
):
    """Mettre à jour le statut d'une commande"""
    try:
        new_status = status_data.get("status")
        message = status_data.get("message", "")
        
        result = await inventory_manager.update_order_status(order_id, new_status, message)
        
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error"))
        
        return {"message": "Statut mis à jour avec succès", "new_status": new_status}
        
    except Exception as e:
        logging.error(f"Error updating order status: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la mise à jour")

@api_router.get("/customer/profile/{email}")
async def get_customer_profile(email: str):
    """Obtenir le profil d'un client"""
    try:
        profile = await db.customer_profiles.find_one({"email": email})
        if not profile:
            # Créer un profil par défaut
            default_profile = CustomerProfile(email=email, name="Client")
            await db.customer_profiles.insert_one(default_profile.dict())
            return default_profile.dict()
        
        return profile
        
    except Exception as e:
        logging.error(f"Error getting customer profile: {e}")
        return None

@api_router.put("/customer/profile/{email}")
async def update_customer_profile(email: str, profile_data: Dict[str, Any]):
    """Mettre à jour le profil d'un client"""
    try:
        profile_data["updated_at"] = datetime.utcnow()
        
        await db.customer_profiles.update_one(
            {"email": email},
            {"$set": profile_data},
            upsert=True
        )
        
        return {"message": "Profil mis à jour avec succès"}
        
    except Exception as e:
        logging.error(f"Error updating customer profile: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la mise à jour du profil")

@api_router.get("/tracking/{tracking_number}")
async def public_tracking(tracking_number: str):
    """Suivi public d'une commande (sans authentification)"""
    try:
        tracking = await db.order_tracking.find_one({"tracking_number": tracking_number})
        if not tracking:
            raise HTTPException(status_code=404, detail="Numéro de suivi non trouvé")
        
        # Retourner seulement les infos publiques
        return {
            "tracking_number": tracking.get("tracking_number"),
            "status": tracking.get("status"),
            "status_history": tracking.get("status_history", []),
            "estimated_delivery": tracking.get("estimated_delivery"),
            "carrier": tracking.get("carrier")
        }
        
    except Exception as e:
        logging.error(f"Error getting public tracking: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors du suivi")


# ========== SOCIAL MEDIA AUTOMATION ENDPOINTS ==========

@crm_router.get("/social-media/dashboard")
async def get_social_media_dashboard(
    current_user: User = Depends(require_role(["manager", "agent"]))
):
    """Dashboard des réseaux sociaux et marketing automation"""
    try:
        dashboard_data = await social_media_automation.get_social_media_dashboard()
        return dashboard_data
        
    except Exception as e:
        logging.error(f"Error getting social media dashboard: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors du chargement du dashboard social media")

@crm_router.get("/campaigns")
async def get_all_campaigns(
    platform: str = None,
    status: str = None,
    current_user: User = Depends(require_role(["manager", "agent"]))
):
    """Obtenir toutes les campagnes publicitaires"""
    try:
        query = {}
        if platform:
            query["platform"] = platform
        if status:
            query["status"] = status
            
        campaigns = await db.campaigns.find(query).sort("created_at", -1).to_list(100)
        
        # Enrichir avec les performances
        performance_data = await social_media_automation.get_campaign_performance()
        
        for campaign in campaigns:
            perf = next((p for p in performance_data if p["campaign_id"] == campaign["campaign_id"]), {})
            campaign["performance"] = perf
        
        return campaigns
        
    except Exception as e:
        logging.error(f"Error getting campaigns: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors du chargement des campagnes")

@crm_router.post("/campaigns")
async def create_campaign(
    campaign_data: Dict[str, Any],
    current_user: User = Depends(require_role(["manager"]))
):
    """Créer une nouvelle campagne publicitaire"""
    try:
        result = await social_media_automation.create_campaign(
            name=campaign_data.get("name"),
            platform=campaign_data.get("platform"),
            objective=campaign_data.get("objective", "conversions"),
            budget=campaign_data.get("budget", 50.0),
            target_country=campaign_data.get("target_country", "FR"),
            target_language=campaign_data.get("target_language", "fr")
        )
        
        if result.get("success"):
            return {"message": "Campagne créée avec succès", **result}
        else:
            raise HTTPException(status_code=400, detail=result.get("error", "Erreur lors de la création"))
            
    except Exception as e:
        logging.error(f"Error creating campaign: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la création de la campagne")

@crm_router.post("/campaigns/optimize-budget")
async def optimize_campaign_budgets(
    current_user: User = Depends(require_role(["manager"]))
):
    """Optimiser automatiquement l'allocation du budget des campagnes"""
    try:
        result = await social_media_automation.optimize_budget_allocation()
        
        if result.get("success"):
            return {"message": "Budget optimisé avec succès", **result}
        else:
            raise HTTPException(status_code=400, detail=result.get("error", "Erreur lors de l'optimisation"))
            
    except Exception as e:
        logging.error(f"Error optimizing budget: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de l'optimisation du budget")

@crm_router.post("/content/generate")
async def generate_social_content(
    content_request: Dict[str, Any],
    current_user: User = Depends(require_role(["manager", "agent"]))
):
    """Générer du contenu pour les réseaux sociaux avec AI"""
    try:
        content = await social_media_automation.generate_content_ai(
            content_type=content_request.get("type", "post"),
            platform=content_request.get("platform", "facebook"),
            language=content_request.get("language", "fr"),
            product_focus=content_request.get("product_focus", "osmoseur")
        )
        
        return {"content_generated": True, "content": content}
        
    except Exception as e:
        logging.error(f"Error generating content: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la génération de contenu")

@crm_router.get("/creatives")
async def get_ad_creatives(
    campaign_id: str = None,
    platform: str = None,
    current_user: User = Depends(require_role(["manager", "agent"]))
):
    """Obtenir les créatifs publicitaires"""
    try:
        query = {}
        if campaign_id:
            query["campaign_id"] = campaign_id
        if platform:
            query["platform"] = platform
            
        creatives = await db.ad_creatives.find(query).sort("created_at", -1).to_list(100)
        return creatives
        
    except Exception as e:
        logging.error(f"Error getting creatives: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors du chargement des créatifs")

@crm_router.get("/performance")
async def get_campaign_performance(
    campaign_id: str = None,
    current_user: User = Depends(require_role(["manager", "agent"]))
):
    """Obtenir les performances des campagnes"""
    try:
        performance_data = await social_media_automation.get_campaign_performance(campaign_id)
        return performance_data
        
    except Exception as e:
        logging.error(f"Error getting performance data: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors du chargement des performances")

@api_router.post("/abandoned-cart-retargeting")
async def setup_abandoned_cart_retargeting(retargeting_data: Dict[str, Any]):
    """Configurer le retargeting pour panier abandonné (endpoint public)"""
    try:
        result = await social_media_automation.setup_abandoned_cart_retargeting(
            customer_email=retargeting_data.get("customer_email"),
            cart_items=retargeting_data.get("cart_items", []),
            platform=retargeting_data.get("platform", "facebook")
        )
        
        if result.get("success"):
            logging.info(f"Abandoned cart retargeting setup for {retargeting_data.get('customer_email')}")
        
        return result
        
    except Exception as e:
        logging.error(f"Error setting up abandoned cart retargeting: {e}")
        return {"success": False, "error": str(e)}

@crm_router.post("/landing-page")
async def create_campaign_landing_page(
    landing_data: Dict[str, Any],
    current_user: User = Depends(require_role(["manager"]))
):
    """Créer une landing page pour une campagne"""
    try:
        result = await social_media_automation.create_landing_page(
            campaign_id=landing_data.get("campaign_id"),
            target_audience=landing_data.get("target_audience", {}),
            language=landing_data.get("language", "fr")
        )
        
        if result.get("success"):
            return {"message": "Landing page créée avec succès", **result}
        else:
            raise HTTPException(status_code=400, detail=result.get("error", "Erreur lors de la création"))
            
    except Exception as e:
        logging.error(f"Error creating landing page: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la création de la landing page")

@crm_router.get("/abandoned-cart-campaigns")
async def get_abandoned_cart_campaigns(
    current_user: User = Depends(require_role(["manager", "agent"]))
):
    """Obtenir les campagnes de panier abandonné actives"""
    try:
        campaigns = await db.abandoned_cart_campaigns.find({"status": "active"}).sort("created_at", -1).to_list(100)
        return campaigns
        
    except Exception as e:
        logging.error(f"Error getting abandoned cart campaigns: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors du chargement des campagnes panier abandonné")

@crm_router.get("/social-accounts")
async def get_social_media_accounts(
    current_user: User = Depends(require_role(["manager", "agent"]))
):
    """Obtenir les comptes de réseaux sociaux"""
    try:
        accounts = await db.social_media_accounts.find().sort("platform", 1).to_list(100)
        return accounts
        
    except Exception as e:
        logging.error(f"Error getting social media accounts: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors du chargement des comptes")

@crm_router.put("/social-accounts/{account_id}")
async def update_social_media_account(
    account_id: str,
    account_data: Dict[str, Any],
    current_user: User = Depends(require_role(["manager"]))
):
    """Mettre à jour un compte de réseau social"""
    try:
        account_data["updated_at"] = datetime.utcnow()
        
        await db.social_media_accounts.update_one(
            {"account_id": account_id},
            {"$set": account_data}
        )
        
        return {"message": "Compte mis à jour avec succès"}
        
    except Exception as e:
        logging.error(f"Error updating social media account: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la mise à jour du compte")


# ========== PROTECTED CRM ENDPOINTS ==========

@crm_router.get("/dashboard/advanced")
async def get_advanced_crm_dashboard(
    current_user: User = Depends(require_role(["manager", "agent", "technique"]))
):
    """Advanced CRM dashboard with detailed analytics"""
    try:
        # Get basic dashboard data
        basic_dashboard = await get_crm_dashboard()
        
        # Add advanced metrics
        advanced_metrics = await get_advanced_analytics()
        
        # Marketing automation stats
        automation_stats = await get_automation_stats()
        
        return {
            **basic_dashboard,
            "advanced_metrics": advanced_metrics,
            "automation": automation_stats,
            "user": {
                "name": current_user.full_name,
                "role": current_user.role,
                "permissions": get_user_permissions(current_user.role)
            }
        }
        
    except Exception as e:
        logger.error(f"Advanced dashboard query failed: {e}")
        raise HTTPException(status_code=500, detail="Error loading advanced dashboard")

@crm_router.get("/marketing/campaigns")
async def get_marketing_campaigns(
    current_user: User = Depends(require_role(["manager"]))
):
    """Get all marketing campaigns"""
    campaigns_data = await db.marketing_campaigns.find().sort("created_at", -1).to_list(100)
    return campaigns_data

@crm_router.post("/marketing/campaigns")
async def create_marketing_campaign(
    campaign_data: Dict[str, Any],
    current_user: User = Depends(require_role(["manager"]))
):
    """Create new marketing campaign"""
    campaign = {
        "id": str(uuid.uuid4()),
        "created_by": current_user.username,
        "created_at": datetime.utcnow(),
        **campaign_data
    }
    
    await db.marketing_campaigns.insert_one(campaign)
    return campaign

@crm_router.get("/automation/logs")
async def get_automation_logs(
    limit: int = 100,
    current_user: User = Depends(require_role(["manager", "agent", "technique"]))
):
    """Get automation logs (emails, SMS, WhatsApp)"""
    
    # Get recent email logs
    email_logs = await db.email_logs.find().sort("sent_at", -1).limit(limit//3).to_list(limit//3)
    
    # Get recent SMS logs
    sms_logs = await db.sms_logs.find().sort("sent_at", -1).limit(limit//3).to_list(limit//3)
    
    # Get recent WhatsApp logs  
    whatsapp_logs = await db.whatsapp_logs.find().sort("sent_at", -1).limit(limit//3).to_list(limit//3)
    
    return {
        "email_logs": email_logs,
        "sms_logs": sms_logs,  
        "whatsapp_logs": whatsapp_logs,
        "total_logs": len(email_logs) + len(sms_logs) + len(whatsapp_logs)
    }

async def get_advanced_analytics():
    """Get advanced analytics for CRM"""
    try:
        # Lead conversion funnel
        funnel_data = {}
        for status in ["new", "contacted", "qualified", "converted"]:
            count = await db.leads.count_documents({"status": status})
            funnel_data[status] = count
        
        # Revenue analytics
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        last_30_days = today - timedelta(days=30)
        
        monthly_revenue = await db.orders.aggregate([
            {"$match": {"created_at": {"$gte": last_30_days}, "status": "paid"}},
            {"$group": {"_id": None, "total": {"$sum": "$total"}}}
        ]).to_list(1)
        
        # Customer lifetime value
        avg_order_value = await db.orders.aggregate([
            {"$match": {"status": "paid"}},
            {"$group": {"_id": None, "avg": {"$avg": "$total"}}}
        ]).to_list(1)
        
        # Lead source analysis
        source_analysis = await db.leads.aggregate([
            {"$group": {"_id": "$source", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]).to_list(10)
        
        return {
            "conversion_funnel": funnel_data,
            "monthly_revenue": monthly_revenue[0]["total"] if monthly_revenue else 0,
            "avg_order_value": avg_order_value[0]["avg"] if avg_order_value else 0,
            "lead_sources": source_analysis,
            "growth_rate": calculate_growth_rate(),
            "customer_segments": await get_customer_segments()
        }
        
    except Exception as e:
        logger.error(f"Advanced analytics failed: {e}")
        return {}

async def get_automation_stats():
    """Get marketing automation statistics"""
    try:
        # Email stats
        email_stats = await db.email_logs.aggregate([
            {"$group": {
                "_id": "$type", 
                "sent": {"$sum": 1},
                "success_rate": {"$avg": {"$cond": [{"$eq": ["$status", "sent"]}, 1, 0]}}
            }}
        ]).to_list(10)
        
        # SMS stats
        sms_count = await db.sms_logs.count_documents({})
        
        # WhatsApp stats  
        whatsapp_count = await db.whatsapp_logs.count_documents({})
        
        # Scheduled actions
        pending_actions = await db.scheduled_actions.count_documents({"status": "pending"})
        
        return {
            "email_campaigns": email_stats,
            "sms_sent": sms_count,
            "whatsapp_sent": whatsapp_count,
            "pending_automations": pending_actions,
            "automation_health": "healthy" if pending_actions < 100 else "busy"
        }
        
    except Exception as e:
        logger.error(f"Automation stats failed: {e}")
        return {}

def get_user_permissions(role: str) -> List[str]:
    """Get user permissions based on role"""
    permissions_map = {
        "admin": ["all"],
        "manager": ["view_analytics", "manage_campaigns", "manage_leads", "view_reports"],
        "agent": ["manage_leads", "view_basic_analytics", "send_messages"],
        "support": ["view_logs", "manage_leads", "technical_support"]
    }
    return permissions_map.get(role, ["view_basic"])

async def calculate_growth_rate():
    """Calculate monthly growth rate"""
    # Simplified growth rate calculation
    return 15.5  # Placeholder

async def get_customer_segments():
    """Get customer segmentation data"""
    segments = await db.leads.aggregate([
        {"$group": {
            "_id": "$customer_type",
            "count": {"$sum": 1},
            "avg_score": {"$avg": "$score"}
        }}
    ]).to_list(10)
    
    return segments

# ========== ROUTER INCLUSION ==========
# Include all routers after all routes are defined
api_router.include_router(crm_router, prefix="/crm")  # Include crm_router in api_router with /crm prefix
app.include_router(api_router)