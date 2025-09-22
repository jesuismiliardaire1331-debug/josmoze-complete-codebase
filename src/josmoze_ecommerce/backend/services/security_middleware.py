"""
Josmoze.com - Security & Performance Middleware
Middleware de sécurité et performance critique pour production
"""

import time
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from collections import defaultdict, deque
import redis
import asyncio
from fastapi import Request, Response, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request as StarletteRequest
from starlette.responses import Response as StarletteResponse
import ipaddress
import re
import hashlib

logger = logging.getLogger(__name__)

# Configuration Redis pour cache et rate limiting
try:
    redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
    redis_client.ping()
    REDIS_AVAILABLE = True
    logger.info("Redis connection established")
except:
    REDIS_AVAILABLE = False
    logger.warning("Redis not available, using memory fallback")

# Configuration sécurité
SECURITY_CONFIG = {
    "rate_limit": {
        "requests_per_minute": 300,
        "requests_per_hour": 5000,
        "burst_limit": 50
    },
    "blocked_ips": set(),
    "suspicious_patterns": [
        r'(?i)(union|select|drop|delete|insert|update)\s+',
        r'(?i)<script[^>]*>.*?</script>',
        r'(?i)javascript:',
        r'(?i)on\w+\s*=',
        r'(?i)(exec|eval|system|cmd)\s*\(',
        r'\.\./.*\.\.',
        r'(?i)(wget|curl|nc|netcat)',
    ],
    "max_request_size": 10 * 1024 * 1024,  # 10MB
    "sensitive_endpoints": ["/api/auth/", "/api/crm/", "/api/admin/"],
    "public_endpoints": ["/api/", "/api/detect-location", "/api/products", "/api/company/legal-info"]
}

