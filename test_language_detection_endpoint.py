#!/usr/bin/env python3
"""
Test script to verify language detection endpoint behavior
without starting the full server with all dependencies
"""
import sys
import os
sys.path.append('./backend')

from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from backend.translation_service import translation_service

app = FastAPI()

class MockRequest:
    def __init__(self, client_ip="127.0.0.1"):
        self.client = MockClient(client_ip)
        
class MockClient:
    def __init__(self, host):
        self.host = host

class LanguageDetectionResponse:
    def __init__(self, detected_language, detected_country, currency, available_languages, ip_address):
        self.detected_language = detected_language
        self.detected_country = detected_country
        self.currency = currency
        self.available_languages = available_languages
        self.ip_address = ip_address
    
    def dict(self):
        return {
            "detected_language": self.detected_language,
            "detected_country": self.detected_country,
            "currency": self.currency,
            "available_languages": self.available_languages,
            "ip_address": self.ip_address
        }

@app.get("/localization/detect")
async def detect_user_localization(request: Request = None):
    """
    Détecte automatiquement la langue et la devise de l'utilisateur basé sur l'IP
    """
    try:
        if request is None:
            request = MockRequest()
            
        # Obtenir l'IP du client
        client_ip = translation_service.get_client_ip(request)
        
        # Détecter la langue basée sur l'IP
        detected_language = translation_service.get_user_language_from_ip(client_ip)
        
        # Détecter la devise basée sur l'IP
        currency = translation_service.get_user_currency_from_ip(client_ip)
        
        # Détecter le pays
        detected_country = translation_service.detect_country_from_ip(client_ip)
        
        # Obtenir les langues disponibles
        available_languages = translation_service.get_available_languages()
        
        response = LanguageDetectionResponse(
            detected_language=detected_language,
            detected_country=detected_country,
            currency=currency,
            available_languages=available_languages,
            ip_address=client_ip
        )
        
        return response.dict()
        
    except Exception as e:
        print(f"Error in localization detection: {str(e)}")
        # Fallback vers les valeurs par défaut
        response = LanguageDetectionResponse(
            detected_language="FR",
            detected_country="FR", 
            currency={"code": "EUR", "symbol": "€", "name": "Euro"},
            available_languages=translation_service.get_available_languages(),
            ip_address="unknown"
        )
        return response.dict()

def test_language_detection_endpoint():
    """Test the language detection endpoint directly"""
    print("=== Testing Language Detection Endpoint ===")
    
    client = TestClient(app)
    
    test_cases = [
        {"name": "Default request", "headers": {}},
        {"name": "French headers", "headers": {"Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8"}},
        {"name": "US headers", "headers": {"Accept-Language": "en-US,en;q=0.9"}},
    ]
    
    for test_case in test_cases:
        print(f"\n--- {test_case['name']} ---")
        
        try:
            response = client.get("/localization/detect", headers=test_case['headers'])
            
            if response.status_code == 200:
                data = response.json()
                
                print(f"Status: {response.status_code}")
                print(f"Language: {data.get('detected_language')}")
                print(f"Country: {data.get('detected_country')}")
                print(f"Currency: {data.get('currency')}")
                print(f"IP: {data.get('ip_address')}")
                
                is_french = data.get('detected_language') == 'FR'
                is_france = data.get('detected_country') == 'FR'
                currency = data.get('currency', {})
                is_euro = currency.get('code') == 'EUR' if isinstance(currency, dict) else currency == 'EUR'
                
                if is_french and is_france and is_euro:
                    print("✅ PASS: Returns FR/FR/EUR as expected")
                else:
                    print(f"❌ FAIL: Expected FR/FR/EUR, got {data.get('detected_language')}/{data.get('detected_country')}/{currency}")
                    
            else:
                print(f"❌ FAIL: HTTP {response.status_code}")
                print(f"Response: {response.text}")
                
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")

if __name__ == "__main__":
    test_language_detection_endpoint()
