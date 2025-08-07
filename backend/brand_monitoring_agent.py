"""
Agent de Surveillance Marque 24/7 - JOSMOSE.COM
Surveille en permanence que :
1. Aucune mention "emergent" ou "made with emergent" n'apparaît
2. Le site reste toujours www.josmose.com
3. Aucune référence indésirable dans le code ou l'interface

FONCTIONNEMENT 24/7 : Cet agent se lance automatiquement au démarrage du serveur
et continue de surveiller indéfiniment chaque minute.
"""

import os
import time
import asyncio
import logging
import re
from datetime import datetime
from typing import List, Dict, Set
import requests
from pathlib import Path
import json
from motor.motor_asyncio import AsyncIOMotorClient

# Configuration de l'agent
MONITORING_CONFIG = {
    "check_interval": 60,  # Vérification toutes les 60 secondes (1 minute)
    "frontend_url": os.environ.get("REACT_APP_BACKEND_URL", "https://67c818fa-35d3-46a9-b7df-5b06cb23e4f4.preview.emergentagent.com").replace("/api", ""),
    "crm_url": os.environ.get("REACT_APP_BACKEND_URL", "https://67c818fa-35d3-46a9-b7df-5b06cb23e4f4.preview.emergentagent.com").replace("/api", "") + "/crm",
    "scan_directories": ["/app/frontend/src", "/app/backend", "/app"],
    "excluded_files": [".git", "node_modules", "__pycache__", ".emergent", "brand_monitoring_agent.py"],
    "alert_threshold": 1  # Alerter immédiatement après la première détection
}

# Mots interdits à surveiller (case-insensitive)
FORBIDDEN_TERMS = [
    "emergent",
    "made with emergent",
    "emergentagent",
    "emergent.com",
    "preview.emergentagent.com"
]

# Termes autorisés (pour éviter les faux positifs)
ALLOWED_TERMS = [
    "emergency",  # Mot différent, autorisé
    "emerging",   # Mot différent, autorisé
    "merged",     # Mot différent, autorisé
]

