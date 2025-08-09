from typing import List, Dict, Optional, Any
import asyncio
import httpx
import os
from datetime import datetime, timedelta
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient
import logging

logger = logging.getLogger(__name__)

class AIAgentConfig(BaseModel):
    agent_type: str  # email, sms, whatsapp, call
    provider: str  # openai, anthropic, twilio, etc.
    api_key: str
    model: str = "claude-3-sonnet-20240229"
    max_tokens: int = 1000

class MarketingCampaign(BaseModel):
    id: str
    name: str
    type: str  # email_sequence, abandoned_cart, lead_nurturing, promo
    target_audience: str  # B2C, B2B, all
    status: str = "active"  # active, paused, completed
    triggers: List[str]  # lead_created, cart_abandoned, purchase_completed
    content_template: str
    success_metrics: Dict[str, float] = {}
    created_at: datetime
    last_run: Optional[datetime] = None

class AIEmailAgent:
    """AI Agent for email marketing automation"""
    
    def __init__(self, db):
        self.db = db
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY", "")
        
    async def generate_email_content(self, 
                                   template_type: str,
                                   customer_data: Dict[str, Any],
                                   product_context: Optional[Dict] = None) -> Dict[str, str]:
        """Generate personalized email content using Claude"""
        
        try:
            # Prepare context for AI
            context = f"""
            Tu es un expert en marketing pour Josmoze.com, spécialiste français des systèmes d'osmose inverse.
            
            CLIENT:
            - Nom: {customer_data.get('name', 'Cher client')}
            - Type: {customer_data.get('customer_type', 'B2C')} ({'Particulier' if customer_data.get('customer_type') == 'B2C' else 'Professionnel'})
            - Email: {customer_data.get('email', '')}
            - Pays: {customer_data.get('country_code', 'FR')}
            
            TYPE D'EMAIL: {template_type}
            
            CONTEXTE PRODUIT:
            - Osmoseur principal: 499€ (au lieu de 599€)
            - Système 4 étapes d'ultrafiltration
            - Installation sans électricité
            - Économies 500-700€/an vs bouteilles
            
            Génère un email professionnel, personnalisé et persuasif en français.
            """
            
            templates = {
                "welcome": self._get_welcome_template(),
                "abandoned_cart": self._get_abandoned_cart_template(),
                "lead_nurturing": self._get_nurturing_template(),
                "promotion": self._get_promotion_template(),
                "follow_up": self._get_followup_template()
            }
            
            template = templates.get(template_type, templates["welcome"])
            
            # Simple template filling for now (in production, would use Claude API)
            subject = template["subject"].format(**customer_data)
            content = template["content"].format(
                name=customer_data.get('name', 'Cher client'),
                customer_type_text='Particulier' if customer_data.get('customer_type') == 'B2C' else 'Professionnel'
            )
            
            return {
                "subject": subject,
                "content": content,
                "template_type": template_type
            }
            
        except Exception as e:
            logger.error(f"Failed to generate email content: {e}")
            return self._get_fallback_email(template_type, customer_data)
    
    def _get_welcome_template(self) -> Dict[str, str]:
        return {
            "subject": "Bienvenue chez Josmose - Votre eau pure vous attend ! 💧",
            "content": """
Bonjour {name},

Merci pour votre intérêt pour nos systèmes d'osmose inverse !

En tant que {customer_type_text}, vous bénéficiez de :
✅ Système 4 étapes d'ultrafiltration
✅ Installation sans électricité en 30 minutes
✅ Économies garanties de 500-700€/an
✅ Élimination de 99% des contaminants

🎯 OFFRE SPÉCIALE : -100€ sur votre première commande
Code: BIENVENUE100 (valable 7 jours)

Besoin d'aide ? Notre équipe d'experts est à votre disposition.

À très bientôt,
L'équipe Josmoze.com 💧

P.S. Regardez cette vidéo de 2 minutes pour voir la différence : [lien vidéo]
            """
        }
    
    def _get_abandoned_cart_template(self) -> Dict[str, str]:
        return {
            "subject": "⏰ {name}, votre osmoseur vous attend ! -10% offert",
            "content": """
Bonjour {name},

Vous avez ajouté notre système d'osmose à votre panier mais n'avez pas finalisé votre commande.

🚨 DERNIÈRE CHANCE : -10% avec le code RETOUR10

⏱️ Cette offre expire dans 24h !

Vos avantages :
• Installation gratuite comprise
• Garantie 2 ans incluse  
• Livraison rapide en Europe
• Support technique 7j/7

👆 Finaliser ma commande maintenant

Questions ? Répondez à cet email ou appelez-nous au 01.XX.XX.XX.XX

L'équipe Josmose 💧
            """
        }
    
    def _get_nurturing_template(self) -> Dict[str, str]:
        return {
            "subject": "💡 {name}, 3 raisons de choisir l'osmose inverse",
            "content": """
Bonjour {name},

Saviez-vous que l'eau du robinet contient plus de 2000 substances potentiellement nocives ?

3 FAITS CHOQUANTS :
1️⃣ Les bouteilles plastique coûtent 300x plus cher que l'eau filtrée
2️⃣ 1 famille française = 1500 bouteilles plastique/an dans la nature
3️⃣ L'eau du robinet contient chlore, calcaire, résidus médicamenteux...

✅ NOTRE SOLUTION : Osmose inverse 4 étapes
→ 99% des contaminants éliminés
→ Goût neutre, idéal pour bébés et personnes sensibles
→ Installation en 30 minutes sans électricien

📞 Consultation gratuite : Nos experts analysent votre eau

Prenez soin de votre famille,
L'équipe Josmoze.com 🌿
            """
        }
    
    def _get_promotion_template(self) -> Dict[str, str]:
        return {
            "subject": "🎉 FLASH SALE : -25% sur tous nos osmoseurs !",
            "content": """
{name}, une opportunité exceptionnelle !

⚡ VENTE FLASH 48H SEULEMENT ⚡
-25% sur TOUS nos systèmes d'osmose inverse !

OSMOSEUR PREMIUM : 374€ au lieu de 499€
+ Installation offerte (valeur 150€)
+ Garantie 3 ans gratuite

💰 ÉCONOMIES TOTALES : 275€ !

Cette offre se termine le {date_expiration}

🏃‍♂️ STOCK LIMITÉ - Ne tardez pas !

Code promo : FLASH25

Commander maintenant >>

Votre santé n'a pas de prix, mais nos prix si ! 😉

L'équipe Josmoze.com
            """
        }
    
    def _get_followup_template(self) -> Dict[str, str]:
        return {
            "subject": "Comment va votre nouveau système Josmose ? ⭐",
            "content": """
Bonjour {name},

Cela fait maintenant 2 semaines que vous avez reçu votre système Josmose !

Comment se passe votre expérience ?

📋 PETIT RAPPEL UTILE :
✅ Changement des filtres dans 4 mois  
✅ Rinçage hebdomadaire recommandé
✅ Support technique gratuit à vie

🎁 BONUS CLIENT :
- 15% sur vos prochains filtres
- Accès VIP à nos nouvelles gammes
- Programme parrainage (50€ par filleul)

Une question ? Répondez à cet email !

Merci de nous faire confiance,
L'équipe Josmoze.com 💙

P.S. Laissez-nous un avis 5⭐ et recevez 10€ offerts !
            """
        }
    
    def _get_fallback_email(self, template_type: str, customer_data: Dict) -> Dict[str, str]:
        """Fallback email if AI generation fails"""
        return {
            "subject": "Josmoze.com - Votre spécialiste osmose inverse",
            "content": f"""
Bonjour {customer_data.get('name', 'Cher client')},

Merci pour votre intérêt pour nos systèmes d'osmose inverse.

Notre équipe vous contactera prochainement.

Cordialement,
L'équipe Josmoze.com
            """
        }

