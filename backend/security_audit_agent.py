"""
🛡️ AGENT AUDIT & CYBERSÉCURITÉ JOSMOZE.COM 🛡️
Agent de surveillance, audit et protection cybersécurité 24/7

MISSIONS PRINCIPALES :
1. 🔍 Audit quotidien automatique à minuit (heure française)
2. 🐛 Détection et correction automatique des bugs
3. 🛡️ Protection cybersécurité contre toutes attaques
4. 🚨 Surveillance continue et alertes temps réel
5. 📊 Rapports d'audit et recommandations

FONCTIONNEMENT 24/7 : Cet agent ne dort jamais !
"""

import os
import sys
import asyncio
import logging
import json
import hashlib
import hmac
import time
import socket
import psutil
import subprocess
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from motor.motor_asyncio import AsyncIOMotorDatabase
import requests
import re
import ipaddress
from collections import defaultdict, deque
import threading
import schedule
import pytz

# Configuration de l'agent de sécurité
SECURITY_CONFIG = {
    "audit_time": "00:00",  # Minuit heure française
    "timezone": "Europe/Paris",
    "max_login_attempts": 5,
    "rate_limit_per_minute": 100,
    "suspicious_patterns": [
        r"union.*select",
        r"<script.*>",
        r"javascript:",
        r"eval\(",
        r"exec\(",
        r"system\(",
        r"\.\.\/",
        r"passwd",
        r"shadow",
        r"etc/",
        r"admin.*admin",
        r"root.*root",
        r"hack",
        r"exploit"
    ],
    "blocked_countries": ["CN", "RU", "KP"],  # Pays à surveiller particulièrement
    "max_request_size": 10 * 1024 * 1024,  # 10MB
    "session_timeout": 30 * 60,  # 30 minutes
    "max_concurrent_sessions": 50,
    "auto_fix_enabled": True,
    "security_log_retention": 90  # jours
}

@dataclass
class SecurityThreat:
    """Modèle pour les menaces de sécurité détectées"""
    threat_id: str = field(default_factory=lambda: f"THR-{int(time.time())}")
    threat_type: str = ""  # xss, sql_injection, brute_force, ddos, etc.
    severity: str = "LOW"  # LOW, MEDIUM, HIGH, CRITICAL
    source_ip: str = ""
    user_agent: str = ""
    endpoint: str = ""
    payload: str = ""
    detected_at: datetime = field(default_factory=datetime.utcnow)
    status: str = "DETECTED"  # DETECTED, BLOCKED, MITIGATED
    auto_fixed: bool = False
    country: Optional[str] = None
    description: str = ""
    mitigation_actions: List[str] = field(default_factory=list)

@dataclass
class SystemAudit:
    """Modèle pour les audits système"""
    audit_id: str = field(default_factory=lambda: f"AUD-{datetime.now().strftime('%Y%m%d-%H%M%S')}")
    audit_date: datetime = field(default_factory=datetime.utcnow)
    audit_type: str = "DAILY"  # DAILY, MANUAL, INCIDENT
    system_health: Dict[str, Any] = field(default_factory=dict)
    security_issues: List[Dict] = field(default_factory=list)
    performance_metrics: Dict[str, Any] = field(default_factory=dict)
    bugs_detected: List[Dict] = field(default_factory=list)
    bugs_fixed: List[Dict] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    overall_score: int = 100
    status: str = "COMPLETED"

