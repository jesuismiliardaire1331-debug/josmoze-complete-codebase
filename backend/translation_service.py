"""
Service de traduction automatique avec géolocalisation IP
Utilise DeepL API pour les traductions et détection IP pour la localisation
"""

import os
import asyncio
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import deepl
import json
from ip2geotools.databases.noncommercial import DbIpCity
from fastapi import Request
import requests
from functools import lru_cache

# Configuration
DEEPL_API_KEY = os.getenv("DEEPL_API_KEY")
translator = deepl.Translator(DEEPL_API_KEY) if DEEPL_API_KEY else None

# Mapping pays vers langues européennes prioritaires
COUNTRY_TO_LANGUAGE = {
    "FR": "FR",      # France -> Français
    "ES": "ES",      # Espagne -> Espagnol
    "IT": "IT",      # Italie -> Italien
    "DE": "DE",      # Allemagne -> Allemand
    "GB": "EN-GB",   # Royaume-Uni -> Anglais britannique
    "IE": "EN-GB",   # Irlande -> Anglais britannique
    "NL": "NL",      # Pays-Bas -> Néerlandais
    "BE": "NL",      # Belgique -> Néerlandais (par défaut, peut être FR aussi)
    "PT": "PT-PT",   # Portugal -> Portugais européen
    "PL": "PL",      # Pologne -> Polonais
    "AT": "DE",      # Autriche -> Allemand
    "CH": "DE",      # Suisse -> Allemand (par défaut)
    "LU": "FR",      # Luxembourg -> Français
    "MT": "EN-GB",   # Malte -> Anglais
    "CY": "EN-GB",   # Chypre -> Anglais
    "GR": "EN-GB",   # Grèce -> Anglais (DeepL ne supporte pas le grec)
    "BG": "EN-GB",   # Bulgarie -> Anglais (DeepL ne supporte pas le bulgare)
    "RO": "EN-GB",   # Roumanie -> Anglais (DeepL ne supporte pas le roumain)
    "HR": "EN-GB",   # Croatie -> Anglais (DeepL ne supporte pas le croate)
    "SI": "EN-GB",   # Slovénie -> Anglais (DeepL ne supporte pas le slovène)
    "SK": "EN-GB",   # Slovaquie -> Anglais (DeepL ne supporte pas le slovaque)
    "CZ": "EN-GB",   # République tchèque -> Anglais (DeepL ne supporte pas le tchèque)
    "HU": "EN-GB",   # Hongrie -> Anglais (DeepL ne supporte pas le hongrois)
    "LT": "EN-GB",   # Lituanie -> Anglais (DeepL ne supporte pas le lituanien)
    "LV": "EN-GB",   # Lettonie -> Anglais (DeepL ne supporte pas le letton)
    "EE": "EN-GB",   # Estonie -> Anglais (DeepL ne supporte pas l'estonien)
    "FI": "EN-GB",   # Finlande -> Anglais (DeepL ne supporte pas le finnois)
    "SE": "EN-GB",   # Suède -> Anglais (DeepL ne supporte pas le suédois)
    "DK": "EN-GB",   # Danemark -> Anglais (DeepL ne supporte pas le danois)
    "NO": "EN-GB",   # Norvège -> Anglais (DeepL ne supporte pas le norvégien)
    "IS": "EN-GB",   # Islande -> Anglais (DeepL ne supporte pas l'islandais)
    "US": "EN-US",   # États-Unis -> Anglais américain
    "CA": "EN-US",   # Canada -> Anglais américain
}

