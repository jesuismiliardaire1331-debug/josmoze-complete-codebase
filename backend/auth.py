from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext
from motor.motor_asyncio import AsyncIOMotorClient
import jwt
from datetime import datetime, timedelta
import os
from typing import Optional, Dict
from pydantic import BaseModel

# Security configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "josmose_crm_secret_key_2024")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 480  # 8 hours

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

class UserAuth(BaseModel):
    username: str  # Now accepts email addresses
    password: str

# Company legal information for payment compliance
COMPANY_INFO = {
    "legal_name": "JOSMOSE SARL",
    "siret": "12345678901234",  # SIRET français (14 chiffres)
    "siren": "123456789",       # SIREN français (9 chiffres) 
    "vat_number": "FR12123456789",  # TVA intracommunautaire française
    "legal_form": "SARL",
    "capital": "10000",  # Capital social en euros
    "address": {
        "street": "123 Avenue de la République",
        "city": "Paris",
        "postal_code": "75011",
        "country": "France"
    },
    "contact": {
        "email": "legal@josmose.com",
        "phone": "+33 1 23 45 67 89"
    },
    "stripe": {
        "account_id": None,  # À configurer avec votre Stripe Account ID
        "mcc": "5999",      # Merchant Category Code pour vente de produits divers
        "business_profile": {
            "product_description": "Systèmes de purification d'eau par osmose inverse",
            "business_type": "company",
            "url": "https://josmose.com"
        }
    }
}

class User(BaseModel):
    id: str
    username: str
    email: str
    professional_email: Optional[str] = None
    role: str  # admin, manager, agent, support, commercial
    full_name: str
    department: Optional[str] = None
    position: Optional[str] = None
    is_active: bool = True
    created_at: datetime
    last_login: Optional[datetime] = None

class Token(BaseModel):
    access_token: str
    token_type: str
    user: User

# Predefined users for CRM access - Updated with correct roles from user interface
CRM_USERS = {
    "naima@josmose.com": {
        "id": "user_naima",
        "username": "naima@josmose.com",
        "email": "naima@josmose.com",  # Email professionnel pour clients
        "professional_email": "naima@josmose.com",
        "full_name": "Naima - Manager",
        "role": "manager",  # Manager role - highest level
        "password_hash": "$2b$12$T3.CqIsUwLAcFv8lM2fyGOBlYKAIJB0TZXXmWrYg2SFim/jgW1Cd2",  # "Naima@2024!Commerce"
        "department": "Direction Commerciale",
        "position": "Directrice Commerciale",
        "is_active": True
    },
    "aziza@josmose.com": {
        "id": "user_aziza", 
        "username": "aziza@josmose.com",
        "email": "aziza@josmose.com",  # Email professionnel pour clients
        "professional_email": "aziza@josmose.com", 
        "full_name": "Aziza - Agent",
        "role": "agent",  # 🔄 RÔLE MODIFIÉ : Agent (au lieu de manager)
        "password_hash": "$2b$12$GHSiiMx03IQ81HMWinZUn.xvyi3MtGhg6k6mZG1QXqCwCZJT5b/vm",  # "Aziza@2024!Director"
        "department": "Équipe Commerciale",
        "position": "Agent Commercial",
        "is_active": True
    },
    "antonio@josmose.com": {
        "id": "user_antonio",
        "username": "antonio@josmose.com",
        "email": "antonio@josmose.com",  # Email professionnel pour clients
        "professional_email": "antonio@josmose.com",
        "full_name": "Antonio - Manager",
        "role": "manager",  # Manager role - same as Naima
        "password_hash": "$2b$12$gWfOtZyEWTzJ2871yBT8W.FfLGIpm9VGEjYGRTZUVOQXQcIR2LRHe",  # "Antonio@2024!Secure"
        "department": "Direction Générale", 
        "position": "Directeur Général",
        "is_active": True
    },
    "support@josmose.com": {
        "id": "user_support",
        "username": "support@josmose.com",
        "email": "support@josmose.com",  # Email professionnel pour clients 
        "professional_email": "support@josmose.com",
        "full_name": "Support - Technique",
        "role": "technique",  # Technical support role - limited access
        "password_hash": "$2b$12$AgqPE73OcPnBKMmpgCQ3IOiShGsj8AuBo.TLETjIUJgS.AD9aFEd.",  # "Support@2024!Help"
        "department": "Support Technique",
        "position": "Technicien Support",
        "is_active": True
    },
    # Nouvelle adresse email pour le service commercial
    "commercial@josmose.com": {
        "id": "user_commercial",
        "username": "commercial@josmose.com", 
        "email": "commercial@josmose.com",  # Email professionnel pour prospects
        "professional_email": "commercial@josmose.com",
        "full_name": "Service Commercial",
        "role": "commercial",  # Role commercial pour prospects
        "password_hash": "$2b$12$JUSY1Xvr16sYMyxClk5m0.JQhAqylyzBZy4I/LPHyR4q9ESP9353G",  # "Commercial@2024!Sales"
        "department": "Service Commercial",
        "position": "Équipe Commerciale",
        "is_active": True
    }
}

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Generate password hash"""
    return pwd_context.hash(password)

def authenticate_user(email_or_username: str, password: str) -> Optional[dict]:
    """Authenticate user credentials - now supports email login"""
    # Try to find user by email first (new primary method)
    user_data = CRM_USERS.get(email_or_username.lower())
    
    # If not found by email, try legacy username search for backward compatibility
    if not user_data:
        for email, data in CRM_USERS.items():
            if data.get("username", "").lower() == email_or_username.lower():
                user_data = data
                break
    
    if not user_data or not user_data["is_active"]:
        return None
    
    if not verify_password(password, user_data["password_hash"]):
        return None
    
    return user_data

def create_access_token(data: dict) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """Get current authenticated user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        email_or_username: str = payload.get("sub")
        if email_or_username is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    
    # Try to find user by email first
    user_data = CRM_USERS.get(email_or_username.lower())
    
    # If not found by email, try legacy username search
    if not user_data:
        for email, data in CRM_USERS.items():
            if data.get("username", "").lower() == email_or_username.lower():
                user_data = data
                break
    
    if user_data is None or not user_data["is_active"]:
        raise credentials_exception
    
    return User(
        id=user_data["id"],
        username=user_data["username"],
        email=user_data["email"],
        professional_email=user_data.get("professional_email"),
        full_name=user_data["full_name"],
        role=user_data["role"],
        department=user_data.get("department"),
        position=user_data.get("position"),
        is_active=user_data["is_active"],
        created_at=datetime.utcnow(),
        last_login=datetime.utcnow()
    )

