#!/usr/bin/env python3
"""
Test MongoDB connection with different URLs to find the correct production database
"""
import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient

async def test_mongo_connection(mongo_url, db_name):
    """Test connection to MongoDB with given URL"""
    try:
        print(f"Testing connection to: {mongo_url}")
        client = AsyncIOMotorClient(mongo_url, serverSelectionTimeoutMS=5000)
        db = client[db_name]
        
        collections = await db.list_collection_names()
        print(f"✅ Connected successfully!")
        print(f"Database: {db_name}")
        print(f"Collections found: {collections[:5]}")
        
        if 'products' in collections:
            product_count = await db.products.count_documents({})
            print(f"Products in database: {product_count}")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

async def main():
    """Test different MongoDB connection URLs"""
    
    test_urls = [
        ("mongodb://localhost:27017", "josmoze_production"),
        ("mongodb+srv://admin:admin@cluster0.mongodb.net", "josmoze_production"),
        ("mongodb+srv://josmoze:josmoze2024@cluster0.mongodb.net", "josmoze_production"),
        ("mongodb://127.0.0.1:27017", "josmoze_production"),
    ]
    
    print("🔍 Testing MongoDB connections...")
    print("=" * 50)
    
    for mongo_url, db_name in test_urls:
        success = await test_mongo_connection(mongo_url, db_name)
        print("-" * 30)
        if success:
            print(f"✅ WORKING CONNECTION FOUND: {mongo_url}")
            break
    
    print("Test completed.")

if __name__ == "__main__":
    asyncio.run(main())
