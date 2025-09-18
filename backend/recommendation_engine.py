"""
Josmoze.com - Smart Product Recommendation Engine
Moteur de recommandations intelligent pour augmenter les ventes
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import json
import math
from motor.motor_asyncio import AsyncIOMotorDatabase

logger = logging.getLogger(__name__)

class ProductRecommendationEngine:
    """Moteur de recommandations de produits intelligent"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        
        # Configuration des recommandations
        self.config = {
            "collaborative_weight": 0.4,  # Filtrage collaboratif
            "content_weight": 0.3,        # Similarité de contenu
            "popularity_weight": 0.2,     # Popularité
            "business_rules_weight": 0.1, # Règles business
            "min_confidence": 0.3,        # Score minimum pour recommander
            "max_recommendations": 6,     # Nombre max de recommandations
            "recency_days": 90            # Période pour calcul de popularité
        }
        
        # Cache pour optimiser les performances
        self._cache = {}
        self._cache_ttl = {}
        self._cache_duration = 1800  # 30 minutes
    
    async def get_recommendations(
        self, 
        customer_id: Optional[str] = None,
        current_cart: List[Dict] = None,
        customer_type: str = "B2C",
        context: Dict = None
    ) -> List[Dict[str, Any]]:
        """
        Obtenir des recommandations personnalisées
        
        Args:
            customer_id: ID du client (si connecté)
            current_cart: Panier actuel du client
            customer_type: B2C ou B2B
            context: Contexte supplémentaire (page, recherche, etc.)
        """
        try:
            cache_key = f"recommendations:{customer_id}:{customer_type}:{hash(str(current_cart))}"
            
            # Vérifier le cache
            if self._is_cached(cache_key):
                return self._get_from_cache(cache_key)
            
            # Calculer les recommandations
            recommendations = await self._calculate_recommendations(
                customer_id, current_cart, customer_type, context
            )
            
            # Mettre en cache
            self._cache_result(cache_key, recommendations)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Recommendation error: {e}")
            # Fallback vers des recommandations basiques
            return await self._get_fallback_recommendations(customer_type)
    
    async def _calculate_recommendations(
        self, customer_id: Optional[str], current_cart: List[Dict], 
        customer_type: str, context: Dict
    ) -> List[Dict[str, Any]]:
        """Calculer les recommandations avec différents algorithmes"""
        
        # 1. Récupérer les données nécessaires
        products = await self._get_products_data()
        customer_history = await self._get_customer_history(customer_id) if customer_id else []
        similar_customers = await self._find_similar_customers(customer_id) if customer_id else []
        
        # 2. Calculer les scores pour chaque produit
        product_scores = {}
        cart_product_ids = [item.get('product_id', item.get('id')) for item in (current_cart or [])]
        
        for product in products:
            product_id = product['id']
            
            # Ignorer les produits déjà dans le panier
            if product_id in cart_product_ids:
                continue
            
            # Calculer les différents scores
            collaborative_score = await self._calculate_collaborative_score(
                product_id, similar_customers, customer_history
            )
            content_score = await self._calculate_content_similarity_score(
                product_id, cart_product_ids, customer_history
            )
            popularity_score = await self._calculate_popularity_score(product_id)
            business_score = await self._calculate_business_rules_score(
                product, customer_type, context
            )
            
            # Score final pondéré
            final_score = (
                collaborative_score * self.config["collaborative_weight"] +
                content_score * self.config["content_weight"] +
                popularity_score * self.config["popularity_weight"] +
                business_score * self.config["business_rules_weight"]
            )
            
            if final_score >= self.config["min_confidence"]:
                product_scores[product_id] = {
                    "product": product,
                    "score": final_score,
                    "reasons": self._generate_recommendation_reasons(
                        collaborative_score, content_score, popularity_score, business_score
                    )
                }
        
        # 3. Trier et limiter les résultats
        sorted_recommendations = sorted(
            product_scores.values(),
            key=lambda x: x["score"],
            reverse=True
        )[:self.config["max_recommendations"]]
        
        # 4. Enrichir avec des métadonnées
        for rec in sorted_recommendations:
            rec.update({
                "recommendation_type": self._determine_recommendation_type(rec["reasons"]),
                "confidence": min(rec["score"], 1.0),
                "timestamp": datetime.now().isoformat()
            })
        
        return sorted_recommendations
    
    async def _calculate_collaborative_score(
        self, product_id: str, similar_customers: List[Dict], customer_history: List[Dict]
    ) -> float:
        """Filtrage collaboratif - "Les clients qui ont acheté X ont aussi acheté Y" """
        if not similar_customers:
            return 0.0
        
        score = 0.0
        total_weight = 0.0
        
        for similar_customer in similar_customers:
            # Vérifier si ce client similaire a acheté le produit
            customer_orders = await self.db.orders.find({
                "customer_email": similar_customer["email"],
                "status": "completed"
            }).to_list(None)
            
            has_product = False
            for order in customer_orders:
                for item in order.get("items", []):
                    if item.get("product_id") == product_id:
                        has_product = True
                        break
                if has_product:
                    break
            
            if has_product:
                # Pondérer par la similarité du client
                similarity = similar_customer.get("similarity", 0.5)
                score += similarity
                total_weight += similarity
        
        return score / total_weight if total_weight > 0 else 0.0
    
    async def _calculate_content_similarity_score(
        self, product_id: str, cart_product_ids: List[str], customer_history: List[Dict]
    ) -> float:
        """Similarité basée sur le contenu des produits"""
        if not cart_product_ids and not customer_history:
            return 0.0
        
        target_product = await self._get_product_by_id(product_id)
        if not target_product:
            return 0.0
        
        similarity_scores = []
        
        # Similarité avec les produits du panier
        for cart_product_id in cart_product_ids:
            cart_product = await self._get_product_by_id(cart_product_id)
            if cart_product:
                similarity = self._calculate_product_similarity(target_product, cart_product)
                similarity_scores.append(similarity)
        
        # Similarité avec l'historique d'achat
        for history_item in customer_history:
            history_product = await self._get_product_by_id(history_item.get("product_id"))
            if history_product:
                similarity = self._calculate_product_similarity(target_product, history_product)
                # Pondérer par l'ancienneté de l'achat
                recency_weight = self._calculate_recency_weight(history_item.get("date"))
                similarity_scores.append(similarity * recency_weight)
        
        return max(similarity_scores) if similarity_scores else 0.0
    
    def _calculate_product_similarity(self, product1: Dict, product2: Dict) -> float:
        """Calculer la similarité entre deux produits"""
        similarity = 0.0
        
        # Similarité de catégorie
        if product1.get("category") == product2.get("category"):
            similarity += 0.4
        
        # Similarité de prix (plus ils sont proches, plus c'est similaire)
        price1 = product1.get("price", 0)
        price2 = product2.get("price", 0)
        if price1 > 0 and price2 > 0:
            price_ratio = min(price1, price2) / max(price1, price2)
            similarity += 0.2 * price_ratio
        
        # Similarité d'audience cible
        if product1.get("target_audience") == product2.get("target_audience"):
            similarity += 0.2
        
        # Similarité des caractéristiques (analyse textuelle simple)
        features1 = set((product1.get("features", []) or []))
        features2 = set((product2.get("features", []) or []))
        if features1 and features2:
            feature_similarity = len(features1 & features2) / len(features1 | features2)
            similarity += 0.2 * feature_similarity
        
        return min(similarity, 1.0)
    
    async def _calculate_popularity_score(self, product_id: str) -> float:
        """Score de popularité basé sur les ventes récentes"""
        try:
            # Période récente
            cutoff_date = datetime.now() - timedelta(days=self.config["recency_days"])
            
            # Compter les ventes récentes
            orders = await self.db.orders.find({
                "created_at": {"$gte": cutoff_date},
                "status": "completed"
            }).to_list(None)
            
            product_sales = 0
            total_sales = 0
            
            for order in orders:
                for item in order.get("items", []):
                    if item.get("product_id") == product_id:
                        product_sales += item.get("quantity", 1)
                    total_sales += item.get("quantity", 1)
            
            # Normaliser le score
            return product_sales / total_sales if total_sales > 0 else 0.0
            
        except Exception as e:
            logger.error(f"Popularity score error: {e}")
            return 0.0
    
    async def _calculate_business_rules_score(
        self, product: Dict, customer_type: str, context: Dict
    ) -> float:
        """Score basé sur les règles business"""
        score = 0.0
        
        # 1. Correspondance avec le type de client
        target_audience = product.get("target_audience", "both")
        if target_audience == "both" or target_audience == customer_type:
            score += 0.3
        elif target_audience != customer_type:
            score -= 0.2  # Pénalité pour mauvaise correspondance
        
        # 2. Produits en stock
        if product.get("in_stock", True):
            score += 0.2
        else:
            score -= 0.5  # Forte pénalité pour produits en rupture
        
        # 3. Marge bénéficiaire (favoriser les produits à haute marge)
        price = product.get("price", 0)
        if price > 200:  # Produits premium
            score += 0.2
        elif price < 50:  # Produits d'entrée de gamme
            score += 0.1
        
        # 4. Saisonnalité et contexte
        if context:
            current_month = datetime.now().month
            
            # Exemple: favoriser les systèmes de filtration en été
            if current_month in [6, 7, 8] and "osmoseur" in product.get("category", ""):
                score += 0.1
        
        # 5. Nouveaux produits (boost temporaire)
        created_date = product.get("created_at")
        if created_date:
            if isinstance(created_date, str):
                created_date = datetime.fromisoformat(created_date.replace('Z', '+00:00'))
            
            days_since_creation = (datetime.now() - created_date.replace(tzinfo=None)).days
            if days_since_creation < 30:  # Nouveau produit
                score += 0.15
        
        return max(0.0, min(score, 1.0))
    
    def _generate_recommendation_reasons(
        self, collaborative: float, content: float, popularity: float, business: float
    ) -> List[str]:
        """Générer les raisons de la recommandation"""
        reasons = []
        
        if collaborative > 0.5:
            reasons.append("Recommandé par des clients similaires")
        
        if content > 0.5:
            reasons.append("Complète vos autres produits")
        
        if popularity > 0.3:
            reasons.append("Très populaire récemment")
        
        if business > 0.5:
            reasons.append("Parfait pour votre profil")
        
        if not reasons:
            reasons.append("Recommandé pour vous")
        
        return reasons
    
    def _determine_recommendation_type(self, reasons: List[str]) -> str:
        """Déterminer le type de recommandation principal"""
        if "clients similaires" in str(reasons):
            return "collaborative"
        elif "Complète" in str(reasons):
            return "complementary"
        elif "populaire" in str(reasons):
            return "trending"
        else:
            return "personalized"
    
    async def _get_products_data(self) -> List[Dict]:
        """Récupérer tous les produits disponibles"""
        try:
            # En production, ceci devrait venir de la base de données
            # Pour l'instant, on utilise les données du serveur
            from server import get_all_products
            return await get_all_products()
        except:
            # Fallback avec produits par défaut
            return [
                {
                    "id": "osmoseur-premium",
                    "name": "Osmoseur Premium - BlueMountain Avancé",
                    "price": 549.0,
                    "category": "osmoseur",
                    "target_audience": "both",
                    "in_stock": True
                }
            ]
    
    async def _get_product_by_id(self, product_id: str) -> Optional[Dict]:
        """Récupérer un produit par son ID"""
        products = await self._get_products_data()
        return next((p for p in products if p["id"] == product_id), None)
    
    async def _get_customer_history(self, customer_id: str) -> List[Dict]:
        """Récupérer l'historique d'achat d'un client"""
        if not customer_id:
            return []
        
        try:
            orders = await self.db.orders.find({
                "customer_email": customer_id,
                "status": "completed"
            }).sort("created_at", -1).limit(50).to_list(None)
            
            history = []
            for order in orders:
                for item in order.get("items", []):
                    history.append({
                        "product_id": item.get("product_id"),
                        "date": order.get("created_at", datetime.now()),
                        "quantity": item.get("quantity", 1),
                        "price": item.get("price", 0)
                    })
            
            return history
            
        except Exception as e:
            logger.error(f"Customer history error: {e}")
            return []
    
    async def _find_similar_customers(self, customer_id: str) -> List[Dict]:
        """Trouver des clients similaires"""
        if not customer_id:
            return []
        
        try:
            # Algorithme simple basé sur les achats communs
            customer_history = await self._get_customer_history(customer_id)
            customer_products = set(item["product_id"] for item in customer_history)
            
            if not customer_products:
                return []
            
            # Trouver d'autres clients qui ont acheté des produits similaires
            similar_customers = []
            
            orders = await self.db.orders.find({
                "customer_email": {"$ne": customer_id},
                "status": "completed"
            }).to_list(None)
            
            customer_similarities = defaultdict(lambda: {"email": "", "common_products": 0, "total_products": 0})
            
            for order in orders:
                other_customer = order.get("customer_email")
                if not other_customer:
                    continue
                
                other_products = set()
                for item in order.get("items", []):
                    other_products.add(item.get("product_id"))
                
                if other_products:
                    common = len(customer_products & other_products)
                    if common > 0:
                        customer_similarities[other_customer]["email"] = other_customer
                        customer_similarities[other_customer]["common_products"] += common
                        customer_similarities[other_customer]["total_products"] += len(other_products)
            
            # Calculer la similarité et trier
            for customer_data in customer_similarities.values():
                common = customer_data["common_products"]
                total_other = customer_data["total_products"]
                total_current = len(customer_products)
                
                # Coefficient de Jaccard
                similarity = common / (total_current + total_other - common)
                customer_data["similarity"] = similarity
                
                if similarity > 0.1:  # Seuil de similarité minimum
                    similar_customers.append(customer_data)
            
            # Retourner les 10 clients les plus similaires
            return sorted(similar_customers, key=lambda x: x["similarity"], reverse=True)[:10]
            
        except Exception as e:
            logger.error(f"Similar customers error: {e}")
            return []
    
    def _calculate_recency_weight(self, date: datetime) -> float:
        """Calculer le poids basé sur l'ancienneté"""
        if not date:
            return 0.5
        
        if isinstance(date, str):
            date = datetime.fromisoformat(date.replace('Z', '+00:00'))
        
        days_ago = (datetime.now() - date.replace(tzinfo=None)).days
        
        # Décroissance exponentielle
        return math.exp(-days_ago / 30.0)  # Demi-vie de 30 jours
    
    async def _get_fallback_recommendations(self, customer_type: str) -> List[Dict[str, Any]]:
        """Recommandations de base en cas d'erreur"""
        try:
            products = await self._get_products_data()
            
            # Filtrer par type de client et popularité
            filtered_products = [
                p for p in products
                if p.get("target_audience") in ["both", customer_type] and p.get("in_stock", True)
            ]
            
            # Trier par prix (produits premium en premier pour B2B, économiques pour B2C)
            if customer_type == "B2B":
                filtered_products.sort(key=lambda x: x.get("price", 0), reverse=True)
            else:
                filtered_products.sort(key=lambda x: x.get("price", 0))
            
            # Formatage des recommandations
            recommendations = []
            for product in filtered_products[:3]:
                recommendations.append({
                    "product": product,
                    "score": 0.5,
                    "reasons": ["Recommandé pour votre profil"],
                    "recommendation_type": "fallback",
                    "confidence": 0.5,
                    "timestamp": datetime.now().isoformat()
                })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Fallback recommendations error: {e}")
            return []
    
    # Méthodes de cache
    def _is_cached(self, key: str) -> bool:
        """Vérifier si une clé est en cache et valide"""
        if key not in self._cache:
            return False
        
        if key not in self._cache_ttl:
            return False
        
        return datetime.now() < self._cache_ttl[key]
    
    def _get_from_cache(self, key: str) -> Any:
        """Récupérer une valeur du cache"""
        return self._cache.get(key)
    
    def _cache_result(self, key: str, value: Any):
        """Mettre en cache un résultat"""
        self._cache[key] = value
        self._cache_ttl[key] = datetime.now() + timedelta(seconds=self._cache_duration)
        
        # Nettoyer le cache si trop gros
        if len(self._cache) > 1000:
            self._clean_cache()
    
    def _clean_cache(self):
        """Nettoyer le cache expiré"""
        now = datetime.now()
        expired_keys = [k for k, ttl in self._cache_ttl.items() if now > ttl]
        
        for key in expired_keys:
            self._cache.pop(key, None)
            self._cache_ttl.pop(key, None)

# Fonction utilitaire pour l'intégration
async def get_smart_recommendations(
    db: AsyncIOMotorDatabase,
    customer_id: Optional[str] = None,
    current_cart: List[Dict] = None,
    customer_type: str = "B2C",
    context: Dict = None
) -> List[Dict[str, Any]]:
    """
    Fonction utilitaire pour obtenir des recommandations
    
    Usage:
        recommendations = await get_smart_recommendations(
            db, 
            customer_id="user@example.com",
            current_cart=[{"id": "product1"}],
            customer_type="B2C"
        )
    """
    engine = ProductRecommendationEngine(db)
    return await engine.get_recommendations(customer_id, current_cart, customer_type, context)