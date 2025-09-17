#!/usr/bin/env python3
"""
🤖 SYSTÈME CONVERSATIONNEL OSMOSE V2.0 - ENRICHI CONTENU MARKETING
=================================================================
Agents IA ultra-performants avec nouveau contenu validé
- Expertise approfondie sur nitrates, pesticides, chlore
- Intégration articles blog optimisés
- Connaissance nouveaux produits (fontaine animaux, sac transport, distributeur)
- Stratégies commerciales renforcées
"""

import openai
from openai import OpenAI
from twilio.rest import Client
import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import asyncio

# Configuration
client = OpenAI(api_key="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")
TWILIO_ACCOUNT_SID = "AC5d37fc46401a27a84540203820d680ca"
TWILIO_AUTH_TOKEN = "ead5696cac732121a4f448942845517c"
TWILIO_PHONE_NUMBER = "+16592518805"
JOSMOSE_WEBSITE = "https://josmoze.com"

# BASE DE CONNAISSANCES ENRICHIE V2.0
KNOWLEDGE_BASE_V2 = {
    "dangers_eau": {
        "nitrates": {
            "origine": "Agriculture intensive (78% des cas), élevages industriels (15%), eaux usées urbaines (7%)",
            "dangers": "Empêchent le sang de transporter l'oxygène chez les bébés (syndrome du bébé bleu), +18% risque cancer colorectal adultes",
            "zones_critiques": "Bretagne 68% communes, Champagne-Ardenne 52%, Beauce 45%",
            "chiffres_choc": "142 cas syndrome bébé bleu recensés depuis 2020",
            "elimination_josmoze": "98,5% d'élimination garantie"
        },
        "pesticides": {
            "prevalence": "5,7 pesticides différents par verre en moyenne, 200+ molécules détectées, 68% points de contrôle contaminés",
            "top_dangers": "Glyphosate 65% (Roundup), Atrazine 78% (interdit mais persistant), Métolachlore 52%",
            "effet_cocktail": "Personne ne sait ce qui se passe quand ces molécules se mélangent dans l'organisme",
            "zones_pires": "Champagne-Ardenne 82%, Centre-Val Loire 79%, Hauts-de-France 76%",
            "elimination_josmoze": "99,2% des 200+ molécules éliminées"
        },
        "chlore": {
            "paradoxe": "Nécessaire pour désinfecter mais crée sous-produits cancérigènes (trihalométhanes)",
            "impact_sante": "Détruit flore intestinale (-23% diversité en 6 mois), troubles digestifs, affaiblissement immunitaire",
            "sous_produits": "Trihalométhanes présents 45% réseaux, classés potentiellement cancérigènes",
            "elimination_josmoze": "99,8% suppression chlore + sous-produits"
        }
    },
    
    "solutions_comparees": {
        "carafe_filtrante": {
            "avantages": "Simple, améliore goût chlore, prix achat 30-50€",
            "inconvenients": "Inefficace nitrates/pesticides, 180€/an filtres, nid à bactéries si mal entretenue",
            "verdict": "Solution de confort, pas de santé"
        },
        "filtre_robinet": {
            "avantages": "Filtre chlore + certains pesticides, plus pratique que carafe",
            "inconvenients": "N'élimine ni nitrates, ni virus, ni métaux lourds, efficacité diminue vite",
            "verdict": "Insuffisant pour protection familiale complète"
        },
        "osmose_inverse": {
            "avantages": "99,9% élimination TOUT, goût parfait, économique long terme (0,12€/L), écologique",
            "principe": "Membrane ultra-fine 0,0001 micron, barrière physique infranchissable",
            "verdict": "Seule solution complète sans compromis"
        }
    },
    
    "nouveaux_produits": {
        "fontaine_animaux": {
            "prix": "49€",
            "description": "Fontaine eau pure pour animaux avec système filtration avancé",
            "avantages": "Même technologie que nos osmoseurs, matériaux premium, garantie 2 ans"
        },
        "sac_transport": {
            "prix": "29€", 
            "description": "Sac transport premium pour animaux avec mini-purificateur d'air intégré",
            "avantages": "Ventilation optimisée, filtres anti-odeurs, compatible IATA"
        },
        "distributeur_nourriture": {
            "prix": "39€",
            "description": "Distributeur nourriture intelligent avec intégration mini-fontaine",
            "avantages": "Application dédiée, système conservation hermétique, compatible IoT"
        }
    },
    
    "offres_commerciales": {
        "pack_famille": {
            "prix_normal": "1290€",
            "prix_promo": "890€",
            "reduction": "31%",
            "bonus": "1 produit animal offert au choix",
            "inclus": "Osmoseur 7 étapes, installation pro, analyse gratuite, formation, filtres 1ère année, app IoT, garantie 5 ans"
        },
        "financement": {
            "mensualite": "37€/mois sur 24 mois",
            "taux": "0%",
            "comparaison": "Moins cher que l'eau en bouteille (40€/mois famille)"
        },
        "economies": {
            "vs_bouteille_5ans": "4800€ économisés",
            "roi": "8 mois d'amortissement", 
            "ecologie": "15000 bouteilles évitées/an"
        }
    },
    
    "arguments_vente": {
        "sante": "Élimine 99,9% contaminants (nitrates, pesticides, chlore, métaux, virus, bactéries)",
        "economie": "ROI 500% sur 10 ans, coût réel 0,12€/L vs 0,25€/L bouteille",
        "ecologie": "Zéro déchet plastique, -87% empreinte carbone vs eau embouteillée",
        "simplicite": "Robinet dédié, réservoir 12L, maintenance 1 visite/an",
        "garanties": "30j satisfait/remboursé, garantie 5 ans totale, installation garantie"
    },
    
    "temoignages_clients": {
        "sophie_lille": "2 ans avec Josmoze. Mes enfants n'ont plus de problèmes digestifs. Je recommande !",
        "dr_claire_nice": "En tant que médecin, je salue cette qualité de filtration. Mes patients vont mieux.",
        "michel_bordeaux": "Installation parfaite, équipe pro. L'économie sur l'eau en bouteille est impressionnante."
    }
}

