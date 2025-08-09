"""
🤖 Système d'Agents IA Sophistiqués avec Stratégies de Schopenhauer
================================================================

Agents créés:
- Socrate 🧠: Agent Prospection & Qualification 24/7
- Aristote 📞: Agent Calls Commercial (9h-18h)
- Cicéron 💬: Agent SMS & Suivi Relationnel
- Démosthène 🛒: Agent Paniers Abandonnés Spécialisé
- Platon 📊: Agent Analytics & Intelligence Prédictive

Features:
- 38 Stratagèmes de Schopenhauer intégrés
- Adaptation personnalisée selon profil client
- Gestion horaires de travail (9h-18h, lundi-vendredi)
- KPIs: Taux conversion, CA, Satisfaction 95%+, Temps réponse <5min
"""

import asyncio
import json
import uuid
from datetime import datetime, time, timedelta
from typing import Dict, List, Optional, Any
import pytz
from enum import Enum
import logging
from dataclasses import dataclass, asdict
import os
from motor.motor_asyncio import AsyncIOMotorClient

# Configuration des stratégies de Schopenhauer
SCHOPENHAUER_STRATAGEMS = {
    1: "Extension - Étendre l'affirmation de l'adversaire au-delà de ses limites naturelles",
    2: "Homonymie - Utiliser des termes ambigus pour créer de la confusion",
    3: "Généralisation abusive - Prendre une affirmation relative comme absolue",
    4: "Prémisse cachée - Cacher ses vraies intentions derrière des prémisses évidentes",
    5: "Fausses prémisses - Utiliser des prémisses fausses ou non démontrées",
    6: "Pétition de principe - Prouver ce qui est en question par ce qui est en question",
    7: "Interrogation multiple - Poser plusieurs questions comme une seule",
    8: "Provocation - Mettre l'adversaire en colère pour l'amener à mal argumenter",
    9: "Ordre des questions - Poser les questions dans un ordre désorientant",
    10: "Contradiction exploitée - Exploiter une petite contradiction pour nier tout l'argument",
    11: "Généralisation - Si l'adversaire ne définit pas un concept, le définir à votre avantage",
    12: "Métaphores - Utiliser des métaphores favorables à votre position",
    13: "Contraires - Présenter les contraires pour faire accepter votre position",
    14: "Victoire proclamée - Proclamer la victoire même si c'est prématuré",
    15: "Paradoxe apparent - Présenter votre thèse comme paradoxale pour forcer la réflexion",
    16: "Arguments ad hominem - Attaquer la personne plutôt que l'argument (à éviter - trop agressif)",
    17: "Exceptions subtiles - Trouver des exceptions subtiles à la règle de l'adversaire",
    18: "Interrompre - Interrompre l'adversaire quand il développe un argument dangereux",
    19: "Argument général - Passer d'un argument particulier à un argument général",
    20: "Conclusion prématurée - Tirer des conclusions des prémisses avant qu'elles ne soient admises",
    21: "Argument sophistique - Utiliser un argument qui semble valide mais ne l'est pas",
    22: "Pétition de principe sophistiquée - Demander ce qui est en question de façon détournée",
    23: "Exagération - Pousser la thèse adverse à l'extrême pour la rendre absurde",
    24: "Fausse analogie - Utiliser des analogies boiteuses à votre avantage",
    25: "Instance contraire - Trouver une seule instance contraire pour réfuter une généralisation",
    26: "Retournement - Retourner l'argument contre son auteur",
    27: "Agacement - Agacer l'adversaire pour qu'il fasse des erreurs",
    28: "Ridicule - Tourner l'argument en ridicule (avec précaution)",
    29: "Diversion - Détourner vers un autre sujet quand on perd",
    30: "Autorité - Utiliser des autorités qui impressionnent mais ne sont pas compétentes",
    31: "Incompétence feinte - Feindre l'incompétence pour que l'adversaire s'explique mal",
    32: "Classification odieuse - Classer l'argument adverse dans une catégorie détestée",
    33: "Théorie et pratique - Distinguer théorie et pratique pour échapper aux conséquences",
    34: "Question subsidiaire - Ne pas répondre directement mais poser une question subsidiaire",
    35: "Motivation - Attaquer les motivations plutôt que l'argument",
    36: "Éblouir - Impressionner par un flot de paroles savantes mais creuses",
    37: "Preuve par l'exemple - Utiliser un exemple favorable même s'il n'est pas représentatif",
    38: "Victoire personnelle - Si tout échoue, devenir personnel et offensant (à éviter absolument)"
}

