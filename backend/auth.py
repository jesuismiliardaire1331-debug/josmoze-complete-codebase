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

# Predefined users for CRM access
CRM_USERS = {
    "naima": {
        "id": "user_naima",
        "username": "naima",
        "email": "naima@josmose.com",
        "full_name": "Naima",
        "role": "manager",
        "password_hash": "$2b$12$LQv3c1yqBwWdPcA5.VWLGuoFZ8z1d1i1G2vWF.R7H9oL9I4QO3B22",  # "naima123"
        "is_active": True
    },
    "aziza": {
        "id": "user_aziza", 
        "username": "aziza",
        "email": "aziza@josmose.com",
        "full_name": "Aziza",
        "role": "agent",
        "password_hash": "$2b$12$LQv3c1yqBwWdPcA5.VWLGuoFZ8z1d1i1G2vWF.R7H9oL9I4QO3B22",  # "aziza123"
        "is_active": True
    },
    "antonio": {
        "id": "user_antonio",
        "username": "antonio", 
        "email": "antonio@josmose.com",
        "full_name": "Antonio",
        "role": "agent",
        "password_hash": "$2b$12$LQv3c1yqBwWdPcA5.VWLGuoFZ8z1d1i1G2vWF.R7H9oL9I4QO3B22",  # "antonio123"
        "is_active": True
    },
    "support": {
        "id": "user_support",
        "username": "support",
        "email": "support@josmose.com", 
        "full_name": "Support Technique",
        "role": "support",
        "password_hash": "$2b$12$LQv3c1yqBwWdPcA5.VWLGuoFZ8z1d1i1G2vWF.R7H9oL9I4QO3B22",  # "support123"
        "is_active": True
    }
}

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Generate password hash"""
    return pwd_context.hash(password)

def authenticate_user(username: str, password: str) -> Optional[dict]:
    """Authenticate user credentials"""
    user_data = CRM_USERS.get(username.lower())
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
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    
    user_data = CRM_USERS.get(username.lower())
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