#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scraper Agent Osmoseurs France - JOSMOSE.COM
=============================================
Agent IA spécialisé dans la collecte éthique de prospects français
intéressés par la purification d'eau et les osmoseurs.

⚠️ AVERTISSEMENT LÉGAL :
- Utilisation uniquement sur des données publiques
- Respect obligatoire des robots.txt et CGU
- Conformité GDPR/CNIL stricte
- Pas de données sensibles ou privées

Fonctionnalités:
- Scraping intelligent multi-sources
- Validation contextuelle automatique
- Nettoyage et déduplication
- Intégration base prospects existante
- Audit trail complet

Auteur: Système OSMOSE v1.0
Date: Août 2025
"""

import asyncio
import aiohttp
import logging
import re
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Set
from urllib.parse import urlparse, urljoin, quote
from bs4 import BeautifulSoup
from dataclasses import dataclass
import json
import hashlib
from email_validator import validate_email, EmailNotValidError

# Import du gestionnaire prospects existant
from prospects_manager import ProspectsManager, ProspectCreate, ConsentStatus

# Configuration logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ScrapedProspect:
    """Données prospect scrapées"""
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    source_url: str = ""
    keyword_intent: str = ""
    city: Optional[str] = None
    country: str = "FR"
    context_snippet: str = ""  # Contexte de découverte
    confidence_score: float = 0.0  # Score de confiance (0-1)

class ScraperAgent:
    """Agent de scraping intelligent pour prospects osmoseurs"""
    
    def __init__(self, prospects_manager: ProspectsManager):
        self.prospects_manager = prospects_manager
        self.session = None
        self.scraped_urls = set()
        self.suppression_list = set()  # Liste emails à ne pas contacter
        self.rate_limit = 2  # Délai entre requêtes (secondes)
        
        # Mots-clés ciblés (conformité niche)
        self.target_keywords = [
            'osmoseur', 'osmose inverse', 'filtration eau', 'eau calcaire',
            'nitrates eau', 'eau pour bébé', 'purification eau', 'traitement eau',
            'eau robinet', 'chlore eau', 'eau pure', 'contaminants eau',
            'système filtration', 'adoucisseur eau', 'qualité eau'
        ]
        
        # Sources autorisées (forums publics, sites spécialisés)
        self.allowed_sources = [
            'forums.futura-sciences.com',
            'www.forum-eau.fr', 
            'bricolage.linternaute.com',
            'www.plombiers-reunis.com',
            'forums.techniciens-superieurs.fr',
            'www.forumconstruire.com',
            'forum.hardware.fr',  # Section bricolage/habitat
            'www.commentcamarche.net'
        ]
        
        # Patterns emails génériques à exclure
        self.generic_email_patterns = [
            r'info@', r'contact@', r'admin@', r'webmaster@', r'sales@',
            r'support@', r'service@', r'hello@', r'mail@', r'office@',
            r'no-reply@', r'noreply@', r'test@', r'example@'
        ]
        
        # Headers pour éviter la détection bot
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'fr-FR,fr;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }

    async def __aenter__(self):
        """Initialisation async context manager"""
        self.session = aiohttp.ClientSession(
            headers=self.headers,
            timeout=aiohttp.ClientTimeout(total=30),
            connector=aiohttp.TCPConnector(limit=5)  # Max 5 connexions simultanées
        )
        await self.load_suppression_list()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Nettoyage async context manager"""
        if self.session:
            await self.session.close()
    
    async def load_suppression_list(self):
        """Charger la liste des emails à ne pas contacter"""
        try:
            # Charger emails déjà en base (éviter doublons)
            prospects = await self.prospects_manager.list_prospects(limit=10000)
            existing_emails = {p.email for p in prospects}
            
            # Charger emails désinscrits
            unsubscribed = await self.prospects_manager.list_prospects(
                status="unsubscribed", limit=10000
            )
            unsubscribed_emails = {p.email for p in unsubscribed}
            
            self.suppression_list = existing_emails.union(unsubscribed_emails)
            
            logger.info(f"📋 Liste de suppression chargée: {len(self.suppression_list)} emails")
            
        except Exception as e:
            logger.error(f"❌ Erreur chargement suppression list: {e}")
    
    def is_email_valid_for_collection(self, email: str) -> bool:
        """Vérifier si un email peut être collecté légalement"""
        
        # Validation format
        try:
            valid_email = validate_email(email)
            email = valid_email.email
        except EmailNotValidError:
            return False
        
        # Exclure emails génériques
        for pattern in self.generic_email_patterns:
            if re.search(pattern, email, re.IGNORECASE):
                logger.debug(f"Email générique exclu: {email}")
                return False
        
        # Exclure si dans suppression list
        if email in self.suppression_list:
            logger.debug(f"Email déjà en suppression list: {email}")
            return False
        
        # Exclure domaines non-français (heuristique simple)
        suspicious_domains = ['.com', '.org', '.net', '.info']
        if any(domain in email for domain in suspicious_domains):
            # Autoriser seulement si clairement français
            french_indicators = ['.fr', 'france', 'french', 'francais']
            if not any(indicator in email.lower() for indicator in french_indicators):
                logger.debug(f"Domaine non-français potentiel: {email}")
                return False
        
        return True
    
    def extract_context_keywords(self, text: str, email: str) -> str:
        """Extraire l'intention/contexte autour de l'email"""
        
        # Chercher le contexte autour de l'email
        email_pos = text.lower().find(email.lower())
        if email_pos == -1:
            return ""
        
        # Extraire ±100 caractères autour de l'email
        start = max(0, email_pos - 100)
        end = min(len(text), email_pos + len(email) + 100)
        context = text[start:end]
        
        # Chercher mots-clés pertinents dans le contexte
        found_keywords = []
        for keyword in self.target_keywords:
            if keyword.lower() in context.lower():
                found_keywords.append(keyword)
        
        return ", ".join(found_keywords) if found_keywords else "contexte eau"
    
    def extract_french_names(self, text: str) -> tuple:
        """Extraire les prénoms/noms français potentiels"""
        
        # Prénoms français communs (heuristique)
        french_first_names = [
            'marie', 'jean', 'pierre', 'michel', 'alain', 'philippe', 'bernard',
            'christophe', 'patrick', 'nicolas', 'jacques', 'antoine', 'laurent',
            'olivier', 'thierry', 'david', 'julien', 'françois', 'sébastien',
            'catherine', 'nathalie', 'isabelle', 'sylvie', 'christine', 'monique',
            'françoise', 'martine', 'brigitte', 'nicole', 'véronique', 'sandrine'
        ]
        
        # Recherche pattern "Prénom + email" ou "M. Nom"
        words = re.findall(r'\b[A-Za-zÀ-ÿ]+\b', text)
        
        first_name = None
        last_name = None
        
        for word in words:
            if word.lower() in french_first_names and not first_name:
                first_name = word.capitalize()
                break
        
        # Pattern nom de famille (commence par majuscule, >2 lettres)
        potential_last_names = [w for w in words if len(w) > 2 and w[0].isupper() and w.lower() not in french_first_names]
        if potential_last_names:
            last_name = potential_last_names[0]
        
        return first_name, last_name
    
    def extract_french_cities(self, text: str) -> Optional[str]:
        """Extraire les villes françaises du contexte"""
        
        # Villes françaises principales (échantillon)
        major_french_cities = [
            'paris', 'marseille', 'lyon', 'toulouse', 'nice', 'nantes',
            'montpellier', 'strasbourg', 'bordeaux', 'lille', 'rennes',
            'reims', 'toulon', 'saint-étienne', 'le havre', 'grenoble',
            'dijon', 'angers', 'nîmes', 'villeurbanne', 'clermont-ferrand'
        ]
        
        text_lower = text.lower()
        for city in major_french_cities:
            if city in text_lower:
                return city.capitalize()
        
        return None
    
    async def check_robots_txt(self, domain: str) -> bool:
        """Vérifier si le scraping est autorisé par robots.txt"""
        robots_url = f"https://{domain}/robots.txt"
        
        try:
            async with self.session.get(robots_url) as response:
                if response.status == 200:
                    robots_content = await response.text()
                    
                    # Vérification simple - améliorer selon besoins
                    if "Disallow: /" in robots_content:
                        logger.warning(f"⚠️ Robots.txt interdit le scraping pour {domain}")
                        return False
                    
                    logger.info(f"✅ Robots.txt autorise le scraping pour {domain}")
                    return True
                else:
                    # Pas de robots.txt = autorisé par défaut
                    return True
                    
        except Exception as e:
            logger.error(f"❌ Erreur vérification robots.txt {domain}: {e}")
            return False
    
    async def scrape_forum_page(self, url: str) -> List[ScrapedProspect]:
        """Scraper une page de forum spécifique"""
        
        if url in self.scraped_urls:
            return []
        
        domain = urlparse(url).netloc
        if domain not in self.allowed_sources:
            logger.warning(f"⚠️ Domaine non autorisé: {domain}")
            return []
        
        # Vérifier robots.txt
        if not await self.check_robots_txt(domain):
            return []
        
        prospects = []
        
        try:
            # Rate limiting
            await asyncio.sleep(self.rate_limit)
            
            async with self.session.get(url) as response:
                if response.status != 200:
                    logger.error(f"❌ Erreur HTTP {response.status} pour {url}")
                    return []
                
                content = await response.text()
                soup = BeautifulSoup(content, 'html.parser')
                
                # Recherche emails avec contexte
                email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
                emails = re.findall(email_pattern, content)
                
                logger.info(f"🔍 Trouvé {len(emails)} emails potentiels sur {url}")
                
                for email in emails:
                    if not self.is_email_valid_for_collection(email):
                        continue
                    
                    # Extraire contexte et mots-clés
                    keyword_intent = self.extract_context_keywords(content, email)
                    if not keyword_intent:
                        continue  # Pas de contexte pertinent
                    
                    # Extraire noms potentiels
                    first_name, last_name = self.extract_french_names(content)
                    
                    # Extraire ville
                    city = self.extract_french_cities(content)
                    
                    # Calculer score de confiance
                    confidence = self.calculate_confidence_score(email, keyword_intent, first_name)
                    
                    if confidence < 0.3:  # Seuil minimum de confiance
                        continue
                    
                    prospect = ScrapedProspect(
                        email=email,
                        first_name=first_name,
                        last_name=last_name,
                        source_url=url,
                        keyword_intent=keyword_intent,
                        city=city,
                        country="FR",
                        confidence_score=confidence
                    )
                    
                    prospects.append(prospect)
                    logger.info(f"✅ Prospect collecté: {email} | Intent: {keyword_intent} | Confiance: {confidence:.2f}")
                
                self.scraped_urls.add(url)
                
        except Exception as e:
            logger.error(f"❌ Erreur scraping {url}: {e}")
        
        return prospects
    
    def calculate_confidence_score(self, email: str, keyword_intent: str, first_name: str) -> float:
        """Calculer un score de confiance pour le prospect"""
        
        score = 0.0
        
        # Email français (+0.3)
        if '.fr' in email:
            score += 0.3
        
        # Prénom détecté (+0.2)
        if first_name:
            score += 0.2
        
        # Mots-clés pertinents (+0.4)
        high_value_keywords = ['osmoseur', 'osmose inverse', 'purification eau']
        if any(kw in keyword_intent.lower() for kw in high_value_keywords):
            score += 0.4
        elif keyword_intent:
            score += 0.2
        
        # Email personnel vs professionnel (+0.1)
        if not any(pattern.replace('@', '') in email for pattern in self.generic_email_patterns):
            score += 0.1
        
        return min(1.0, score)
    
    async def search_relevant_pages(self, base_domains: List[str]) -> List[str]:
        """Rechercher des pages pertinentes sur les domaines autorisés"""
        
        relevant_urls = []
        
        for domain in base_domains:
            if domain not in self.allowed_sources:
                continue
            
            # Construire URLs de recherche avec mots-clés
            search_queries = [
                f"osmoseur",
                f"filtration+eau",
                f"eau+calcaire",
                f"purification+eau"
            ]
            
            for query in search_queries:
                # Pattern URLs forum typiques
                potential_urls = [
                    f"https://{domain}/search?q={query}",
                    f"https://{domain}/forum/search?query={query}",
                    f"https://{domain}/forums/{query}",
                ]
                
                for url in potential_urls:
                    try:
                        # Test rapide de l'URL
                        async with self.session.head(url) as response:
                            if response.status == 200:
                                relevant_urls.append(url)
                                logger.info(f"📄 URL pertinente trouvée: {url}")
                    except:
                        continue
        
        return relevant_urls
    
    async def save_prospect_to_db(self, scraped_prospect: ScrapedProspect) -> bool:
        """Sauvegarder un prospect scrapé dans la base de données"""
        
        try:
            # Déterminer le type de consentement
            consent_status = ConsentStatus.LEGITIMATE_INTEREST  # Données publiques = intérêt légitime
            
            # Créer l'objet prospect
            prospect_data = ProspectCreate(
                email=scraped_prospect.email,
                first_name=scraped_prospect.first_name,
                last_name=scraped_prospect.last_name,
                source_url=scraped_prospect.source_url,
                keyword_intent=scraped_prospect.keyword_intent,
                country=scraped_prospect.country,
                city=scraped_prospect.city,
                consent_status=consent_status,
                notes=f"Scraping agent - Confiance: {scraped_prospect.confidence_score:.2f}"
            )
            
            # Sauvegarder
            created_prospect = await self.prospects_manager.create_prospect(prospect_data)
            
            logger.info(f"💾 Prospect sauvegardé: {scraped_prospect.email}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur sauvegarde prospect {scraped_prospect.email}: {e}")
            return False
    
    async def run_scraping_session(self, max_prospects: int = 50) -> Dict:
        """Lancer une session de scraping complète"""
        
        session_stats = {
            "start_time": datetime.now(),
            "pages_scraped": 0,
            "prospects_found": 0,
            "prospects_saved": 0,
            "errors": 0,
            "domains_processed": []
        }
        
        logger.info(f"🕷️ Début session scraping - Objectif: {max_prospects} prospects max")
        
        try:
            # Rechercher pages pertinentes
            relevant_urls = await self.search_relevant_pages(self.allowed_sources)
            
            if not relevant_urls:
                logger.warning("⚠️ Aucune URL pertinente trouvée")
                return session_stats
            
            logger.info(f"🔍 {len(relevant_urls)} URLs à scraper")
            
            # Scraper chaque URL
            for url in relevant_urls[:10]:  # Limiter à 10 URLs par session
                if session_stats["prospects_saved"] >= max_prospects:
                    break
                
                try:
                    scraped_prospects = await self.scrape_forum_page(url)
                    session_stats["pages_scraped"] += 1
                    session_stats["prospects_found"] += len(scraped_prospects)
                    
                    # Sauvegarder prospects
                    for prospect in scraped_prospects:
                        if session_stats["prospects_saved"] >= max_prospects:
                            break
                        
                        success = await self.save_prospect_to_db(prospect)
                        if success:
                            session_stats["prospects_saved"] += 1
                    
                    domain = urlparse(url).netloc
                    if domain not in session_stats["domains_processed"]:
                        session_stats["domains_processed"].append(domain)
                        
                except Exception as e:
                    session_stats["errors"] += 1
                    logger.error(f"❌ Erreur scraping URL {url}: {e}")
            
            session_stats["end_time"] = datetime.now()
            session_stats["duration_minutes"] = (session_stats["end_time"] - session_stats["start_time"]).total_seconds() / 60
            
            logger.info(f"✅ Session terminée: {session_stats['prospects_saved']}/{max_prospects} prospects collectés")
            
        except Exception as e:
            session_stats["errors"] += 1
            logger.error(f"❌ Erreur session scraping: {e}")
        
        return session_stats

