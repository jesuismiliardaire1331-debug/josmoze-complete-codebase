#!/usr/bin/env python3
"""
Test utilitaire pour générer un token de désinscription
"""

import os
import hmac
import hashlib
import base64
from datetime import datetime, timezone

def generate_unsubscribe_token(email: str) -> str:
    """Générer un token sécurisé pour la désinscription"""
    try:
        secret_key = os.environ.get('UNSUBSCRIBE_SECRET_KEY', 'josmoze_unsubscribe_secret_2024!')
        
        # Créer le payload avec timestamp
        payload = f"{email}:{int(datetime.now(timezone.utc).timestamp())}"
        
        # Créer la signature HMAC
        signature = hmac.new(
            secret_key.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        # Encoder en base64 pour l'URL
        token_data = f"{payload}:{signature}"
        token = base64.urlsafe_b64encode(token_data.encode('utf-8')).decode('utf-8')
        
        return token
        
    except Exception as e:
        print(f"Erreur lors de la génération du token: {e}")
        return ""

def verify_unsubscribe_token(token: str) -> str:
    """Vérifier et décoder un token de désinscription"""
    try:
        secret_key = os.environ.get('UNSUBSCRIBE_SECRET_KEY', 'josmoze_unsubscribe_secret_2024!')
        
        # Décoder le token
        token_data = base64.urlsafe_b64decode(token.encode('utf-8')).decode('utf-8')
        parts = token_data.split(':')
        
        if len(parts) != 3:
            return None
        
        email, timestamp, signature = parts
        payload = f"{email}:{timestamp}"
        
        # Vérifier la signature HMAC
        expected_signature = hmac.new(
            secret_key.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        if not hmac.compare_digest(signature, expected_signature):
            return None
        
        # Vérifier l'expiration (30 jours)
        token_timestamp = int(timestamp)
        current_timestamp = int(datetime.now(timezone.utc).timestamp())
        
        if current_timestamp - token_timestamp > 2592000:  # 30 jours
            return None
        
        return email
        
    except Exception as e:
        print(f"Erreur lors de la vérification du token: {e}")
        return None

if __name__ == "__main__":
    # Test avec un email
    test_email = "test-desinscription@example.com"
    
    print(f"🧪 Test de génération de token pour: {test_email}")
    token = generate_unsubscribe_token(test_email)
    print(f"✅ Token généré: {token}")
    
    print(f"\n🔍 Vérification du token...")
    decoded_email = verify_unsubscribe_token(token)
    print(f"✅ Email décodé: {decoded_email}")
    
    if decoded_email == test_email:
        print("✅ Token valide!")
        print(f"\n🔗 Lien de test complet:")
        print(f"https://chatbot-debug-2.preview.emergentagent.com/unsubscribe?token={token}")
    else:
        print("❌ Erreur de validation du token!")