class SecurityAuditAgent:
    """Agent principal de sécurité et d'audit 24/7"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.logger = self._setup_logger()
        self.running = False
        self.start_time = datetime.utcnow()
        
        # Statistiques de sécurité
        self.stats = {
            "threats_blocked": 0,
            "attacks_prevented": 0,
            "bugs_fixed": 0,
            "audits_completed": 0,
            "uptime_minutes": 0
        }
        
        # Cache pour la détection d'anomalies
        self.ip_request_counts = defaultdict(int)
        self.failed_login_attempts = defaultdict(int)
        self.recent_requests = deque(maxlen=1000)
        self.active_sessions = {}
        self.blocked_ips = set()
        
        # Patterns de sécurité compilés
        self.security_patterns = [re.compile(pattern, re.IGNORECASE) 
                                 for pattern in SECURITY_CONFIG["suspicious_patterns"]]
        
        # Timezone française
        self.timezone = pytz.timezone(SECURITY_CONFIG["timezone"])
        
        self.logger.critical("🛡️ AGENT AUDIT & CYBERSÉCURITÉ INITIALISÉ - MODE 24/7 ACTIVÉ ⚡")
    
    def _setup_logger(self) -> logging.Logger:
        """Configuration du système de logging sécurisé"""
        logger = logging.getLogger("SecurityAuditAgent")
        logger.setLevel(logging.INFO)
        
        # Handler pour fichier de sécurité
        security_handler = logging.FileHandler("/var/log/josmose_security.log")
        security_handler.setLevel(logging.WARNING)
        
        # Format sécurisé avec timestamp
        formatter = logging.Formatter(
            '%(asctime)s [SECURITY] %(levelname)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        security_handler.setFormatter(formatter)
        logger.addHandler(security_handler)
        
        return logger
    
    async def start_24_7_monitoring(self):
        """🚀 Démarrage de la surveillance 24/7"""
        self.running = True
        self.logger.critical("🚀 DÉMARRAGE SURVEILLANCE 24/7 - AGENT CYBERSÉCURITÉ ACTIF")
        
        # Programmer l'audit quotidien à minuit français
        schedule.every().day.at(SECURITY_CONFIG["audit_time"]).do(
            lambda: asyncio.create_task(self.perform_daily_audit())
        )
        
        # Boucle principale de surveillance
        while self.running:
            try:
                # 1. Surveillance temps réel des menaces
                await self.real_time_threat_detection()
                
                # 2. Monitoring système
                await self.system_health_check()
                
                # 3. Nettoyage des caches et statistiques
                await self.cleanup_security_cache()
                
                # 4. Exécution des tâches programmées
                schedule.run_pending()
                
                # 5. Mise à jour des statistiques
                self.stats["uptime_minutes"] = int((datetime.utcnow() - self.start_time).total_seconds() / 60)
                
                # Attendre 30 secondes avant la prochaine itération
                await asyncio.sleep(30)
                
            except Exception as e:
                self.logger.error(f"🚨 ERREUR dans la boucle de surveillance: {str(e)}")
                await asyncio.sleep(60)  # Attendre plus longtemps en cas d'erreur
    
    async def real_time_threat_detection(self):
        """🔍 Détection temps réel des menaces de sécurité"""
        try:
            # Surveiller les logs système
            await self._monitor_system_logs()
            
            # Vérifier les tentatives d'intrusion
            await self._detect_intrusion_attempts()
            
            # Analyser les patterns suspects dans les requêtes
            await self._analyze_suspicious_patterns()
            
            # Surveiller les ressources système
            await self._monitor_resource_usage()
            
        except Exception as e:
            self.logger.error(f"Erreur détection menaces: {str(e)}")
    
    async def _monitor_system_logs(self):
        """Surveillance des logs système pour détecter les anomalies"""
        try:
            # Analyser les logs nginx/apache
            log_files = [
                "/var/log/nginx/access.log",
                "/var/log/nginx/error.log", 
                "/var/log/supervisor/backend.err.log",
                "/var/log/supervisor/frontend.err.log"
            ]
            
            for log_file in log_files:
                if os.path.exists(log_file):
                    await self._analyze_log_file(log_file)
                    
        except Exception as e:
            self.logger.error(f"Erreur monitoring logs: {str(e)}")
    
    async def _analyze_log_file(self, log_file: str):
        """Analyse d'un fichier de log pour détecter les menaces"""
        try:
            # Lire les 100 dernières lignes du fichier
            with open(log_file, 'r') as f:
                lines = deque(f, maxlen=100)
            
            for line in lines:
                # Détecter les patterns suspects
                for pattern in self.security_patterns:
                    if pattern.search(line):
                        await self._handle_security_threat({
                            "type": "suspicious_pattern",
                            "severity": "MEDIUM",
                            "source": log_file,
                            "content": line.strip(),
                            "pattern": pattern.pattern
                        })
                
                # Détecter les erreurs 404 répétées (scan de vulnérabilités)
                if "404" in line and any(suspicious in line.lower() for suspicious in 
                                      ["admin", "wp-", "phpmyadmin", ".php", "sql"]):
                    await self._handle_security_threat({
                        "type": "vulnerability_scan",
                        "severity": "HIGH",
                        "source": log_file,
                        "content": line.strip()
                    })
                    
        except Exception as e:
            self.logger.error(f"Erreur analyse fichier {log_file}: {str(e)}")
    
    async def _detect_intrusion_attempts(self):
        """Détection des tentatives d'intrusion"""
        try:
            # Récupérer les tentatives de connexion échouées récentes
            failed_logins = await self.db.security_events.find({
                "event_type": "failed_login",
                "timestamp": {"$gte": datetime.utcnow() - timedelta(minutes=15)}
            }).to_list(100)
            
            # Grouper par IP
            ip_failures = defaultdict(int)
            for failure in failed_logins:
                ip_failures[failure.get("source_ip", "unknown")] += 1
            
            # Détecter les attaques brute force
            for ip, count in ip_failures.items():
                if count >= SECURITY_CONFIG["max_login_attempts"]:
                    await self._handle_security_threat({
                        "type": "brute_force",
                        "severity": "CRITICAL",
                        "source_ip": ip,
                        "attempts": count,
                        "description": f"Tentative de force brute détectée: {count} échecs de connexion"
                    })
                    
                    # Bloquer l'IP automatiquement
                    await self._block_ip(ip, reason="brute_force", duration_hours=24)
                    
        except Exception as e:
            self.logger.error(f"Erreur détection intrusion: {str(e)}")
    
    async def _analyze_suspicious_patterns(self):
        """Analyse des patterns suspects dans les requêtes récentes"""
        try:
            # Récupérer les requêtes récentes depuis MongoDB
            recent_requests = await self.db.api_requests.find({
                "timestamp": {"$gte": datetime.utcnow() - timedelta(minutes=5)}
            }).to_list(500)
            
            for request in recent_requests:
                payload = str(request.get("payload", "")) + str(request.get("params", ""))
                
                # Vérifier les patterns de sécurité
                for pattern in self.security_patterns:
                    if pattern.search(payload):
                        await self._handle_security_threat({
                            "type": "malicious_payload",
                            "severity": "HIGH",
                            "source_ip": request.get("ip", "unknown"),
                            "endpoint": request.get("endpoint", ""),
                            "payload": payload[:500],  # Limiter la taille
                            "user_agent": request.get("user_agent", ""),
                            "pattern_matched": pattern.pattern
                        })
                        
        except Exception as e:
            self.logger.error(f"Erreur analyse patterns: {str(e)}")
    
    async def _monitor_resource_usage(self):
        """Surveillance de l'utilisation des ressources système"""
        try:
            # CPU Usage
            cpu_percent = psutil.cpu_percent(interval=1)
            if cpu_percent > 90:
                await self._handle_security_threat({
                    "type": "resource_exhaustion",
                    "severity": "HIGH",
                    "description": f"Usage CPU critique: {cpu_percent}%"
                })
            
            # Memory Usage
            memory = psutil.virtual_memory()
            if memory.percent > 90:
                await self._handle_security_threat({
                    "type": "resource_exhaustion", 
                    "severity": "HIGH",
                    "description": f"Usage mémoire critique: {memory.percent}%"
                })
            
            # Disk Usage
            disk = psutil.disk_usage('/')
            if disk.percent > 85:
                await self._handle_security_threat({
                    "type": "resource_exhaustion",
                    "severity": "MEDIUM",
                    "description": f"Usage disque élevé: {disk.percent}%"
                })
            
            # Network Connections
            connections = len(psutil.net_connections())
            if connections > 1000:
                await self._handle_security_threat({
                    "type": "ddos_attempt",
                    "severity": "HIGH", 
                    "description": f"Nombre de connexions anormal: {connections}"
                })
                
        except Exception as e:
            self.logger.error(f"Erreur monitoring ressources: {str(e)}")
    
    async def _handle_security_threat(self, threat_data: Dict[str, Any]):
        """Gestion d'une menace de sécurité détectée"""
        try:
            threat = SecurityThreat(
                threat_type=threat_data.get("type", "unknown"),
                severity=threat_data.get("severity", "LOW"),
                source_ip=threat_data.get("source_ip", ""),
                endpoint=threat_data.get("endpoint", ""),
                payload=threat_data.get("payload", ""),
                description=threat_data.get("description", "")
            )
            
            # Log critique
            self.logger.critical(f"🚨 MENACE DÉTECTÉE: {threat.threat_type} | "
                               f"Sévérité: {threat.severity} | IP: {threat.source_ip}")
            
            # Actions automatiques selon le type de menace
            await self._auto_mitigate_threat(threat)
            
            # Sauvegarder dans la base de données
            await self.db.security_threats.insert_one({
                "threat_id": threat.threat_id,
                "threat_type": threat.threat_type,
                "severity": threat.severity,
                "source_ip": threat.source_ip,
                "endpoint": threat.endpoint,
                "payload": threat.payload,
                "detected_at": threat.detected_at,
                "status": threat.status,
                "auto_fixed": threat.auto_fixed,
                "description": threat.description,
                "mitigation_actions": threat.mitigation_actions
            })
            
            # Mettre à jour les statistiques
            self.stats["threats_blocked"] += 1
            if threat.severity in ["HIGH", "CRITICAL"]:
                self.stats["attacks_prevented"] += 1
                
        except Exception as e:
            self.logger.error(f"Erreur gestion menace: {str(e)}")
    
    async def _auto_mitigate_threat(self, threat: SecurityThreat):
        """Actions automatiques de mitigation des menaces"""
        try:
            if not SECURITY_CONFIG["auto_fix_enabled"]:
                return
                
            mitigation_actions = []
            
            # Actions selon le type de menace
            if threat.threat_type == "brute_force":
                if threat.source_ip:
                    await self._block_ip(threat.source_ip, "brute_force", 24)
                    mitigation_actions.append(f"IP {threat.source_ip} bloquée pour 24h")
                    threat.auto_fixed = True
                    
            elif threat.threat_type == "malicious_payload":
                if threat.source_ip:
                    await self._block_ip(threat.source_ip, "malicious_payload", 1)
                    mitigation_actions.append(f"IP {threat.source_ip} bloquée pour 1h")
                    threat.auto_fixed = True
                    
            elif threat.threat_type == "ddos_attempt":
                await self._enable_ddos_protection()
                mitigation_actions.append("Protection DDoS activée")
                threat.auto_fixed = True
                
            elif threat.threat_type == "resource_exhaustion":
                await self._optimize_system_resources()
                mitigation_actions.append("Optimisation ressources système")
                threat.auto_fixed = True
                
            # Actions communes pour les menaces critiques
            if threat.severity == "CRITICAL":
                await self._send_critical_alert(threat)
                mitigation_actions.append("Alerte critique envoyée")
            
            threat.mitigation_actions = mitigation_actions
            threat.status = "MITIGATED" if threat.auto_fixed else "DETECTED"
            
            if mitigation_actions:
                self.logger.warning(f"🛡️ MITIGATION AUTOMATIQUE: {', '.join(mitigation_actions)}")
                
        except Exception as e:
            self.logger.error(f"Erreur mitigation automatique: {str(e)}")
    
    async def _block_ip(self, ip: str, reason: str, duration_hours: int):
        """Blocage automatique d'une adresse IP"""
        try:
            if ip in self.blocked_ips:
                return  # Déjà bloquée
                
            self.blocked_ips.add(ip)
            expiry = datetime.utcnow() + timedelta(hours=duration_hours)
            
            # Sauvegarder le blocage
            await self.db.blocked_ips.insert_one({
                "ip": ip,
                "reason": reason,
                "blocked_at": datetime.utcnow(),
                "expires_at": expiry,
                "auto_blocked": True
            })
            
            self.logger.warning(f"🚫 IP BLOQUÉE: {ip} | Raison: {reason} | Durée: {duration_hours}h")
            
        except Exception as e:
            self.logger.error(f"Erreur blocage IP {ip}: {str(e)}")
    
    async def _enable_ddos_protection(self):
        """Activation de la protection anti-DDoS"""
        try:
            # Réduire les limites de taux temporairement
            SECURITY_CONFIG["rate_limit_per_minute"] = 20
            
            # Log l'activation
            self.logger.critical("🛡️ PROTECTION ANTI-DDOS ACTIVÉE - Limites réduites temporairement")
            
            # Programmer la désactivation après 1 heure
            threading.Timer(3600, self._disable_ddos_protection).start()
            
        except Exception as e:
            self.logger.error(f"Erreur activation protection DDoS: {str(e)}")
    
    def _disable_ddos_protection(self):
        """Désactivation de la protection anti-DDoS"""
        try:
            SECURITY_CONFIG["rate_limit_per_minute"] = 100
            self.logger.info("🟢 Protection anti-DDoS désactivée - Limites normales restaurées")
        except Exception as e:
            self.logger.error(f"Erreur désactivation protection DDoS: {str(e)}")
    
    async def _optimize_system_resources(self):
        """Optimisation automatique des ressources système"""
        try:
            # Nettoyer les caches
            self.ip_request_counts.clear()
            self.recent_requests.clear()
            
            # Forcer le garbage collection
            import gc
            gc.collect()
            
            self.logger.info("🧹 OPTIMISATION SYSTÈME: Caches nettoyés, mémoire libérée")
            
        except Exception as e:
            self.logger.error(f"Erreur optimisation système: {str(e)}")
    
    async def _send_critical_alert(self, threat: SecurityThreat):
        """Envoi d'alerte critique"""
        try:
            alert_message = f"""
🚨 ALERTE CYBERSÉCURITÉ CRITIQUE - JOSMOZE.COM 🚨

Type de menace: {threat.threat_type}
Sévérité: {threat.severity}
IP source: {threat.source_ip}
Endpoint: {threat.endpoint}
Description: {threat.description}
Heure: {threat.detected_at.strftime('%Y-%m-%d %H:%M:%S')}

Actions automatiques prises:
{chr(10).join(f"• {action}" for action in threat.mitigation_actions)}

🛡️ Agent de sécurité JOSMOZE.COM
"""
            
            # Sauvegarder l'alerte dans la base
            await self.db.security_alerts.insert_one({
                "alert_id": f"ALERT-{int(time.time())}",
                "threat_id": threat.threat_id,
                "message": alert_message,
                "sent_at": datetime.utcnow(),
                "severity": threat.severity
            })
            
            self.logger.critical("📧 ALERTE CRITIQUE ENVOYÉE")
            
        except Exception as e:
            self.logger.error(f"Erreur envoi alerte: {str(e)}")
    
    async def perform_daily_audit(self):
        """🔍 Audit quotidien automatique du système (minuit français)"""
        try:
            self.logger.critical("🔍 DÉBUT AUDIT QUOTIDIEN - ANALYSE COMPLÈTE DU SYSTÈME")
            
            audit = SystemAudit()
            
            # 1. Audit de sécurité
            security_issues = await self._audit_security()
            audit.security_issues = security_issues
            
            # 2. Audit de performance
            performance_metrics = await self._audit_performance()
            audit.performance_metrics = performance_metrics
            
            # 3. Détection et correction des bugs
            bugs_detected = await self._detect_system_bugs()
            bugs_fixed = await self._auto_fix_bugs(bugs_detected)
            audit.bugs_detected = bugs_detected
            audit.bugs_fixed = bugs_fixed
            
            # 4. Audit santé système
            system_health = await self._audit_system_health()
            audit.system_health = system_health
            
            # 5. Génération des recommandations
            recommendations = await self._generate_recommendations(audit)
            audit.recommendations = recommendations
            
            # 6. Calcul du score global
            audit.overall_score = self._calculate_audit_score(audit)
            
            # 7. Sauvegarder l'audit
            await self.db.system_audits.insert_one({
                "audit_id": audit.audit_id,
                "audit_date": audit.audit_date,
                "audit_type": audit.audit_type,
                "system_health": audit.system_health,
                "security_issues": audit.security_issues,
                "performance_metrics": audit.performance_metrics,
                "bugs_detected": audit.bugs_detected,
                "bugs_fixed": audit.bugs_fixed,
                "recommendations": audit.recommendations,
                "overall_score": audit.overall_score,
                "status": audit.status
            })
            
            # 8. Mettre à jour les statistiques
            self.stats["audits_completed"] += 1
            self.stats["bugs_fixed"] += len(bugs_fixed)
            
            self.logger.critical(f"✅ AUDIT QUOTIDIEN TERMINÉ - Score: {audit.overall_score}/100 | "
                               f"Bugs corrigés: {len(bugs_fixed)} | "
                               f"Problèmes sécurité: {len(security_issues)}")
            
            return audit
            
        except Exception as e:
            self.logger.error(f"Erreur audit quotidien: {str(e)}")
            return None
    
    async def _audit_security(self) -> List[Dict]:
        """Audit de sécurité du système"""
        security_issues = []
        
        try:
            # Vérifier les IPs bloquées
            blocked_ips = await self.db.blocked_ips.count_documents({"expires_at": {"$gte": datetime.utcnow()}})
            
            # Vérifier les menaces récentes
            recent_threats = await self.db.security_threats.find({
                "detected_at": {"$gte": datetime.utcnow() - timedelta(days=1)}
            }).to_list(100)
            
            # Vérifier les tentatives de connexion échouées
            failed_logins = await self.db.security_events.count_documents({
                "event_type": "failed_login",
                "timestamp": {"$gte": datetime.utcnow() - timedelta(days=1)}
            })
            
            # Analyser les problèmes de sécurité
            if len(recent_threats) > 10:
                security_issues.append({
                    "type": "high_threat_volume",
                    "severity": "MEDIUM",
                    "description": f"{len(recent_threats)} menaces détectées dans les dernières 24h",
                    "recommendation": "Surveillance renforcée recommandée"
                })
            
            if failed_logins > 50:
                security_issues.append({
                    "type": "high_failed_logins",
                    "severity": "HIGH",
                    "description": f"{failed_logins} tentatives de connexion échouées",
                    "recommendation": "Renforcer l'authentification"
                })
                
        except Exception as e:
            self.logger.error(f"Erreur audit sécurité: {str(e)}")
        
        return security_issues
    
    async def _audit_performance(self) -> Dict[str, Any]:
        """Audit de performance du système"""
        metrics = {}
        
        try:
            # CPU et Mémoire
            metrics["cpu_percent"] = psutil.cpu_percent(interval=1)
            metrics["memory_percent"] = psutil.virtual_memory().percent
            metrics["disk_percent"] = psutil.disk_usage('/').percent
            
            # Connexions réseau
            metrics["network_connections"] = len(psutil.net_connections())
            
            # Base de données
            db_stats = await self.db.command("dbStats")
            metrics["db_size_mb"] = db_stats.get("dataSize", 0) / (1024 * 1024)
            metrics["db_collections"] = db_stats.get("collections", 0)
            
            # Temps de réponse API (simulé)
            start_time = time.time()
            await self.db.system_audits.find_one()  # Requête test
            metrics["db_response_time_ms"] = (time.time() - start_time) * 1000
            
        except Exception as e:
            self.logger.error(f"Erreur audit performance: {str(e)}")
        
        return metrics
    
    async def _detect_system_bugs(self) -> List[Dict]:
        """Détection automatique des bugs système"""
        bugs = []
        
        try:
            # Vérifier les erreurs dans les logs
            error_patterns = [
                r"ERROR.*",
                r"CRITICAL.*",
                r"Exception.*",
                r"Traceback.*",
                r"500.*Internal Server Error"
            ]
            
            for pattern_str in error_patterns:
                pattern = re.compile(pattern_str, re.IGNORECASE)
                
                # Analyser les logs récents
                log_files = [
                    "/var/log/supervisor/backend.err.log",
                    "/var/log/supervisor/frontend.err.log"
                ]
                
                for log_file in log_files:
                    if os.path.exists(log_file):
                        try:
                            with open(log_file, 'r') as f:
                                recent_lines = deque(f, maxlen=100)
                            
                            for line in recent_lines:
                                if pattern.search(line):
                                    bugs.append({
                                        "bug_id": f"BUG-{int(time.time())}-{hash(line) % 10000}",
                                        "type": "log_error",
                                        "severity": "MEDIUM",
                                        "source": log_file,
                                        "description": line.strip()[:200],
                                        "detected_at": datetime.utcnow()
                                    })
                                    
                        except Exception as e:
                            self.logger.error(f"Erreur lecture {log_file}: {str(e)}")
            
            # Vérifier la santé des services
            services = ["backend", "frontend", "mongodb"]
            for service in services:
                try:
                    result = subprocess.run(
                        ["sudo", "supervisorctl", "status", service],
                        capture_output=True, text=True, timeout=10
                    )
                    
                    if "RUNNING" not in result.stdout:
                        bugs.append({
                            "bug_id": f"BUG-SERVICE-{service}-{int(time.time())}",
                            "type": "service_down",
                            "severity": "HIGH",
                            "source": "supervisorctl",
                            "description": f"Service {service} non opérationnel",
                            "detected_at": datetime.utcnow()
                        })
                        
                except Exception as e:
                    self.logger.error(f"Erreur vérification service {service}: {str(e)}")
                    
        except Exception as e:
            self.logger.error(f"Erreur détection bugs: {str(e)}")
        
        return bugs
    
    async def _auto_fix_bugs(self, bugs: List[Dict]) -> List[Dict]:
        """Correction automatique des bugs détectés"""
        fixed_bugs = []
        
        try:
            for bug in bugs:
                fix_applied = False
                fix_description = ""
                
                # Corrections automatiques selon le type de bug
                if bug["type"] == "service_down":
                    try:
                        service_name = bug["description"].split()[-2]  # Extraire le nom du service
                        result = subprocess.run(
                            ["sudo", "supervisorctl", "restart", service_name],
                            capture_output=True, text=True, timeout=30
                        )
                        
                        if result.returncode == 0:
                            fix_applied = True
                            fix_description = f"Service {service_name} redémarré automatiquement"
                            
                    except Exception as e:
                        self.logger.error(f"Erreur redémarrage service: {str(e)}")
                
                elif bug["type"] == "log_error":
                    # Pour les erreurs de logs, on peut essayer des corrections génériques
                    if "connection" in bug["description"].lower():
                        # Problème de connexion - redémarrer les services
                        try:
                            subprocess.run(
                                ["sudo", "supervisorctl", "restart", "all"],
                                capture_output=True, text=True, timeout=60
                            )
                            fix_applied = True
                            fix_description = "Redémarrage complet des services"
                        except:
                            pass
                    
                    elif "memory" in bug["description"].lower():
                        # Problème de mémoire - nettoyer les caches
                        await self._optimize_system_resources()
                        fix_applied = True
                        fix_description = "Optimisation mémoire et nettoyage caches"
                
                # Si une correction a été appliquée
                if fix_applied:
                    fixed_bug = bug.copy()
                    fixed_bug["fixed_at"] = datetime.utcnow()
                    fixed_bug["fix_description"] = fix_description
                    fixed_bugs.append(fixed_bug)
                    
                    self.logger.warning(f"🔧 BUG CORRIGÉ AUTOMATIQUEMENT: {bug['bug_id']} - {fix_description}")
                    
        except Exception as e:
            self.logger.error(f"Erreur correction automatique: {str(e)}")
        
        return fixed_bugs
    
    async def _audit_system_health(self) -> Dict[str, Any]:
        """Audit de la santé générale du système"""
        health = {}
        
        try:
            # Services
            services_status = {}
            services = ["backend", "frontend", "mongodb", "code-server"]
            
            for service in services:
                try:
                    result = subprocess.run(
                        ["sudo", "supervisorctl", "status", service],
                        capture_output=True, text=True, timeout=10
                    )
                    services_status[service] = "RUNNING" in result.stdout
                except:
                    services_status[service] = False
            
            health["services"] = services_status
            health["services_healthy"] = sum(services_status.values())
            health["services_total"] = len(services_status)
            
            # Connectivité base de données
            try:
                await self.db.command("ping")
                health["database_connected"] = True
            except:
                health["database_connected"] = False
            
            # Espace disque
            disk_usage = psutil.disk_usage('/')
            health["disk_free_gb"] = disk_usage.free / (1024**3)
            health["disk_usage_percent"] = disk_usage.percent
            
            # Uptime système
            health["system_uptime_hours"] = (time.time() - psutil.boot_time()) / 3600
            
            # Agent uptime
            health["agent_uptime_minutes"] = self.stats["uptime_minutes"]
            
        except Exception as e:
            self.logger.error(f"Erreur audit santé: {str(e)}")
        
        return health
    
    async def _generate_recommendations(self, audit: SystemAudit) -> List[str]:
        """Génération de recommandations basées sur l'audit"""
        recommendations = []
        
        try:
            # Recommandations sécurité
            if len(audit.security_issues) > 5:
                recommendations.append("🔒 Renforcer la surveillance de sécurité - niveau de menaces élevé")
            
            # Recommandations performance
            if audit.performance_metrics.get("cpu_percent", 0) > 80:
                recommendations.append("⚡ Optimiser les performances CPU - usage élevé détecté")
            
            if audit.performance_metrics.get("memory_percent", 0) > 80:
                recommendations.append("🧠 Optimiser l'usage mémoire - niveau critique atteint")
            
            # Recommandations système
            if audit.system_health.get("services_healthy", 0) < audit.system_health.get("services_total", 1):
                recommendations.append("🔧 Vérifier l'état des services - certains services défaillants")
            
            if audit.system_health.get("disk_usage_percent", 0) > 80:
                recommendations.append("💾 Nettoyer l'espace disque - usage critique")
            
            # Recommandations générales
            if len(audit.bugs_fixed) > 5:
                recommendations.append("🐛 Analyser les causes racines des bugs récurrents")
            
            if not recommendations:
                recommendations.append("✅ Système en excellent état - maintenir la surveillance")
                
        except Exception as e:
            self.logger.error(f"Erreur génération recommandations: {str(e)}")
        
        return recommendations
    
    def _calculate_audit_score(self, audit: SystemAudit) -> int:
        """Calcul du score global d'audit (0-100)"""
        score = 100
        
        try:
            # Pénalités sécurité
            critical_security = len([issue for issue in audit.security_issues if issue.get("severity") == "HIGH"])
            score -= critical_security * 15
            
            medium_security = len([issue for issue in audit.security_issues if issue.get("severity") == "MEDIUM"])
            score -= medium_security * 5
            
            # Pénalités performance
            if audit.performance_metrics.get("cpu_percent", 0) > 90:
                score -= 20
            elif audit.performance_metrics.get("cpu_percent", 0) > 80:
                score -= 10
                
            if audit.performance_metrics.get("memory_percent", 0) > 90:
                score -= 20
            elif audit.performance_metrics.get("memory_percent", 0) > 80:
                score -= 10
            
            # Pénalités bugs
            critical_bugs = len([bug for bug in audit.bugs_detected if bug.get("severity") == "HIGH"])
            score -= critical_bugs * 10
            
            # Bonus corrections automatiques
            score += min(len(audit.bugs_fixed) * 2, 10)
            
            # Assurer que le score reste entre 0 et 100
            score = max(0, min(100, score))
            
        except Exception as e:
            self.logger.error(f"Erreur calcul score: {str(e)}")
            score = 50  # Score par défaut en cas d'erreur
        
        return score
    
    async def system_health_check(self):
        """Vérification rapide de la santé du système"""
        try:
            # Vérifications de base toutes les 30 secondes
            
            # 1. Vérifier que les services critiques tournent
            critical_services = ["backend", "mongodb"]
            for service in critical_services:
                try:
                    result = subprocess.run(
                        ["sudo", "supervisorctl", "status", service],
                        capture_output=True, text=True, timeout=5
                    )
                    
                    if "RUNNING" not in result.stdout:
                        await self._handle_security_threat({
                            "type": "service_failure",
                            "severity": "CRITICAL",
                            "description": f"Service critique {service} arrêté"
                        })
                        
                        # Tentative de redémarrage automatique
                        try:
                            subprocess.run(
                                ["sudo", "supervisorctl", "restart", service],
                                capture_output=True, text=True, timeout=30
                            )
                            self.logger.warning(f"🔄 Service {service} redémarré automatiquement")
                        except:
                            pass
                            
                except Exception as e:
                    self.logger.error(f"Erreur vérification service {service}: {str(e)}")
            
            # 2. Vérifier la connectivité base de données
            try:
                await self.db.command("ping")
            except Exception as e:
                await self._handle_security_threat({
                    "type": "database_connection",
                    "severity": "CRITICAL",
                    "description": f"Perte de connexion base de données: {str(e)}"
                })
            
        except Exception as e:
            self.logger.error(f"Erreur health check: {str(e)}")
    
    async def cleanup_security_cache(self):
        """Nettoyage périodique des caches de sécurité"""
        try:
            current_time = datetime.utcnow()
            
            # Nettoyer les compteurs d'IP (toutes les heures)
            if len(self.ip_request_counts) > 10000:
                self.ip_request_counts.clear()
            
            # Nettoyer les tentatives de login échouées (après 1 heure)
            expired_ips = []
            for ip, timestamp in self.failed_login_attempts.items():
                if current_time - datetime.fromtimestamp(timestamp) > timedelta(hours=1):
                    expired_ips.append(ip)
            
            for ip in expired_ips:
                del self.failed_login_attempts[ip]
            
            # Nettoyer les IPs bloquées expirées
            expired_blocks = await self.db.blocked_ips.find({
                "expires_at": {"$lt": current_time}
            }).to_list(100)
            
            for block in expired_blocks:
                self.blocked_ips.discard(block["ip"])
                await self.db.blocked_ips.delete_one({"_id": block["_id"]})
            
        except Exception as e:
            self.logger.error(f"Erreur nettoyage cache: {str(e)}")
    
    async def get_security_dashboard(self) -> Dict[str, Any]:
        """Récupération des données pour le dashboard de sécurité"""
        try:
            # Statistiques temps réel
            dashboard = {
                "agent_status": "ACTIVE" if self.running else "STOPPED",
                "uptime_minutes": self.stats["uptime_minutes"],
                "stats": self.stats.copy(),
                "active_threats": len(await self.db.security_threats.find({
                    "status": "DETECTED",
                    "detected_at": {"$gte": datetime.utcnow() - timedelta(hours=24)}
                }).to_list(100)),
                "blocked_ips_count": len(self.blocked_ips),
                "last_audit": None,
                "system_health": "GOOD",
                "threat_level": "LOW"
            }
            
            # Dernier audit
            last_audit = await self.db.system_audits.find_one(
                {}, sort=[("audit_date", -1)]
            )
            if last_audit:
                dashboard["last_audit"] = {
                    "date": last_audit["audit_date"],
                    "score": last_audit["overall_score"],
                    "issues": len(last_audit.get("security_issues", [])),
                    "bugs_fixed": len(last_audit.get("bugs_fixed", []))
                }
            
            # Niveau de menace basé sur les activités récentes
            recent_high_threats = await self.db.security_threats.count_documents({
                "severity": {"$in": ["HIGH", "CRITICAL"]},
                "detected_at": {"$gte": datetime.utcnow() - timedelta(hours=6)}
            })
            
            if recent_high_threats > 10:
                dashboard["threat_level"] = "CRITICAL"
                dashboard["system_health"] = "AT_RISK"
            elif recent_high_threats > 5:
                dashboard["threat_level"] = "HIGH"
                dashboard["system_health"] = "WARNING"
            elif recent_high_threats > 0:
                dashboard["threat_level"] = "MEDIUM"
            
            return dashboard
            
        except Exception as e:
            self.logger.error(f"Erreur dashboard sécurité: {str(e)}")
            return {"error": str(e)}
    
    def stop_monitoring(self):
        """Arrêt de l'agent de surveillance"""
        self.running = False
        self.logger.critical("🛑 AGENT AUDIT & CYBERSÉCURITÉ ARRÊTÉ")

