#!/usr/bin/env python3
"""
🤖 THOMAS CHATBOT OSMOSEURS - VERSION DÉFINITIVE
===============================================
Agent commercial expert en osmoseurs Josmose.com
- Focus 100% osmoseurs et purification d'eau
- Ton bienveillant et commercial
- Connaissance parfaite du catalogue BlueMountain 2025
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class ThomasChatbot:
    def __init__(self):
        """Thomas - Conseiller Expert en Purification d'Eau chez Josmoze"""
        
        # NOUVEAU PROMPT THOMAS V2 PROFESSIONNEL
        self.thomas_identity = """
        IDENTITÉ :
        Tu es Thomas, conseiller expert en purification d'eau chez Josmoze. 
        Tu accueilles chaleureusement les visiteurs avec professionnalisme et bienveillance.

        PERSONNALITÉ :
        - Amical et rassurant
        - Expert technique mais accessible  
        - Pointe d'humour légère et appropriée
        - Toujours orienté solution

        MISSION :
        - Comprendre les besoins du prospect
        - Recommander le bon osmoseur
        - Accompagner vers l'achat
        - Rassurer sur la qualité/service
        """
        
        # BASE DE CONNAISSANCES OSMOSEURS JOSMOZE.COM V2
        self.osmoseurs_catalog = {
            "osmoseur-essentiel": {
                "name": "Osmoseur Essentiel",
                "price": 449.0,
                "description": "Familles 2-3 personnes, efficace",
                "ideal_for": "Familles 2-3 personnes, solution efficace et économique",
                "features": ["5 étapes de filtration", "Réservoir 12L", "Installation professionnelle"],
                "benefits": "Parfait pour débuter, rapport qualité-prix excellent",
                "thomas_pitch": "L'Essentiel à 449€ est parfait pour débuter ! Idéal pour les familles de 2-3 personnes."
            },
            "osmoseur-premium": {
                "name": "Osmoseur Premium", 
                "price": 549.0,
                "description": "Familles 4-5 personnes, technologie avancée",
                "ideal_for": "Familles 4-5 personnes, technologie avancée",
                "features": ["6 étapes + reminéralisation", "Réservoir 15L", "Robinet LED", "Auto-rinçage"],
                "benefits": "Notre bestseller ! Eau parfaitement équilibrée",
                "thomas_pitch": "Le Premium à 549€ est notre bestseller ! Parfait pour les familles de 4-5 personnes avec sa technologie avancée."
            },
            "osmoseur-prestige": {
                "name": "Osmoseur Prestige",
                "price": 899.0,
                "description": "Solution professionnelle, écran tactile",
                "ideal_for": "Solution professionnelle, grandes familles, écran tactile",
                "features": ["7 étapes + UV", "Double réservoir 20L", "Écran tactile", "App mobile"],
                "benefits": "Technologie de pointe, monitoring temps réel",
                "thomas_pitch": "Le Prestige à 899€ est notre solution professionnelle avec écran tactile. Pour ceux qui veulent le meilleur !"
            },
            "filtre-douche": {
                "name": "Filtre Douche",
                "price": 39.90,
                "description": "Complément bien-être peau/cheveux",
                "ideal_for": "Complément bien-être pour peau et cheveux",
                "features": ["Installation 2 minutes", "Cartouche 6-8 mois", "Anti-calcaire", "Universel"],
                "benefits": "Peau plus douce, cheveux plus brillants",
                "thomas_pitch": "Le Filtre Douche à 39.90€ est le complément parfait ! Peau plus douce et cheveux plus brillants."
            }
        }
        
        # RÉPONSES TYPES THOMAS V2
        self.response_templates = {
            "accueil": "Bonjour ! Je suis Thomas, votre conseiller Josmoze. Comment puis-je vous aider à trouver l'osmoseur parfait pour votre famille ? 😊",
            "budget_serre": "Je comprends, la qualité de l'eau n'a pas de prix mais le budget compte ! L'Essentiel à 449€ est parfait pour débuter.",
            "hesitation": "Pas de souci pour réfléchir ! Puis-je vous poser 2-3 questions pour mieux vous conseiller ?",
            "objection_prix": "C'est vrai que c'est un investissement, mais pensez aux économies sur l'eau en bouteille ! En 6 mois c'est rentabilisé.",
            "call_to_action": [
                "Voulez-vous que je vous aide à choisir ?",
                "Puis-je vous montrer notre questionnaire rapide ?",
                "Souhaitez-vous ajouter cet osmoseur à votre panier ?"
            ]
        }
        
        # AVANTAGES OSMOSE INVERSE
        self.osmosis_benefits = {
            "pureté": "Élimine 99% des contaminants : chlore, nitrates, pesticides, métaux lourds, bactéries",
            "santé": "Eau pure comme en montagne, sans goût ni odeur, idéale pour toute la famille",
            "économie": "Divise par 10 le coût de l'eau pure vs bouteilles plastique",
            "écologie": "Fini les bouteilles plastique, geste écologique majeur",
            "praticité": "Eau pure illimitée directement au robinet, 24h/24"
        }
        
        # PROCESSUS OSMOSE INVERSE SIMPLIFIÉ
        self.how_it_works = [
            "1️⃣ Pré-filtration : Élimine sédiments et chlore",
            "2️⃣ Membrane osmose : Filtre ultra-fin (0.0001 micron)",
            "3️⃣ Post-filtration : Affinage du goût",
            "4️⃣ Reminéralisation : Équilibre parfait (modèles Premium/Prestige)",
            "5️⃣ Stockage : Réservoir eau pure toujours disponible"
        ]
    
    def get_product_recommendation(self, budget: str = None, household_size: str = None, housing_type: str = None) -> Dict:
        """Recommande l'osmoseur idéal selon les critères"""
        
        # Logique de recommandation osmoseurs
        if budget == "700+" or household_size == "5+":
            return self.osmoseurs_catalog["osmoseur-prestige"]
        elif budget == "400-700" or household_size == "3-4" or housing_type == "maison":
            return self.osmoseurs_catalog["osmoseur-premium"]
        elif budget == "200-400" or household_size == "1-2" or housing_type == "appartement":
            return self.osmoseurs_catalog["osmoseur-essentiel"]
        else:
            # Par défaut Premium (le plus populaire)
            return self.osmoseurs_catalog["osmoseur-premium"]
    
    def generate_response(self, user_message: str, user_context: Dict = None) -> Dict:
        """
        Génère une réponse Thomas V2 avec nouveau prompt professionnel
        """
        try:
            message_lower = user_message.lower()
            
            # ACCUEIL THOMAS V2
            if any(word in message_lower for word in ["bonjour", "salut", "hello", "bonsoir", "coucou"]):
                return {
                    "message": self.response_templates["accueil"],
                    "suggestions": ["💰 Voir les prix", "🏠 Recommandation famille", "💧 Comment ça marche ?"]
                }
            
            # DEMANDE DE PRIX AVEC PRIX CORRECTS V2
            if any(word in message_lower for word in ["prix", "coût", "combien", "tarif", "budget"]):
                prix_message = f"""💰 **Nos prix osmoseurs Josmoze** :

🔹 **Osmoseur Essentiel** : **449€**
   👨‍👩‍👧 Familles 2-3 personnes, efficace

🔸 **Osmoseur Premium** : **549€** ⭐ *Le plus populaire*
   👨‍👩‍👧‍👦 Familles 4-5 personnes, technologie avancée

🔹 **Osmoseur Prestige** : **899€**
   🏢 Solution professionnelle, écran tactile

🚿 **Filtre Douche** : **39.90€**
   ✨ Complément bien-être peau/cheveux

{self.response_templates["objection_prix"]}

{self.response_templates["call_to_action"][0]}"""
                
                return {
                    "message": prix_message,
                    "suggestions": ["🛒 Ajouter au panier", "❓ Plus d'infos", "📞 Parler à un expert"]
                }
            
            # OBJECTION BUDGET - TON BIENVEILLANT V2
            if any(word in message_lower for word in ["cher", "chère", "budget", "trop", "moins cher", "économique"]):
                return {
                    "message": f"""{self.response_templates["budget_serre"]}

💡 **Pourquoi l'Essentiel à 449€** :
• ✅ Eau pure illimitée pour toute la famille
• 💰 Économies bouteilles = rentabilisé en 6 mois  
• 🏠 Parfait pour débuter sans compromis qualité
• 🔧 Installation professionnelle incluse

{self.response_templates["call_to_action"][1]}""",
                    "suggestions": ["📋 Questionnaire rapide", "🛒 Essentiel 449€", "💬 Autres questions"]
                }
            
            # HÉSITATION - ACCOMPAGNEMENT V2
            if any(word in message_lower for word in ["hésite", "réfléchir", "voir", "décider", "peut-être"]):
                return {
                    "message": f"""{self.response_templates["hesitation"]}

🎯 **Questions pour vous conseiller** :
1️⃣ Combien de personnes dans votre foyer ?
2️⃣ Quel est votre budget approximatif ?
3️⃣ Priorité : économique ou haut de gamme ?

Je trouve l'osmoseur parfait selon vos besoins ! 😊""",
                    "suggestions": ["👨‍👩‍👧 2-3 personnes", "👨‍👩‍👧‍👦 4-5 personnes", "💰 Budget serré"]
                }
            
            # RECOMMANDATION FAMILLE - LOGIQUE THOMAS V2
            if any(word in message_lower for word in ["famille", "personnes", "foyer", "combien de personnes", "quel osmoseur"]):
                # Logique de recommandation selon nombre de personnes
                if any(word in message_lower for word in ["4", "quatre", "4-5", "4 personnes", "famille 4"]):
                    produit = self.osmoseurs_catalog["osmoseur-premium"]
                    return {
                        "message": f"""🎯 **Pour une famille de 4 personnes, je recommande le {produit['name']} !**

{produit['thomas_pitch']}

✅ **Pourquoi c'est parfait pour vous** :
• 4-5 personnes = consommation optimale
• 6 étapes + reminéralisation = eau parfaitement équilibrée  
• Réservoir 15L = débit suffisant
• Auto-rinçage = maintenance minimale

💰 **Prix** : {produit['price']}€ - Notre bestseller !

{self.response_templates["call_to_action"][2]}""",
                        "suggestions": ["🛒 Ajouter Premium 549€", "📋 Comparer modèles", "❓ Plus d'infos"]
                    }
                elif any(word in message_lower for word in ["2", "3", "deux", "trois", "couple", "petit"]):
                    produit = self.osmoseurs_catalog["osmoseur-essentiel"]
                    return {
                        "message": f"""🎯 **Pour 2-3 personnes, l'{produit['name']} est idéal !**

{produit['thomas_pitch']}

✅ **Parfait pour votre foyer** :
• 2-3 personnes = dimensionnement optimal
• 5 étapes de filtration = efficacité prouvée
• Installation professionnelle incluse
• Économique sans compromis qualité

{self.response_templates["call_to_action"][2]}""",
                        "suggestions": ["🛒 Essentiel 449€", "⬆️ Voir Premium", "❓ Questions"]
                    }
                else:
                    # Réponse générale pour recommandation
                    return {
                        "message": f"""🏠 **Laissez-moi vous conseiller selon votre foyer !**

🎯 **Mes recommandations par famille** :
• **2-3 personnes** → Essentiel 449€ (efficace et économique)
• **4-5 personnes** → Premium 549€ ⭐ (notre bestseller !)
• **5+ personnes** → Prestige 899€ (solution professionnelle)

{self.response_templates["hesitation"]}""",
                        "suggestions": ["👨‍👩‍👧 2-3 personnes", "👨‍👩‍👧‍👦 4-5 personnes", "👥 5+ personnes"]
                    }
            if any(word in message_lower for word in ["essentiel", "premium", "prestige", "filtre douche"]):
                if "essentiel" in message_lower:
                    produit = self.osmoseurs_catalog["osmoseur-essentiel"]
                    return {
                        "message": f"""🔹 **{produit['name']} - {produit['price']}€**

{produit['thomas_pitch']}

✅ **Caractéristiques** :
{chr(10).join(f'• {feature}' for feature in produit['features'])}

🎯 **Idéal pour** : {produit['ideal_for']}

{self.response_templates["call_to_action"][2]}""",
                        "suggestions": ["🛒 Ajouter au panier", "📋 Comparer", "❓ Questions"]
                    }
                elif "premium" in message_lower:
                    produit = self.osmoseurs_catalog["osmoseur-premium"]
                    return {
                        "message": f"""🔸 **{produit['name']} - {produit['price']}€** ⭐

{produit['thomas_pitch']}

✅ **Caractéristiques** :
{chr(10).join(f'• {feature}' for feature in produit['features'])}

🎯 **Idéal pour** : {produit['ideal_for']}

{self.response_templates["call_to_action"][2]}""",
                        "suggestions": ["🛒 Ajouter au panier", "📋 Comparer", "❓ Questions"]
                    }
                elif "prestige" in message_lower:
                    produit = self.osmoseurs_catalog["osmoseur-prestige"] 
                    return {
                        "message": f"""🔹 **{produit['name']} - {produit['price']}€**

{produit['thomas_pitch']}

✅ **Caractéristiques** :
{chr(10).join(f'• {feature}' for feature in produit['features'])}

🎯 **Idéal pour** : {produit['ideal_for']}

{self.response_templates["call_to_action"][2]}""",
                        "suggestions": ["🛒 Ajouter au panier", "📋 Comparer", "❓ Questions"]
                    }
                elif "filtre" in message_lower and "douche" in message_lower:
                    produit = self.osmoseurs_catalog["filtre-douche"]
                    return {
                        "message": f"""🚿 **{produit['name']} - {produit['price']}€**

{produit['thomas_pitch']}

✅ **Avantages** :
{chr(10).join(f'• {feature}' for feature in produit['features'])}

🎯 **Parfait pour** : {produit['ideal_for']}

Installation en 2 minutes, résultats immédiats ! ✨""",
                        "suggestions": ["🛒 Ajouter 39.90€", "💧 + Osmoseur", "❓ Installation"]
                    }
            
            # RÉPONSE GÉNÉRALE THOMAS V2 - EXPERTISE ACCESSIBLE
            return {
                "message": f"""Thomas ici ! 😊 Expert en purification d'eau chez Josmoze.

🎯 **Ma mission** : Vous aider à choisir l'osmoseur parfait !

💧 **Notre gamme 2025** :
• **Essentiel 449€** : Familles 2-3 pers.
• **Premium 549€** : Familles 4-5 pers. ⭐
• **Prestige 899€** : Solution professionnelle  
• **Filtre Douche 39.90€** : Bien-être quotidien

{self.response_templates["call_to_action"][0]}""",
                "suggestions": ["💰 Voir les prix", "📋 Questionnaire", "💬 Poser une question"]
            }
            
        except Exception as e:
            logger.error(f"Erreur génération réponse Thomas: {str(e)}")
            # Fallback avec nouveau prompt V2
            return {
                "message": self.response_templates["accueil"],
                "suggestions": ["💰 Voir les prix", "🏠 Recommandation", "❓ Questions"]
            }

# Instance globale Thomas Osmoseurs
thomas_osmoseurs = ThomasChatbot()

def get_thomas_response(message: str, user_context: Dict = None) -> Dict:
    """Interface pour Thomas Expert Osmoseurs"""
    return thomas_osmoseurs.generate_response(message, user_context)