#!/usr/bin/env python3
"""
🚀 PHASE 9 - SYSTÈME AUTHENTIFICATION UTILISATEUR
Backend pour Josmoze.com - Espace client complet

FONCTIONNALITÉS :
1. **Inscription/Connexion** : Système sécurisé avec hash password
2. **Espace Client** : Profil, historique commandes, parrainage
3. **Gestion Session** : JWT tokens pour authentification
4. **Intégration Promotions** : Codes promo personnels et parrainage

SÉCURITÉ :
- Hash bcrypt pour mots de passe
- JWT tokens avec expiration
- Validation email format
- Protection contre attaques
"""

import logging
import hashlib
import secrets
import jwt
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import bcrypt
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel, Field, EmailStr, validator
import uuid
import re

logger = logging.getLogger(__name__)

# Configuration JWT
JWT_SECRET = "josmoze_secret_key_2024_phase9_ultra_secure"  # À changer en production
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

# ========== MODELS PYDANTIC ==========

class UserRegistration(BaseModel):
    """Modèle inscription utilisateur"""
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    phone: Optional[str] = None
    customer_type: str = "B2C"  # B2C ou B2B
    company: Optional[str] = None
    accept_terms: bool = True
    newsletter: bool = False
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Mot de passe minimum 8 caractères')
        if not re.search(r'[A-Za-z]', v):
            raise ValueError('Mot de passe doit contenir au moins une lettre')
        if not re.search(r'\d', v):
            raise ValueError('Mot de passe doit contenir au moins un chiffre')
        return v

class UserLogin(BaseModel):
    """Modèle connexion utilisateur"""
    email: EmailStr
    password: str
    remember_me: bool = False

class UserProfile(BaseModel):
    """Modèle profil utilisateur"""
    id: str
    email: str
    first_name: str
    last_name: str
    phone: Optional[str]
    customer_type: str
    company: Optional[str]
    address: Optional[Dict[str, str]]
    is_active: bool
    email_verified: bool
    total_orders: int
    total_spent: float
    referral_code: Optional[str]
    created_at: datetime
    last_login: Optional[datetime]

class UserAddress(BaseModel):
    """Modèle adresse utilisateur"""
    street: str
    city: str
    postal_code: str
    country: str = "France"
    is_default: bool = True

