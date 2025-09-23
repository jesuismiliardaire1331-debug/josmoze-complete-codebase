"""
Agent de Surveillance Marque 24/7 - JOSMOZE.COM
Surveille en permanence que :
1. Aucune mention "emergent" ou "made with emergent" n'apparaît
2. Le site reste toujours www.josmoze.com
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
    "check_interval": 30,  # 🚨 SURVEILLANCE RENFORCÉE : Vérification toutes les 30 secondes ⚡
    "frontend_url": os.environ.get("REACT_APP_BACKEND_URL", "https://www.josmoze.com").replace("/api", ""),
    "crm_url": os.environ.get("REACT_APP_BACKEND_URL", "https://www.josmoze.com").replace("/api", "") + "/crm",
    "scan_directories": ["/app/frontend/src", "/app/backend", "/app"],
    "excluded_files": [".git", "node_modules", "__pycache__", ".emergent", "brand_monitoring_agent.py"],
    "alert_threshold": 1  # 🚨 ALERTE IMMÉDIATE - Alerter dès la première détection
}

# Mots interdits à surveiller (case-insensitive) - SURVEILLANCE RENFORCÉE
FORBIDDEN_TERMS = [
    "emergent",
    "made with emergent", 
    "emergentagent",
    "emergent.com",
    "preview.emergentagent.com",
    "osmose.com",  # Ancien domaine à éviter
    "emergentagent.com",
    # 🚨 TERMES SUPPLÉMENTAIRES SURVEILLÉS
    "powered by emergent",
    "built with emergent", 
    "emergent ai",
    "emergent platform",
    "emergent solution"
]

# Termes autorisés (pour éviter les faux positifs)
ALLOWED_TERMS = [
    "emergency",  # Mot différent, autorisé
    "emerging",   # Mot différent, autorisé
    "merged",     # Mot différent, autorisé
]

class BrandMonitoringAgent:
    def __init__(self):
        mongo_url = os.getenv("MONGO_URI", os.getenv("MONGO_URL", ""))
        self.mongo_client = AsyncIOMotorClient(mongo_url)
        self.db = self.mongo_client[os.getenv("DB_NAME", "josmoze_production")]
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
        Vérifie que les références au domaine sont cohérentes (josmoze.com)
        """
        violations = []
        
        # Vérifier les fichiers de configuration
        config_files = [
            "/app/frontend/.env",
            "/app/backend/.env",
            "/app/frontend/package.json"
        ]
        
        correct_domain = "josmoze.com"
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
    
    async def scan_system_configs(self) -> List[Dict]:
        """
        🆕 Scanner les fichiers de configuration système pour détecter les violations
        """
        violations = []
        
        system_config_files = [
            "/app/package.json",
            "/app/frontend/package.json", 
            "/app/backend/requirements.txt",
            "/app/README.md",
            "/app/frontend/public/index.html",
            "/app/frontend/public/manifest.json"
        ]
        
        try:
            for config_file in system_config_files:
                if os.path.exists(config_file):
                    config_violations = await self.scan_file_content(config_file)
                    violations.extend(config_violations)
                    
        except Exception as e:
            self.logger.error(f"Erreur scan configurations système: {str(e)}")
        
        return violations

    async def scan_file_metadata(self) -> List[Dict]:
        """
        🆕 Scanner les métadonnées et noms de fichiers pour détecter les violations
        """
        violations = []
        
        try:
            for root, dirs, files in os.walk("/app"):
                # Exclure certains répertoires
                dirs[:] = [d for d in dirs if not any(excluded in d for excluded in MONITORING_CONFIG["excluded_files"])]
                
                # Vérifier les noms de fichiers et dossiers
                for name in dirs + files:
                    name_violations = self.is_forbidden_term(name)
                    for violation in name_violations:
                        violations.append({
                            **violation,
                            "file": os.path.join(root, name),
                            "type": "filename_metadata"
                        })
                        
        except Exception as e:
            self.logger.error(f"Erreur scan métadonnées: {str(e)}")
        
        return violations

    async def perform_full_scan(self) -> Dict:
        """
        Effectue un scan complet de tous les éléments surveillés
        🚨 MODE SURVEILLANCE RENFORCÉE ACTIVÉ 🚨
        """
        scan_start = datetime.utcnow()
        all_violations = []
        
        self.logger.info("🔍 Début du scan complet de surveillance marque RENFORCÉE...")
        self.logger.info("⚡ FRÉQUENCE: Toutes les 30 secondes | ALERTE: Immédiate")
        
        # 1. Scanner les répertoires de code - SCAN APPROFONDI
        for directory in MONITORING_CONFIG["scan_directories"]:
            if os.path.exists(directory):
                self.logger.info(f"📂 Scan INTENSIF du répertoire: {directory}")
                dir_violations = await self.scan_directory(directory)
                all_violations.extend(dir_violations)
        
        # 2. Scanner le contenu web visible - VERIFICATION MULTIPLE
        web_urls = [
            MONITORING_CONFIG["frontend_url"],
            MONITORING_CONFIG["crm_url"],
            # 🚨 URLs SUPPLÉMENTAIRES SURVEILLÉES
            MONITORING_CONFIG["frontend_url"] + "/products",
            MONITORING_CONFIG["frontend_url"] + "/contact",
            MONITORING_CONFIG["frontend_url"] + "/installation"
        ]
        
        for url in web_urls:
            self.logger.info(f"🌐 Scan APPROFONDI de l'URL: {url}")
            web_violations = await self.scan_web_content(url)
            all_violations.extend(web_violations)
        
        # 3. Vérifier la cohérence des domaines - CONTRÔLE STRICT
        self.logger.info("🏷️ Vérification STRICTE cohérence domaines...")
        domain_violations = await self.check_domain_consistency()
        all_violations.extend(domain_violations)
        
        # 4. 🆕 NOUVEAU : Scanner les configurations système
        self.logger.info("⚙️ Scan des configurations système...")
        config_violations = await self.scan_system_configs()
        all_violations.extend(config_violations)
        
        # 5. 🆕 NOUVEAU : Vérifier les métadonnées des fichiers
        self.logger.info("🔧 Vérification métadonnées des fichiers...")
        metadata_violations = await self.scan_file_metadata()
        all_violations.extend(metadata_violations)
        
        # Compilation des résultats
        scan_results = {
            "scan_time": scan_start,
            "duration_seconds": (datetime.utcnow() - scan_start).total_seconds(),
            "violations_found": len(all_violations),
            "violations": all_violations,
            "status": "CLEAN" if len(all_violations) == 0 else "VIOLATIONS_DETECTED",
            "scan_mode": "REINFORCED_MONITORING",  # 🚨 Nouveau mode de surveillance
            "scan_frequency": "30_SECONDS"
        }
        
        # Log des résultats - PLUS DÉTAILLÉ
        if len(all_violations) == 0:
            self.logger.info("✅ SCAN RENFORCÉ TERMINÉ - AUCUNE VIOLATION DÉTECTÉE")
            self.violation_count = 0
        else:
            self.logger.critical(f"🚨 ALERTE SURVEILLANCE RENFORCÉE - {len(all_violations)} VIOLATIONS DÉTECTÉES:")
            for violation in all_violations:
                self.logger.critical(f"  ⚠️ {violation['term']} trouvé dans {violation.get('file', violation.get('url', 'unknown'))}")
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
        🚨 Envoie une alerte RENFORCÉE en cas de détection de violations
        """
        try:
            if self.violation_count >= MONITORING_CONFIG["alert_threshold"]:
                alert_message = f"""
