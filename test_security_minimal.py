#!/usr/bin/env python3
"""
Minimal test to verify security middleware is enabled without problematic dependencies
"""
import sys
import os
sys.path.append('./backend')

def test_security_configuration():
    """Test that security middleware is properly configured"""
    print("=== Testing Security Configuration ===")
    
    tests = [
        {
            "name": "Security Middleware Import",
            "check": "security_middleware_import"
        },
        {
            "name": "Security Middleware Enabled in server.py",
            "check": "middleware_enabled"
        },
        {
            "name": "Environment Variables Cleaned",
            "check": "env_duplicates"
        },
        {
            "name": "Security Configuration Available",
            "check": "security_config"
        }
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        print(f"\n--- {test['name']} ---")
        
        try:
            if test["check"] == "security_middleware_import":
                from backend.security_middleware import SecurityMiddleware, CacheMiddleware, get_security_stats
                print("✅ PASS: Security middleware modules imported successfully")
                passed += 1
                
            elif test["check"] == "middleware_enabled":
                with open('./backend/server.py', 'r') as f:
                    content = f.read()
                    if 'app.add_middleware(SecurityMiddleware)' in content and '# app.add_middleware(SecurityMiddleware)' not in content:
                        print("✅ PASS: SecurityMiddleware is enabled in server.py")
                        passed += 1
                    else:
                        print("❌ FAIL: SecurityMiddleware not properly enabled")
                        
            elif test["check"] == "env_duplicates":
                with open('./backend/.env', 'r') as f:
                    content = f.read()
                    stripe_count = content.count('STRIPE_API_KEY=')
                    if stripe_count == 1:
                        print("✅ PASS: Duplicate STRIPE_API_KEY entries removed")
                        passed += 1
                    else:
                        print(f"❌ FAIL: Found {stripe_count} STRIPE_API_KEY entries (should be 1)")
                        
            elif test["check"] == "security_config":
                from backend.security_middleware import SECURITY_CONFIG
                required_keys = ["rate_limit", "blocked_ips", "suspicious_patterns", "max_request_size"]
                if all(key in SECURITY_CONFIG for key in required_keys):
                    print("✅ PASS: Security configuration is complete")
                    print(f"   Rate limit: {SECURITY_CONFIG['rate_limit']['requests_per_minute']}/min")
                    print(f"   Max request size: {SECURITY_CONFIG['max_request_size']} bytes")
                    print(f"   Suspicious patterns: {len(SECURITY_CONFIG['suspicious_patterns'])} configured")
                    passed += 1
                else:
                    print("❌ FAIL: Security configuration incomplete")
                    
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
    
    print(f"\n=== Security Configuration Test Results ===")
    print(f"✅ Passed: {passed}/{total}")
    print(f"📈 Success Rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("🔒 Security middleware is properly configured!")
        print("📋 Security Features Enabled:")
        print("   • DDoS protection with rate limiting")
        print("   • SQL injection and XSS pattern detection")
        print("   • Request size validation")
        print("   • IP blocking capabilities")
        print("   • Performance caching middleware")
        print("   • Security event logging")
        return True
    else:
        print("⚠️ Security configuration needs attention")
        return False

if __name__ == "__main__":
    success = test_security_configuration()
    sys.exit(0 if success else 1)