class Order(BaseModel):
    """Modèle commande simple pour historique"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_email: str
    order_number: str
    status: str  # pending, confirmed, shipped, delivered, cancelled
    items: List[Dict[str, Any]]
    subtotal: float
    discount_amount: float = 0.0
    shipping_cost: float = 0.0
    total: float
    promotion_code: Optional[str] = None
    referral_code: Optional[str] = None
    shipping_address: Dict[str, str]
    billing_address: Dict[str, str]
    payment_method: str
    payment_status: str  # pending, paid, failed, refunded
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    delivered_at: Optional[datetime] = None

# ========== SYSTÈME AUTHENTIFICATION ==========

class UserAuthSystem:
    """Gestionnaire authentification et espace client"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.users_collection = db.users
        self.orders_collection = db.orders
        self.sessions_collection = db.user_sessions
        
    async def initialize(self):
        """Initialiser collections et index"""
        try:
            # Index pour performance et sécurité
            await self.users_collection.create_index("email", unique=True)
            # Index pour referral_code (skip l'index pour éviter le problème null)
            # await self.users_collection.create_index("referral_code", unique=True, sparse=True)
            await self.users_collection.create_index("is_active")
            
            await self.orders_collection.create_index("user_email")
            await self.orders_collection.create_index("order_number", unique=True)
            await self.orders_collection.create_index("status")
            await self.orders_collection.create_index("created_at")
            
            await self.sessions_collection.create_index("user_email")
            await self.sessions_collection.create_index("expires_at")
            
            logger.info("✅ UserAuthSystem initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing UserAuthSystem: {e}")
            raise
    
    # ========== UTILITAIRES SÉCURITÉ ==========
    
    def _hash_password(self, password: str) -> str:
        """Hash sécurisé du mot de passe"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def _verify_password(self, password: str, hashed: str) -> bool:
        """Vérifier mot de passe"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    def _generate_jwt_token(self, user_email: str, user_id: str, remember_me: bool = False) -> str:
        """Générer JWT token"""
        expiration = datetime.utcnow() + timedelta(
            hours=168 if remember_me else JWT_EXPIRATION_HOURS  # 7 jours si "remember me"
        )
        
        payload = {
            'user_email': user_email,
            'user_id': user_id,
            'exp': expiration,
            'iat': datetime.utcnow()
        }
        
        return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    
    def _verify_jwt_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Vérifier JWT token"""
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    # ========== INSCRIPTION/CONNEXION ==========
    
    async def register_user(self, registration_data: UserRegistration) -> Dict[str, Any]:
        """Inscription nouvel utilisateur"""
        try:
            # Vérifier si email existe déjà
            existing_user = await self.users_collection.find_one({"email": registration_data.email})
            if existing_user:
                return {"success": False, "error": "Email déjà utilisé"}
            
            # Hash du mot de passe
            password_hash = self._hash_password(registration_data.password)
            
            # Créer utilisateur
            user_data = {
                "id": str(uuid.uuid4()),
                "email": registration_data.email,
                "password_hash": password_hash,
                "first_name": registration_data.first_name,
                "last_name": registration_data.last_name,
                "phone": registration_data.phone,
                "customer_type": registration_data.customer_type,
                "company": registration_data.company,
                "is_active": True,
                "email_verified": False,  # À implémenter si nécessaire
                "total_orders": 0,
                "total_spent": 0.0,
                # Ne pas insérer referral_code: None pour éviter le conflit d'index
                "created_at": datetime.utcnow(),
                "last_login": None,
                "address": None
            }
            
            await self.users_collection.insert_one(user_data)
            
            # Générer token de connexion
            token = self._generate_jwt_token(registration_data.email, user_data["id"])
            
            logger.info(f"✅ Utilisateur inscrit: {registration_data.email}")
            
            return {
                "success": True,
                "message": "Inscription réussie",
                "user": {
                    "id": user_data["id"],
                    "email": user_data["email"],
                    "first_name": user_data["first_name"],
                    "last_name": user_data["last_name"],
                    "customer_type": user_data["customer_type"]
                },
                "token": token
            }
            
        except Exception as e:
            logger.error(f"Error registering user: {e}")
            return {"success": False, "error": "Erreur lors de l'inscription"}
    
    async def login_user(self, login_data: UserLogin) -> Dict[str, Any]:
        """Connexion utilisateur"""
        try:
            # Récupérer utilisateur
            user = await self.users_collection.find_one({"email": login_data.email})
            if not user:
                return {"success": False, "error": "Email ou mot de passe incorrect"}
            
            # Vérifier mot de passe
            if not self._verify_password(login_data.password, user["password_hash"]):
                return {"success": False, "error": "Email ou mot de passe incorrect"}
            
            # Vérifier si compte actif
            if not user.get("is_active", True):
                return {"success": False, "error": "Compte désactivé"}
            
            # Mettre à jour dernière connexion
            await self.users_collection.update_one(
                {"email": login_data.email},
                {"$set": {"last_login": datetime.utcnow()}}
            )
            
            # Générer token
            token = self._generate_jwt_token(login_data.email, user["id"], login_data.remember_me)
            
            logger.info(f"✅ Connexion réussie: {login_data.email}")
            
            return {
                "success": True,
                "message": "Connexion réussie",
                "user": {
                    "id": user["id"],
                    "email": user["email"],
                    "first_name": user["first_name"],
                    "last_name": user["last_name"],
                    "customer_type": user["customer_type"],
                    "referral_code": user.get("referral_code")
                },
                "token": token
            }
            
        except Exception as e:
            logger.error(f"Error logging in user: {e}")
            return {"success": False, "error": "Erreur lors de la connexion"}
    
    async def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Vérifier token et récupérer utilisateur"""
        try:
            payload = self._verify_jwt_token(token)
            if not payload:
                return None
            
            user = await self.users_collection.find_one({"email": payload["user_email"]})
            if not user or not user.get("is_active", True):
                return None
            
            return {
                "id": user["id"],
                "email": user["email"],
                "first_name": user["first_name"],
                "last_name": user["last_name"],
                "customer_type": user["customer_type"],
                "referral_code": user.get("referral_code")
            }
            
        except Exception as e:
            logger.error(f"Error verifying token: {e}")
            return None
    
    # ========== GESTION PROFIL ==========
    
    async def get_user_profile(self, user_email: str) -> Optional[UserProfile]:
        """Récupérer profil utilisateur complet"""
        try:
            user = await self.users_collection.find_one({"email": user_email})
            if not user:
                return None
            
            # Supprimer données sensibles
            if "_id" in user:
                del user["_id"]
            if "password_hash" in user:
                del user["password_hash"]
            
            return UserProfile(**user)
            
        except Exception as e:
            logger.error(f"Error getting user profile: {e}")
            return None
    
    async def update_user_profile(self, user_email: str, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Mettre à jour profil utilisateur"""
        try:
            # Champs autorisés à la modification
            allowed_fields = {
                "first_name", "last_name", "phone", "company", "address"
            }
            
            update_data = {k: v for k, v in profile_data.items() if k in allowed_fields}
            
            if not update_data:
                return {"success": False, "error": "Aucune donnée à mettre à jour"}
            
            result = await self.users_collection.update_one(
                {"email": user_email},
                {"$set": update_data}
            )
            
            if result.modified_count > 0:
                logger.info(f"✅ Profil mis à jour: {user_email}")
                return {"success": True, "message": "Profil mis à jour"}
            else:
                return {"success": False, "error": "Aucune modification effectuée"}
                
        except Exception as e:
            logger.error(f"Error updating user profile: {e}")
            return {"success": False, "error": "Erreur lors de la mise à jour"}
    
    # ========== GESTION COMMANDES ==========
    
    async def create_order(self, order_data: Dict[str, Any]) -> str:
        """Créer nouvelle commande"""
        try:
            # Générer numéro de commande unique
            order_number = f"JOS{datetime.now().strftime('%Y%m%d')}{secrets.token_hex(3).upper()}"
            
            order_data["order_number"] = order_number
            order_data["created_at"] = datetime.utcnow()
            order_data["updated_at"] = datetime.utcnow()
            
            order = Order(**order_data)
            await self.orders_collection.insert_one(order.dict())
            
            # Mettre à jour statistiques utilisateur
            await self.users_collection.update_one(
                {"email": order_data["user_email"]},
                {
                    "$inc": {
                        "total_orders": 1,
                        "total_spent": order_data["total"]
                    }
                }
            )
            
            logger.info(f"✅ Commande créée: {order_number}")
            return order.id
            
        except Exception as e:
            logger.error(f"Error creating order: {e}")
            raise
    
    async def get_user_orders(self, user_email: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Récupérer historique commandes utilisateur"""
        try:
            orders = await self.orders_collection.find(
                {"user_email": user_email}
            ).sort("created_at", -1).limit(limit).to_list(limit)
            
            # Supprimer ObjectId pour sérialisation
            for order in orders:
                if "_id" in order:
                    del order["_id"]
            
            return orders
            
        except Exception as e:
            logger.error(f"Error getting user orders: {e}")
            return []
    
    async def get_order_by_id(self, order_id: str, user_email: str = None) -> Optional[Dict[str, Any]]:
        """Récupérer commande par ID"""
        try:
            query = {"id": order_id}
            if user_email:
                query["user_email"] = user_email
            
            order = await self.orders_collection.find_one(query)
            
            if order and "_id" in order:
                del order["_id"]
            
            return order
            
        except Exception as e:
            logger.error(f"Error getting order by ID: {e}")
            return None
    
    async def update_order_status(self, order_id: str, new_status: str) -> bool:
        """Mettre à jour statut commande"""
        try:
            result = await self.orders_collection.update_one(
                {"id": order_id},
                {
                    "$set": {
                        "status": new_status,
                        "updated_at": datetime.utcnow(),
                        "delivered_at": datetime.utcnow() if new_status == "delivered" else None
                    }
                }
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"Error updating order status: {e}")
            return False

# ========== INSTANCE GLOBALE ==========

user_auth_system = None

async def get_user_auth_system(db: AsyncIOMotorDatabase) -> UserAuthSystem:
    """Obtenir instance système authentification"""
    global user_auth_system
    if user_auth_system is None:
        user_auth_system = UserAuthSystem(db)
        await user_auth_system.initialize()
    return user_auth_system

async def init_user_auth_system(db: AsyncIOMotorDatabase):
    """Initialiser système authentification"""
    global user_auth_system
    user_auth_system = UserAuthSystem(db)
    await user_auth_system.initialize()
    return user_auth_system