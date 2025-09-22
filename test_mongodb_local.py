#!/usr/bin/env python3
"""
Test local MongoDB connection and verify it's ready for import scripts
"""
import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient

async def test_atlas_mongodb():
    """Test connection to MongoDB Atlas instance"""
    try:
        print("🔍 Testing MongoDB Atlas connection...")
        atlas_url = "mongodb+srv://jesuismiliardaire1331_db_user:NWNCcv9h3OOFkavQ@cluster0.jhfn6ic.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
        client = AsyncIOMotorClient(atlas_url, serverSelectionTimeoutMS=10000)
        db = client.josmoze_production
        
        collections = await db.list_collection_names()
        print(f"✅ Connected to MongoDB Atlas successfully!")
        print(f"Database: josmoze_production")
        print(f"Collections: {collections}")
        
        test_collection = db.test_connection
        result = await test_collection.insert_one({"test": "connection", "timestamp": "2025-09-21"})
        print(f"✅ Write test successful: {result.inserted_id}")
        
        await test_collection.delete_one({"_id": result.inserted_id})
        print("✅ Cleanup successful")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_atlas_mongodb())
    if success:
        print("\n🚀 MongoDB Atlas is ready for import scripts!")
    else:
        print("\n❌ MongoDB Atlas setup needs attention")