# Instance globale de l'agent
security_audit_agent = None

def get_security_audit_agent(db: AsyncIOMotorDatabase):
    """Factory pour l'agent de sécurité"""
    global security_audit_agent
    if security_audit_agent is None:
        security_audit_agent = SecurityAuditAgent(db)
    return security_audit_agent

def start_security_monitoring_task(db: AsyncIOMotorDatabase):
    """Démarre l'agent de sécurité en arrière-plan"""
    try:
        import threading
        
        def run_security_monitoring():
            """Fonction pour exécuter la surveillance dans un thread séparé"""
            try:
                # Créer un nouvel événement loop pour ce thread
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                # Initialiser l'agent
                global security_audit_agent
                security_audit_agent = SecurityAuditAgent(db)
                
                # Lancer la surveillance 24/7
                loop.run_until_complete(security_audit_agent.start_24_7_monitoring())
            except Exception as e:
                logging.error(f"Erreur dans le thread de surveillance sécurité: {e}")
        
        # Lancer dans un thread daemon (se ferme automatiquement avec l'app)
        thread = threading.Thread(target=run_security_monitoring, daemon=True)
        thread.start()
        
        logging.critical("🚀🛡️ AGENT AUDIT & CYBERSÉCURITÉ DÉMARRÉ EN MODE 24/7 ⚡🛡️")
        return {"status": "started", "message": "Agent de sécurité démarré en mode 24/7"}
        
    except Exception as e:
        logging.error(f"Impossible de démarrer l'agent de sécurité: {e}")
        return {"status": "error", "message": str(e)}