class SecurityMiddleware(BaseHTTPMiddleware):
    """Middleware de sécurité avancé pour protection DDoS, injections, etc."""
    
    def __init__(self, app, config: Dict = None):
        super().__init__(app)
        self.config = config or SECURITY_CONFIG
        self.ip_requests = defaultdict(lambda: deque(maxlen=1000))
        self.blocked_until = defaultdict(datetime)
        
        # Compiler les patterns de sécurité
        self.compiled_patterns = [re.compile(pattern) for pattern in self.config["suspicious_patterns"]]
    
    async def dispatch(self, request: Request, call_next) -> Response:
        start_time = time.time()
        client_ip = self._get_client_ip(request)
        
        try:
            # 1. Vérifier les IPs bloquées
            if await self._is_ip_blocked(client_ip):
                logger.warning(f"Blocked IP attempt: {client_ip}")
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Too many requests. Try again later."
                )
            
            # 2. Rate limiting
            if not await self._check_rate_limit(client_ip, request.url.path):
                await self._block_ip_temporarily(client_ip, minutes=15)
                logger.warning(f"Rate limit exceeded: {client_ip} - {request.url.path}")
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Rate limit exceeded"
                )
            
            # 3. Validation de la requête
            await self._validate_request(request)
            
            # 4. Exécuter la requête
            response = await call_next(request)
            
            # 5. Mesurer les performances
            process_time = time.time() - start_time
            response.headers["X-Process-Time"] = str(process_time)
            
            # 6. Log de sécurité
            await self._log_request(request, response, process_time, client_ip)
            
            return response
            
        except HTTPException as e:
            # Log les tentatives suspectes
            await self._log_security_event(client_ip, request, str(e.detail))
            raise
        
        except Exception as e:
            logger.error(f"Security middleware error: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
            )
    
    def _get_client_ip(self, request: Request) -> str:
        """Obtenir l'IP réelle du client (gestion proxy/CDN)"""
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        return request.client.host if request.client else "unknown"
    
    async def _is_ip_blocked(self, ip: str) -> bool:
        """Vérifier si une IP est bloquée"""
        if ip in self.config["blocked_ips"]:
            return True
        
        # Vérifier le blocage temporaire
        if ip in self.blocked_until:
            if datetime.now() < self.blocked_until[ip]:
                return True
            else:
                del self.blocked_until[ip]
        
        # Vérifier dans Redis si disponible
        if REDIS_AVAILABLE:
            try:
                blocked = redis_client.get(f"blocked_ip:{ip}")
                return blocked == "1"
            except:
                pass
        
        return False
    
    async def _check_rate_limit(self, ip: str, path: str) -> bool:
        """Rate limiting intelligent par IP et endpoint"""
        now = datetime.now()
        
        # Configuration spéciale pour les endpoints sensibles
        if any(path.startswith(sensitive) for sensitive in self.config["sensitive_endpoints"]):
            limit_per_minute = 10
            limit_per_hour = 100
        elif any(path.startswith(public) for public in self.config["public_endpoints"]):
            limit_per_minute = 120
            limit_per_hour = 2000
        else:
            limit_per_minute = self.config["rate_limit"]["requests_per_minute"]
            limit_per_hour = self.config["rate_limit"]["requests_per_hour"]
        
        if REDIS_AVAILABLE:
            try:
                # Utiliser Redis pour le rate limiting distribué
                pipe = redis_client.pipeline()
                
                # Compteur par minute
                minute_key = f"rate_limit:{ip}:{now.strftime('%Y%m%d%H%M')}"
                pipe.incr(minute_key)
                pipe.expire(minute_key, 60)
                
                # Compteur par heure
                hour_key = f"rate_limit:{ip}:{now.strftime('%Y%m%d%H')}"
                pipe.incr(hour_key)
                pipe.expire(hour_key, 3600)
                
                results = pipe.execute()
                
                minute_count = results[0]
                hour_count = results[2]
                
                return minute_count <= limit_per_minute and hour_count <= limit_per_hour
                
            except Exception as e:
                logger.warning(f"Redis rate limiting failed: {e}")
        
        # Fallback en mémoire
        requests = self.ip_requests[ip]
        
        # Nettoyer les anciennes requêtes
        cutoff = now - timedelta(hours=1)
        while requests and requests[0] < cutoff:
            requests.popleft()
        
        # Ajouter la requête actuelle
        requests.append(now)
        
        # Compter les requêtes par minute et par heure
        minute_ago = now - timedelta(minutes=1)
        minute_requests = sum(1 for req_time in requests if req_time > minute_ago)
        hour_requests = len(requests)
        
        return minute_requests <= limit_per_minute and hour_requests <= limit_per_hour
    
    async def _block_ip_temporarily(self, ip: str, minutes: int):
        """Bloquer temporairement une IP"""
        until = datetime.now() + timedelta(minutes=minutes)
        self.blocked_until[ip] = until
        
        if REDIS_AVAILABLE:
            try:
                redis_client.setex(f"blocked_ip:{ip}", minutes * 60, "1")
            except:
                pass
        
        logger.warning(f"IP {ip} blocked temporarily for {minutes} minutes")
    
    async def _validate_request(self, request: Request):
        """Validation avancée des requêtes"""
        # 1. Taille de la requête
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > self.config["max_request_size"]:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="Request too large"
            )
        
        # 2. Validation des headers
        user_agent = request.headers.get("user-agent", "")
        if not user_agent or len(user_agent) < 10:
            logger.warning(f"Suspicious user agent: {user_agent}")
        
        # 3. Validation des paramètres URL
        query_params = str(request.url.query)
        if self._contains_suspicious_patterns(query_params):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid request parameters"
            )
        
        # 4. Validation du path
        path = str(request.url.path)
        if self._contains_suspicious_patterns(path):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid request path"
            )
    
    def _contains_suspicious_patterns(self, text: str) -> bool:
        """Détecter les patterns suspects (injections SQL, XSS, etc.)"""
        for pattern in self.compiled_patterns:
            if pattern.search(text):
                return True
        return False
    
    async def _log_request(self, request: Request, response: Response, process_time: float, client_ip: str):
        """Log des requêtes pour monitoring"""
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "ip": client_ip,
            "method": request.method,
            "path": str(request.url.path),
            "status_code": response.status_code,
            "process_time": process_time,
            "user_agent": request.headers.get("user-agent", ""),
            "referer": request.headers.get("referer", "")
        }
        
        # Log en base si nécessaire (pour analytics)
        if REDIS_AVAILABLE and process_time > 2.0:  # Log des requêtes lentes
            try:
                redis_client.lpush("slow_requests", json.dumps(log_data))
                redis_client.ltrim("slow_requests", 0, 999)  # Garder les 1000 dernières
            except:
                pass
    
    async def _log_security_event(self, ip: str, request: Request, event: str):
        """Log des événements de sécurité"""
        security_event = {
            "timestamp": datetime.now().isoformat(),
            "ip": ip,
            "event": event,
            "method": request.method,
            "path": str(request.url.path),
            "user_agent": request.headers.get("user-agent", ""),
            "query_params": str(request.url.query)
        }
        
        logger.warning(f"Security event: {json.dumps(security_event)}")
        
        if REDIS_AVAILABLE:
            try:
                redis_client.lpush("security_events", json.dumps(security_event))
                redis_client.ltrim("security_events", 0, 4999)  # Garder les 5000 derniers
            except:
                pass