class ConversationalAgentV2:
    def __init__(self, name: str, role: str, personality: str):
        self.name = name
        self.role = role 
        self.personality = personality
        self.twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        self.conversation_memory = {}
        self.knowledge_base = KNOWLEDGE_BASE_V2
        
    def get_conversation_context(self, client_phone: str) -> str:
        """Récupère le contexte de conversation précédent"""
        if client_phone in self.conversation_memory:
            history = self.conversation_memory[client_phone]
            context = "Historique conversation:\n"
            for msg in history[-5:]:
                timestamp = msg.get('timestamp', 'Inconnu')
                sender = msg.get('sender', 'Inconnu')
                text = msg.get('text', '')
                context += f"[{timestamp}] {sender}: {text}\n"
            return context
        return "Première conversation avec ce client."
    
    def save_message(self, client_phone: str, sender: str, message: str):
        """Sauvegarde un message dans l'historique"""
        if client_phone not in self.conversation_memory:
            self.conversation_memory[client_phone] = []
        
        self.conversation_memory[client_phone].append({
            'timestamp': datetime.now().strftime("%H:%M:%S"),
            'sender': sender,
            'text': message
        })
        
        if len(self.conversation_memory[client_phone]) > 20:
            self.conversation_memory[client_phone] = self.conversation_memory[client_phone][-20:]
    
    def detect_specific_topics(self, message: str) -> List[str]:
        """Détecte les sujets spécifiques dans le message pour réponses ultra-ciblées"""
        message_lower = message.lower()
        detected_topics = []
        
        # Détection dangers spécifiques
        if any(word in message_lower for word in ["nitrate", "bébé", "nourrisson", "enfant", "cancer"]):
            detected_topics.append("nitrates_danger")
        
        if any(word in message_lower for word in ["pesticide", "glyphosate", "roundup", "agricole", "chimique"]):
            detected_topics.append("pesticides_danger")
            
        if any(word in message_lower for word in ["chlore", "javel", "goût", "odeur", "microbiote", "intestin"]):
            detected_topics.append("chlore_danger")
        
        # Détection solutions
        if any(word in message_lower for word in ["carafe", "brita", "filtre", "alternative"]):
            detected_topics.append("solutions_alternatives")
            
        if any(word in message_lower for word in ["bouteille", "plastique", "evian", "contrex"]):
            detected_topics.append("eau_bouteille")
        
        # Détection objections prix
        if any(word in message_lower for word in ["cher", "coût", "budget", "économie", "rentable"]):
            detected_topics.append("objection_prix")
        
        # Détection intérêt animaux
        if any(word in message_lower for word in ["chien", "chat", "animal", "fontaine", "sac", "distributeur"]):
            detected_topics.append("produits_animaux")
        
        return detected_topics

    async def generate_enhanced_response(self, client_message: str, client_phone: str, client_name: str = "Client") -> str:
        """Génère une réponse ultra-enrichie avec la nouvelle base de connaissances"""
        
        conversation_context = self.get_conversation_context(client_phone)
        message_lower = client_message.lower()
        
        # Détection d'intention (comme avant) + sujets spécifiques
        intentions = {
            "prix_tarif": ["prix", "coût", "tarif", "combien", "€", "euros", "cher", "budget"],
            "info_produit": ["info", "information", "produit", "catalogue", "voir", "détails"],
            "achat_commande": ["acheter", "commander", "commande", "veux", "intéressé"],
            "comparaison": ["comparai", "différence", "mieux", "quel", "choisir", "conseil"],
            "technique": ["technique", "fonctionne", "installation", "filtre", "garantie"],
            "sante_dangers": ["santé", "danger", "risque", "bébé", "famille", "sécurisé"],
            "animaux": ["chien", "chat", "animal", "fontaine", "sac", "distributeur"],
            "urgence": ["urgent", "rapidement", "vite", "maintenant"],
            "hésitation": ["hésite", "réfléchis", "pas sûr", "doute"],
            "positif": ["oui", "ok", "d'accord", "intéresse", "parfait"],
            "négatif": ["non", "pas intéressé", "cher", "plus tard"]
        }
        
        # Détection intention principale
        detected_intention = "general"
        max_score = 0
        for intention, keywords in intentions.items():
            score = sum(1 for keyword in keywords if keyword in message_lower)
            if score > max_score:
                max_score = score
                detected_intention = intention
        
        # Détection sujets spécifiques
        specific_topics = self.detect_specific_topics(client_message)
        
        # Construction prompt ultra-enrichi par agent
        enhanced_prompts = {
            "Thomas": {
                "sante_dangers": f"""Client préoccupé par santé/dangers eau. Utilise données PRÉCISES:
                - 68% points contrôle contiennent pesticides (5,7 différents/verre)
                - Nitrates: syndrome bébé bleu, 142 cas depuis 2020
                - Chlore: détruit microbiote (-23% en 6 mois)
                Rassure avec solution Josmoze: 99,9% élimination. Lien {JOSMOSE_WEBSITE}. Question famille/enfants?""",
                
                "comparaison": f"""Client compare solutions. Éduque avec faits:
                - Carafe: 0% nitrates/pesticides, juste goût chlore
                - Robinet: 70% pesticides mais 0% nitrates/virus
                - Osmose Josmoze: 99,9% TOUT éliminé
                Guide {JOSMOSE_WEBSITE}. Priorité: santé ou budget?""",
                
                "info_produit": f"""Client veut infos. Donne avantages clés nouveaux:
                - Système 7 étapes breveté (vs 3-5 concurrents)
                - Reminéralisation intelligente (eau vivante)
                - Monitoring IoT app mobile
                Catalogue {JOSMOSE_WEBSITE}. Usage prévu?""",
                
                "général": f"Bonjour {client_name}! Expert qualité eau Josmoze. Préoccupation eau du robinet? Conseils {JOSMOSE_WEBSITE}. Votre situation?"
            },
            
            "Sophie": {
                "prix_tarif": f"""Client demande prix. Présente valeur:
                Pack famille 890€ (-31%) vs 1290€ normal
                37€/mois 0% (moins que bouteilles!)
                Économies 4800€ sur 5 ans
                Configurateur {JOSMOSE_WEBSITE}. Budget mensuel OK?""",
                
                "achat_commande": f"""Client veut acheter. Facilite:
                Parfait {client_name}! Pack famille 890€ tout inclus
                + produit animal OFFERT (fontaine 49€, sac 29€, distributeur 39€)
                Commande {JOSMOSE_WEBSITE}. Quel cadeau animal?""",
                
                "objection_prix": f"""Client trouve cher. Repositionne valeur:
                890€ = 37€/mois vs 40€/mois bouteilles famille
                ROI 8 mois + santé famille garantie
                Financement 0% {JOSMOSE_WEBSITE}. Calculons ensemble?""",
                
                "hésitation": f"""Client hésite. Lève objections:
                Normal d'hésiter {client_name}. 30j satisfait/remboursé
                Déjà 847 familles satisfaites (4,8/5)
                Analyse gratuite {JOSMOSE_WEBSITE}. Quelle hésitation?""",
                
                "général": f"Bonjour {client_name}! Sophie, conseillère Josmoze. Protégeons votre famille! Solutions {JOSMOSE_WEBSITE}. Besoins urgents?"
            },
            
            "Marie": {
                "technique": f"""Client question technique. Expertise rassurante:
                Membrane 0,0001 micron (technologie NASA)
                Installation 1h45 par technicien certifié
                Maintenance 1 visite/an incluse
                Guides {JOSMOSE_WEBSITE}. Logement type?""",
                
                "service": f"""Client problème/service. Accompagnement:
                {client_name}, Marie du service Josmoze
                Résolvons ensemble rapidement
                Support 7j/7 garantie 5 ans
                Assistance {JOSMOSE_WEBSITE}. Précisez problème?""",
                
                "général": f"Bonjour {client_name}! Marie, relation client Josmoze. Accompagnement personnalisé garanti! Aide {JOSMOSE_WEBSITE}. Comment aider?"
            },
            
            "Julien": {
                "negatif": f"""Client négatif/récupération. Dernière chance:
                Compris {client_name}. Offre exceptionnelle dernières heures:
                Pack 890€ + animal OFFERT + financement 0%
                Stock limité 8 osmoseurs
                Urgence {JOSMOSE_WEBSITE}. Dernière opportunité?""",
                
                "hésitation": f"""Client hésite. Urgence douce:
                {client_name}, pack famille -31% se termine ce soir
                Plus que 8 osmoseurs disponibles
                Réservation {JOSMOSE_WEBSITE}. Sécurisez maintenant?""",
                
                "général": f"{client_name}, Julien récupération Josmoze. Offre expire bientôt! Opportunité {JOSMOSE_WEBSITE}. Dernière chance?"
            },
            
            "Caroline": {
                "technique": f"""Client technique. Données précises:
                Tests laboratoire Suez: 98,8% nitrates éliminés
                Certification NSF International (standard mondial)
                Membrane TFC 3 couches ultra-fines
                Documentation {JOSMOSE_WEBSITE}. Paramètres spécifiques?""",
                
                "comparaison": f"""Client compare. Analyse objective:
                Osmose 99,9% vs Carafe 30% vs Robinet 70%
                Coût réel 0,12€/L vs bouteille 0,25€/L
                ROI 500% sur 10 ans prouvé
                Comparatifs {JOSMOSE_WEBSITE}. Critères décision?""",
                
                "général": f"{client_name}, Caroline analyste Josmoze. Données objectives disponibles! Insights {JOSMOSE_WEBSITE}. Quels paramètres?"
            }
        }
        
        # Gestion sujets spécifiques avec données enrichies
        specific_responses = {
            "nitrates_danger": f"Nitrates dangereux: syndrome bébé bleu (142 cas depuis 2020), +18% cancer. Bretagne 68% communes touchées. Josmoze élimine 98,5%.",
            "pesticides_danger": f"Pesticides: 5,7 différents/verre, Glyphosate 65% échantillons. Effet cocktail inconnu. Josmoze élimine 99,2% des 200+ molécules.",
            "chlore_danger": f"Chlore détruit microbiote (-23% en 6 mois), crée sous-produits cancérigènes. Josmoze supprime 99,8% chlore + sous-produits.",
            "solutions_alternatives": f"Carafe: 0% nitrates/pesticides. Robinet: 70% pesticides mais 0% nitrates. Seule osmose = 99,9% TOUT.",
            "eau_bouteille": f"Bouteilles: microplastiques + 40€/mois famille. Osmose 37€/mois + 0 déchet. Économies 4800€/5 ans.",
            "produits_animaux": f"Nouveauté! Fontaine animaux 49€, sac transport 29€, distributeur 39€. 1 OFFERT avec osmoseur.",
            "objection_prix": f"890€ = 37€/mois vs 40€/mois bouteilles. ROI 8 mois. Santé famille: sans prix!"
        }
        
        # Sélection du template approprié
        agent_templates = enhanced_prompts.get(self.name, enhanced_prompts["Thomas"])
        base_template = agent_templates.get(detected_intention, agent_templates.get("général", ""))
        
        # Enrichissement avec sujets spécifiques
        topic_enrichment = ""
        for topic in specific_topics[:2]:  # Max 2 sujets pour éviter surcharge
            if topic in specific_responses:
                topic_enrichment += f"\nSUJET SPÉCIFIQUE {topic}: {specific_responses[topic]}"
        
        # Prompt final ultra-enrichi
        enhanced_directive = f"""
        Tu es {self.name}, {self.role} chez Josmoze (purificateurs d'eau par osmose inverse).
        Personnalité: {self.personality}
        
        CLIENT: {client_name}
        INTENTION: {detected_intention}
        SUJETS SPÉCIFIQUES: {', '.join(specific_topics) if specific_topics else 'Aucun'}
        MESSAGE: "{client_message}"
        
        CONTEXTE CONVERSATION:
        {conversation_context}
        
        TEMPLATE PERSONNALISÉ AGENT:
        {base_template}
        
        ENRICHISSEMENT SUJETS:
        {topic_enrichment}
        
        BASE CONNAISSANCES V2 (utilise si pertinent):
        - Dangers eau: nitrates (syndrome bébé bleu), pesticides (5,7/verre), chlore (microbiote -23%)
        - Solutions: carafe inefficace, robinet limité, osmose 99,9% tout
        - Josmoze: 7 étapes, 890€, garantie 5 ans, économies 4800€/5ans
        - Nouveaux produits animaux: fontaine 49€, sac 29€, distributeur 39€
        
        RÈGLES SMS OPTIMALES:
        1. Maximum 160 caractères SMS
        2. Inclure {JOSMOSE_WEBSITE} si intention commerciale
        3. Question engageante
        4. Ton personnalisé agent
        5. Action concrète
        6. Données précises si technique
        7. Maximum 1-2 émojis
        8. Personnalisation nom client
        
        Génère la réponse SMS PARFAITE enrichie des nouvelles connaissances.
        """
        
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": enhanced_directive},
                    {"role": "user", "content": f"Génère le SMS enrichi pour {client_name}"}
                ],
                max_tokens=120,
                temperature=0.7
            )
            
            enhanced_response = response.choices[0].message.content.strip()
            
            # Optimisation finale (comme avant mais avec enrichissements)
            critical_intentions = ["prix_tarif", "info_produit", "achat_commande", "comparaison", "technique", "sante_dangers"]
            
            if len(enhanced_response) > 160:
                parts = enhanced_response.split(' ')
                compressed = ""
                for part in parts:
                    if len(compressed + " " + part) <= 155:
                        compressed = compressed + " " + part if compressed else part
                    else:
                        break
                        
                if JOSMOSE_WEBSITE not in compressed and detected_intention in critical_intentions:
                    url_space = len(JOSMOSE_WEBSITE) + 1
                    available_space = 155 - url_space
                    if available_space > 20:
                        text_part = enhanced_response[:available_space].rsplit(' ', 1)[0]
                        enhanced_response = f"{text_part} {JOSMOSE_WEBSITE}"
                    else:
                        enhanced_response = compressed
                else:
                    enhanced_response = compressed
                    
            if detected_intention in critical_intentions and JOSMOSE_WEBSITE not in enhanced_response:
                if len(enhanced_response) < 120:
                    enhanced_response += f" {JOSMOSE_WEBSITE}"
                else:
                    available = 155 - len(JOSMOSE_WEBSITE)
                    text_part = enhanced_response[:available].rsplit(' ', 1)[0]
                    enhanced_response = f"{text_part} {JOSMOSE_WEBSITE}"
            
            # Sauvegarde enrichie
            self.save_message(client_phone, f"Client ({client_name})", client_message)
            self.save_message(client_phone, f"{self.name} [V2-{detected_intention}]", enhanced_response)
            
            return enhanced_response
            
        except Exception as e:
            print(f"❌ Erreur IA V2: {str(e)}")
            
            # Réponses de secours enrichies
            enhanced_emergency = {
                "prix_tarif": f"{client_name}, pack famille 890€ vs 1290€ (-31%). 37€/mois 0%. Détails {JOSMOSE_WEBSITE}. Budget OK?",
                "sante_dangers": f"{client_name}, 68% eaux contiennent pesticides. Josmoze élimine 99,9%. Sécurité {JOSMOSE_WEBSITE}. Enfants?",
                "info_produit": f"{client_name}, osmose 7 étapes + app IoT. Catalogue {JOSMOSE_WEBSITE}. Usage prévu?",
                "achat_commande": f"Parfait {client_name}! Pack 890€ + animal offert. Commande {JOSMOSE_WEBSITE}. Quel cadeau?",
                "animaux": f"{client_name}, nouveauté! Fontaine/sac/distributeur animaux. 1 offert avec osmoseur {JOSMOSE_WEBSITE}. Animaux?",
                "général": f"Merci {client_name}! Expert eau pure Josmoze. Solutions {JOSMOSE_WEBSITE}. Besoins?"
            }
            
            return enhanced_emergency.get(detected_intention, f"Merci {client_name}! Solutions eau pure: {JOSMOSE_WEBSITE}")

    async def send_enhanced_sms(self, to_number: str, client_message: str, client_name: str = "Client") -> bool:
        """Envoie SMS avec réponse enrichie V2"""
        try:
            response = await self.generate_enhanced_response(client_message, to_number, client_name)
            
            sms = self.twilio_client.messages.create(
                body=response,
                from_=TWILIO_PHONE_NUMBER,
                to=to_number
            )
            
            print(f"✅ {self.name} V2 → SMS enrichi: {response}")
            print(f"📋 SID: {sms.sid}")
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur envoi SMS V2: {str(e)}")
            return False