class WhatsAppAgent:
    """AI Agent for WhatsApp automation (B2C)"""
    
    def __init__(self, db):
        self.db = db
        self.twilio_account_sid = os.getenv("TWILIO_ACCOUNT_SID", "")
        self.twilio_auth_token = os.getenv("TWILIO_AUTH_TOKEN", "")
    
    async def send_whatsapp_message(self, to_number: str, message_type: str, customer_data: Dict) -> bool:
        """Send WhatsApp message (would integrate with Twilio WhatsApp API)"""
        
        templates = {
            "welcome": "🌊 Bonjour {name} ! Bienvenue chez Josmose. Votre système d'osmose vous attend avec -10% : BIENVENUE10",
            "cart_reminder": "⏰ {name}, finalisez votre commande osmoseur en 1 clic ! -10% avec RETOUR10 (expire ce soir)",
            "promotion": "🎉 FLASH ! -25% sur tous nos osmoseurs aujourd'hui seulement ! Code: FLASH25",
            "follow_up": "Bonjour {name} ! Comment allez-vous avec votre nouveau système Josmose ? Questions ?"
        }
        
        message = templates.get(message_type, templates["welcome"]).format(
            name=customer_data.get('name', 'Cher client')
        )
        
        # Log message instead of sending (for development)
        logger.info(f"WhatsApp to {to_number}: {message}")
        
        # Store message in database
        await self.db.whatsapp_logs.insert_one({
            "to_number": to_number,
            "message": message,
            "message_type": message_type,
            "customer_data": customer_data,
            "sent_at": datetime.utcnow(),
            "status": "sent"
        })
        
        return True

