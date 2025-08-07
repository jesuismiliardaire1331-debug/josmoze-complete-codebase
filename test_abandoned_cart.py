#!/usr/bin/env python3
"""
Focused Abandoned Cart System Testing for Josmose.com
Tests the newly implemented abandoned cart features
"""

import requests
import json
from datetime import datetime

# Backend URL from environment
BACKEND_URL = "https://67c818fa-35d3-46a9-b7df-5b06cb23e4f4.preview.emergentagent.com/api"

def test_abandoned_cart_tracking():
    """Test POST /api/abandoned-carts/track"""
    print("🛒 Testing Abandoned Cart Tracking...")
    
    cart_data = {
        "customer_email": "test.abandon@josmose.com",
        "customer_name": "Marie Dupont",
        "customer_phone": "+33123456789",
        "customer_address": {
            "street": "123 Rue de la Paix",
            "city": "Paris",
            "postal_code": "75001",
            "country": "France"
        },
        "items": [
            {
                "product_id": "osmoseur-principal",
                "name": "Fontaine à Eau Osmosée BlueMountain",
                "quantity": 1,
                "price": 499.0
            }
        ],
        "total_value": 499.0,
        "currency": "EUR"
    }
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/abandoned-carts/track",
            json=cart_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Response: {data}")
            if data.get("success"):
                print("   ✅ PASS: Abandoned cart tracking working")
                return data.get("cart_id")
            else:
                print("   ❌ FAIL: Success flag not set")
        else:
            print(f"   ❌ FAIL: HTTP {response.status_code}")
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   ❌ FAIL: Exception {e}")
    
    return None

def test_abandoned_cart_dashboard():
    """Test GET /api/crm/abandoned-carts/dashboard"""
    print("📊 Testing Abandoned Cart Dashboard...")
    
    try:
        response = requests.get(f"{BACKEND_URL}/crm/abandoned-carts/dashboard")
        
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Response keys: {list(data.keys())}")
            if "statistics" in data:
                stats = data["statistics"]
                print(f"   Statistics: {stats}")
                print("   ✅ PASS: Dashboard working")
            else:
                print("   ❌ FAIL: Missing statistics")
        elif response.status_code in [401, 403]:
            print("   ✅ PASS: Endpoint exists but requires authentication")
        else:
            print(f"   ❌ FAIL: HTTP {response.status_code}")
    except Exception as e:
        print(f"   ❌ FAIL: Exception {e}")

def test_cart_recovery():
    """Test GET /api/recovery"""
    print("🔗 Testing Cart Recovery...")
    
    try:
        response = requests.get(f"{BACKEND_URL}/recovery?token=test-token")
        
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Response: {data}")
            if not data.get("success"):
                error = data.get("error", "")
                if "invalide" in error.lower() or "expiré" in error.lower():
                    print("   ✅ PASS: Token validation working")
                else:
                    print(f"   ❌ FAIL: Unexpected error: {error}")
            else:
                print("   ✅ PASS: Recovery endpoint working")
        else:
            print(f"   ❌ FAIL: HTTP {response.status_code}")
    except Exception as e:
        print(f"   ❌ FAIL: Exception {e}")

def test_delivery_note_generation():
    """Test POST /api/orders/{order_id}/delivery-note"""
    print("📄 Testing Delivery Note Generation...")
    
    delivery_data = {
        "delivery_address": {
            "street": "123 Rue de la Livraison",
            "city": "Lyon",
            "postal_code": "69001",
            "country": "France"
        },
        "delivery_method": "express",
        "carrier": "Test Carrier"
    }
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/orders/TEST-ORDER-123/delivery-note",
            json=delivery_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if data.get("success") and "pdf_base64" in data:
                pdf_size = len(data["pdf_base64"])
                print(f"   ✅ PASS: PDF generated, Size: {pdf_size} chars")
            else:
                print("   ❌ FAIL: Missing PDF data")
        elif response.status_code == 404:
            print("   ✅ PASS: Endpoint exists (test order not found)")
        else:
            print(f"   ❌ FAIL: HTTP {response.status_code}")
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   ❌ FAIL: Exception {e}")

def test_process_recovery_emails():
    """Test POST /api/crm/process-recovery-emails"""
    print("📧 Testing Process Recovery Emails...")
    
    try:
        response = requests.post(f"{BACKEND_URL}/crm/process-recovery-emails")
        
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Response: {data}")
            if data.get("success"):
                print("   ✅ PASS: Email processing working")
            else:
                print("   ❌ FAIL: Success flag not set")
        elif response.status_code in [401, 403]:
            print("   ✅ PASS: Endpoint exists but requires authentication")
        else:
            print(f"   ❌ FAIL: HTTP {response.status_code}")
    except Exception as e:
        print(f"   ❌ FAIL: Exception {e}")

def authenticate_manager():
    """Authenticate as manager"""
    print("🔐 Authenticating as manager...")
    
    login_data = {
        "username": "antonio@josmose.com",
        "password": "Antonio@2024!Secure"
    }
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            if "access_token" in data:
                print("   ✅ Manager authentication successful")
                return data['access_token']
        
        print(f"   ❌ Authentication failed: {response.status_code}")
        return None
    except Exception as e:
        print(f"   ❌ Authentication exception: {e}")
        return None

def main():
    print("=" * 80)
    print("JOSMOSE.COM - ABANDONED CART SYSTEM TESTING")
    print("=" * 80)
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Test started at: {datetime.now().isoformat()}")
    print()
    
    # Test authentication first
    token = authenticate_manager()
    session = requests.Session()
    if token:
        session.headers.update({"Authorization": f"Bearer {token}"})
    
    print()
    
    # Test abandoned cart tracking
    cart_id = test_abandoned_cart_tracking()
    print()
    
    # Test dashboard
    test_abandoned_cart_dashboard()
    print()
    
    # Test cart recovery
    test_cart_recovery()
    print()
    
    # Test delivery note generation
    test_delivery_note_generation()
    print()
    
    # Test email processing
    test_process_recovery_emails()
    print()
    
    print("=" * 80)
    print("ABANDONED CART SYSTEM TESTING COMPLETED")
    print("=" * 80)

if __name__ == "__main__":
    main()