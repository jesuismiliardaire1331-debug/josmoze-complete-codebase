#!/usr/bin/env python3
"""
🤖 THOMAS CHATBOT - AGENT COMMERCIAL BIENVEILLANT V3.0
====================================================
Agent conversationnel optimisé pour Josmose.com avec:
- Ton bienveillant et commercial (pas agressif)
- Connaissance complète des nouveaux produits BlueMountain
- Redirection vers questionnaire
- Aide au choix produit personnalisée
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class ThomasChatbot:
    def __init__(self):
        """Initialise Thomas avec la base des connaissances actualisée"""
        self.context = []
        self.user_preferences = {}
        
        # BASE DE CONNAISSANCES NOUVEAUX PRODUITS JOSMOSE.COM 2025
        self.knowledge = {
            "products": {
                "osmoseur-essentiel": {
                    "name": "Osmoseur Essentiel - BlueMountain Compact",
                    "price": 449.0,
                    "description": "Solution économique parfaite pour les petits foyers. Filtration 5 étapes, réservoir 12L.",
                    "ideal_for": "1-2 personnes, appartements, budgets 200-400€",
                    "features": ["5 étapes filtration", "Réservoir 12L", "Robinet inox", "Installation facile"]
                },
                "osmoseur-premium": {
                    "name": "Osmoseur Premium - BlueMountain Avancé", 
                    "price": 549.0,
                    "description": "Notre bestseller! Filtration 6 étapes + reminéralisation. Idéal familles 3-4 personnes.",
                    "ideal_for": "3-4 personnes, maisons, budgets 400-700€",
                    "features": ["6 étapes + reminéralisation", "Réservoir 15L", "Robinet LED", "Auto-rinçage"]
                },
                "osmoseur-prestige": {
                    "name": "Osmoseur Prestige - BlueMountain De Comptoir",
                    "price": 899.0,
                    "description": "Le haut de gamme! 7 étapes + UV + reminéralisation avec écran tactile.",
                    "ideal_for": "5+ personnes, maisons, budgets 700€+",
                    "features": ["7 étapes + UV", "Double réservoir 20L", "Écran tactile", "App mobile"]
                },
                "fontaine-animaux": {
                    "name": "Fontaine à Eau pour Animaux AquaPet Premium",
                    "price": 49.0,
                    "description": "Fontaine intelligente pour chiens et chats avec filtration avancée.",
                    "features": ["Filtration intégrée", "Débit ajustable", "Capteur niveau", "Design moderne"]
                },
                "purificateur-portable": {
                    "name": "Purificateur Portable à Hydrogène H2 Pro",
                    "price": 79.0,
                    "description": "Purificateur nomade qui enrichit l'eau en hydrogène antioxydant.",
                    "features": ["Technologie H2", "Batterie longue durée", "Léger et portable", "Anti-oxydant"]
                }
            },
            "benefits": {
                "health": "99.9% des contaminants éliminés (nitrates, pesticides, chlore, métaux lourds)",
                "taste": "Eau pure au goût neutre, plus de goût de chlore ou d'odeurs",
                "economy": "Jusqu'à 80% d'économies vs eau en bouteille",
                "ecology": "Fini les bouteilles plastiques, 1 osmoseur = 10 000 bouteilles évitées/an"
            },
            "guarantees": {
                "warranty": "Garantie 2 à 5 ans selon modèle",
                "installation": "Installation professionnelle gratuite",
                "support": "Support technique 7j/7",
                "satisfaction": "Satisfait ou remboursé 30 jours"
            }
        }
        
        # QUESTIONS QUESTIONNAIRE
        self.questionnaire_questions = [
            "Combien de personnes dans votre foyer ?",
            "Type de logement ?", 
            "Niveau de bricolage ?",
            "Budget approximatif ?"
        ]
    
    def get_product_recommendation(self, budget: str = None, household_size: str = None) -> Dict:
        """Recommande un produit basé sur les critères"""
        
        # Logique de recommandation
        if budget == "700+":
            return self.knowledge["products"]["osmoseur-prestige"]
        elif budget == "400-700" or household_size == "3-4":
            return self.knowledge["products"]["osmoseur-premium"]
        elif budget == "200-400" or household_size == "1-2":
            return self.knowledge["products"]["osmoseur-essentiel"]
        else:
            # Par défaut, recommander le Premium
            return self.knowledge["products"]["osmoseur-premium"]
    
    def generate_response(self, user_message: str, user_context: Dict = None) -> Dict:
        """
        Génère une réponse bienveillante et commerciale de Thomas
        """
        try:
            user_message_lower = user_message.lower()
            
            # Salutation initiale
            if any(word in user_message_lower for word in ["bonjour", "salut", "hello", "bonsoir"]):
                return {
                    "message": "Bonjour ! 👋 Je suis Thomas, votre conseiller eau pure chez Josmose.com.\n\nJe suis là pour vous aider à choisir l'osmoseur parfait pour votre foyer ! 💧\n\n✨ **Nos nouveaux osmoseurs BlueMountain** sont arrivés avec des technologies révolutionnaires.\n\nPour vous conseiller au mieux, préférez-vous :\n🎯 **Faire notre questionnaire personnalisé** (2 minutes)\n📦 **Voir directement nos produits**\n❓ **Me poser une question spécifique**",
                    "suggestions": ["🎯 Questionnaire personnalisé", "📦 Voir les produits", "❓ Question spécifique"],
                    "type": "greeting"
                }
            
            # Questionnaire
            if any(word in user_message_lower for word in ["questionnaire", "personnalisé", "conseiller", "recommandation"]):
                return {
                    "message": "Parfait ! 🎯 Notre questionnaire personnalisé va identifier l'osmoseur idéal pour vous.\n\n**4 questions simples :**\n1️⃣ Combien de personnes dans votre foyer ?\n2️⃣ Type de logement ?\n3️⃣ Niveau de bricolage ?\n4️⃣ Budget approximatif ?\n\n➡️ **Cliquez sur le bouton 'Trouvez votre osmoseur' sur la page pour commencer !**",
                    "suggestions": ["🔍 Autres questions", "📦 Voir tous les produits"],
                    "type": "questionnaire_redirect"
                }
            
            # Questions sur produits spécifiques
            if any(word in user_message_lower for word in ["produits", "osmoseur", "prix", "comparaison"]):
                return {
                    "message": "Excellente question ! 😊 Voici notre nouvelle gamme **BlueMountain 2025** :\n\n💧 **Essentiel Compact** - 449€\n• 1-2 personnes, appartements\n• 5 étapes, réservoir 12L\n• Économique et efficace\n\n🌟 **Premium Avancé** - 549€ ⭐ *Le plus populaire*\n• 3-4 personnes, maisons\n• 6 étapes + reminéralisation\n• Notre bestseller!\n\n👑 **Prestige De Comptoir** - 899€\n• 5+ personnes, haut de gamme\n• 7 étapes + UV + écran tactile\n• Technologie premium\n\nQuel type de foyer avez-vous ? Je peux vous conseiller plus précisément ! 🏠",
                    "suggestions": ["🎯 Questionnaire personnalisé", "❓ Quelle différence entre les modèles ?", "💰 Garanties et services"],
                    "type": "product_info"
                }
            
            # Questions sur les bénéfices
            if any(word in user_message_lower for word in ["pourquoi", "bénéfices", "avantages", "santé", "qualité"]):
                return {
                    "message": "Excellente question ! 🌟 Un osmoseur Josmose vous apporte :\n\n🏥 **Pour votre santé :**\n• 99.9% des contaminants éliminés\n• Fini nitrates, pesticides, chlore\n• Eau pure comme en montagne\n\n💰 **Pour votre budget :**\n• Jusqu'à 80% d'économie vs bouteilles\n• 1 osmoseur = 10 ans d'eau pure\n• Retour sur investissement en 8 mois\n\n🌍 **Pour la planète :**\n• Plus de bouteilles plastiques\n• 1 osmoseur = 10 000 bouteilles évitées/an\n• Geste écologique majeur\n\nVoulez-vous que je vous aide à choisir le modèle idéal ? 😊",
                    "suggestions": ["🎯 Oui, conseille-moi !", "💧 Plus d'infos techniques", "📞 Parler à un expert"],
                    "type": "benefits"
                }
            
            # Questions techniques
            if any(word in user_message_lower for word in ["installation", "technique", "comment", "marche", "étapes"]):
                return {
                    "message": "C'est un point important ! 🔧 Chez Josmose, tout est prévu :\n\n✅ **Installation professionnelle GRATUITE**\n• Technicien certifié se déplace\n• Installation sous évier en 2h\n• Test et mise en service inclus\n\n📋 **Maintenance simplifiée :**\n• Changement filtres 1 fois/an\n• Cartouches livrées à domicile\n• Guide illustré fourni\n\n🛡️ **Garanties complètes :**\n• 2 à 5 ans selon modèle\n• Support technique 7j/7\n• Satisfait ou remboursé 30 jours\n\nPas de stress, on s'occupe de tout ! 😊\n\nQuel modèle vous intéresse ?",
                    "suggestions": ["🎯 Conseille-moi un modèle", "📦 Voir tous les produits", "📞 Appeler un technicien"],
                    "type": "technical"
                }
            
            # Prix et budget
            if any(word in user_message_lower for word in ["prix", "coût", "budget", "combien", "cher"]):
                return {
                    "message": "Parlons budget ! 💰 Nos osmoseurs sont un investissement rentable :\n\n🏷️ **Nos prix 2025 :**\n• **Essentiel** : 449€ (parfait 1-2 pers.)\n• **Premium** : 549€ (idéal familles)\n• **Prestige** : 899€ (haut de gamme)\n\n💡 **Rentabilité garantie :**\n• Famille 4 pers. : 150€/mois bouteilles ➜ **STOP !**\n• Avec osmoseur : 15€/mois (filtres)\n• **Économie : 135€/mois = 1620€/an**\n\n🎁 **Inclus :**\n• Installation gratuite\n• Garantie longue durée\n• Support technique illimité\n\nQuel est votre budget approximatif ? Je vous guide ! 😊",
                    "suggestions": ["💰 200-400€", "💰 400-700€", "💰 700€+"],
                    "type": "pricing"
                }
            
            # Budget spécifique - réponses ciblées
            if "200-400" in user_message or "400-700" in user_message or "700+" in user_message:
                if "200-400" in user_message:
                    product = self.knowledge["products"]["osmoseur-essentiel"]
                    return {
                        "message": f"Parfait ! 🎯 Pour votre budget, je recommande l'**{product['name']}** à **{product['price']}€**\n\n✨ **Pourquoi c'est le bon choix :**\n• {product['description']}\n• Idéal pour {product['ideal_for']}\n• Tout inclus : installation + garantie 2 ans\n\n💧 **Vous obtenez :**\n• Eau pure 99.9% des contaminants éliminés\n• Économie immédiate sur les bouteilles\n• Installation professionnelle gratuite\n\nVoulez-vous voir cette fiche produit complète ? 📋",
                        "suggestions": ["📋 Voir la fiche produit", "🎯 Questionnaire complet", "📞 Parler à un conseiller"],
                        "type": "recommendation"
                    }
                elif "400-700" in user_message:
                    product = self.knowledge["products"]["osmoseur-premium"]
                    return {
                        "message": f"Excellent choix ! 🌟 Pour votre budget, l'**{product['name']}** à **{product['price']}€** est PARFAIT !\n\n⭐ **Notre bestseller car :**\n• {product['description']}\n• Idéal pour {product['ideal_for']}\n• Reminéralisation = eau équilibrée\n• Installation + garantie 3 ans incluses\n\n🏆 **Le plus populaire car :**\n• Rapport qualité-prix exceptionnel\n• Technologie avancée accessible\n• Satisfait 95% de nos clients\n\nJe vous montre sa fiche détaillée ? 📋",
                        "suggestions": ["📋 Voir la fiche produit", "🔍 Comparer avec d'autres", "✅ Commander maintenant"],
                        "type": "recommendation"
                    }
                else:  # 700€+
                    product = self.knowledge["products"]["osmoseur-prestige"]
                    return {
                        "message": f"Magnifique ! 👑 Pour un budget premium, l'**{product['name']}** à **{product['price']}€** est exceptionnel !\n\n✨ **Le top de la technologie :**\n• {product['description']}\n• Idéal pour {product['ideal_for']}\n• Écran tactile + app mobile\n• Garantie 5 ans premium\n\n🚀 **Fonctionnalités uniques :**\n• Monitoring qualité temps réel\n• Nettoyage automatique\n• Service maintenance inclus\n• Technologie connectée\n\nVoulez-vous découvrir toutes ses capacités ? 📋",
                        "suggestions": ["📋 Voir la fiche complète", "📱 Démo app mobile", "📞 Consultation expert"],
                        "type": "recommendation"
                    }
            
            # Contact/rendez-vous
            if any(word in user_message_lower for word in ["contact", "appeler", "téléphone", "rendez-vous", "conseiller"]):
                return {
                    "message": "Bien sûr ! 📞 Nos experts sont là pour vous :\n\n🕒 **Disponibilité :**\n• Lundi-Vendredi : 9h-18h\n• Support technique : 7j/7\n• Conseils gratuits et sans engagement\n\n📞 **Plusieurs options :**\n• **Cliquez sur 'Contact'** dans le menu\n• **Consultation vidéo** disponible\n• **Visite technicien gratuite** pour devis\n\nNos conseillers connaissent parfaitement chaque produit et votre région. Ils vous guideront vers le choix optimal ! 😊\n\nUne préférence pour le contact ?",
                    "suggestions": ["📞 Appel téléphonique", "💻 Consultation vidéo", "🏠 Visite à domicile"],
                    "type": "contact"
                }
            
            # Message par défaut - bienveillant
            return {
                "message": "Je comprends votre question ! 😊 \n\nJe suis Thomas, votre conseiller spécialisé en osmoseurs Josmose. Je peux vous aider avec :\n\n🎯 **Choisir votre osmoseur idéal**\n📋 **Comparer nos modèles BlueMountain**\n💰 **Calculer vos économies**\n🔧 **Infos installation et garanties**\n📞 **Vous mettre en contact avec un expert**\n\nQue puis-je faire pour vous aujourd'hui ? N'hésitez pas à être précis, je suis là pour vous guider ! 💧",
                "suggestions": ["🎯 Questionnaire personnalisé", "📦 Voir les produits", "💰 Calculer mes économies"],
                "type": "help"
            }
            
        except Exception as e:
            logger.error(f"Erreur génération réponse Thomas: {e}")
            return {
                "message": "Désolé, j'ai eu un petit problème technique ! 😅\n\nMais je suis toujours là pour vous aider à choisir votre osmoseur idéal.\n\nPour commencer, vous préférez :\n🎯 Faire notre questionnaire personnalisé\n📦 Voir nos produits BlueMountain\n📞 Parler directement à un conseiller",
                "suggestions": ["🎯 Questionnaire", "📦 Produits", "📞 Conseiller"],
                "type": "error"
            }

# Instance globale
thomas_chatbot = ThomasChatbot()

def get_thomas_response(message: str, user_context: Dict = None) -> Dict:
    """Interface principale pour obtenir une réponse de Thomas"""
    return thomas_chatbot.generate_response(message, user_context)