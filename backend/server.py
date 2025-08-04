from fastapi import FastAPI, APIRouter, HTTPException, Request
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime
import httpx
import re


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


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
    items: List[CartItem]
    subtotal: float
    shipping_cost: float
    total: float
    currency: str
    status: str = "pending"
    payment_method: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ContactForm(BaseModel):
    name: str
    email: str
    phone: str
    message: str
    request_type: str = "quote"  # quote, support, general
    created_at: datetime = Field(default_factory=datetime.utcnow)

class CountryDetection(BaseModel):
    country_code: str
    country_name: str
    currency: str
    language: str
    shipping_cost: float


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
    return {"message": "Josmose.com API - Système d'Osmose Inverse"}

@api_router.get("/detect-location")
async def detect_location(request: Request):
    """Detect user location, currency, and language"""
    client_ip = get_client_ip(request)
    country_code = await detect_country_from_ip(client_ip)
    
    if not country_code:
        # Fallback to Accept-Language header
        accept_language = request.headers.get("accept-language", "")
        detected_language = detect_language_from_header(accept_language)
        
        # Default country based on language
        lang_country_map = {"fr": "FR", "es": "ES", "de": "DE", "it": "IT"}
        country_code = lang_country_map.get(detected_language, "FR")
    
    config = COUNTRY_CONFIG.get(country_code, COUNTRY_CONFIG["FR"])
    
    return CountryDetection(
        country_code=country_code,
        country_name=config["name"],
        currency=config["currency"],
        language=config["language"],
        shipping_cost=config["shipping"]
    )

@api_router.get("/products")
async def get_products():
    """Get all products"""
    products_data = await db.products.find().to_list(1000)
    if not products_data:
        # Initialize with default products if empty
        await initialize_products()
        products_data = await db.products.find().to_list(1000)
    
    return [Product(**product) for product in products_data]

@api_router.get("/products/{product_id}")
async def get_product(product_id: str):
    """Get single product"""
    product_data = await db.products.find_one({"id": product_id})
    if not product_data:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return Product(**product_data)

@api_router.post("/orders")
async def create_order(order: Order):
    """Create new order"""
    order_dict = order.dict()
    await db.orders.insert_one(order_dict)
    
    # Send order confirmation (placeholder)
    logging.info(f"New order created: {order.id} for {order.customer_email}")
    
    return order

@api_router.post("/contact")
async def submit_contact_form(form: ContactForm):
    """Submit contact form"""
    form_dict = form.dict()
    await db.contact_forms.insert_one(form_dict)
    
    logging.info(f"New contact form: {form.email} - {form.request_type}")
    
    return {"message": "Votre demande a été envoyée avec succès!"}

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


# ========== INITIALIZATION ==========

async def initialize_products():
    """Initialize products in database"""
    products = [
        {
            "id": "osmoseur-principal",
            "name": "Fontaine à Eau Osmosée - Système d'Ultrafiltration",
            "description": "Système de filtration d'eau par osmose inverse avec 4 étapes de filtration. Élimine virus, bactéries, chlore et particules organiques. Installation simple sans électricité.",
            "price": 499.0,
            "original_price": 599.0,
            "image": "https://images.unsplash.com/photo-1610312973684-e47446aa260b",
            "category": "osmoseur",
            "specifications": {
                "Débit": "Variable selon pression réseau",
                "Filtration": "4 étapes (PP, GAC, CTO, Ultrafiltration)",
                "Taille des pores": "0,01 micron",
                "Installation": "Sans électricité",
                "Garantie": "1 an incluse"
            },
            "features": [
                "Élimination des virus et bactéries",
                "Réduction du chlore et particules organiques",
                "Installation simple sans professionnel",
                "Design compact et élégant",
                "Aucun rejet d'eau",
                "Cartouches à baïonnette faciles à changer"
            ],
            "in_stock": True
        },
        {
            "id": "filtres-rechange",
            "name": "Lot de Filtres de Rechange",
            "description": "Set complet de filtres de rechange pour votre système d'osmose. Durée recommandée : 6 mois.",
            "price": 49.0,
            "image": "https://images.unsplash.com/photo-1586509595512-800193191f79",
            "category": "accessoire",
            "specifications": {
                "Compatibilité": "Système osmoseur principal",
                "Durée de vie": "6 mois",
                "Contenu": "4 cartouches (PP, GAC, CTO, UF)"
            },
            "features": [
                "Cartouches haute qualité",
                "Installation facile",
                "Maintient l'efficacité de filtration",
                "Compatible avec tous nos systèmes"
            ],
            "in_stock": True
        },
        {
            "id": "garantie-2ans",
            "name": "Extension Garantie 2 ans",
            "description": "Étendez votre garantie à 2 ans pour une tranquillité d'esprit totale.",
            "price": 39.0,
            "image": "https://cdn.pixabay.com/photo/2018/07/17/21/59/water-3545115_640.jpg",
            "category": "service",
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
            "name": "Extension Garantie 5 ans",
            "description": "Protection maximale avec garantie étendue à 5 ans.",
            "price": 59.0,
            "image": "https://cdn.pixabay.com/photo/2018/07/17/21/59/water-3545115_640.jpg",
            "category": "service",
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
        }
    ]
    
    for product in products:
        await db.products.replace_one({"id": product["id"]}, product, upsert=True)
    
    logging.info("Products initialized")

# Include the router in the main app
app.include_router(api_router)

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

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()