# Mapping devise par pays
COUNTRY_TO_CURRENCY = {
    # Zone Euro
    "FR": {"code": "EUR", "symbol": "€", "name": "Euro"},
    "ES": {"code": "EUR", "symbol": "€", "name": "Euro"},
    "IT": {"code": "EUR", "symbol": "€", "name": "Euro"},
    "DE": {"code": "EUR", "symbol": "€", "name": "Euro"},
    "NL": {"code": "EUR", "symbol": "€", "name": "Euro"},
    "BE": {"code": "EUR", "symbol": "€", "name": "Euro"},
    "PT": {"code": "EUR", "symbol": "€", "name": "Euro"},
    "AT": {"code": "EUR", "symbol": "€", "name": "Euro"},
    "LU": {"code": "EUR", "symbol": "€", "name": "Euro"},
    "MT": {"code": "EUR", "symbol": "€", "name": "Euro"},
    "CY": {"code": "EUR", "symbol": "€", "name": "Euro"},
    "GR": {"code": "EUR", "symbol": "€", "name": "Euro"},
    "SI": {"code": "EUR", "symbol": "€", "name": "Euro"},
    "SK": {"code": "EUR", "symbol": "€", "name": "Euro"},
    "EE": {"code": "EUR", "symbol": "€", "name": "Euro"},
    "LV": {"code": "EUR", "symbol": "€", "name": "Euro"},
    "LT": {"code": "EUR", "symbol": "€", "name": "Euro"},
    "FI": {"code": "EUR", "symbol": "€", "name": "Euro"},
    "IE": {"code": "EUR", "symbol": "€", "name": "Euro"},
    
    # Autres devises européennes
    "GB": {"code": "GBP", "symbol": "£", "name": "Livre Sterling"},
    "CH": {"code": "CHF", "symbol": "CHF", "name": "Franc Suisse"},
    "PL": {"code": "PLN", "symbol": "zł", "name": "Złoty"},
    "CZ": {"code": "CZK", "symbol": "Kč", "name": "Couronne Tchèque"},
    "DK": {"code": "DKK", "symbol": "kr", "name": "Couronne Danoise"},
    "SE": {"code": "SEK", "symbol": "kr", "name": "Couronne Suédoise"},
    "NO": {"code": "NOK", "symbol": "kr", "name": "Couronne Norvégienne"},
    "HU": {"code": "HUF", "symbol": "Ft", "name": "Forint"},
    "RO": {"code": "RON", "symbol": "lei", "name": "Leu Roumain"},
    "BG": {"code": "BGN", "symbol": "лв", "name": "Lev Bulgare"},
    "HR": {"code": "HRK", "symbol": "kn", "name": "Kuna Croate"},
    "IS": {"code": "ISK", "symbol": "kr", "name": "Couronne Islandaise"},
    
    # Amérique du Nord
    "US": {"code": "USD", "symbol": "$", "name": "Dollar US"},
    "CA": {"code": "CAD", "symbol": "C$", "name": "Dollar Canadien"},
}

# Langues disponibles avec leurs noms natifs
AVAILABLE_LANGUAGES = {
    "FR": {"name": "Français", "native_name": "Français", "flag": "🇫🇷"},
    "EN-GB": {"name": "English", "native_name": "English", "flag": "🇬🇧"},
    "EN-US": {"name": "English (US)", "native_name": "English (US)", "flag": "🇺🇸"},
    "ES": {"name": "Español", "native_name": "Español", "flag": "🇪🇸"},
    "IT": {"name": "Italiano", "native_name": "Italiano", "flag": "🇮🇹"},
    "DE": {"name": "Deutsch", "native_name": "Deutsch", "flag": "🇩🇪"},
    "NL": {"name": "Nederlands", "native_name": "Nederlands", "flag": "🇳🇱"},
    "PT-PT": {"name": "Português", "native_name": "Português", "flag": "🇵🇹"},
    "PL": {"name": "Polski", "native_name": "Polski", "flag": "🇵🇱"},
}