def require_role(required_roles: list):
    """Decorator to require specific roles"""
    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return current_user
    return role_checker

def get_company_info():
    """Get company legal information for payment processing"""
    return COMPANY_INFO

def get_user_permissions(role: str) -> Dict[str, bool]:
    """Get user permissions based on role"""
    permissions = {
        "manager": {
            "view_dashboard": True,
            "view_leads": True,
            "edit_leads": True,
            "delete_leads": True,
            "view_orders": True,
            "edit_orders": True,
            "view_stock": True,
            "edit_stock": True,
            "view_invoices": True,
            "view_marketing": True,
            "edit_marketing": True,
            "view_campaigns": True,
            "edit_campaigns": True,
            "manage_users": True,
            "view_analytics": True,
            "export_data": True
        },
        "agent": {
            "view_dashboard": True,
            "view_leads": True,
            "edit_leads": True,
            "delete_leads": False,
            "view_orders": True,
            "edit_orders": False,
            "view_stock": True,
            "edit_stock": False,
            "view_invoices": True,
            "view_marketing": False,
            "edit_marketing": False,
            "view_campaigns": True,
            "edit_campaigns": False,
            "manage_users": False,
            "view_analytics": True,
            "export_data": False
        },
        "technique": {
            "view_dashboard": True,
            "view_leads": True,
            "edit_leads": False,
            "delete_leads": False,
            "view_orders": True,
            "edit_orders": False,
            "view_stock": True,
            "edit_stock": False,
            "view_invoices": False,
            "view_marketing": False,
            "edit_marketing": False,
            "view_campaigns": False,
            "edit_campaigns": False,
            "manage_users": False,
            "view_analytics": False,
            "export_data": False
        },
        "commercial": {
            "view_dashboard": True,
            "view_leads": True,
            "edit_leads": True,
            "delete_leads": False,
            "view_orders": True,
            "edit_orders": True,
            "view_stock": True,
            "edit_stock": False,
            "view_invoices": True,
            "view_marketing": True,
            "edit_marketing": True,
            "view_campaigns": True,
            "edit_campaigns": True,
            "manage_users": False,
            "view_analytics": True,
            "export_data": True
        }
    }
    
    return permissions.get(role, permissions["technique"])

# Initialize default users
async def init_users_db():
    """Initialize users in database if needed"""
    # This would normally create users in MongoDB
    # For now, using in-memory CRM_USERS dict
    pass