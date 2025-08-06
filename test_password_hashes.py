#!/usr/bin/env python3
"""
Test password hashes for @osmose.com email system
"""

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Test passwords
test_passwords = {
    "antonio@josmose.com": "Antonio@2024!Secure",
    "aziza@josmose.com": "Aziza@2024!Director", 
    "naima@josmose.com": "Naima@2024!Commerce",
    "commercial@josmose.com": "Commercial@2024!Sales",
    "support@josmose.com": "Support@2024!Help"
}

# Current hashes from auth.py
current_hashes = {
    "antonio@josmose.com": "$2b$12$gWfOtZyEWTzJ2871yBT8W.FfLGIpm9VGEjYGRTZUVOQXQcIR2LRHe",
    "aziza@josmose.com": "$2b$12$GHSiiMx03IQ81HMWinZUn.xvyi3MtGhg6k6mZG1QXqCwCZJT5b/vm",
    "naima@josmose.com": "$2b$12$T3.CqIsUwLAcFv8lM2fyGOBlYKAIJB0TZXXmWrYg2SFim/jgW1Cd2",
    "commercial@josmose.com": "$2b$12$T3.CqIsUwLAcFv8lM2fyGOBlYKAIJB0TZXXmWrYg2SFim/jgW1Cd2",  # Same as Naima - WRONG!
    "support@josmose.com": "$2b$12$AgqPE73OcPnBKMmpgCQ3IOiShGsj8AuBo.TLETjIUJgS.AD9aFEd."
}

print("🔐 Testing password hashes for @osmose.com email system")
print("=" * 60)

for email, password in test_passwords.items():
    current_hash = current_hashes[email]
    is_valid = pwd_context.verify(password, current_hash)
    
    if is_valid:
        print(f"✅ {email}: Password matches hash")
    else:
        print(f"❌ {email}: Password does NOT match hash")
        # Generate correct hash
        correct_hash = pwd_context.hash(password)
        print(f"   Correct hash should be: {correct_hash}")

print("\n🔧 ISSUE FOUND:")
print("The commercial@josmose.com user is using the same password hash as naima@josmose.com")
print("This means it's trying to authenticate 'Commercial@2024!Sales' against 'Naima@2024!Commerce' hash")
print("\nFIX: Update the commercial user's password_hash in auth.py")