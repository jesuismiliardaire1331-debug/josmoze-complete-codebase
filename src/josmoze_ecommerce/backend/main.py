"""
Main FastAPI application entry point for Josmoze E-commerce
Modern package structure with proper imports
"""
import os
import logging
from datetime import datetime
from fastapi import FastAPI, HTTPException, Request, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

from .routers import products, auth, crm, ai_agents
from fastapi import APIRouter

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from .services.stripe_service import StripeCheckout, CheckoutSessionResponse, CheckoutStatusResponse, CheckoutSessionRequest
    logger.info("✅ Stripe service imported successfully")
except ImportError as e:
    logger.warning(f"⚠️ Stripe service import failed: {e}")
    StripeCheckout = None

# Create the main app
app = FastAPI(
    title="Josmoze E-commerce API", 
    version="2.0.0",
    description="Modern e-commerce platform with AI-powered features"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

blog_router = APIRouter(prefix="/blog", tags=["blog"])

@blog_router.get("/articles")
async def get_blog_articles():
    """Get all blog articles"""
    try:
        import os
        from motor.motor_asyncio import AsyncIOMotorClient
        
        MONGO_URL = os.environ.get("MONGO_URI", os.environ.get("MONGO_URL", ""))
        DB_NAME = os.environ.get("DB_NAME", "josmoze_production")
        
        client = AsyncIOMotorClient(MONGO_URL)
        db = client[DB_NAME]
        
        cursor = db.blog_articles.find({})
        articles = await cursor.to_list(length=None)
        
        # Convert ObjectId to string for JSON serialization
        for article in articles:
            if "_id" in article:
                article["_id"] = str(article["_id"])
        
        return {
            "articles": articles,
            "count": len(articles),
            "message": f"Found {len(articles)} blog articles"
        }
    except Exception as e:
        logger.error(f"Error getting blog articles: {e}")
        return {"articles": [], "count": 0, "error": str(e)}

app.include_router(products.router, prefix="/api")
app.include_router(auth.router, prefix="/api")
app.include_router(crm.router, prefix="/api")
app.include_router(ai_agents.router, prefix="/api")
app.include_router(blog_router, prefix="/api")

db_client = None
db = None
stripe_checkout = None

@app.on_event("startup")
async def startup_event():
    """Initialize all services on application startup"""
    global db_client, db, stripe_checkout
    
    try:
        # Initialize MongoDB connection
        mongodb_url = os.getenv("MONGO_URI", os.getenv("MONGO_URL", ""))
        db_name = os.getenv("DB_NAME", "josmoze_production")
        
        logger.info(f"🔍 MongoDB Configuration - URL: {'***CONFIGURED***' if mongodb_url else 'NOT SET'}, DB: {db_name}")
        
        db_client = AsyncIOMotorClient(mongodb_url)
        db = db_client[db_name]
        
        await db_client.admin.command('ping')
        logger.info("✅ MongoDB connected successfully")
        
        # Initialize Stripe
        stripe_api_key = os.getenv("STRIPE_SECRET_KEY")
        stripe_webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")
        if stripe_api_key and StripeCheckout:
            stripe_checkout = StripeCheckout(stripe_api_key, stripe_webhook_secret)
            logger.info("✅ Stripe initialized successfully")
        
        # Initialize other services
        try:
            from .services.payment_manager import get_payment_manager
            await get_payment_manager()
            logger.info("✅ Payment manager initialized")
        except ImportError as e:
            logger.warning(f"⚠️ Payment manager not available: {e}")
        
        logger.info("🚀 All services initialized successfully")
        
    except Exception as e:
        logger.error(f"❌ Error during startup: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up on application shutdown"""
    if db_client:
        db_client.close()
        logger.info("✅ Database connection closed")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Josmoze E-commerce API v2.0.0", 
        "status": "running",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy", 
        "database": "connected" if db is not None else "disconnected",
        "stripe": "configured" if stripe_checkout is not None else "not_configured",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Global exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "type": type(exc).__name__}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