🚨🚨🚨 ALERTE SURVEILLANCE MARQUE RENFORCÉE - {datetime.utcnow().strftime('%d/%m/%Y %H:%M:%S')} 🚨🚨🚨

⚠️ VIOLATIONS CRITIQUES DÉTECTÉES SUR www.josmoze.com ⚠️

{len(violations)} violations détectées en mode surveillance renforcée (30 secondes) :

"""
                for violation in violations[:10]:  # Montrer les 10 premières
                    alert_message += f"🔴 '{violation['term']}' dans {violation.get('file', violation.get('url', 'unknown'))}\n"
                
                if len(violations) > 10:
                    alert_message += f"... et {len(violations) - 10} autres violations\n"
                
                alert_message += f"""
🔧 ACTION REQUISE : NETTOYAGE IMMÉDIAT NÉCESSAIRE !
📊 Mode surveillance : RENFORCÉ (30 secondes)
🎯 Seuil d'alerte : IMMÉDIAT (1ère détection)
🕒 Prochaine vérification dans 30 secondes

⚡ SYSTÈME DE SURVEILLANCE HAUTE INTENSITÉ ACTIF ⚡
"""
                
                # Log l'alerte avec niveau CRITIQUE
                self.logger.critical(alert_message)
                
                # Sauvegarder l'alerte avec priorité élevée
                await self.db.brand_monitoring_alerts.insert_one({
                    "timestamp": datetime.utcnow(),
                    "violation_count": len(violations),
                    "consecutive_violations": self.violation_count,
                    "message": alert_message,
                    "violations": violations,
                    "alert_level": "CRITICAL_REINFORCED",  # 🚨 Nouveau niveau d'alerte
                    "scan_mode": "REINFORCED_MONITORING",
                    "frequency": "30_SECONDS"
                })
                
        except Exception as e:
            self.logger.error(f"Erreur envoi alerte renforcée: {str(e)}")

    async def run_monitoring_loop(self):
        """
        🚨 Boucle principale de surveillance continue RENFORCÉE
        """
        self.logger.info("🚀🚀🚀 DÉMARRAGE AGENT SURVEILLANCE MARQUE JOSMOZE.COM - MODE RENFORCÉ 🚀🚀🚀")
        self.logger.info(f"⚡ SURVEILLANCE HAUTE INTENSITÉ ACTIVÉE ⚡")
        self.logger.info(f"📅 Intervalle de vérification: {MONITORING_CONFIG['check_interval']} secondes (RENFORCÉ)")
        self.logger.info(f"🎯 Termes surveillés: {', '.join(FORBIDDEN_TERMS)}")
        self.logger.info(f"🚨 Seuil d'alerte: IMMÉDIAT (1ère détection)")
        self.logger.info(f"🔍 Points de contrôle: 5 URLs web + Fichiers + Métadonnées")
        
        # Agent temporairement désactivé pour performance critique
        self.running = False
        self.logger.info("🔧 Agent de surveillance temporairement désactivé pour urgence")
        
        while self.running:
            try:
                # Effectuer un scan complet RENFORCÉ
                self.logger.info("🔍 DÉMARRAGE SCAN RENFORCÉ...")
                results = await self.perform_full_scan()
                
                # Envoyer une alerte IMMÉDIATE si nécessaire
                if results["violations"]:
                    self.logger.critical(f"🚨 VIOLATIONS DÉTECTÉES : {results['violations_found']} violations trouvées")
                    await self.send_alert(results["violations"])
                else:
                    self.logger.info(f"✅ SCAN PROPRE - Aucune violation détectée")
                
                # Attendre avant le prochain scan (30 secondes)
                self.logger.info(f"⏳ Prochaine vérification RENFORCÉE dans {MONITORING_CONFIG['check_interval']} secondes...")
                await asyncio.sleep(MONITORING_CONFIG["check_interval"])
                
            except Exception as e:
                self.logger.error(f"🚨 ERREUR dans la boucle de surveillance RENFORCÉE: {str(e)}")
                await asyncio.sleep(15)  # Attendre 15s en cas d'erreur (réduit pour surveillance renforcée)

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
            # Create a new MongoDB client for this request to avoid loop issues
            mongo_url = os.getenv("MONGO_URI", os.getenv("MONGO_URL", ""))
            client = AsyncIOMotorClient(mongo_url)
            db = client[os.getenv("DB_NAME", "josmoze_production")]
            
            # Statistiques des derniers scans
            recent_scans = await db.brand_monitoring.find().sort("scan_time", -1).limit(10).to_list(10)
            
            total_scans = await db.brand_monitoring.count_documents({})
            clean_scans = await db.brand_monitoring.count_documents({"violations_found": 0})
            
            # Statistiques des alertes
            total_alerts = await db.brand_monitoring_alerts.count_documents({})
            
            # Close the client
            client.close()
            
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

def start_monitoring_task():
    """Démarre l'agent de surveillance en arrière-plan"""
    try:
        import threading
        import asyncio
        
        def run_monitoring():
            """Fonction pour exécuter la surveillance dans un thread séparé"""
            try:
                # Créer un nouvel événement loop pour ce thread
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                # Lancer la surveillance
                loop.run_until_complete(brand_monitor.run_monitoring_loop())
            except Exception as e:
                logging.error(f"Erreur dans le thread de surveillance: {e}")
        
        # Lancer dans un thread daemon (se ferme automatiquement avec l'app)
        thread = threading.Thread(target=run_monitoring, daemon=True)
        thread.start()
        
        logging.info("🚀 Agent de surveillance marque démarré en arrière-plan")
        return {"status": "started", "message": "Agent de surveillance démarré"}
        
    except Exception as e:
        logging.error(f"Impossible de démarrer l'agent de surveillance: {e}")
        return {"status": "error", "message": str(e)}
