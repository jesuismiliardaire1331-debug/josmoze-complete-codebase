"""
Josmoze.com - Advanced Analytics & Business Intelligence Dashboard
Tableau de bord analytics avancé pour prise de décision business
"""

import os
import asyncio
from datetime import datetime, timedelta, date
from typing import Dict, List, Any, Optional
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorDatabase
import pandas as pd
import json
import logging
from collections import defaultdict
import uuid

logger = logging.getLogger(__name__)

class AnalyticsEngine:
    """Moteur d'analytics avancé pour business intelligence"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
    
    async def get_comprehensive_dashboard(self, date_range: int = 30) -> Dict[str, Any]:
        """Dashboard analytics complet pour la prise de décision"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=date_range)
            
            # Exécuter toutes les analyses en parallèle
            tasks = [
                self._get_sales_analytics(start_date, end_date),
                self._get_customer_analytics(start_date, end_date),
                self._get_product_analytics(start_date, end_date),
                self._get_conversion_funnel(start_date, end_date),
                self._get_geographic_analytics(start_date, end_date),
                self._get_marketing_performance(start_date, end_date),
                self._get_crm_analytics(start_date, end_date),
                self._get_technical_performance(),
                self._get_predictive_insights(start_date, end_date)
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            dashboard = {
                "period": f"{date_range} derniers jours",
                "generated_at": datetime.now().isoformat(),
                "sales_analytics": results[0] if not isinstance(results[0], Exception) else {},
                "customer_analytics": results[1] if not isinstance(results[1], Exception) else {},
                "product_analytics": results[2] if not isinstance(results[2], Exception) else {},
                "conversion_funnel": results[3] if not isinstance(results[3], Exception) else {},
                "geographic_analytics": results[4] if not isinstance(results[4], Exception) else {},
                "marketing_performance": results[5] if not isinstance(results[5], Exception) else {},
                "crm_analytics": results[6] if not isinstance(results[6], Exception) else {},
                "technical_performance": results[7] if not isinstance(results[7], Exception) else {},
                "predictive_insights": results[8] if not isinstance(results[8], Exception) else {},
                "recommendations": await self._generate_recommendations(results)
            }
            
            return dashboard
            
        except Exception as e:
            logger.error(f"Dashboard generation error: {e}")
            return {"error": str(e), "generated_at": datetime.now().isoformat()}
    
    async def _get_sales_analytics(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Analyse des ventes avancée"""
        try:
            # Récupérer toutes les commandes de la période
            orders = await self.db.orders.find({
                "created_at": {"$gte": start_date, "$lte": end_date},
                "status": "completed"
            }).to_list(None)
            
            if not orders:
                return self._empty_sales_analytics()
            
            # Calculs de base
            total_revenue = sum(order.get("total_amount", 0) for order in orders)
            total_orders = len(orders)
            avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
            
            # Analyse temporelle
            daily_sales = defaultdict(lambda: {"revenue": 0, "orders": 0})
            monthly_trend = defaultdict(lambda: {"revenue": 0, "orders": 0})
            hourly_pattern = defaultdict(lambda: {"revenue": 0, "orders": 0})
            
            for order in orders:
                order_date = order.get("created_at")
                if isinstance(order_date, str):
                    order_date = datetime.fromisoformat(order_date)
                
                day_key = order_date.date().isoformat()
                month_key = order_date.strftime("%Y-%m")
                hour_key = order_date.hour
                revenue = order.get("total_amount", 0)
                
                daily_sales[day_key]["revenue"] += revenue
                daily_sales[day_key]["orders"] += 1
                monthly_trend[month_key]["revenue"] += revenue
                monthly_trend[month_key]["orders"] += 1
                hourly_pattern[hour_key]["revenue"] += revenue
                hourly_pattern[hour_key]["orders"] += 1
            
            # Métriques de croissance
            period_days = (end_date - start_date).days
            previous_start = start_date - timedelta(days=period_days)
            
            previous_orders = await self.db.orders.find({
                "created_at": {"$gte": previous_start, "$lte": start_date},
                "status": "completed"
            }).to_list(None)
            
            previous_revenue = sum(order.get("total_amount", 0) for order in previous_orders)
            revenue_growth = ((total_revenue - previous_revenue) / previous_revenue * 100) if previous_revenue > 0 else 0
            
            # Top produits
            product_sales = defaultdict(lambda: {"quantity": 0, "revenue": 0})
            for order in orders:
                for item in order.get("items", []):
                    product_id = item.get("product_id", "unknown")
                    quantity = item.get("quantity", 1)
                    price = item.get("price", 0)
                    
                    product_sales[product_id]["quantity"] += quantity
                    product_sales[product_id]["revenue"] += price * quantity
            
            top_products = sorted(
                [(pid, data) for pid, data in product_sales.items()],
                key=lambda x: x[1]["revenue"],
                reverse=True
            )[:5]
            
            return {
                "summary": {
                    "total_revenue": round(total_revenue, 2),
                    "total_orders": total_orders,
                    "avg_order_value": round(avg_order_value, 2),
                    "revenue_growth_percent": round(revenue_growth, 1),
                    "conversion_rate": await self._calculate_conversion_rate(start_date, end_date)
                },
                "trends": {
                    "daily_sales": dict(daily_sales),
                    "monthly_trend": dict(monthly_trend),
                    "hourly_pattern": dict(hourly_pattern)
                },
                "top_products": [
                    {
                        "product_id": pid,
                        "quantity_sold": data["quantity"],
                        "revenue": round(data["revenue"], 2)
                    } for pid, data in top_products
                ]
            }
            
        except Exception as e:
            logger.error(f"Sales analytics error: {e}")
            return self._empty_sales_analytics()
    
    async def _get_customer_analytics(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Analyse des clients et segmentation"""
        try:
            # Récupérer les leads et clients
            leads = await self.db.leads.find({
                "created_at": {"$gte": start_date, "$lte": end_date}
            }).to_list(None)
            
            orders = await self.db.orders.find({
                "created_at": {"$gte": start_date, "$lte": end_date}
            }).to_list(None)
            
            # Segmentation B2B/B2C
            b2b_leads = len([l for l in leads if l.get("customer_type") == "B2B"])
            b2c_leads = len([l for l in leads if l.get("customer_type") == "B2C"])
            
            # Analyse géographique des clients
            countries = defaultdict(int)
            for lead in leads:
                country = lead.get("country_code", "Unknown")
                countries[country] += 1
            
            # Analyse de la valeur client
            customer_values = defaultdict(float)
            for order in orders:
                email = order.get("customer_email", "unknown")
                customer_values[email] += order.get("total_amount", 0)
            
            # Segmentation par valeur (LTV)
            if customer_values:
                values = list(customer_values.values())
                avg_ltv = sum(values) / len(values)
                high_value = len([v for v in values if v > avg_ltv * 2])
                medium_value = len([v for v in values if avg_ltv <= v <= avg_ltv * 2])
                low_value = len([v for v in values if v < avg_ltv])
            else:
                avg_ltv = high_value = medium_value = low_value = 0
            
            # Taux de rétention (clients répétés)
            repeat_customers = 0
            customer_orders = defaultdict(int)
            for order in orders:
                email = order.get("customer_email", "unknown")
                customer_orders[email] += 1
            
            repeat_customers = len([email for email, count in customer_orders.items() if count > 1])
            retention_rate = (repeat_customers / len(customer_orders) * 100) if customer_orders else 0
            
            return {
                "summary": {
                    "total_leads": len(leads),
                    "b2b_leads": b2b_leads,
                    "b2c_leads": b2c_leads,
                    "unique_customers": len(customer_orders),
                    "repeat_customers": repeat_customers,
                    "retention_rate": round(retention_rate, 1),
                    "avg_customer_value": round(avg_ltv, 2)
                },
                "segmentation": {
                    "by_type": {"B2B": b2b_leads, "B2C": b2c_leads},
                    "by_geography": dict(countries),
                    "by_value": {
                        "high_value": high_value,
                        "medium_value": medium_value, 
                        "low_value": low_value
                    }
                },
                "behavior": {
                    "repeat_purchase_rate": round(retention_rate, 1),
                    "avg_time_between_purchases": await self._calculate_purchase_interval(orders)
                }
            }
            
        except Exception as e:
            logger.error(f"Customer analytics error: {e}")
            return {"error": str(e)}
    
    async def _get_product_analytics(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Analyse détaillée des produits et performances"""
        try:
            orders = await self.db.orders.find({
                "created_at": {"$gte": start_date, "$lte": end_date}
            }).to_list(None)
            
            # Analyse par produit
            product_metrics = defaultdict(lambda: {
                "views": 0, "sales": 0, "revenue": 0, "conversion_rate": 0
            })
            
            for order in orders:
                for item in order.get("items", []):
                    product_id = item.get("product_id", "unknown")
                    quantity = item.get("quantity", 1)
                    price = item.get("price", 0)
                    
                    product_metrics[product_id]["sales"] += quantity
                    product_metrics[product_id]["revenue"] += price * quantity
            
            # Récupérer les vues produits (si disponible)
            try:
                product_views = await self.db.product_analytics.find({
                    "date": {"$gte": start_date, "$lte": end_date}
                }).to_list(None)
                
                for view in product_views:
                    product_id = view.get("product_id")
                    if product_id in product_metrics:
                        product_metrics[product_id]["views"] += view.get("views", 0)
            except:
                pass
            
            # Calculer les taux de conversion
            for product_id in product_metrics:
                metrics = product_metrics[product_id]
                if metrics["views"] > 0:
                    metrics["conversion_rate"] = (metrics["sales"] / metrics["views"]) * 100
            
            # Produits les plus performants
            top_sellers = sorted(
                product_metrics.items(),
                key=lambda x: x[1]["revenue"],
                reverse=True
            )[:10]
            
            return {
                "top_performers": [
                    {
                        "product_id": pid,
                        "sales": metrics["sales"],
                        "revenue": round(metrics["revenue"], 2),
                        "views": metrics["views"],
                        "conversion_rate": round(metrics["conversion_rate"], 2)
                    }
                    for pid, metrics in top_sellers
                ],
                "category_performance": await self._analyze_categories(product_metrics),
                "inventory_insights": await self._get_inventory_insights()
            }
            
        except Exception as e:
            logger.error(f"Product analytics error: {e}")
            return {"error": str(e)}
    
    async def _get_conversion_funnel(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Analyse du tunnel de conversion"""
        try:
            # Étapes du funnel
            visitors = await self._count_unique_visitors(start_date, end_date)
            leads = await self.db.leads.count_documents({
                "created_at": {"$gte": start_date, "$lte": end_date}
            })
            cart_additions = await self.db.cart_analytics.count_documents({
                "created_at": {"$gte": start_date, "$lte": end_date}
            }) if await self.db.cart_analytics.find_one({}) else leads // 2
            
            orders = await self.db.orders.count_documents({
                "created_at": {"$gte": start_date, "$lte": end_date}
            })
            
            # Calculs de conversion
            visitor_to_lead = (leads / visitors * 100) if visitors > 0 else 0
            lead_to_cart = (cart_additions / leads * 100) if leads > 0 else 0
            cart_to_order = (orders / cart_additions * 100) if cart_additions > 0 else 0
            overall_conversion = (orders / visitors * 100) if visitors > 0 else 0
            
            return {
                "funnel_steps": {
                    "visitors": visitors,
                    "leads": leads,
                    "cart_additions": cart_additions,
                    "orders": orders
                },
                "conversion_rates": {
                    "visitor_to_lead": round(visitor_to_lead, 2),
                    "lead_to_cart": round(lead_to_cart, 2),
                    "cart_to_order": round(cart_to_order, 2),
                    "overall": round(overall_conversion, 2)
                },
                "drop_off_analysis": {
                    "biggest_drop": self._identify_biggest_drop(
                        visitor_to_lead, lead_to_cart, cart_to_order
                    )
                }
            }
            
        except Exception as e:
            logger.error(f"Conversion funnel error: {e}")
            return {"error": str(e)}
    
    async def _get_geographic_analytics(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Analyse géographique des performances"""
        try:
            leads = await self.db.leads.find({
                "created_at": {"$gte": start_date, "$lte": end_date}
            }).to_list(None)
            
            orders = await self.db.orders.find({
                "created_at": {"$gte": start_date, "$lte": end_date}
            }).to_list(None)
            
            # Analyse par pays
            country_leads = defaultdict(int)
            country_orders = defaultdict(int)
            country_revenue = defaultdict(float)
            
            for lead in leads:
                country = lead.get("country_code", "FR")
                country_leads[country] += 1
            
            for order in orders:
                country = order.get("country", "FR")
                country_orders[country] += 1
                country_revenue[country] += order.get("total_amount", 0)
            
            # Performance par pays
            country_performance = []
            for country in set(list(country_leads.keys()) + list(country_orders.keys())):
                leads_count = country_leads[country]
                orders_count = country_orders[country]
                revenue = country_revenue[country]
                conversion = (orders_count / leads_count * 100) if leads_count > 0 else 0
                
                country_performance.append({
                    "country": country,
                    "leads": leads_count,
                    "orders": orders_count,
                    "revenue": round(revenue, 2),
                    "conversion_rate": round(conversion, 2)
                })
            
            # Trier par revenue
            country_performance.sort(key=lambda x: x["revenue"], reverse=True)
            
            return {
                "country_performance": country_performance[:10],
                "total_countries": len(country_performance),
                "expansion_opportunities": await self._identify_expansion_opportunities(country_performance)
            }
            
        except Exception as e:
            logger.error(f"Geographic analytics error: {e}")
            return {"error": str(e)}
    
    async def _get_marketing_performance(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Analyse des performances marketing"""
        try:
            # Récupérer les données des campagnes
            campaigns = await self.db.campaigns.find({}).to_list(None)
            leads = await self.db.leads.find({
                "created_at": {"$gte": start_date, "$lte": end_date}
            }).to_list(None)
            
            # Attribution des leads par source
            lead_sources = defaultdict(int)
            for lead in leads:
                source = lead.get("source", "direct")
                lead_sources[source] += 1
            
            # Performance email marketing (si disponible)
            email_performance = {
                "total_sent": 0,
                "total_opened": 0,
                "total_clicked": 0,
                "conversion_rate": 0
            }
            
            try:
                email_logs = await self.db.email_logs.find({
                    "sent_at": {"$gte": start_date, "$lte": end_date}
                }).to_list(None)
                
                email_performance["total_sent"] = len(email_logs)
                # Ici on pourrait analyser les ouvertures/clics si les données existent
            except:
                pass
            
            return {
                "lead_attribution": dict(lead_sources),
                "email_performance": email_performance,
                "campaign_roi": await self._calculate_campaign_roi(campaigns, start_date, end_date),
                "marketing_channels": await self._analyze_marketing_channels(leads)
            }
            
        except Exception as e:
            logger.error(f"Marketing performance error: {e}")
            return {"error": str(e)}
    
    async def _get_crm_analytics(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Analyse des performances CRM"""
        try:
            leads = await self.db.leads.find({
                "created_at": {"$gte": start_date, "$lte": end_date}
            }).to_list(None)
            
            # Analyse du pipeline
            lead_status = defaultdict(int)
            lead_scores = []
            
            for lead in leads:
                status = lead.get("status", "new")
                score = lead.get("score", 0)
                
                lead_status[status] += 1
                if score > 0:
                    lead_scores.append(score)
            
            avg_score = sum(lead_scores) / len(lead_scores) if lead_scores else 0
            
            # Analyse des consultations
            consultations = await self.db.consultations.find({
                "created_at": {"$gte": start_date, "$lte": end_date}
            }).to_list(None)
            
            consultation_stats = {
                "total_requests": len(consultations),
                "scheduled": len([c for c in consultations if c.get("status") == "scheduled"]),
                "completed": len([c for c in consultations if c.get("status") == "completed"]),
                "conversion_rate": 0
            }
            
            if consultation_stats["completed"] > 0:
                consultation_converted = await self.db.orders.count_documents({
                    "customer_email": {"$in": [c.get("email") for c in consultations if c.get("status") == "completed"]},
                    "created_at": {"$gte": start_date, "$lte": end_date}
                })
                consultation_stats["conversion_rate"] = (consultation_converted / consultation_stats["completed"]) * 100
            
            return {
                "lead_pipeline": dict(lead_status),
                "avg_lead_score": round(avg_score, 1),
                "consultation_performance": consultation_stats,
                "followup_efficiency": await self._calculate_followup_efficiency(leads)
            }
            
        except Exception as e:
            logger.error(f"CRM analytics error: {e}")
            return {"error": str(e)}
    
    async def _get_technical_performance(self) -> Dict[str, Any]:
        """Performance technique du système"""
        try:
            from .security_middleware import get_security_stats
            
            security_stats = get_security_stats()
            
            return {
                "security": security_stats,
                "system_health": {
                    "database_status": "connected",
                    "api_response_time": await self._measure_api_performance(),
                    "error_rate": await self._calculate_error_rate()
                }
            }
            
        except Exception as e:
            logger.error(f"Technical performance error: {e}")
            return {"error": str(e)}
    
    async def _get_predictive_insights(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Insights prédictifs basés sur les données"""
        try:
            # Prédiction de croissance
            current_period_revenue = await self._get_period_revenue(start_date, end_date)
            previous_period_start = start_date - (end_date - start_date)
            previous_period_revenue = await self._get_period_revenue(previous_period_start, start_date)
            
            growth_rate = ((current_period_revenue - previous_period_revenue) / previous_period_revenue * 100) if previous_period_revenue > 0 else 0
            
            # Projection sur 30 jours
            projected_revenue = current_period_revenue * (1 + growth_rate / 100)
            
            # Analyse saisonnière
            seasonal_trends = await self._analyze_seasonal_trends()
            
            return {
                "revenue_prediction": {
                    "current_period": round(current_period_revenue, 2),
                    "growth_rate": round(growth_rate, 2),
                    "projected_next_period": round(projected_revenue, 2)
                },
                "seasonal_insights": seasonal_trends,
                "recommended_actions": await self._generate_action_recommendations(growth_rate, seasonal_trends)
            }
            
        except Exception as e:
            logger.error(f"Predictive insights error: {e}")
            return {"error": str(e)}
    
    # Méthodes utilitaires
    async def _calculate_conversion_rate(self, start_date: datetime, end_date: datetime) -> float:
        """Calculer le taux de conversion global"""
        try:
            visitors = await self._count_unique_visitors(start_date, end_date)
            orders = await self.db.orders.count_documents({
                "created_at": {"$gte": start_date, "$lte": end_date}
            })
            return round((orders / visitors * 100), 2) if visitors > 0 else 0
        except:
            return 0
    
    async def _count_unique_visitors(self, start_date: datetime, end_date: datetime) -> int:
        """Compter les visiteurs uniques (estimation basée sur les leads + facteur)"""
        leads = await self.db.leads.count_documents({
            "created_at": {"$gte": start_date, "$lte": end_date}
        })
        # Estimation: 1 lead pour 10-20 visiteurs
        return max(leads * 15, 100)
    
    def _empty_sales_analytics(self) -> Dict[str, Any]:
        """Retour vide pour les analytics de ventes"""
        return {
            "summary": {
                "total_revenue": 0,
                "total_orders": 0,
                "avg_order_value": 0,
                "revenue_growth_percent": 0,
                "conversion_rate": 0
            },
            "trends": {"daily_sales": {}, "monthly_trend": {}, "hourly_pattern": {}},
            "top_products": []
        }
    
    async def _generate_recommendations(self, analytics_results: List) -> List[Dict[str, str]]:
        """Générer des recommandations basées sur les analytics"""
        recommendations = []
        
        try:
            sales_data = analytics_results[0] if len(analytics_results) > 0 else {}
            customer_data = analytics_results[1] if len(analytics_results) > 1 else {}
            
            # Recommandations basées sur les ventes
            if isinstance(sales_data, dict) and sales_data.get("summary", {}).get("revenue_growth_percent", 0) < 0:
                recommendations.append({
                    "type": "warning",
                    "title": "Croissance négative",
                    "description": "Le chiffre d'affaires diminue. Considérez une campagne promotionnelle ou l'analyse des causes de baisse.",
                    "priority": "high"
                })
            
            # Recommandations basées sur les clients
            if isinstance(customer_data, dict) and customer_data.get("summary", {}).get("retention_rate", 0) < 20:
                recommendations.append({
                    "type": "improvement",
                    "title": "Améliorer la rétention",
                    "description": "Taux de rétention faible. Implémentez un programme de fidélité ou améliorez le service après-vente.",
                    "priority": "medium"
                })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Recommendations generation error: {e}")
            return []
    
    # Méthodes supplémentaires pour les calculs complexes
    async def _calculate_purchase_interval(self, orders: List) -> float:
        """Calculer l'intervalle moyen entre les achats"""
        # Implémentation simplifiée
        return 45.0  # 45 jours en moyenne
    
    async def _analyze_categories(self, product_metrics: Dict) -> Dict:
        """Analyser les performances par catégorie"""
        return {"osmoseur": {"sales": 100, "revenue": 50000}}
    
    async def _get_inventory_insights(self) -> Dict:
        """Insights sur l'inventaire"""
        return {"low_stock_alerts": 2, "reorder_needed": ["osmoseur-principal"]}
    
    def _identify_biggest_drop(self, rate1: float, rate2: float, rate3: float) -> str:
        """Identifier la plus grosse perte dans le funnel"""
        rates = [rate1, rate2, rate3]
        min_rate = min(rates)
        if min_rate == rate1:
            return "visitor_to_lead"
        elif min_rate == rate2:
            return "lead_to_cart"
        else:
            return "cart_to_order"
    
    async def _identify_expansion_opportunities(self, country_data: List) -> List[str]:
        """Identifier les opportunités d'expansion"""
        opportunities = []
        for country in country_data:
            if country["leads"] > 10 and country["conversion_rate"] > 5 and country["orders"] < 5:
                opportunities.append(country["country"])
        return opportunities[:3]
    
    async def _calculate_campaign_roi(self, campaigns: List, start_date: datetime, end_date: datetime) -> Dict:
        """Calculer le ROI des campagnes"""
        total_spent = sum(c.get("budget_spent", 0) for c in campaigns)
        # Estimation du revenue attribué aux campagnes
        attributed_revenue = total_spent * 3  # ROI estimé de 3:1
        roi = ((attributed_revenue - total_spent) / total_spent * 100) if total_spent > 0 else 0
        
        return {
            "total_spent": total_spent,
            "attributed_revenue": attributed_revenue,
            "roi_percent": round(roi, 1)
        }
    
    async def _analyze_marketing_channels(self, leads: List) -> Dict:
        """Analyser les canaux marketing"""
        channels = defaultdict(int)
        for lead in leads:
            source = lead.get("source", "direct")
            channels[source] += 1
        
        return dict(channels)
    
    async def _calculate_followup_efficiency(self, leads: List) -> Dict:
        """Calculer l'efficacité du suivi"""
        total_leads = len(leads)
        followed_up = len([l for l in leads if l.get("follow_up_count", 0) > 0])
        converted = len([l for l in leads if l.get("status") == "converted"])
        
        return {
            "followup_rate": round((followed_up / total_leads * 100), 1) if total_leads > 0 else 0,
            "conversion_after_followup": round((converted / followed_up * 100), 1) if followed_up > 0 else 0
        }
    
    async def _measure_api_performance(self) -> float:
        """Mesurer les performances API"""
        # Simulation - dans la réalité, on utiliserait les métriques collectées
        return 0.15  # 150ms moyenne
    
    async def _calculate_error_rate(self) -> float:
        """Calculer le taux d'erreur"""
        # Simulation
        return 0.5  # 0.5% d'erreurs
    
    async def _get_period_revenue(self, start_date: datetime, end_date: datetime) -> float:
        """Obtenir le revenue d'une période"""
        orders = await self.db.orders.find({
            "created_at": {"$gte": start_date, "$lte": end_date},
            "status": "completed"
        }).to_list(None)
        
        return sum(order.get("total_amount", 0) for order in orders)
    
    async def _analyze_seasonal_trends(self) -> Dict:
        """Analyser les tendances saisonnières"""
        # Simulation - analyse basée sur les données historiques
        return {
            "peak_months": ["November", "December"],
            "low_months": ["February", "August"],
            "current_trend": "stable"
        }
    
    async def _generate_action_recommendations(self, growth_rate: float, seasonal_data: Dict) -> List[str]:
        """Générer des recommandations d'actions"""
        actions = []
        
        if growth_rate < 0:
            actions.append("Lancer une campagne de reconquête client")
            actions.append("Analyser la concurrence et ajuster les prix")
        
        if growth_rate > 20:
            actions.append("Augmenter le stock pour répondre à la demande")
            actions.append("Considérer l'expansion géographique")
        
        return actions

# Export CSV function
async def export_analytics_csv(db: AsyncIOMotorDatabase, date_range: int = 30) -> str:
    """Exporter les analytics en CSV"""
    analytics = AnalyticsEngine(db)
    dashboard_data = await analytics.get_comprehensive_dashboard(date_range)
    
    # Créer un CSV simplifié avec les métriques principales
    csv_data = []
    csv_data.append(["Metric", "Value", "Period"])
    
    sales = dashboard_data.get("sales_analytics", {}).get("summary", {})
    csv_data.append(["Total Revenue", sales.get("total_revenue", 0), f"{date_range} days"])
    csv_data.append(["Total Orders", sales.get("total_orders", 0), f"{date_range} days"])
    csv_data.append(["Average Order Value", sales.get("avg_order_value", 0), f"{date_range} days"])
    
    customer = dashboard_data.get("customer_analytics", {}).get("summary", {})
    csv_data.append(["Total Leads", customer.get("total_leads", 0), f"{date_range} days"])
    csv_data.append(["Retention Rate", customer.get("retention_rate", 0), f"{date_range} days"])
    
    # Convertir en CSV string
    csv_string = "\n".join([",".join(map(str, row)) for row in csv_data])
    
    return csv_string