class ClientPersonality(Enum):
    ANALYTIQUE = "analytique"  # Demande des preuves, des chiffres
    AMICAL = "amical"         # Relationnel, cherche le contact humain
    EXPRESSIF = "expressif"   # Émotionnel, spontané
    PILOTE = "pilote"        # Direct, orienté résultats
    SKEPTIQUE = "skeptique"   # Méfiant, critique
    PRESSE = "presse"        # Veut du rapide, de l'efficace
    ECONOMIQUE = "economique" # Sensible au prix
    TECHNIQUE = "technique"   # Veut tous les détails techniques

class AgentStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive" 
    PAUSED = "paused"
    SCHEDULED = "scheduled"

class ConversationStage(Enum):
    PROSPECT = "prospect"       # Première approche
    QUALIFICATION = "qualification"  # Qualification du besoin
    OBJECTION = "objection"     # Traitement des objections
    CLOSING = "closing"         # Closing/finalisation
    FOLLOWUP = "followup"       # Suivi relationnel
    RECOVERY = "recovery"       # Récupération panier abandonné

@dataclass
class ClientProfile:
    id: str
    name: str
    email: str
    phone: str
    personality: ClientPersonality
    interaction_history: List[Dict]
    objections_raised: List[str]
    conversion_probability: float
    last_interaction: datetime
    preferred_contact_time: Dict[str, Any]
    cart_abandoned: bool = False
    purchase_history: List[Dict] = None
    
    def __post_init__(self):
        if self.purchase_history is None:
            self.purchase_history = []

@dataclass
class AgentConfig:
    name: str
    specialty: str
    model_provider: str
    model_name: str
    working_hours: Dict[str, Any]
    max_conversations_per_hour: int
    personality_traits: List[str]
    status: AgentStatus = AgentStatus.INACTIVE
    performance_kpis: Dict[str, float] = None
    
    def __post_init__(self):
        if self.performance_kpis is None:
            self.performance_kpis = {
                "conversion_rate": 0.0,
                "satisfaction_score": 0.0,
                "response_time_seconds": 0.0,
                "revenue_generated": 0.0
            }

