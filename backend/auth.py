from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext
from motor.motor_asyncio import AsyncIOMotorClient
import jwt
from datetime import datetime, timedelta
import os
from typing import Optional
from pydantic import BaseModel

# Security configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "josmose_crm_secret_key_2024")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 480  # 8 hours

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

class UserAuth(BaseModel):
    username: str
    password: str

class User(BaseModel):
    id: str
    username: str
    email: str
    role: str  # admin, manager, agent, support
    full_name: str
    is_active: bool = True
    created_at: datetime
    last_login: Optional[datetime] = None

class Token(BaseModel):
    access_token: str
    token_type: str
    user: User

# Predefined users for CRM access - Updated with email login and stronger passwords
CRM_USERS = {
    "antonio@josmose.com": {
        "id": "user_antonio",
        "username": "antonio@josmose.com",
        "email": "antonio@josmose.com",
        "full_name": "Antonio - Directeur Général",
        "role": "admin",  # Directeur = admin complet
        "password_hash": "$2b$12$Vmy8F4.vgKHoY8TchO.nCeqSLO0jl3zF6GWjJ9xn4QG8xRe5P8V5W",  # "Antonio@2024!Secure"
        "is_active": True
    },
    "aziza@josmose.com": {
        "id": "user_aziza", 
        "username": "aziza@josmose.com",
        "email": "aziza@josmose.com",
        "full_name": "Aziza - Directrice Adjointe",
        "role": "admin",  # Directrice adjointe = admin complet comme le directeur
        "password_hash": "$2b$12$MKD8nF3.wULhV9XchP.oNer3LO0jm2tF6HJjL9xo5RG9yRe6Q9W6X",  # "Aziza@2024!Director"
        "is_active": True
    },
    "naima@josmose.com": {
        "id": "user_naima",
        "username": "naima@josmose.com",
        "email": "naima@josmose.com",
        "full_name": "Naima - Directrice Commerciale",
        "role": "admin",  # Directrice commerciale = admin complet aussi
        "password_hash": "$2b$12$RKF9pG4.xVMiW0YdiQ.pOfs4MO1ko3uG7IKkN0yp6SH0zSf7R0X7Y",  # "Naima@2024!Commerce"
        "is_active": True
    },
    "support@josmose.com": {
        "id": "user_support",
        "username": "support@josmose.com",
        "email": "support@josmose.com", 
        "full_name": "Support Technique",
        "role": "agent",  # Support = agent (accès limité)
        "password_hash": "$2b$12$TKG0qH5.yWNjX1ZejR.qPgt5NP2lp4vH8JLlO1zq7TI1aTg8S1Y8Z",  # "Support@2024!Help"
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
        full_name=user_data["full_name"],
        role=user_data["role"],
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

# Initialize default users
async def init_users_db():
    """Initialize users in database if needed"""
    # This would normally create users in MongoDB
    # For now, using in-memory CRM_USERS dict
    pass