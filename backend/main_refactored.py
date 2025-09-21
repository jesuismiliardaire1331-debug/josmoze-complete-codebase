"""
Refactored main FastAPI application with router modules
This demonstrates the architectural improvement from monolithic server.py
"""
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from dotenv import load_dotenv

from routers import products, auth, localization, crm, ai_agents

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ.get('DB_NAME', 'josmoze')]

# Create the main app
app = FastAPI(title="Josmose CRM & Marketing Automation - Refactored", version="2.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup event to initialize services
@app.on_event("startup")
async def startup_event():
    """Initialize all services on application startup"""
    logging.info("🚀 Refactored application starting up...")
    logging.info("✅ All router modules loaded successfully")

app.include_router(products.router)
app.include_router(auth.router)
app.include_router(localization.router)
app.include_router(crm.router)
app.include_router(ai_agents.router)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Josmose API - Refactored Architecture",
        "version": "2.1.0",
        "status": "healthy",
        "architecture": "modular_routers",
        "routers": ["products", "auth", "localization", "crm", "ai_agents"]
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "architecture": "refactored",
        "routers_loaded": 5
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
