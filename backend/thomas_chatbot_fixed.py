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
        
        # AMÉLIORATION THOMAS V2 : Liens cliquables et boutons CTA
        self.product_links = {
            "essentiel": "/produit/osmoseur-essentiel",
            "premium": "/produit/osmoseur-premium", 
            "prestige": "/produit/osmoseur-prestige",
            "filtre-douche": "/produit/filtre-douche"
        }
        
        self.cta_buttons = {
            "add_to_cart": "🛒 Ajouter au panier",
            "view_product": "👀 Voir le produit",
            "ask_question": "❓ Poser une question",
            "get_quote": "💰 Devis gratuit",
            "schedule_call": "📞 Rappel gratuit"
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
    
    def format_response_with_links_and_ctas(self, text: str, product_key: str = None, cta_actions: List[str] = None) -> Dict:
        """🚀 THOMAS V2 COMMERCIAL - Formatter réponse avec liens cliquables et données panier"""
        
        # Ajouter liens cliquables aux produits mentionnés
        formatted_text = text
        
        # Remplacer mentions produits par liens cliquables (éviter double remplacement)
        product_replacements = {
            "Osmoseur Essentiel": f'<a href="{self.product_links["essentiel"]}" class="product-link">Osmoseur Essentiel (449€)</a>',
            "Osmoseur Premium": f'<a href="{self.product_links["premium"]}" class="product-link">Osmoseur Premium (549€)</a>',
            "Osmoseur Prestige": f'<a href="{self.product_links["prestige"]}" class="product-link">Osmoseur Prestige (899€)</a>',
            "Filtre Douche": f'<a href="{self.product_links["filtre-douche"]}" class="product-link">Filtre Douche (39.90€)</a>',
            "l'Essentiel": f'l\'<a href="{self.product_links["essentiel"]}" class="product-link">Essentiel (449€)</a>',
            "le Premium": f'le <a href="{self.product_links["premium"]}" class="product-link">Premium (549€)</a>',
            "le Prestige": f'le <a href="{self.product_links["prestige"]}" class="product-link">Prestige (899€)</a>'
        }
        
        for mention, link in product_replacements.items():
            # Éviter double remplacement en vérifiant si déjà transformé
            if mention in formatted_text and '<a href=' not in formatted_text.replace(mention, ''):
                formatted_text = formatted_text.replace(mention, link, 1)  # Une seule occurrence
        
        # 🚀 NOUVEAUTÉ PHASE 8 - Données panier pour "Add to Cart" fonctionnel
        cart_data = None
        if product_key and product_key in self.osmoseurs_catalog:
            product_info = self.osmoseurs_catalog[product_key]
            
            # Mapping des clés internes vers IDs de base de données
            product_id_mapping = {
                "osmoseur-essentiel": "osmoseur-essentiel",
                "osmoseur-premium": "osmoseur-premium", 
                "osmoseur-prestige": "osmoseur-prestige",
                "filtre-douche": "purificateur-portable-hydrogene"  # Ajustement selon la base de données
            }
            
            cart_data = {
                "id": product_id_mapping.get(product_key, product_key),
                "name": product_info["name"],
                "price": product_info["price"],
                "image": "https://images.unsplash.com/photo-1628239532623-c035054bff4e?w=400&h=400&fit=crop&q=80",  # Image par défaut
                "quantity": 1
            }
        
        # Ajouter boutons CTA si spécifié
        if cta_actions:
            cta_html = "\n\n<div class='thomas-cta-buttons' style='margin-top: 15px;'>\n"
            for action in cta_actions:
                if action in self.cta_buttons:
                    if action == "add_to_cart" and product_key:
                        cta_html += f'  <button class="cta-button add-to-cart thomas-add-to-cart" data-product-id="{cart_data["id"] if cart_data else product_key}" style="margin: 5px; padding: 8px 15px; background: #10b981; color: white; border: none; border-radius: 5px; cursor: pointer; font-weight: 600;">{self.cta_buttons[action]}</button>\n'
                    elif action == "view_product" and product_key:
                        cta_html += f'  <a href="{self.product_links.get(product_key, "#")}" class="cta-button view-product" style="display: inline-block; margin: 5px; padding: 8px 15px; background: #059669; color: white; text-decoration: none; border-radius: 5px;">{self.cta_buttons[action]}</a>\n'
                    elif action == "ask_question":
                        cta_html += f'  <button class="cta-button ask-question" style="margin: 5px; padding: 8px 15px; background: #dc2626; color: white; border: none; border-radius: 5px; cursor: pointer;">{self.cta_buttons[action]}</button>\n'
                    else:
                        cta_html += f'  <button class="cta-button {action}" style="margin: 5px; padding: 8px 15px; background: #7c3aed; color: white; border: none; border-radius: 5px; cursor: pointer;">{self.cta_buttons[action]}</button>\n'
            cta_html += "</div>"
            formatted_text += cta_html
        
        # Retourner un dictionnaire avec le texte formaté et les données panier
        return {
            "formatted_text": formatted_text,
            "cart_data": cart_data,
            "product_recommended": product_key
        }

    def get_user_context_analysis(self, message: str, conversation_history: List = None) -> Dict:
        """🚀 THOMAS V2 - Analyser contexte utilisateur pour recommandations personnalisées"""
        
        analysis = {
            "family_size": None,
            "budget_range": None,
            "concerns": [],
            "previous_questions": [],
            "intent": "information"
        }
        
        message_lower = message.lower()
        
        # Analyser taille famille
        if any(word in message_lower for word in ["2", "couple", "deux"]):
            analysis["family_size"] = "2-3"
        elif any(word in message_lower for word in ["4", "quatre", "famille"]):
            analysis["family_size"] = "4-5"
        elif any(word in message_lower for word in ["5", "6", "grand", "nombreux"]):
            analysis["family_size"] = "5+"
        
        # Analyser budget
        if any(word in message_lower for word in ["budget", "cher", "prix", "coût"]):
            if any(word in message_lower for word in ["serré", "limité", "économique"]):
                analysis["budget_range"] = "budget_serre"
            elif any(word in message_lower for word in ["élevé", "premium", "haut"]):
                analysis["budget_range"] = "premium"
            else:
                analysis["budget_range"] = "moyen"
        
        # Analyser préoccupations
        if any(word in message_lower for word in ["santé", "enfant", "bébé"]):
            analysis["concerns"].append("health")
        if any(word in message_lower for word in ["goût", "odeur", "chlore"]):
            analysis["concerns"].append("taste")
        if any(word in message_lower for word in ["économie", "bouteille", "plastique"]):
            analysis["concerns"].append("economy")
        
        # Analyser intention
        if any(word in message_lower for word in ["acheter", "commander", "panier"]):
            analysis["intent"] = "purchase"
        elif any(word in message_lower for word in ["comparer", "différence"]):
            analysis["intent"] = "comparison"
        elif any(word in message_lower for word in ["hésite", "réfléchir"]):
            analysis["intent"] = "hesitation"
        
        return analysis
    
    def generate_response(self, user_message: str, user_context: Dict = None) -> Dict:
        """
        🚀 THOMAS V2 - Génère réponse avec liens cliquables et CTA fonctionnels
        """
        try:
            message_lower = user_message.lower()
            
            # Analyser contexte utilisateur pour personnalisation
            context_analysis = self.get_user_context_analysis(user_message, 
                user_context.get('conversation_history', []) if user_context else [])
            
            # ACCUEIL THOMAS V2 AMÉLIORÉ
            if any(word in message_lower for word in ["bonjour", "salut", "hello", "bonsoir", "coucou"]):
                formatted_response = self.format_response_with_links_and_ctas(
                    self.response_templates["accueil"],
                    cta_actions=["view_product", "ask_question"]
                )
                return {
                    "message": formatted_response["formatted_text"],
                    "suggestions": ["💰 Voir les prix", "🏠 Recommandation famille", "💧 Comment ça marche ?"],
                    "cart_data": formatted_response.get("cart_data"),
                    "type": "greeting"
                }
            
            # DEMANDE DE PRIX AVEC LIENS CLIQUABLES
            if any(word in message_lower for word in ["prix", "coût", "combien", "tarif", "budget"]):
                prix_message = f"""💰 **Nos prix osmoseurs Josmoze** :

🔹 **<a href="{self.product_links["essentiel"]}" class="product-link">Osmoseur Essentiel (449€)</a>**
   👨‍👩‍👧 Familles 2-3 personnes, efficace

🔸 **<a href="{self.product_links["premium"]}" class="product-link">Osmoseur Premium (549€)</a>** ⭐ *Le plus populaire*
   👨‍👩‍👧‍👦 Familles 4-5 personnes, technologie avancée

🔹 **<a href="{self.product_links["prestige"]}" class="product-link">Osmoseur Prestige (899€)</a>**
   🏢 Solution professionnelle, écran tactile

🚿 **<a href="{self.product_links["filtre-douche"]}" class="product-link">Filtre Douche (39.90€)</a>**
   ✨ Complément bien-être peau/cheveux

{self.response_templates["objection_prix"]}

{self.response_templates["call_to_action"][0]}"""
                
                formatted_response = self.format_response_with_links_and_ctas(
                    prix_message,
                    product_key="premium",  # Recommandation par défaut
                    cta_actions=["add_to_cart", "get_quote", "ask_question"]
                )
                
                return {
                    "message": formatted_response["formatted_text"],
                    "suggestions": ["🛒 Ajouter Premium au panier", "❓ Plus d'infos", "📞 Parler à un expert"],
                    "cart_data": formatted_response.get("cart_data"),
                    "type": "pricing"
                }
            
            # OBJECTION BUDGET - TON ULTRA BIENVEILLANT V2
            if any(word in message_lower for word in ["cher", "chère", "budget", "trop", "moins cher", "économique", "argent", "coûteux"]):
                return {
                    "message": f"""😊 **{self.response_templates["budget_serre"]}**

💡 **Laissez-moi vous expliquer pourquoi c'est un excellent investissement** :

🏠 **L'Essentiel à 449€** :
✅ Eau pure illimitée pour toute la famille  
✅ Fini les bouteilles plastique (économie 100€/mois)
✅ Santé de votre famille protégée
✅ Installation pro + garantie incluses
✅ **Rentabilisé en 4-5 mois seulement !**

💚 **Ma promesse** : Vous allez adorer avoir une eau pure directement au robinet, et votre portefeuille aussi !

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
            
            # RECOMMANDATION FAMILLE - PERSONNALISÉE SELON CONTEXTE
            if any(word in message_lower for word in ["famille", "personnes", "foyer", "combien de personnes", "quel osmoseur"]):
                
                # Recommandation intelligente selon contexte
                if context_analysis["family_size"] == "4-5" or any(word in message_lower for word in ["4", "quatre", "4-5", "4 personnes", "famille 4"]):
                    produit = self.osmoseurs_catalog["osmoseur-premium"]
                    product_key = "premium"
                    
                    response_text = f"""🎯 **Pour une famille de 4 personnes, je recommande le <a href="{self.product_links[product_key]}" class="product-link">{produit['name']} (549€)</a> !**

{produit['thomas_pitch']}

✅ **Pourquoi c'est parfait pour vous** :
• 4-5 personnes = consommation optimale
• 6 étapes + reminéralisation = eau parfaitement équilibrée  
• Réservoir 15L = débit suffisant
• Auto-rinçage = maintenance minimale

💰 **Prix** : {produit['price']}€ - Notre bestseller !

{self.response_templates["call_to_action"][2]}"""
                    
                    formatted_response = self.format_response_with_links_and_ctas(
                        response_text, 
                        product_key=product_key,
                        cta_actions=["add_to_cart", "view_product", "ask_question"]
                    )
                    
                    return {
                        "message": formatted_response,
                        "suggestions": ["🛒 Ajouter Premium 549€", "📋 Comparer modèles", "❓ Plus d'infos"]
                    }
                
                elif context_analysis["family_size"] == "2-3" or any(word in message_lower for word in ["2", "3", "deux", "trois", "couple", "petit"]):
                    produit = self.osmoseurs_catalog["osmoseur-essentiel"]
                    product_key = "essentiel"
                    
                    response_text = f"""🎯 **Pour 2-3 personnes, l'<a href="{self.product_links[product_key]}" class="product-link">{produit['name']} (449€)</a> est idéal !**

{produit['thomas_pitch']}

✅ **Parfait pour votre foyer** :
• 2-3 personnes = dimensionnement optimal
• 5 étapes de filtration = efficacité prouvée
• Installation professionnelle incluse
• Économique sans compromis qualité

{self.response_templates["call_to_action"][2]}"""
                    
                    formatted_response = self.format_response_with_links_and_ctas(
                        response_text,
                        product_key=product_key,
                        cta_actions=["add_to_cart", "view_product", "ask_question"]
                    )
                    
                    return {
                        "message": formatted_response,
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