class BrandMonitoringAgent:
    def __init__(self):
        self.mongo_client = AsyncIOMotorClient(os.getenv("MONGO_URL", "mongodb://localhost:27017"))
        self.db = self.mongo_client[os.getenv("DB_NAME", "test_database")]
        self.setup_logging()
        self.running = False
        self.violation_count = 0
        self.last_scan_results = {}

    def setup_logging(self):
        """Configuration du système de logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - BrandMonitor - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('/var/log/brand_monitoring.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def is_forbidden_term(self, text: str) -> List[Dict]:
        """
        Vérifie si le texte contient des termes interdits
        Retourne la liste des violations trouvées
        """
        violations = []
        text_lower = text.lower()
        
        for term in FORBIDDEN_TERMS:
            if term.lower() in text_lower:
                # Vérifier que ce n'est pas un terme autorisé
                is_allowed = False
                for allowed in ALLOWED_TERMS:
                    if allowed.lower() in text_lower:
                        is_allowed = True
                        break
                
                if not is_allowed:
                    # Trouver les positions exactes
                    pattern = re.compile(re.escape(term), re.IGNORECASE)
                    matches = pattern.finditer(text)
                    
                    for match in matches:
                        violations.append({
                            "term": term,
                            "found_text": match.group(),
                            "position": match.start(),
                            "context": text[max(0, match.start()-50):match.end()+50]
                        })
        
        return violations

    async def scan_file_content(self, file_path: str) -> List[Dict]:
        """
        Scanne le contenu d'un fichier pour détecter les violations
        """
        violations = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            file_violations = self.is_forbidden_term(content)
            
            for violation in file_violations:
                violations.append({
                    **violation,
                    "file": file_path,
                    "type": "file_content"
                })
                
        except Exception as e:
            self.logger.error(f"Erreur lecture fichier {file_path}: {str(e)}")
        
        return violations

    async def scan_directory(self, directory: str) -> List[Dict]:
        """
        Scanne récursivement un répertoire pour détecter les violations
        """
        violations = []
        
        try:
            for root, dirs, files in os.walk(directory):
                # Exclure certains répertoires
                dirs[:] = [d for d in dirs if not any(excluded in d for excluded in MONITORING_CONFIG["excluded_files"])]
                
                for file in files:
                    # Exclure certains types de fichiers
                    if any(excluded in file for excluded in MONITORING_CONFIG["excluded_files"]):
                        continue
                    
                    # Vérifier seulement les fichiers texte/code
                    if file.endswith(('.py', '.js', '.jsx', '.ts', '.tsx', '.html', '.css', '.json', '.md', '.txt', '.env')):
                        file_path = os.path.join(root, file)
                        file_violations = await self.scan_file_content(file_path)
                        violations.extend(file_violations)
                        
        except Exception as e:
            self.logger.error(f"Erreur scan répertoire {directory}: {str(e)}")
        
        return violations

    async def scan_web_content(self, url: str) -> List[Dict]:
        """
        Scanne le contenu web visible pour détecter les violations
        """
        violations = []
        
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                content = response.text
                
                web_violations = self.is_forbidden_term(content)
                
                for violation in web_violations:
                    violations.append({
                        **violation,
                        "url": url,
                        "type": "web_content"
                    })
            else:
                self.logger.warning(f"Impossible d'accéder à {url}: {response.status_code}")
                
        except Exception as e:
            self.logger.error(f"Erreur scan web {url}: {str(e)}")
        
        return violations

    async def check_domain_consistency(self) -> List[Dict]:
        """
        Vérifie que les références au domaine sont cohérentes (josmose.com)
        """
        violations = []
        
        # Vérifier les fichiers de configuration
        config_files = [
            "/app/frontend/.env",
            "/app/backend/.env",
            "/app/frontend/package.json"
        ]
        
        correct_domain = "josmose.com"
        incorrect_domains = [
            "osmose.com",
            "emergentagent.com",
            "preview.emergentagent.com"
        ]
        
        for config_file in config_files:
            try:
                if os.path.exists(config_file):
                    with open(config_file, 'r') as f:
                        content = f.read()
                    
                    for incorrect_domain in incorrect_domains:
                        if incorrect_domain in content and "preview.emergentagent.com" not in config_file:
                            violations.append({
                                "term": incorrect_domain,
                                "found_text": incorrect_domain,
                                "file": config_file,
                                "type": "domain_inconsistency",
                                "context": f"Domaine incorrect trouvé : {incorrect_domain}"
                            })
            except Exception as e:
                self.logger.error(f"Erreur vérification domaine {config_file}: {str(e)}")
        
        return violations

    async def perform_full_scan(self) -> Dict:
        """
        Effectue un scan complet de tous les éléments surveillés
        """
        scan_start = datetime.utcnow()
        all_violations = []
        
        self.logger.info("🔍 Début du scan complet de surveillance marque...")
        
        # 1. Scanner les répertoires de code
        for directory in MONITORING_CONFIG["scan_directories"]:
            if os.path.exists(directory):
                self.logger.info(f"📂 Scan du répertoire: {directory}")
                dir_violations = await self.scan_directory(directory)
                all_violations.extend(dir_violations)
        
        # 2. Scanner le contenu web visible
        web_urls = [
            MONITORING_CONFIG["frontend_url"],
            MONITORING_CONFIG["crm_url"]
        ]
        
        for url in web_urls:
            self.logger.info(f"🌐 Scan de l'URL: {url}")
            web_violations = await self.scan_web_content(url)
            all_violations.extend(web_violations)
        
        # 3. Vérifier la cohérence des domaines
        self.logger.info("🏷️ Vérification cohérence domaines...")
        domain_violations = await self.check_domain_consistency()
        all_violations.extend(domain_violations)
        
        # Compilation des résultats
        scan_results = {
            "scan_time": scan_start,
            "duration_seconds": (datetime.utcnow() - scan_start).total_seconds(),
            "violations_found": len(all_violations),
            "violations": all_violations,
            "status": "CLEAN" if len(all_violations) == 0 else "VIOLATIONS_DETECTED"
        }
        
        # Log des résultats
        if len(all_violations) == 0:
            self.logger.info("✅ SCAN TERMINÉ - AUCUNE VIOLATION DÉTECTÉE")
            self.violation_count = 0
        else:
            self.logger.warning(f"⚠️ SCAN TERMINÉ - {len(all_violations)} VIOLATIONS DÉTECTÉES:")
            for violation in all_violations:
                self.logger.warning(f"  - {violation['term']} trouvé dans {violation.get('file', violation.get('url', 'unknown'))}")
            self.violation_count += 1
        
        # Sauvegarder les résultats
        await self.save_scan_results(scan_results)
        self.last_scan_results = scan_results
        
        return scan_results

    async def save_scan_results(self, results: Dict):
        """
        Sauvegarde les résultats du scan dans la base de données
        """
        try:
            # Convertir les résultats pour MongoDB
            mongo_results = {
                **results,
                "_id": f"scan_{results['scan_time'].strftime('%Y%m%d_%H%M%S')}",
                "scan_time": results['scan_time']
            }
            
            await self.db.brand_monitoring.insert_one(mongo_results)
            
            # Garder seulement les 100 derniers scans
            old_scans = self.db.brand_monitoring.find().sort("scan_time", -1).skip(100)
            async for old_scan in old_scans:
                await self.db.brand_monitoring.delete_one({"_id": old_scan["_id"]})
                
        except Exception as e:
            self.logger.error(f"Erreur sauvegarde résultats: {str(e)}")

    async def send_alert(self, violations: List[Dict]):
        """
        Envoie une alerte en cas de détection de violations
        """
        try:
            if self.violation_count >= MONITORING_CONFIG["alert_threshold"]:
                alert_message = f"""
