"""
Product-related API endpoints
Extracted from monolithic server.py for better organization
"""
from fastapi import APIRouter, HTTPException, Request, Depends
from typing import List, Optional, Dict, Any
import logging
import os
from datetime import datetime

router = APIRouter(prefix="/products", tags=["products"])

async def get_database():
    """Get shared database connection from main app"""
    from ..main import db
    return db

@router.get("/")
async def get_products():
    """Get all products with stock information"""
    try:
        db = await get_database()
        cursor = db.products.find({})
        products = await cursor.to_list(length=None)
        
        # Convert ObjectId to string for JSON serialization
        for product in products:
            if "_id" in product:
                product["_id"] = str(product["_id"])
        
        return {
            "products": products,
            "count": len(products),
            "message": f"Found {len(products)} products"
        }
    except Exception as e:
        logging.error(f"Error getting products: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{product_id}")
async def get_product_detail(product_id: str):
    """Get detailed product information"""
    try:
        db = await get_database()
        product = await db.products.find_one({"id": product_id})
        
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Convert ObjectId to string for JSON serialization
        if "_id" in product:
            product["_id"] = str(product["_id"])
        
        return product
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error getting product detail: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/translated")
async def get_translated_products():
    """Get products translated to user's language"""
    try:
        db = await get_database()
        cursor = db.products.find({})
        products = await cursor.to_list(length=None)
        
        # Convert ObjectId to string for JSON serialization
        for product in products:
            if "_id" in product:
                product["_id"] = str(product["_id"])
        
        return {
            "products": products,
            "count": len(products),
            "message": f"Found {len(products)} translated products"
        }
    except Exception as e:
        logging.error(f"Error getting translated products: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/admin/populate")
async def populate_products():
    """Admin endpoint to populate products from products_final.py"""
    try:
        import sys
        sys.path.append('./src')
        from josmoze_ecommerce.backend.models.products_final import FINAL_PRODUCTS
        
        db = await get_database()
        
        await db.products.delete_many({})
        
        if FINAL_PRODUCTS:
            result = await db.products.insert_many(FINAL_PRODUCTS)
            inserted_count = len(result.inserted_ids)
        else:
            inserted_count = 0
        
        return {
            "success": True,
            "message": f"Successfully populated {inserted_count} products",
            "inserted_count": inserted_count
        }
    except Exception as e:
        logging.error(f"Error populating products: {e}")
        raise HTTPException(status_code=500, detail=str(e))
