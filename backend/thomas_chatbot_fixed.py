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
        """Thomas - Expert Osmoseurs Josmose.com"""
        
        # BASE DE CONNAISSANCES OSMOSEURS JOSMOSE.COM
        self.osmoseurs_catalog = {
            "osmoseur-essentiel": {
                "name": "Osmoseur Essentiel - BlueMountain Compact",
                "price": 449.0,
                "description": "Osmoseur économique 5 étapes pour petits foyers. Élimine 99% des contaminants.",
                "ideal_for": "1-2 personnes, appartements, budget serré",
                "features": ["5 étapes de filtration", "Réservoir 12L", "Robinet inox", "Installation simple"],
                "benefits": "Eau pure à petit prix, parfait pour débuter"
            },
            "osmoseur-premium": {
                "name": "Osmoseur Premium - BlueMountain Avancé", 
                "price": 549.0,
                "description": "Notre bestseller ! Osmoseur 6 étapes + reminéralisation pour familles.",
                "ideal_for": "3-4 personnes, maisons, meilleur rapport qualité-prix",
                "features": ["6 étapes + reminéralisation", "Réservoir 15L", "Robinet LED", "Auto-rinçage"],
                "benefits": "Le plus populaire, eau parfaitement équilibrée"
            },
            "osmoseur-prestige": {
                "name": "Osmoseur Prestige - BlueMountain De Comptoir",
                "price": 899.0,
                "description": "Osmoseur haut de gamme 7 étapes + UV avec écran tactile.",
                "ideal_for": "5+ personnes, technologie premium, budget confortable",
                "features": ["7 étapes + UV", "Double réservoir 20L", "Écran tactile", "App mobile"],
                "benefits": "Technologie de pointe, monitoring temps réel"
            }
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
        Génère une réponse expert en osmoseurs
        """
        try:
            message_lower = user_message.lower()
            
            # Salutation
            if any(word in message_lower for word in ["bonjour", "salut", "hello", "bonsoir", "coucou"]):
                return {
                    "message": "Bonjour ! 👋 Je suis Thomas, votre expert osmoseurs chez Josmose.com.\n\n💧 **Spécialiste en purification d'eau par osmose inverse**\n\nJe vous aide à choisir l'osmoseur parfait pour avoir une eau pure illimitée chez vous !\n\n🎯 **Notre gamme BlueMountain 2025** :\n• **Essentiel** 449€ (1-2 pers.)\n• **Premium** 549€ (3-4 pers.) ⭐ *Le plus populaire*\n• **Prestige** 899€ (5+ pers.)\n\nComment puis-je vous conseiller ? 😊",
                    "suggestions": ["💧 Comment ça marche ?", "💰 Lequel pour mon budget ?", "🏠 Lequel pour ma famille ?"],
                    "type": "greeting"
                }
            
            # Fonctionnement osmose inverse
            if any(word in message_lower for word in ["marche", "fonctionne", "comment", "principe", "osmose"]):
                steps = "\n".join(self.how_it_works)
                return {
                    "message": f"Excellente question ! 🔬 **L'osmose inverse expliquée simplement** :\n\n{steps}\n\n💡 **Résultat** : Eau 99% pure, sans chlore, sans nitrates, sans pesticides !\n\nC'est la même technologie que les stations spatiales. Votre eau du robinet devient plus pure que l'eau en bouteille ! 🚀\n\nQuel aspect vous intéresse le plus ?",
                    "suggestions": ["💰 Prix des osmoseurs", "🏠 Lequel choisir ?", "🔧 Installation facile ?"],
                    "type": "explanation"
                }
            
            # Prix et budget
            if any(word in message_lower for word in ["prix", "coût", "budget", "combien", "tarif"]):
                return {
                    "message": "💰 **Nos osmoseurs BlueMountain 2025** - Prix tout inclus :\n\n🥉 **Essentiel Compact** - **449€**\n• 1-2 personnes, appartements\n• 5 étapes, réservoir 12L\n• Installation + garantie 2 ans\n\n🥈 **Premium Avancé** - **549€** ⭐\n• 3-4 personnes, maisons\n• 6 étapes + reminéralisation\n• Notre bestseller ! Installation + garantie 3 ans\n\n🥇 **Prestige De Comptoir** - **899€**\n• 5+ personnes, haut de gamme\n• 7 étapes + UV + écran tactile\n• Installation + garantie 5 ans\n\n💡 **Rentabilité** : Famille 4 pers. économise 1500€/an vs bouteilles !\n\nQuel budget avez-vous en tête ?",
                    "suggestions": ["💰 200-400€", "💰 400-700€", "💰 700€+"],
                    "type": "pricing"
                }
            
            # Recommandations par budget
            if "200-400" in user_message or "400-700" in user_message or "700+" in user_message:
                if "200-400" in user_message:
                    product = self.osmoseurs_catalog["osmoseur-essentiel"]
                    return {
                        "message": f"🎯 **Pour votre budget, je recommande l'{product['name']}** !\n\n✨ **Pourquoi c'est parfait** :\n• Prix : **{product['price']}€** tout inclus\n• {product['description']}\n• Idéal pour {product['ideal_for']}\n\n🔧 **Vous obtenez** :\n• Installation professionnelle gratuite\n• Garantie 2 ans complète\n• Eau pure illimitée immédiatement\n• Économie dès le 1er mois vs bouteilles\n\nVoulez-vous voir sa fiche technique complète ?",
                        "suggestions": ["📋 Fiche technique", "🔧 Comment ça marche ?", "📞 Parler à un expert"],
                        "type": "recommendation"
                    }
                elif "400-700" in user_message:
                    product = self.osmoseurs_catalog["osmoseur-premium"]
                    return {
                        "message": f"🌟 **Excellent choix ! L'{product['name']}** est PARFAIT !\n\n⭐ **Pourquoi c'est notre bestseller** :\n• Prix : **{product['price']}€** tout inclus\n• {product['description']}\n• Idéal pour {product['ideal_for']}\n\n🏆 **Avantages exclusifs** :\n• Reminéralisation = eau parfaitement équilibrée\n• Robinet LED indicateur de qualité\n• Auto-rinçage automatique\n• 95% de nos clients le choisissent !\n\nJe vous montre pourquoi il cartonne ?",
                        "suggestions": ["📋 Pourquoi si populaire ?", "🔧 Installation incluse ?", "✅ Je le veux !"],
                        "type": "recommendation"
                    }
                else:  # 700€+
                    product = self.osmoseurs_catalog["osmoseur-prestige"]
                    return {
                        "message": f"👑 **Pour un budget premium, l'{product['name']}** est exceptionnel !\n\n🚀 **Le top de la technologie osmoseurs** :\n• Prix : **{product['price']}€** tout inclus\n• {product['description']}\n• Idéal pour {product['ideal_for']}\n\n✨ **Technologie unique** :\n• Écran tactile avec monitoring temps réel\n• App mobile pour contrôle à distance\n• UV stérilisation supplémentaire\n• Service maintenance premium 5 ans\n\nC'est l'osmoseur du futur ! Intéressé ?",
                        "suggestions": ["📱 Voir app mobile", "🏆 Toutes les fonctions", "📞 Consultation expert"],
                        "type": "recommendation"
                    }
            
            # Avantages et bénéfices
            if any(word in message_lower for word in ["avantage", "bénéfice", "pourquoi", "intérêt", "santé"]):
                return {
                    "message": "🌟 **Pourquoi choisir un osmoseur Josmose ?**\n\n🏥 **Pour votre santé** :\n• 99% des contaminants éliminés\n• Fini chlore, nitrates, pesticides, métaux lourds\n• Eau pure comme en montagne\n\n💰 **Pour votre porte-monnaie** :\n• Famille 4 pers : 150€/mois bouteilles → 15€/mois osmoseur\n• Économie : 1620€/an !\n• Retour sur investissement en 4-6 mois\n\n🌍 **Pour la planète** :\n• Plus de bouteilles plastique\n• 1 osmoseur = 10 000 bouteilles évitées/an\n• Empreinte carbone divisée par 100\n\n🚰 **Pour le confort** :\n• Eau pure illimitée 24h/24\n• Direct au robinet, toujours fraîche\n• Plus de courses bouteilles lourdes\n\nQuel aspect vous motive le plus ?",
                    "suggestions": ["💰 Calculer mes économies", "🏠 Lequel choisir ?", "🔧 Installation facile ?"],
                    "type": "benefits"
                }
            
            # Installation
            if any(word in message_lower for word in ["installation", "installer", "pose", "technique"]):
                return {
                    "message": "🔧 **Installation osmoseur - Simple et rapide !**\n\n✅ **Service inclus gratuit** :\n• Technicien expert se déplace chez vous\n• Installation complète en 2h maximum\n• Sous évier, raccordement eau froide\n• Tests et mise en service immédiate\n\n📋 **Étapes installation** :\n1️⃣ Perçage évier pour robinet dédié\n2️⃣ Raccordement arrivée d'eau\n3️⃣ Installation système + réservoir\n4️⃣ Tests complets + formation\n\n🛡️ **Garanties** :\n• 2 à 5 ans selon modèle\n• Maintenance annuelle simple\n• Support technique 7j/7\n• Satisfait ou remboursé 30 jours\n\nAucun stress, on gère tout ! Des questions sur l'installation ?",
                    "suggestions": ["🏠 Convient à mon logement ?", "💰 Voir les prix", "📞 Prendre RDV"],
                    "type": "installation"
                }
            
            # Contact
            if any(word in message_lower for word in ["contact", "téléphone", "appeler", "rdv", "expert"]):
                return {
                    "message": "📞 **Parfait ! Nos experts osmoseurs vous attendent :**\n\n🕒 **Disponibilité** :\n• Lundi-Vendredi : 9h-18h\n• Conseils gratuits et sans engagement\n• Devis personnalisé immédiat\n\n💬 **Plusieurs options** :\n• **Formulaire contact** sur le site\n• **Consultation vidéo** pour voir les produits\n• **Visite technique gratuite** pour devis sur-mesure\n\nNos conseillers sont des vrais experts osmoseurs. Ils connaissent chaque produit par cœur et sauront vous orienter selon votre situation exacte ! 😊\n\nComment préférez-vous être contacté ?",
                    "suggestions": ["📞 Appel téléphonique", "💻 Consultation vidéo", "🏠 Visite gratuite"],
                    "type": "contact"
                }
            
            # Questions famille/logement
            if any(word in message_lower for word in ["famille", "personnes", "maison", "appartement", "logement"]):
                return {
                    "message": "🏠 **Choisir selon votre foyer** :\n\n👥 **1-2 personnes** (appartement) :\n➜ **Essentiel 449€** - Compact et économique\n\n👨‍👩‍👧 **3-4 personnes** (maison) :\n➜ **Premium 549€** - Notre bestseller ! ⭐\n\n👨‍👩‍👧‍👦 **5+ personnes** (grande maison) :\n➜ **Prestige 899€** - Capacité maximale\n\n💡 **Conseil d'expert** : Le Premium convient à 90% des foyers français. Réservoir 15L, reminéralisation, auto-rinçage... C'est le sweet spot qualité-prix !\n\nCombien êtes-vous à la maison ?",
                    "suggestions": ["👥 1-2 personnes", "👨‍👩‍👧 3-4 personnes", "👨‍👩‍👧‍👦 5+ personnes"],
                    "type": "family_sizing"
                }
            
            # Message par défaut - expert osmoseurs
            return {
                "message": "🤔 Bonne question ! Je suis Thomas, **expert osmoseurs** chez Josmose.com 💧\n\n**Je peux vous aider avec** :\n🎯 Choisir l'osmoseur parfait pour votre foyer\n💰 Calculer vos économies vs bouteilles\n🔧 Tout savoir sur l'installation gratuite\n🏥 Comprendre les bénéfices santé\n📞 Vous mettre en contact avec un expert\n\n**Notre spécialité** : Transformer votre eau du robinet en eau plus pure que les bouteilles, directement chez vous !\n\nQue voulez-vous savoir sur nos osmoseurs ?",
                "suggestions": ["💧 Comment ça marche ?", "💰 Voir les prix", "🏠 Lequel choisir ?"],
                "type": "help"
            }
            
        except Exception as e:
            logger.error(f"Erreur Thomas osmoseurs: {e}")
            return {
                "message": "Désolé pour ce petit bug ! 😅\n\nJe suis Thomas, votre expert osmoseurs Josmose.com.\n\n💧 **Je peux vous aider à** :\n🎯 Choisir votre osmoseur idéal\n💰 Calculer vos économies\n🔧 Tout savoir sur l'installation\n\nQue souhaitez-vous savoir sur nos osmoseurs BlueMountain ?",
                "suggestions": ["💧 Comment ça marche ?", "💰 Prix osmoseurs", "📞 Expert au téléphone"],
                "type": "error"
            }

# Instance globale Thomas Osmoseurs
thomas_osmoseurs = ThomasChatbot()

def get_thomas_response(message: str, user_context: Dict = None) -> Dict:
    """Interface pour Thomas Expert Osmoseurs"""
    return thomas_osmoseurs.generate_response(message, user_context)