class TranslationService:
    def __init__(self):
        self.translator = translator
        self.cache = {}
        self.setup_logging()

    def setup_logging(self):
        """Configure logging pour le service de traduction"""
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    @lru_cache(maxsize=100)
    def detect_country_from_ip(self, ip_address: str) -> str:
        """
        Détecte le pays à partir de l'adresse IP
        Utilise un cache pour éviter les appels répétés
        """
        try:
            if not ip_address or ip_address == "127.0.0.1" or ip_address.startswith("192.168."):
                # IP locale - retourner France par défaut
                return "FR"
            
            # Utilise ip2geotools pour détecter le pays
            response = DbIpCity.get(ip_address, api_key='free')
            country_code = response.country
            
            self.logger.info(f"IP {ip_address} -> Pays détecté: {country_code}")
            return country_code or "FR"
            
        except Exception as e:
            self.logger.error(f"Erreur détection pays pour IP {ip_address}: {str(e)}")
            return "FR"  # Fallback vers France

    def get_user_language_from_ip(self, ip_address: str) -> str:
        """
        Détermine la langue préférée basée sur l'IP
        """
        country = self.detect_country_from_ip(ip_address)
        language = COUNTRY_TO_LANGUAGE.get(country, "FR")
        
        self.logger.info(f"IP {ip_address} -> Pays: {country} -> Langue: {language}")
        return language

    def get_user_currency_from_ip(self, ip_address: str) -> Dict[str, str]:
        """
        Détermine la devise appropriée basée sur l'IP
        """
        country = self.detect_country_from_ip(ip_address)
        currency = COUNTRY_TO_CURRENCY.get(country, {"code": "EUR", "symbol": "€", "name": "Euro"})
        
        self.logger.info(f"IP {ip_address} -> Pays: {country} -> Devise: {currency}")
        return currency

    def get_client_ip(self, request: Request) -> str:
        """
        Extrait l'adresse IP réelle du client depuis les headers
        Gère les proxies et CDN
        """
        # Vérifier les headers de proxy dans l'ordre de priorité
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # Prendre la première IP (IP originale du client)
            ip = forwarded_for.split(",")[0].strip()
            if ip:
                return ip

        # Autres headers possibles
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip.strip()

        cf_connecting_ip = request.headers.get("CF-Connecting-IP")  # Cloudflare
        if cf_connecting_ip:
            return cf_connecting_ip.strip()

        # Fallback vers l'IP de connexion directe
        return request.client.host if request.client else "127.0.0.1"

    async def translate_text(self, text: str, target_language: str, source_language: str = "FR") -> str:
        """
        Traduit un texte vers la langue cible
        Utilise le cache pour éviter les appels répétés à l'API
        """
        if not self.translator:
            self.logger.error("DeepL translator not initialized - API key missing")
            return text

        if target_language == source_language:
            return text

        # Clé de cache
        cache_key = f"{source_language}:{target_language}:{hash(text)}"
        
        if cache_key in self.cache:
            return self.cache[cache_key]

        try:
            result = await asyncio.to_thread(
                self.translator.translate_text,
                text,
                source_lang=source_language,
                target_lang=target_language
            )
            
            translated_text = result.text
            self.cache[cache_key] = translated_text
            
            self.logger.info(f"Traduction: {source_language} -> {target_language}")
            return translated_text
            
        except Exception as e:
            self.logger.error(f"Erreur traduction DeepL: {str(e)}")
            return text  # Retourner le texte original en cas d'erreur

    async def translate_object(self, obj: Dict, target_language: str, source_language: str = "FR") -> Dict:
        """
        Traduit récursivement un objet/dictionnaire
        Traduit seulement les valeurs string, préserve la structure
        """
        if not isinstance(obj, dict):
            return obj

        translated_obj = {}
        
        for key, value in obj.items():
            if isinstance(value, str):
                # Traduire les valeurs string
                translated_obj[key] = await self.translate_text(value, target_language, source_language)
            elif isinstance(value, dict):
                # Récursion pour les objets imbriqués
                translated_obj[key] = await self.translate_object(value, target_language, source_language)
            elif isinstance(value, list):
                # Traiter les listes
                translated_list = []
                for item in value:
                    if isinstance(item, str):
                        translated_list.append(await self.translate_text(item, target_language, source_language))
                    elif isinstance(item, dict):
                        translated_list.append(await self.translate_object(item, target_language, source_language))
                    else:
                        translated_list.append(item)
                translated_obj[key] = translated_list
            else:
                # Préserver les autres types (nombres, booléens, etc.)
                translated_obj[key] = value

        return translated_obj

    def get_available_languages(self) -> Dict[str, Dict[str, str]]:
        """
        Retourne la liste des langues disponibles avec leurs métadonnées
        """
        return AVAILABLE_LANGUAGES

    def get_language_info(self, language_code: str) -> Dict[str, str]:
        """
        Retourne les informations d'une langue spécifique
        """
        return AVAILABLE_LANGUAGES.get(language_code, AVAILABLE_LANGUAGES["FR"])

    async def translate_product_list(self, products: List[Dict], target_language: str) -> List[Dict]:
        """
        Traduit une liste de produits
        Optimisé pour les données e-commerce
        """
        translated_products = []
        
        for product in products:
            translated_product = await self.translate_object(product, target_language)
            translated_products.append(translated_product)
        
        return translated_products

    def clear_cache(self):
        """
        Vide le cache de traductions
        Utile pour les mises à jour ou tests
        """
        self.cache.clear()
        self.logger.info("Cache de traduction vidé")

    def get_cache_stats(self) -> Dict[str, int]:
        """
        Retourne les statistiques du cache
        """
        return {
            "cache_size": len(self.cache),
            "max_size": 1000  # Limite arbitraire
        }

# Instance globale du service
translation_service = TranslationService()