🚨 ALERTE SURVEILLANCE MARQUE - {datetime.utcnow().strftime('%d/%m/%Y %H:%M:%S')}

{len(violations)} violations détectées sur www.josmose.com :

"""
                for violation in violations[:5]:  # Montrer les 5 premières
                    alert_message += f"• '{violation['term']}' dans {violation.get('file', violation.get('url', 'unknown'))}\n"
                
                if len(violations) > 5:
                    alert_message += f"... et {len(violations) - 5} autres violations\n"
                
                alert_message += "\n🔧 Action requise : Nettoyage immédiat nécessaire !"
                
                # Log l'alerte (dans un vrai système, on enverrait un email/SMS)
                self.logger.critical(alert_message)
                
                # Sauvegarder l'alerte
                await self.db.brand_monitoring_alerts.insert_one({
                    "timestamp": datetime.utcnow(),
                    "violation_count": len(violations),
                    "consecutive_violations": self.violation_count,
                    "message": alert_message,
                    "violations": violations
                })
                
        except Exception as e:
            self.logger.error(f"Erreur envoi alerte: {str(e)}")

    async def run_monitoring_loop(self):
        """
        Boucle principale de surveillance continue
        """
        self.logger.info("🚀 DÉMARRAGE AGENT SURVEILLANCE MARQUE JOSMOSE.COM")
        self.logger.info(f"📅 Intervalle de vérification: {MONITORING_CONFIG['check_interval']} secondes")
        self.logger.info(f"🎯 Termes surveillés: {', '.join(FORBIDDEN_TERMS)}")
        
        self.running = True
        
        while self.running:
            try:
                # Effectuer un scan complet
                results = await self.perform_full_scan()
                
                # Envoyer une alerte si nécessaire
                if results["violations"]:
                    await self.send_alert(results["violations"])
                
                # Attendre avant le prochain scan
                self.logger.info(f"⏳ Prochaine vérification dans {MONITORING_CONFIG['check_interval']} secondes...")
                await asyncio.sleep(MONITORING_CONFIG["check_interval"])
                
            except Exception as e:
                self.logger.error(f"Erreur dans la boucle de surveillance: {str(e)}")
                await asyncio.sleep(30)  # Attendre 30s en cas d'erreur

    def stop_monitoring(self):
        """
        Arrête l'agent de surveillance
        """
        self.logger.info("🛑 ARRÊT AGENT SURVEILLANCE MARQUE")
        self.running = False

    async def get_monitoring_stats(self) -> Dict:
        """
        Retourne les statistiques de surveillance
        """
        try:
            # Statistiques des derniers scans
            recent_scans = await self.db.brand_monitoring.find().sort("scan_time", -1).limit(10).to_list(10)
            
            total_scans = await self.db.brand_monitoring.count_documents({})
            clean_scans = await self.db.brand_monitoring.count_documents({"violations_found": 0})
            
            # Statistiques des alertes
            total_alerts = await self.db.brand_monitoring_alerts.count_documents({})
            
            return {
                "status": "RUNNING" if self.running else "STOPPED",
                "last_scan": self.last_scan_results,
                "total_scans": total_scans,
                "clean_scans": clean_scans,
                "violation_scans": total_scans - clean_scans,
                "total_alerts": total_alerts,
                "recent_scans": recent_scans,
                "current_violation_streak": self.violation_count
            }
            
        except Exception as e:
            self.logger.error(f"Erreur récupération stats: {str(e)}")
            return {"error": str(e)}

# Instance globale de l'agent
brand_monitor = BrandMonitoringAgent()

# Fonctions utilitaires pour l'intégration
async def start_brand_monitoring():
    """Démarre l'agent de surveillance"""
    return await brand_monitor.run_monitoring_loop()

async def stop_brand_monitoring():
    """Arrête l'agent de surveillance"""
    brand_monitor.stop_monitoring()

async def get_brand_monitoring_status():
    """Récupère le statut de surveillance"""
    return await brand_monitor.get_monitoring_stats()

async def force_brand_scan():
    """Force un scan immédiat"""
    return await brand_monitor.perform_full_scan()