class CacheMiddleware(BaseHTTPMiddleware):
    """Middleware de cache intelligent pour améliorer les performances"""
    
    def __init__(self, app):
        super().__init__(app)
        self.memory_cache = {}
        self.cache_ttl = {
            "/api/products": 300,  # 5 minutes
            "/api/detect-location": 3600,  # 1 heure
            "/api/company/legal-info": 3600,  # 1 heure
            "/api/crm/dashboard": 60,  # 1 minute
        }
    
    async def dispatch(self, request: Request, call_next) -> Response:
        # Only cache GET requests
        if request.method != "GET":
            return await call_next(request)
        
        cache_key = self._get_cache_key(request)
        ttl = self._get_ttl(request.url.path)
        
        if ttl == 0:  # No caching
            return await call_next(request)
        
        # Check cache
        cached_response = await self._get_from_cache(cache_key)
        if cached_response:
            logger.debug(f"Cache hit: {cache_key}")
            return cached_response
        
        # Execute request
        response = await call_next(request)
        
        # Cache successful responses
        if response.status_code == 200:
            await self._store_in_cache(cache_key, response, ttl)
        
        return response
    
    def _get_cache_key(self, request: Request) -> str:
        """Générer une clé de cache unique"""
        path = request.url.path
        query = request.url.query
        return f"cache:{hashlib.md5(f'{path}?{query}'.encode()).hexdigest()}"
    
    def _get_ttl(self, path: str) -> int:
        """Obtenir le TTL pour un path donné"""
        for cached_path, ttl in self.cache_ttl.items():
            if path.startswith(cached_path):
                return ttl
        return 0  # No cache by default
    
    async def _get_from_cache(self, key: str) -> Optional[Response]:
        """Récupérer du cache"""
        if REDIS_AVAILABLE:
            try:
                cached_data = redis_client.get(key)
                if cached_data:
                    data = json.loads(cached_data)
                    return Response(
                        content=data["content"],
                        status_code=data["status_code"],
                        headers={**data["headers"], "X-Cache": "HIT"},
                        media_type=data.get("media_type")
                    )
            except Exception as e:
                logger.warning(f"Redis cache get failed: {e}")
        
        # Fallback to memory cache
        if key in self.memory_cache:
            cached_data, expiry = self.memory_cache[key]
            if datetime.now() < expiry:
                data = json.loads(cached_data)
                return Response(
                    content=data["content"],
                    status_code=data["status_code"],
                    headers={**data["headers"], "X-Cache": "HIT-MEMORY"},
                    media_type=data.get("media_type")
                )
            else:
                del self.memory_cache[key]
        
        return None
    
    async def _store_in_cache(self, key: str, response: Response, ttl: int):
        """Stocker en cache"""
        try:
            # Read response body
            response_body = b""
            async for chunk in response.body_iterator:
                response_body += chunk
            
            cache_data = {
                "content": response_body.decode("utf-8"),
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "media_type": response.media_type
            }
            
            cache_json = json.dumps(cache_data)
            
            if REDIS_AVAILABLE:
                try:
                    redis_client.setex(key, ttl, cache_json)
                except Exception as e:
                    logger.warning(f"Redis cache set failed: {e}")
            
            # Fallback to memory cache
            expiry = datetime.now() + timedelta(seconds=ttl)
            self.memory_cache[key] = (cache_json, expiry)
            
            # Recreate response with cached body
            return Response(
                content=response_body,
                status_code=response.status_code,
                headers={**response.headers, "X-Cache": "MISS"},
                media_type=response.media_type
            )
            
        except Exception as e:
            logger.error(f"Cache store error: {e}")
            return response

# Fonctions utilitaires
def get_security_stats() -> Dict:
    """Obtenir les statistiques de sécurité"""
    stats = {
        "blocked_ips_count": len(SECURITY_CONFIG["blocked_ips"]),
        "redis_available": REDIS_AVAILABLE,
        "security_events_24h": 0,
        "slow_requests_24h": 0
    }
    
    if REDIS_AVAILABLE:
        try:
            # Compter les événements de sécurité
            events = redis_client.lrange("security_events", 0, -1)
            yesterday = datetime.now() - timedelta(days=1)
            
            recent_events = 0
            for event_json in events:
                try:
                    event = json.loads(event_json)
                    event_time = datetime.fromisoformat(event["timestamp"])
                    if event_time > yesterday:
                        recent_events += 1
                except:
                    continue
            
            stats["security_events_24h"] = recent_events
            
            # Compter les requêtes lentes
            slow_requests = redis_client.lrange("slow_requests", 0, -1)
            recent_slow = 0
            for request_json in slow_requests:
                try:
                    request = json.loads(request_json)
                    request_time = datetime.fromisoformat(request["timestamp"])
                    if request_time > yesterday:
                        recent_slow += 1
                except:
                    continue
            
            stats["slow_requests_24h"] = recent_slow
            
        except Exception as e:
            logger.error(f"Error getting security stats: {e}")
    
    return stats

async def clear_cache(pattern: str = "*"):
    """Nettoyer le cache"""
    cleared = 0
    
    if REDIS_AVAILABLE:
        try:
            keys = redis_client.keys(f"cache:{pattern}")
            if keys:
                cleared = redis_client.delete(*keys)
        except Exception as e:
            logger.error(f"Redis cache clear error: {e}")
    
    return {"cleared_keys": cleared, "redis_available": REDIS_AVAILABLE}