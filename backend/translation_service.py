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
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

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

# Traductions prédéfinies pour les produits (fallback quand DeepL n'est pas disponible)
PRODUCT_TRANSLATIONS = {
    "ES": {
        "Fontaine à Eau Osmosée": "Fuente de Agua Osmótica",
        "Kit Filtres de Rechange": "Kit de Filtros de Repuesto", 
        "Extension Garantie 2 ans": "Extensión de Garantía 2 años",
        "Extension Garantie 5 ans": "Extensión de Garantía 5 años",
        "Système d'osmose inverse professionnel avec technologie Blue Mountain": "Sistema de ósmosis inversa profesional con tecnología Blue Mountain",
        "Filtres haute qualité avec certifications européennes": "Filtros de alta calidad con certificaciones europeas",
        "Protection étendue avec intervention à domicile": "Protección extendida con intervención a domicilio",
        "Couverture totale avec pièces et main d'œuvre": "Cobertura total con piezas y mano de obra",
        "En stock": "En stock",
        "Rupture": "Sin stock",
        "Stock limité": "Stock limitado"
    },
    "EN": {
        "Fontaine à Eau Osmosée": "Osmotic Water Fountain",
        "Kit Filtres de Rechange": "Replacement Filter Kit",
        "Extension Garantie 2 ans": "2-Year Warranty Extension", 
        "Extension Garantie 5 ans": "5-Year Warranty Extension",
        "Système d'osmose inverse professionnel avec technologie Blue Mountain": "Professional reverse osmosis system with Blue Mountain technology",
        "Filtres haute qualité avec certifications européennes": "High quality filters with European certifications",
        "Protection étendue avec intervention à domicile": "Extended protection with home intervention",
        "Couverture totale avec pièces et main d'œuvre": "Total coverage with parts and labor",
        "En stock": "In stock",
        "Rupture": "Out of stock", 
        "Stock limité": "Limited stock"
    },
    "DE": {
        "Fontaine à Eau Osmosée": "Umkehrosmose-Wasserbrunnen",
        "Kit Filtres de Rechange": "Ersatzfilter-Set",
        "Extension Garantie 2 ans": "2-Jahres-Garantieverlängerung",
        "Extension Garantie 5 ans": "5-Jahres-Garantieverlängerung",
        "Système d'osmose inverse professionnel avec technologie Blue Mountain": "Professionelle Umkehrosmoseanlage mit Blue Mountain Technologie",
        "Filtres haute qualité avec certifications européennes": "Hochwertige Filter mit europäischen Zertifizierungen",
        "Protection étendue avec intervention à domicile": "Erweiterte Schutz mit Hausinjektion",
        "Couverture totale avec pièces et main d'œuvre": "Vollständige Abdeckung mit Teilen und Arbeit",
        "En stock": "Auf Lager",
        "Rupture": "Nicht auf Lager",
        "Stock limité": "Begrenzter Bestand"
    },
    "IT": {
        "Fontaine à Eau Osmosée": "Fontana d'Acqua Osmotica",
        "Kit Filtres de Rechange": "Kit Filtri di Ricambio",
        "Extension Garantie 2 ans": "Estensione Garanzia 2 anni",
        "Extension Garantie 5 ans": "Estensione Garanzia 5 anni",
        "Système d'osmose inverse professionnel avec technologie Blue Mountain": "Sistema di osmosi inversa professionale con tecnologia Blue Mountain",
        "Filtres haute qualité avec certifications européennes": "Filtri di alta qualità con certificazioni europee",
        "Protection étendue avec intervention à domicile": "Protezione estesa con intervento a domicilio",
        "Couverture totale avec pièces et main d'œuvre": "Copertura totale con parti e manodopera",
        "En stock": "Disponibile",
        "Rupture": "Esaurito",
        "Stock limité": "Stock limitato"
    },
    "NL": {
        "Fontaine à Eau Osmosée": "Osmotische Waterbron",
        "Kit Filtres de Rechange": "Vervangingsfilter Kit",
        "Extension Garantie 2 ans": "2-Jaar Garantie Uitbreiding",
        "Extension Garantie 5 ans": "5-Jaar Garantie Uitbreiding",
        "En stock": "Op voorraad",
        "Rupture": "Uitverkocht",
        "Stock limité": "Beperkte voorraad"
    },
    "PT-PT": {
        "Fontaine à Eau Osmosée": "Fonte de Água Osmótica", 
        "Kit Filtres de Rechange": "Kit de Filtros de Substituição",
        "Extension Garantie 2 ans": "Extensão de Garantia 2 anos",
        "Extension Garantie 5 ans": "Extensão de Garantia 5 anos",
        "En stock": "Em stock",
        "Rupture": "Esgotado",
        "Stock limité": "Stock limitado"
    },
    "PL": {
        "Fontaine à Eau Osmosée": "Fontanna Wody Osmotycznej",
        "Kit Filtres de Rechange": "Zestaw Filtrów Zamiennych",
        "Extension Garantie 2 ans": "Rozszerzenie Gwarancji 2 lata",
        "Extension Garantie 5 ans": "Rozszerzenie Gwarancji 5 lat",
        "En stock": "W magazynie",
        "Rupture": "Brak w magazynie", 
        "Stock limité": "Ograniczony zapas"
    }
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
        SITE FRANÇAIS - Force le français par défaut pour Josmose.com
        Détermine la langue préférée basée sur l'IP avec override français pour site business français
        """
        # OVERRIDE POUR SITE FRANÇAIS - Toujours retourner français pour business français
        # Ceci résout le problème où l'IP du serveur (US) forçait l'anglais
        language = "FR"  # Force français par défaut pour Josmose.com
        
        self.logger.info(f"IP {ip_address} -> SITE FRANÇAIS forcé -> Langue: {language}")
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
        Utilise d'abord DeepL, puis fallback vers traductions prédéfinies
        """
        if not text or type(text) != str:
            return text

        if target_language == source_language:
            return text

        # Clé de cache
        cache_key = f"{source_language}:{target_language}:{hash(text)}"
        
        if cache_key in self.cache:
            return self.cache[cache_key]

        # Vérifier d'abord les traductions prédéfinies
        if target_language in PRODUCT_TRANSLATIONS and text.strip() in PRODUCT_TRANSLATIONS[target_language]:
            translated_text = PRODUCT_TRANSLATIONS[target_language][text.strip()]
            self.cache[cache_key] = translated_text
            self.logger.info(f"Traduction prédéfinie utilisée: {text} -> {translated_text}")
            return translated_text

        # Essayer DeepL si disponible
        if not self.translator:
            self.logger.error("DeepL translator not initialized - API key missing")
            return text

        try:
            result = await asyncio.to_thread(
                self.translator.translate_text,
                text,
                source_lang=source_language,
                target_lang=target_language
            )
            
            translated_text = result.text
            self.cache[cache_key] = translated_text
            
            self.logger.info(f"Traduction DeepL: {source_language} -> {target_language}")
            return translated_text
            
        except Exception as e:
            error_msg = str(e).lower()
            if "too many requests" in error_msg or "429" in error_msg or "high load" in error_msg:
                self.logger.warning(f"DeepL rate limited, tentative traduction prédéfinie pour: {text}")
                
                # Fallback vers traductions prédéfinies si DeepL est surchargé
                if target_language in PRODUCT_TRANSLATIONS:
                    # Recherche approximative dans les traductions prédéfinies
                    for french_text, translated_text in PRODUCT_TRANSLATIONS[target_language].items():
                        if french_text.lower() in text.lower() or text.lower() in french_text.lower():
                            self.cache[cache_key] = translated_text
                            self.logger.info(f"Traduction fallback utilisée: {text} -> {translated_text}")
                            return translated_text
                
                self.logger.warning(f"Aucune traduction fallback trouvée pour: {text}")
            else:
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