# Agents conversationnels V2 enrichis
conversational_agents_v2 = {
    "thomas": ConversationalAgentV2(
        name="Thomas",
        role="expert qualité eau et dangers sanitaires",
        personality="Empathique, éducateur, expert nitrates/pesticides/chlore, protecteur familles"
    ),
    
    "sophie": ConversationalAgentV2(
        name="Sophie", 
        role="conseillère commerciale spécialisée osmose inverse",
        personality="Professionnelle, ROI-orientée, experte objections prix, facilitatrice décisions"
    ),
    
    "marie": ConversationalAgentV2(
        name="Marie",
        role="spécialiste relation client et support technique",
        personality="Chaleureuse, technicienne confirmée, garanties rassurantes, fidélisatrice"
    ),
    
    "julien": ConversationalAgentV2(
        name="Julien", 
        role="expert récupération et offres exceptionnelles",
        personality="Motivateur, urgence maîtrisée, facilitateur dernière chance, créateur opportunités"
    ),
    
    "caroline": ConversationalAgentV2(
        name="Caroline",
        role="analyste performance eau et conseils data-driven", 
        personality="Scientifique, données précises, certifications, preuves laboratoire"
    )
}

def detect_enhanced_agent(message: str) -> str:
    """Détection agent améliorée avec nouveaux critères"""
    
    message_lower = message.lower()
    
    # Mots-clés enrichis V2
    enhanced_keywords = {
        "thomas": [
            "santé", "danger", "bébé", "enfant", "famille", "sécurité", "risque",
            "nitrate", "pesticide", "chlore", "qualité", "pure", "conseil", "info"
        ],
        "sophie": [
            "prix", "coût", "acheter", "commander", "budget", "économie", "rentable",
            "offre", "promo", "pack", "financement", "intéressé", "vendre"
        ],
        "marie": [
            "installation", "technique", "garantie", "service", "support", "aide",
            "problème", "maintenance", "assistance", "accompagnement"
        ],
        "julien": [
            "hésite", "réfléchir", "cher", "plus tard", "abandonné", "urgent",
            "dernière", "rapide", "maintenant", "décision", "opportunité"
        ],
        "caroline": [
            "comparaison", "test", "analyse", "étude", "données", "laboratoire",
            "certification", "performance", "technique", "scientifique"
        ]
    }
    
    # Score enrichi par agent
    scores = {}
    for agent, words in enhanced_keywords.items():
        scores[agent] = sum(1 for word in words if word in message_lower)
    
    # Agent avec meilleur score
    best_agent = max(scores.items(), key=lambda x: x[1])
    
    # Si égalité ou pas de match, Thomas par défaut (expert général)
    return best_agent[0] if best_agent[1] > 0 else "thomas"