class SMSAgent:
    """AI Agent for SMS automation (B2B preferred)"""
    
    def __init__(self, db):
        self.db = db
        self.twilio_account_sid = os.getenv("TWILIO_ACCOUNT_SID", "")
        self.twilio_auth_token = os.getenv("TWILIO_AUTH_TOKEN", "")
    
    async def send_sms(self, to_number: str, message_type: str, customer_data: Dict) -> bool:
        """Send SMS message"""
        
        templates = {
            "consultation_reminder": "📞 {name}, n'oubliez pas votre consultation osmose gratuite demain à {time}. Questions ? Répondez STOP.",
            "quote_ready": "💼 {name}, votre devis osmose professionnel est prêt ! Consultez-le: [lien]. Support: 01.XX.XX",
            "promo_b2b": "🏢 {name}, -20% sur solutions pro osmose ce mois ! Consultation gratuite: 01.XX.XX. STOP=stop",
            "follow_up": "Bonjour {name}, comment se passe votre installation osmose ? Notre expert reste dispo. STOP=stop"
        }
        
        message = templates.get(message_type, templates["follow_up"]).format(
            name=customer_data.get('name', 'Cher client'),
            time=customer_data.get('consultation_time', '14h00')
        )
        
        # Log message
        logger.info(f"SMS to {to_number}: {message}")
        
        # Store in database
        await self.db.sms_logs.insert_one({
            "to_number": to_number,
            "message": message,
            "message_type": message_type,
            "customer_data": customer_data,
            "sent_at": datetime.utcnow(),
            "status": "sent"
        })
        
        return True

class MarketingAutomation:
    """Main marketing automation orchestrator"""
    
    def __init__(self, db):
        self.db = db
        self.email_agent = AIEmailAgent(db)
        self.whatsapp_agent = WhatsAppAgent(db)
        self.sms_agent = SMSAgent(db)
    
    async def trigger_welcome_sequence(self, lead_data: Dict):
        """Trigger welcome sequence based on customer type"""
        
        customer_type = lead_data.get('customer_type', 'B2C')
        
        if customer_type == 'B2C':
            # B2C: Email + WhatsApp if phone available
            await self.email_agent.generate_email_content("welcome", lead_data)
            
            if lead_data.get('phone'):
                await self.whatsapp_agent.send_whatsapp_message(
                    lead_data['phone'], "welcome", lead_data
                )
        else:
            # B2B: Email + SMS
            await self.email_agent.generate_email_content("welcome", lead_data)
            
            if lead_data.get('phone'):
                await self.sms_agent.send_sms(
                    lead_data['phone'], "consultation_reminder", lead_data
                )
    
    async def trigger_abandoned_cart_sequence(self, customer_email: str, cart_data: Dict):
        """Trigger abandoned cart recovery sequence"""
        
        # Get customer data
        customer_data = await self.db.leads.find_one({"email": customer_email})
        if not customer_data:
            return
        
        # Send immediate email
        await self.email_agent.generate_email_content("abandoned_cart", customer_data)
        
        # Schedule follow-up messages
        await self._schedule_followup_sequence(customer_data, "abandoned_cart")
    
    async def trigger_lead_nurturing(self, lead_id: str):
        """Trigger lead nurturing sequence"""
        
        lead_data = await self.db.leads.find_one({"id": lead_id})
        if not lead_data:
            return
        
        # Send nurturing email
        await self.email_agent.generate_email_content("lead_nurturing", lead_data)
        
        # Schedule next nurturing email in 3 days
        await self._schedule_delayed_action(
            action="nurturing_followup",
            data=lead_data,
            delay_days=3
        )
    
    async def _schedule_followup_sequence(self, customer_data: Dict, sequence_type: str):
        """Schedule follow-up messages"""
        
        # This would integrate with a job scheduler like Celery
        # For now, just log the scheduled actions
        
        schedule = {
            "abandoned_cart": [
                {"delay_hours": 2, "type": "whatsapp", "message": "cart_reminder"},
                {"delay_days": 1, "type": "email", "message": "abandoned_cart"},
                {"delay_days": 3, "type": "sms", "message": "final_reminder"}
            ],
            "lead_nurturing": [
                {"delay_days": 2, "type": "email", "message": "nurturing"},
                {"delay_days": 7, "type": "whatsapp", "message": "check_in"},
                {"delay_days": 14, "type": "email", "message": "promotion"}
            ]
        }
        
        for action in schedule.get(sequence_type, []):
            await self.db.scheduled_actions.insert_one({
                "customer_email": customer_data.get('email'),
                "action_type": action['type'],
                "message_type": action['message'],
                "customer_data": customer_data,
                "scheduled_for": datetime.utcnow() + timedelta(
                    days=action.get('delay_days', 0),
                    hours=action.get('delay_hours', 0)
                ),
                "status": "pending",
                "created_at": datetime.utcnow()
            })
    
    async def _schedule_delayed_action(self, action: str, data: Dict, delay_days: int):
        """Schedule a delayed action"""
        
        await self.db.scheduled_actions.insert_one({
            "action_type": action,
            "data": data,
            "scheduled_for": datetime.utcnow() + timedelta(days=delay_days),
            "status": "pending",
            "created_at": datetime.utcnow()
        })

# Global marketing automation instance
marketing_automation = None

def get_marketing_automation(db):
    global marketing_automation
    if marketing_automation is None:
        marketing_automation = MarketingAutomation(db)
    return marketing_automation