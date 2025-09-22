#!/usr/bin/env python3
"""
Test script to verify the new package structure imports work correctly
"""
import sys
from pathlib import Path

src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def test_stripe_service_import():
    """Test that the new Stripe service can be imported"""
    try:
        from josmoze_ecommerce.backend.services.stripe_service import StripeCheckout
        print('✅ Stripe service import successful')
        return True
    except Exception as e:
        print(f'❌ Stripe service import failed: {e}')
        return False

def test_main_app_import():
    """Test that the main app can be imported"""
    try:
        from josmoze_ecommerce.backend.main import app
        print('✅ Main app import successful')
        return True
    except Exception as e:
        print(f'❌ Main app import failed: {e}')
        return False

def test_models_import():
    """Test that models can be imported"""
    try:
        from josmoze_ecommerce.backend.models import Product, Order, Lead
        print('✅ Models import successful')
        return True
    except Exception as e:
        print(f'❌ Models import failed: {e}')
        return False

def test_utils_import():
    """Test that utils can be imported"""
    try:
        from josmoze_ecommerce.backend.utils import validate_email, calculate_lead_score
        print('✅ Utils import successful')
        return True
    except Exception as e:
        print(f'❌ Utils import failed: {e}')
        return False

def test_payment_manager_import():
    """Test that payment manager can be imported with new structure"""
    try:
        from josmoze_ecommerce.backend.services.payment_manager import PaymentManager
        print('✅ Payment manager import successful')
        return True
    except Exception as e:
        print(f'❌ Payment manager import failed: {e}')
        return False

if __name__ == "__main__":
    print("Testing new package structure imports...")
    print("=" * 50)
    
    tests = [
        test_stripe_service_import,
        test_main_app_import,
        test_models_import,
        test_utils_import,
        test_payment_manager_import
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All imports working correctly!")
        sys.exit(0)
    else:
        print("❌ Some imports failed - need to fix package structure")
        sys.exit(1)