# Tests enrichis avec nouveau contenu
async def test_enhanced_system():
    """Test du système V2 enrichi"""
    
    print("🤖 TEST SYSTÈME CONVERSATIONNEL V2.0 ENRICHI")
    print("=" * 55)
    
    client_phone = "+15068893760"  
    client_name = "Madame Dubois"
    
    # Conversations de test enrichies
    enhanced_conversations = [
        ("Bonjour, l'eau du robinet est-elle dangereuse pour mon bébé ?", "thomas"),
        ("Vos prix sont élevés, combien exactement ?", "sophie"), 
        ("Quelle est la différence avec une carafe Brita ?", "caroline"),
        ("J'hésite, c'est un gros investissement...", "julien"),
        ("Avez-vous des produits pour les animaux ?", "thomas")
    ]
    
    print(f"🧪 Test conversation V2 enrichie avec {client_name}")
    
    for i, (message, preferred_agent) in enumerate(enhanced_conversations, 1):
        print(f"\n--- Échange V2 {i} ---")
        print(f"👤 {client_name}: {message}")
        
        # Détection automatique enrichie
        detected_agent = detect_enhanced_agent(message)
        agent_name = preferred_agent or detected_agent
        agent = conversational_agents_v2[agent_name]
        
        print(f"🤖 Agent V2 sélectionné: {agent.name}")
        
        # Réponse enrichie
        success = await agent.send_enhanced_sms(client_phone, message, client_name)
        
        if success:
            print(f"✅ SMS V2 enrichi envoyé")
        else:
            print(f"❌ Échec envoi V2")
        
        await asyncio.sleep(3)
    
    print(f"\n🌊 Test V2 terminé ! Système enrichi avec nouveau contenu actif.")

if __name__ == "__main__":
    # Test système V2 enrichi
    asyncio.run(test_enhanced_system())