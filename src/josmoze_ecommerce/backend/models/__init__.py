"""
Pydantic models for the Josmoze E-commerce application
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class Product(BaseModel):
    id: str
    name: str
    description: str
    price: float
    currency: str = "eur"
    category: str
    image_url: Optional[str] = None
    stock_quantity: int = 0
    is_active: bool = True

class CartItem(BaseModel):
    product_id: str
    quantity: int

class Order(BaseModel):
    id: Optional[str] = None
    customer_email: str
    customer_name: str
    items: List[CartItem]
    total_amount: float
    currency: str = "eur"
    status: str = "pending"
    created_at: Optional[datetime] = None
    payment_method: Optional[str] = None
    shipping_address: Optional[Dict[str, str]] = None

class Lead(BaseModel):
    id: Optional[str] = None
    email: str
    name: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    source: str = "website"
    score: int = 0
    status: str = "new"
    created_at: Optional[datetime] = None
    notes: Optional[str] = None

class ContactForm(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    company: Optional[str] = None
    message: str
    request_type: str = "general"
    customer_type: str = "particulier"

class PaymentTransaction(BaseModel):
    id: Optional[str] = None
    session_id: str
    amount: float
    currency: str = "eur"
    status: str = "pending"
    payment_method: str = "stripe"
    customer_email: str
    created_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
