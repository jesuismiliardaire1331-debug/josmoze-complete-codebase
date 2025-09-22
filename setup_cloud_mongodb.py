#!/usr/bin/env python3
"""
Setup script to create a simple cloud MongoDB solution using MongoDB Atlas
or configure for production deployment
"""
import os
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

ATLAS_CONNECTION_TEMPLATE = """

"""

async def test_atlas_connection(connection_string):
    """Test connection to MongoDB Atlas"""
    try:
        client = AsyncIOMotorClient(connection_string, serverSelectionTimeoutMS=10000)
        db = client.josmoze_production
        
        collections = await db.list_collection_names()
        print(f"✅ Connected to MongoDB Atlas successfully!")
        print(f"Database: josmoze_production")
        print(f"Collections: {collections}")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"❌ Atlas connection failed: {e}")
        return False

def create_atlas_setup_instructions():
    """Create setup instructions for MongoDB Atlas"""
    instructions = """

1. Go to https://cloud.mongodb.com/
2. Create free account or sign in
3. Create new cluster (free tier M0)
4. Create database user with read/write permissions
5. Add IP address 0.0.0.0/0 to network access (for development)
6. Get connection string from "Connect" button
7. Replace connection string in .env file
8. Use mongorestore to import data

"""
    
    with open('/home/ubuntu/atlas_setup_instructions.txt', 'w') as f:
        f.write(instructions)
    
    print("📋 Atlas setup instructions created at /home/ubuntu/atlas_setup_instructions.txt")

if __name__ == "__main__":
    print("🌐 MongoDB Atlas Setup Helper")
    print("=" * 50)
    
    create_atlas_setup_instructions()
    
    atlas_url = os.environ.get('MONGODB_ATLAS_URL')
    if atlas_url:
        print(f"Testing provided Atlas URL...")
        success = asyncio.run(test_atlas_connection(atlas_url))
        if success:
            print("🚀 Atlas connection successful!")
        else:
            print("❌ Atlas connection failed")
    else:
        print("💡 Set MONGODB_ATLAS_URL environment variable to test connection")
        print("💡 Or manually create Atlas cluster and update .env file")
