#!/usr/bin/env python3
"""
Test script to verify authentication system behavior
"""
import sys
import os
sys.path.append('./backend')

from fastapi import FastAPI
from fastapi.testclient import TestClient
from backend.auth import authenticate_user, create_access_token, CRM_USERS

app = FastAPI()

@app.post("/auth/login")
async def login(user_auth: dict):
    """Test login endpoint"""
    from backend.auth import UserAuth, User, Token
    from datetime import datetime
    
    user_data = authenticate_user(user_auth["username"], user_auth["password"])
    
    if not user_data:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )
    
    # Create JWT token
    access_token = create_access_token(data={"sub": user_data["username"]})
    
    user = User(
        id=user_data["id"],
        username=user_data["username"],
        email=user_data["email"],
        full_name=user_data["full_name"],
        role=user_data["role"],
        is_active=user_data["is_active"],
        created_at=datetime.utcnow(),
        last_login=datetime.utcnow()
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user.dict()
    }

def test_authentication():
    """Test authentication system"""
    print("=== Testing Authentication System ===")
    
    client = TestClient(app)
    
    test_cases = [
        {
            "name": "Admin login",
            "credentials": {"username": "admin@josmoze.com", "password": "JosmozAdmin2025!"},
            "should_succeed": True
        },
        {
            "name": "Manager login (Naima)",
            "credentials": {"username": "naima@josmoze.com", "password": "Naima@2024!Commerce"},
            "should_succeed": True
        },
        {
            "name": "Invalid credentials",
            "credentials": {"username": "invalid@josmoze.com", "password": "wrongpassword"},
            "should_succeed": False
        },
        {
            "name": "Valid email, wrong password",
            "credentials": {"username": "admin@josmoze.com", "password": "wrongpassword"},
            "should_succeed": False
        }
    ]
    
    for test_case in test_cases:
        print(f"\n--- {test_case['name']} ---")
        
        try:
            response = client.post("/auth/login", json=test_case['credentials'])
            
            if test_case['should_succeed']:
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ PASS: Login successful")
                    print(f"   Token: {data.get('access_token', 'N/A')[:20]}...")
                    print(f"   User: {data.get('user', {}).get('full_name', 'N/A')}")
                    print(f"   Role: {data.get('user', {}).get('role', 'N/A')}")
                else:
                    print(f"❌ FAIL: Expected success but got {response.status_code}")
                    print(f"   Response: {response.text}")
            else:
                if response.status_code == 401:
                    print(f"✅ PASS: Correctly rejected invalid credentials")
                else:
                    print(f"❌ FAIL: Expected 401 but got {response.status_code}")
                    print(f"   Response: {response.text}")
                    
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
    
    print(f"\n--- Direct Authentication Function Tests ---")
    
    user_data = authenticate_user("admin@josmoze.com", "JosmozAdmin2025!")
    if user_data:
        print(f"✅ PASS: Direct auth successful for admin")
        print(f"   User: {user_data['full_name']}")
        print(f"   Role: {user_data['role']}")
    else:
        print(f"❌ FAIL: Direct auth failed for valid admin credentials")
    
    user_data = authenticate_user("invalid@josmoze.com", "wrongpassword")
    if not user_data:
        print(f"✅ PASS: Direct auth correctly rejected invalid credentials")
    else:
        print(f"❌ FAIL: Direct auth should have rejected invalid credentials")
    
    print(f"\n--- Available CRM Users ---")
    for email, user_data in CRM_USERS.items():
        print(f"   {email}: {user_data['full_name']} ({user_data['role']})")

if __name__ == "__main__":
    test_authentication()
