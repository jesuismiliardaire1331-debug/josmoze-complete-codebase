#!/usr/bin/env python3
"""
Test script to verify the refactored architecture works correctly
"""
import sys
import os
sys.path.append('./backend')

from fastapi.testclient import TestClient
from backend.main_refactored import app

def test_refactored_architecture():
    """Test the refactored architecture with router modules"""
    print("=== Testing Refactored Architecture ===")
    
    client = TestClient(app)
    
    tests = [
        {
            "name": "Root Endpoint",
            "method": "GET",
            "url": "/",
            "expected_status": 200,
            "check_architecture": True
        },
        {
            "name": "Health Check",
            "method": "GET",
            "url": "/health",
            "expected_status": 200
        },
        {
            "name": "Products Router",
            "method": "GET",
            "url": "/products/",
            "expected_status": 200
        },
        {
            "name": "Product Detail Router",
            "method": "GET",
            "url": "/products/test-product",
            "expected_status": 200
        },
        {
            "name": "Localization Router",
            "method": "GET",
            "url": "/localization/detect",
            "expected_status": 200,
            "check_french": True
        },
        {
            "name": "Auth Router",
            "method": "POST",
            "url": "/auth/login",
            "data": {"username": "test@example.com", "password": "test"},
            "expected_status": 200
        },
        {
            "name": "CRM Router",
            "method": "GET",
            "url": "/crm/dashboard",
            "expected_status": 200
        },
        {
            "name": "AI Agents Router",
            "method": "POST",
            "url": "/ai-agents/chat",
            "data": {"message": "Hello"},
            "expected_status": 200
        }
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        print(f"\n--- {test['name']} ---")
        
        try:
            if test["method"] == "GET":
                response = client.get(test["url"])
            else:
                response = client.post(test["url"], json=test.get("data", {}))
            
            if response.status_code == test["expected_status"]:
                print(f"✅ PASS: Status {response.status_code}")
                
                data = response.json()
                
                if test.get("check_architecture"):
                    architecture = data.get("architecture")
                    routers = data.get("routers", [])
                    if architecture == "modular_routers" and len(routers) >= 5:
                        print(f"✅ PASS: Modular architecture confirmed")
                        print(f"   Routers: {routers}")
                    else:
                        print(f"❌ FAIL: Architecture not properly modular")
                        continue
                
                if test.get("check_french"):
                    language = data.get("detected_language")
                    currency = data.get("currency", {})
                    if language == "FR" and currency.get("code") == "EUR":
                        print(f"✅ PASS: Returns FR/EUR as expected")
                    else:
                        print(f"❌ FAIL: Expected FR/EUR, got {language}/{currency}")
                        continue
                
                passed += 1
                print(f"   Response: {str(data)[:100]}...")
                
            else:
                print(f"❌ FAIL: Expected {test['expected_status']}, got {response.status_code}")
                print(f"   Response: {response.text}")
                
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
    
    print(f"\n=== Refactored Architecture Test Results ===")
    print(f"✅ Passed: {passed}/{total}")
    print(f"📈 Success Rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("🎉 Refactored architecture is working correctly!")
        print("📦 Router modules successfully separated from monolithic server.py")
        return True
    else:
        print("⚠️ Some router modules need additional work")
        return False

if __name__ == "__main__":
    success = test_refactored_architecture()
    sys.exit(0 if success else 1)
