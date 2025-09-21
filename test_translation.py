#!/usr/bin/env python3
"""
Test script to verify translation service behavior
"""
import sys
import os
sys.path.append('./backend')

from backend.translation_service import translation_service

def test_translation_service():
    print("=== Testing Translation Service ===")
    
    test_ip = "127.0.0.1"
    print(f"\nTesting with IP: {test_ip}")
    
    country = translation_service.detect_country_from_ip(test_ip)
    print(f"Country from IP: {country}")
    
    language = translation_service.get_user_language_from_ip(test_ip)
    print(f"Language from IP: {language}")
    
    currency = translation_service.get_user_currency_from_ip(test_ip)
    print(f"Currency from IP: {currency}")
    
    test_ip_us = "8.8.8.8"
    print(f"\nTesting with US IP: {test_ip_us}")
    
    country_us = translation_service.detect_country_from_ip(test_ip_us)
    print(f"Country from US IP: {country_us}")
    
    language_us = translation_service.get_user_language_from_ip(test_ip_us)
    print(f"Language from US IP: {language_us}")
    
    currency_us = translation_service.get_user_currency_from_ip(test_ip_us)
    print(f"Currency from US IP: {currency_us}")
    
    print("\n=== Expected Results ===")
    print("All results should be FR/EUR regardless of IP due to French site override")

if __name__ == "__main__":
    test_translation_service()