class AIAgentSystem:
    def __init__(self, mongo_url: str, db_name: str):
        self.client = AsyncIOMotorClient(mongo_url)
        self.db = self.client[db_name]
        self.agents = {}
        self.active_conversations = {}
        self.paris_tz = pytz.timezone('Europe/Paris')
        
        # Configuration des agents
        self._initialize_agents()
        
    def _initialize_agents(self):
        """Initialize all AI agents with their specific configurations"""
        
        # Thomas 👨‍💼 - Agent Prospection & Qualification 24/7
        self.agents["thomas"] = AgentConfig(
            name="Thomas 👨‍💼",
            specialty="Prospection et Qualification des leads 24/7",
            model_provider="openai",
            model_name="gpt-4o",
            working_hours={"always_active": True},  # 24/7 pour la prospection
            max_conversations_per_hour=50,
            personality_traits=[
                "Philosophe curieux qui pose les bonnes questions",
                "Socratique - amène le client à découvrir ses propres besoins", 
                "Maître de l'art du questionnement subtil",
                "Expert en qualification sans pression"
            ]
        )
        
        # Sophie 👩‍💼 - Agent Calls Commercial (9h-18h) - DÉSACTIVÉ POUR FOCUS SMS
        self.agents["sophie"] = AgentConfig(
            name="Sophie 👩‍💼",
            specialty="Appels commerciaux et gestion objections",
            model_provider="openai", 
            model_name="gpt-4o",
            working_hours={
                "days": ["monday", "tuesday", "wednesday", "thursday", "friday"],
                "start_time": "09:00",
                "end_time": "18:00",
                "timezone": "Europe/Paris"
            },
            max_conversations_per_hour=10,  # Plus de temps par call
            personality_traits=[
                "Logicien aristotélicien - structure parfaite des arguments",
                "Rhétorique persuasive mais respectueuse",
                "Expert en syllogismes commerciaux",
                "Maîtrise parfaite des 38 stratagèmes de Schopenhauer"
            ]
        )
        
        # Cicéron 💬 - Agent SMS & Suivi Relationnel  
        self.agents["ciceron"] = AgentConfig(
            name="Cicéron 💬",
            specialty="SMS personnalisés et suivi relationnel",
            model_provider="openai",
            model_name="gpt-4o", 
            working_hours={
                "days": ["monday", "tuesday", "wednesday", "thursday", "friday"],
                "start_time": "09:00", 
                "end_time": "20:00",  # Plus tard pour SMS
                "timezone": "Europe/Paris"
            },
            max_conversations_per_hour=100,  # SMS rapides
            personality_traits=[
                "Orateur empathique et chaleureux",
                "Messages courts mais impactants",
                "Maître de la persuasion douce",
                "Expert en timing relationnel"
            ]
        )
        
        # Démosthène 🛒 - Agent Paniers Abandonnés
        self.agents["demosthene"] = AgentConfig(
            name="Démosthène 🛒", 
            specialty="Récupération paniers abandonnés - Expert urgence",
            model_provider="openai",
            model_name="gpt-4o",
            working_hours={
                "days": ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"],
                "start_time": "09:00",
                "end_time": "18:00", 
                "timezone": "Europe/Paris"
            },
            max_conversations_per_hour=30,
            personality_traits=[
                "Orateur passionné qui sait créer l'urgence",
                "Spécialiste de la reconquête client", 
                "Empathique mais déterminé",
                "Expert en offres irrésistibles"
            ]
        )
        
        # Platon 📊 - Agent Analytics & Intelligence Prédictive
        self.agents["platon"] = AgentConfig(
            name="Platon 📊",
            specialty="Analytics avancés et intelligence prédictive", 
            model_provider="openai",
            model_name="gpt-4o",
            working_hours={"always_active": True},  # 24/7 pour l'analyse
            max_conversations_per_hour=5,  # Analyses approfondies
            personality_traits=[
                "Philosophe des données et des patterns",
                "Vision stratégique globale", 
                "Prédictions basées sur l'observation",
                "Sagesse analytique pour l'optimisation"
            ]
        )

    def get_schopenhauer_strategy(self, client_profile: ClientProfile, conversation_stage: ConversationStage) -> Dict[str, Any]:
        """Sélectionne les meilleures stratégies de Schopenhauer selon le client et le contexte"""
        
        strategies = []
        
        # Stratégies selon la personnalité du client
        if client_profile.personality == ClientPersonality.ANALYTIQUE:
            strategies.extend([1, 3, 19, 25, 37])  # Extension, généralisation, preuves par l'exemple
        elif client_profile.personality == ClientPersonality.SKEPTIQUE:
            strategies.extend([10, 17, 26, 33])  # Exploitation contradictions, retournement
        elif client_profile.personality == ClientPersonality.EMOTIF:
            strategies.extend([12, 13, 15, 24])  # Métaphores, contraires, paradoxes
        elif client_profile.personality == ClientPersonality.PRESSE:
            strategies.extend([14, 20, 29])  # Victoire proclamée, conclusion rapide
        elif client_profile.personality == ClientPersonality.ECONOMIQUE:
            strategies.extend([23, 25, 32])  # Exagération coûts concurrence, classification
            
        # Stratégies selon l'étape de conversation
        if conversation_stage == ConversationStage.PROSPECT:
            strategies.extend([4, 9, 11])  # Prémisse cachée, ordre questions, définitions
        elif conversation_stage == ConversationStage.OBJECTION:
            strategies.extend([17, 26, 33, 34])  # Exceptions, retournement, théorie/pratique
        elif conversation_stage == ConversationStage.CLOSING:
            strategies.extend([14, 20, 15])  # Victoire proclamée, conclusion prématurée
            
        # Éviter les stratégies trop agressives (16, 27, 28, 35, 38)
        safe_strategies = [s for s in strategies if s not in [16, 27, 28, 35, 38]]
        
        return {
            "primary_strategies": safe_strategies[:3],  # Top 3 stratégies
            "fallback_strategies": safe_strategies[3:6] if len(safe_strategies) > 3 else [],
            "context_description": f"Client {client_profile.personality.value} en phase {conversation_stage.value}",
            "strategy_explanations": {str(s): SCHOPENHAUER_STRATAGEMS[s] for s in safe_strategies[:5]}
        }

    def is_agent_active(self, agent_name: str) -> bool:
        """Vérifie si un agent doit être actif selon ses horaires de travail"""
        
        if agent_name not in self.agents:
            return False
            
        agent = self.agents[agent_name]
        now = datetime.now(self.paris_tz)
        
        # Agents 24/7
        if agent.working_hours.get("always_active", False):
            return True
            
        # Vérification jour de la semaine
        current_day = now.strftime("%A").lower()
        if current_day not in agent.working_hours.get("days", []):
            return False
            
        # Vérification heures
        start_time = datetime.strptime(agent.working_hours["start_time"], "%H:%M").time()
        end_time = datetime.strptime(agent.working_hours["end_time"], "%H:%M").time()
        current_time = now.time()
        
        return start_time <= current_time <= end_time

    async def create_personalized_message(self, agent_name: str, client_profile: ClientProfile, 
                                        conversation_stage: ConversationStage, context: str = "") -> str:
        """Crée un message personnalisé en utilisant les stratégies de Schopenhauer"""
        
        if agent_name not in self.agents:
            return "Agent non trouvé"
            
        agent = self.agents[agent_name]
        strategies = self.get_schopenhauer_strategy(client_profile, conversation_stage)
        
        # Construction du prompt système avec stratégies Schopenhauer
        system_prompt = f"""Tu es {agent.name}, un expert commercial spécialisé en {agent.specialty}.

PERSONNALITÉ AGENT: {', '.join(agent.personality_traits)}

CLIENT PROFIL:
- Nom: {client_profile.name}  
- Personnalité: {client_profile.personality.value}
- Objections précédentes: {', '.join(client_profile.objections_raised[-3:]) if client_profile.objections_raised else 'Aucune'}
- Probabilité conversion: {client_profile.conversion_probability:.0%}
- Panier abandonné: {'Oui' if client_profile.cart_abandoned else 'Non'}

STRATÉGIES SCHOPENHAUER À UTILISER:
{json.dumps(strategies['strategy_explanations'], indent=2, ensure_ascii=False)}

DIRECTIVES:
1. Utilise les stratégies Schopenhauer de façon subtile et éthique
2. Adapte ton discours à la personnalité du client ({client_profile.personality.value})
3. Sois empathique et conseiller, jamais forceur
4. Traite les objections avec finesse
5. Message court (max 100 mots pour SMS, 200 pour appel)
6. Français professionnel mais chaleureux
7. OBJECTIF: Satisfaction client 95%+ et conversion optimale

CONTEXTE ACTUEL: {context}
ÉTAPE CONVERSATION: {conversation_stage.value}
"""

        # Simulation de réponse IA personnalisée (sera remplacé par vraie API)
        simulated_responses = {
            "socrate": f"Bonjour {client_profile.name} ! 🌊 J'espère que vous allez bien. Je réfléchissais à votre situation... Avez-vous déjà remarqué la différence de goût entre l'eau du robinet le matin et le soir ? C'est fascinant comme notre corps perçoit ces nuances. Qu'est-ce qui vous préoccupe le plus concernant la qualité de votre eau actuellement ?",
            
            "aristote": f"Bonjour {client_profile.name}, merci de me consacrer ce temps. En analysant votre situation, je vois trois points essentiels : 1) Votre santé familiale 2) Votre budget long-terme 3) Votre tranquillité d'esprit. Si je vous démontrais qu'investir dans la purification peut résoudre ces trois aspects simultanément, seriez-vous prêt(e) à examiner les détails ?",
            
            "ciceron": f"Salut {client_profile.name} ! 💬 Petite question rapide : avez-vous goûté votre eau ce matin ? Je demande car 73% de nos clients découvrent une différence flagrante dès le premier verre avec notre système. Curieux de votre ressenti ! Répondez-moi quand vous avez 30 secondes 😊",
            
            "demosthene": f"Bonjour {client_profile.name}, je remarque que vous aviez sélectionné notre purificateur hier... Puis-je vous demander ce qui vous a fait hésiter au dernier moment ? Souvent c'est juste un petit détail qu'on peut clarifier ensemble. J'ai d'excellentes nouvelles à vous partager ! 🎁",
            
            "platon": f"Analyse pour {client_profile.name}: Basé sur vos interactions, je détecte un profil {client_profile.personality.value} avec {client_profile.conversion_probability:.0%} de probabilité de conversion. Recommandation: approche {strategies['context_description']} avec focus sur {'les bénéfices techniques' if client_profile.personality == ClientPersonality.TECHNIQUE else 'les avantages pratiques'}."
        }
        
        return simulated_responses.get(agent_name, f"Message de {agent.name} pour {client_profile.name}")

    async def process_client_interaction(self, client_data: Dict, agent_name: str, message_type: str = "sms") -> Dict[str, Any]:
        """Traite une interaction client avec l'agent IA spécifié"""
        
        # Créer ou récupérer le profil client
        client_profile = await self._get_or_create_client_profile(client_data)
        
        # Déterminer l'étape de conversation
        conversation_stage = self._determine_conversation_stage(client_profile)
        
        # Vérifier si l'agent est actif
        if not self.is_agent_active(agent_name):
            return {
                "status": "agent_inactive", 
                "message": f"Agent {self.agents[agent_name].name} non disponible actuellement",
                "next_availability": self._get_next_availability(agent_name)
            }
        
        # Générer le message personnalisé
        context = f"Interaction {message_type} - {datetime.now().strftime('%H:%M')}"
        message = await self.create_personalized_message(agent_name, client_profile, conversation_stage, context)
        
        # Logger l'interaction
        interaction_log = {
            "timestamp": datetime.now(),
            "agent": agent_name,
            "client_id": client_profile.id,
            "message_type": message_type,
            "conversation_stage": conversation_stage.value,
            "strategies_used": self.get_schopenhauer_strategy(client_profile, conversation_stage)["primary_strategies"],
            "message_sent": message
        }
        
        # Sauvegarder en DB
        await self._save_interaction_log(interaction_log)
        
        # Mettre à jour le profil client
        client_profile.last_interaction = datetime.now()
        client_profile.interaction_history.append(interaction_log)
        await self._update_client_profile(client_profile)
        
        return {
            "status": "success",
            "agent": self.agents[agent_name].name,
            "message": message,
            "client_profile": asdict(client_profile),
            "strategies_used": self.get_schopenhauer_strategy(client_profile, conversation_stage),
            "next_recommended_action": self._get_next_action_recommendation(client_profile)
        }

    async def get_agent_performance_dashboard(self) -> Dict[str, Any]:
        """Génère le dashboard de performance des agents"""
        
        dashboard = {
            "timestamp": datetime.now().isoformat(),
            "agents_status": {},
            "global_kpis": {
                "total_conversations": 0,
                "average_conversion_rate": 0.0,
                "average_satisfaction": 0.0,
                "total_revenue": 0.0,
                "average_response_time": 0.0
            },
            "active_conversations": len(self.active_conversations),
            "recommendations": []
        }
        
        # Stats par agent
        for agent_name, agent in self.agents.items():
            is_active = self.is_agent_active(agent_name)
            
            dashboard["agents_status"][agent_name] = {
                "name": agent.name,
                "specialty": agent.specialty,
                "status": "active" if is_active else "inactive",
                "performance": agent.performance_kpis,
                "working_hours": agent.working_hours,
                "conversations_today": await self._get_daily_conversation_count(agent_name)
            }
        
        # Recommandations automatiques
        dashboard["recommendations"] = await self._generate_performance_recommendations()
        
        return dashboard

    async def toggle_agent_status(self, agent_name: str, new_status: AgentStatus) -> Dict[str, Any]:
        """Active/désactive un agent"""
        
        if agent_name not in self.agents:
            return {"status": "error", "message": "Agent non trouvé"}
            
        old_status = self.agents[agent_name].status
        self.agents[agent_name].status = new_status
        
        # Log du changement
        await self.db.agent_logs.insert_one({
            "timestamp": datetime.now(),
            "agent": agent_name,
            "action": "status_change",
            "old_status": old_status.value,
            "new_status": new_status.value,
            "changed_by": "system"  # Sera remplacé par user ID
        })
        
        return {
            "status": "success",
            "agent": self.agents[agent_name].name,
            "old_status": old_status.value,
            "new_status": new_status.value,
            "message": f"Agent {self.agents[agent_name].name} mis à jour: {new_status.value}"
        }

    # Méthodes utilitaires privées
    
    async def _get_or_create_client_profile(self, client_data: Dict) -> ClientProfile:
        """Récupère ou crée un profil client"""
        
        client_id = client_data.get("email", str(uuid.uuid4()))
        
        # Chercher en DB
        existing = await self.db.client_profiles.find_one({"id": client_id})
        
        if existing:
            return ClientProfile(**existing)
        
        # Créer nouveau profil avec analyse de personnalité
        personality = self._analyze_client_personality(client_data)
        
        profile = ClientProfile(
            id=client_id,
            name=client_data.get("name", "Client"),
            email=client_data.get("email", ""),
            phone=client_data.get("phone", ""),
            personality=personality,
            interaction_history=[],
            objections_raised=[],
            conversion_probability=0.3,  # Base 30%
            last_interaction=datetime.now(),
            preferred_contact_time={"morning": True, "afternoon": True, "evening": False},
            cart_abandoned=client_data.get("cart_abandoned", False)
        )
        
        # Sauvegarder
        await self.db.client_profiles.insert_one(asdict(profile))
        
        return profile
    
    def _analyze_client_personality(self, client_data: Dict) -> ClientPersonality:
        """Analyse simple de personnalité basée sur les données disponibles"""
        
        # Logique simplifiée - sera améliorée avec plus de données
        if "prix" in str(client_data).lower() or "coût" in str(client_data).lower():
            return ClientPersonality.ECONOMIQUE
        elif "technique" in str(client_data).lower() or "spécification" in str(client_data).lower():
            return ClientPersonality.TECHNIQUE  
        elif client_data.get("cart_abandoned"):
            return ClientPersonality.SKEPTIQUE
        else:
            return ClientPersonality.AMICAL  # Défaut
    
    def _determine_conversation_stage(self, client_profile: ClientProfile) -> ConversationStage:
        """Détermine l'étape de conversation selon l'historique"""
        
        if client_profile.cart_abandoned:
            return ConversationStage.RECOVERY
        elif len(client_profile.interaction_history) == 0:
            return ConversationStage.PROSPECT
        elif len(client_profile.objections_raised) > 0:
            return ConversationStage.OBJECTION
        elif client_profile.conversion_probability > 0.7:
            return ConversationStage.CLOSING
        else:
            return ConversationStage.QUALIFICATION
    
    def _get_next_availability(self, agent_name: str) -> str:
        """Calcule la prochaine disponibilité d'un agent"""
        
        agent = self.agents[agent_name]
        now = datetime.now(self.paris_tz)
        
        if agent.working_hours.get("always_active"):
            return "Immédiatement"
            
        # Logique simplifiée - calcul prochain créneau
        return "Demain 9h00"
    
    async def _get_daily_conversation_count(self, agent_name: str) -> int:
        """Nombre de conversations de l'agent aujourd'hui"""
        
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        count = await self.db.interaction_logs.count_documents({
            "agent": agent_name,
            "timestamp": {"$gte": today}
        })
        return count
    
    def _get_next_action_recommendation(self, client_profile: ClientProfile) -> str:
        """Recommande la prochaine action selon le profil"""
        
        if client_profile.cart_abandoned:
            return "Relance urgente panier abandonné avec offre spéciale"
        elif client_profile.conversion_probability > 0.8:
            return "Appel de closing - client très chaud"
        elif len(client_profile.objections_raised) > 2:
            return "SMS empathique pour surmonter résistances"
        else:
            return "Nurturing relationnel avec contenu de valeur"
    
    async def _generate_performance_recommendations(self) -> List[str]:
        """Génère des recommandations d'optimisation"""
        
        recommendations = []
        
        # Analyse des performances globales
        total_agents = len([a for a in self.agents.values() if self.is_agent_active(a.name)])
        
        if total_agents < 3:
            recommendations.append("💡 Activez plus d'agents pour couvrir tous les créneaux")
            
        # Recommandations basées sur l'heure
        now = datetime.now(self.paris_tz)
        if 9 <= now.hour <= 12:
            recommendations.append("🌅 Période optimale pour appels - activez Aristote")
        elif 14 <= now.hour <= 17:
            recommendations.append("📞 Créneau idéal closing - intensifiez les calls")
        elif 17 <= now.hour <= 20:
            recommendations.append("💬 Horaire SMS - activez Cicéron pour relances")
            
        return recommendations
    
    async def _save_interaction_log(self, interaction_log: Dict):
        """Sauvegarde un log d'interaction"""
        await self.db.interaction_logs.insert_one(interaction_log)
        
    async def _update_client_profile(self, client_profile: ClientProfile):
        """Met à jour un profil client"""
        await self.db.client_profiles.update_one(
            {"id": client_profile.id},
            {"$set": asdict(client_profile)}
        )

# Instance globale du système
ai_agent_system = None

async def get_ai_agent_system():
    """Récupère l'instance globale du système d'agents"""
    global ai_agent_system
    
    if ai_agent_system is None:
        mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
        db_name = os.environ.get('DB_NAME', 'test_database')
        ai_agent_system = AIAgentSystem(mongo_url, db_name)
        
    return ai_agent_system