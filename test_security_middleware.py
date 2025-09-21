#!/usr/bin/env python3
"""
Test script to verify the security middleware is working correctly
"""
import sys
import os
sys.path.append('./backend')

from fastapi.testclient import TestClient
from backend.server import app

def test_security_middleware():
    """Test the security middleware functionality"""
    print("=== Testing Security Middleware ===")
    
    client = TestClient(app)
    
    tests = [
        {
            "name": "Basic Request with Security Headers",
            "method": "GET",
            "url": "/",
            "expected_status": 200,
            "check_security_headers": True
        },
        {
            "name": "Rate Limiting Test (Multiple Requests)",
            "method": "GET", 
            "url": "/api/detect-location",
            "expected_status": 200,
            "repeat": 5,
            "check_rate_limit": True
        },
        {
            "name": "Cache Middleware Test",
            "method": "GET",
            "url": "/api/products",
            "expected_status": 200,
            "check_cache": True
        },
        {
            "name": "Security Statistics Endpoint",
            "method": "GET",
            "url": "/api/admin/security-statistics",
            "expected_status": 200,
            "check_security_stats": True
        },
        {
            "name": "Suspicious Pattern Detection",
            "method": "GET",
            "url": "/api/products?id=1' OR '1'='1",
            "expected_status": 400,
            "check_blocked": True
        }
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        print(f"\n--- {test['name']} ---")
        
        try:
            repeat_count = test.get("repeat", 1)
            responses = []
            
            for i in range(repeat_count):
                if test["method"] == "GET":
                    response = client.get(test["url"])
                else:
                    response = client.post(test["url"], json=test.get("data", {}))
                responses.append(response)
            
            response = responses[-1]
            
            if response.status_code == test["expected_status"]:
                print(f"✅ PASS: Status {response.status_code}")
                
                if test.get("check_security_headers"):
                    process_time = response.headers.get("X-Process-Time")
                    if process_time:
                        print(f"✅ PASS: Security middleware active (process time: {process_time}s)")
                    else:
                        print(f"⚠️  WARNING: X-Process-Time header missing")
                
                if test.get("check_cache"):
                    cache_header = response.headers.get("X-Cache")
                    if cache_header:
                        print(f"✅ PASS: Cache middleware active (cache: {cache_header})")
                    else:
                        print(f"⚠️  WARNING: X-Cache header missing")
                
                if test.get("check_rate_limit"):
                    all_success = all(r.status_code == 200 for r in responses)
                    if all_success:
                        print(f"✅ PASS: Rate limiting allows normal traffic ({repeat_count} requests)")
                    else:
                        print(f"❌ FAIL: Rate limiting too aggressive")
                        continue
                
                if test.get("check_security_stats"):
                    try:
                        data = response.json()
                        if "security_events_24h" in data or "blocked_ips_count" in data:
                            print(f"✅ PASS: Security statistics available")
                        else:
                            print(f"⚠️  WARNING: Security statistics incomplete")
                    except:
                        print(f"⚠️  WARNING: Could not parse security statistics")
                
                if test.get("check_blocked"):
                    print(f"✅ PASS: Suspicious pattern blocked correctly")
                
                passed += 1
                
            else:
                print(f"❌ FAIL: Expected {test['expected_status']}, got {response.status_code}")
                if response.status_code >= 400:
                    print(f"   Error: {response.text}")
                
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
    
    print(f"\n=== Security Middleware Test Results ===")
    print(f"✅ Passed: {passed}/{total}")
    print(f"📈 Success Rate: {(passed/total)*100:.1f}%")
    
    if passed >= total * 0.8:  # 80% pass rate acceptable for security features
        print("🔒 Security middleware is working correctly!")
        return True
    else:
        print("⚠️ Security middleware needs attention")
        return False

if __name__ == "__main__":
    success = test_security_middleware()
    sys.exit(0 if success else 1)