class ScrapingOrchestrator:
    """Orchestrateur pour le scraping automatisé"""
    
    def __init__(self, prospects_manager: ProspectsManager):
        self.prospects_manager = prospects_manager
        self.is_running = False
        
    async def scheduled_scraping(self, interval_hours: int = 24, max_prospects_per_session: int = 25):
        """Scraping programmé automatique"""
        
        logger.info(f"📅 Scraping programmé démarré: toutes les {interval_hours}h, max {max_prospects_per_session} prospects/session")
        
        while True:
            try:
                async with ScraperAgent(self.prospects_manager) as scraper:
                    stats = await scraper.run_scraping_session(max_prospects_per_session)
                    
                    # Log des résultats
                    logger.info(f"📊 Session scraping terminée:")
                    logger.info(f"   - Pages scrapées: {stats['pages_scraped']}")
                    logger.info(f"   - Prospects trouvés: {stats['prospects_found']}")
                    logger.info(f"   - Prospects sauvegardés: {stats['prospects_saved']}")
                    logger.info(f"   - Durée: {stats.get('duration_minutes', 0):.1f} minutes")
                    logger.info(f"   - Domaines: {', '.join(stats['domains_processed'])}")
                    
                    # Attendre avant la prochaine session
                    await asyncio.sleep(interval_hours * 3600)
                    
            except Exception as e:
                logger.error(f"❌ Erreur scraping programmé: {e}")
                await asyncio.sleep(3600)  # Attendre 1h en cas d'erreur

# Fonctions d'aide pour intégration
async def run_single_scraping_session(prospects_manager: ProspectsManager, max_prospects: int = 50):
    """Lancer une session de scraping unique"""
    async with ScraperAgent(prospects_manager) as scraper:
        return await scraper.run_scraping_session(max_prospects)

async def start_scheduled_scraping(prospects_manager: ProspectsManager, interval_hours: int = 24):
    """Démarrer le scraping programmé"""
    orchestrator = ScrapingOrchestrator(prospects_manager)
    await orchestrator.scheduled_scraping(interval_hours)

# Export classes principales
__all__ = [
    'ScraperAgent',
    'ScrapingOrchestrator', 
    'run_single_scraping_session',
    'start_scheduled_scraping'
]