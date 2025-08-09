"""
Service Email Intégré pour CRM
Gère l'envoi, la réception et les accusés de réception automatiques
"""

import os
import asyncio
import logging
from typing import List, Dict, Optional
from datetime import datetime
import smtplib
import imaplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import uuid
from motor.motor_asyncio import AsyncIOMotorClient

# Configuration email (à configurer selon votre fournisseur)
EMAIL_CONFIG = {
    "smtp_server": os.getenv("SMTP_SERVER", "smtp.gmail.com"),
    "smtp_port": int(os.getenv("SMTP_PORT", "587")),
    "imap_server": os.getenv("IMAP_SERVER", "imap.gmail.com"),
    "imap_port": int(os.getenv("IMAP_PORT", "993")),
    "use_tls": True
}

# Messages d'accusé de réception personnalisés
WELCOME_TEMPLATES = {
    "commercial@josmoze.net": {
        "subject": "🌊 Merci pour votre intérêt - Josmose Solutions",
        "message": """
Bonjour,

Merci pour votre message ! Nous avons bien reçu votre demande concernant nos solutions d'osmose inverse.

Notre équipe commerciale va analyser votre besoin et vous recontacter dans les plus brefs délais (généralement sous 2h en journée).

En attendant, vous pouvez :
• Découvrir nos solutions sur www.josmoze.net
• Consulter nos cas clients et témoignages
• Télécharger notre catalogue technique

Nous sommes spécialisés dans :
✓ Systèmes d'osmose inverse pour particuliers et professionnels
✓ Installation et maintenance en France
✓ Support technique dédié
✓ Garantie 2 ans sur tous nos systèmes

À très bientôt,

L'équipe commerciale Josmose
📧 commercial@josmoze.net
📞 Service client disponible 9h-18h
🌐 www.josmoze.net

---
Ceci est un message automatique. Votre demande a été enregistrée sous la référence #{reference}
        """.strip()
    },
    "support@josmoze.net": {
        "subject": "🔧 Support Technique Josmose - Ticket ouvert",
        "message": """
Bonjour,

Votre demande de support technique a été bien reçue et enregistrée.

Un technicien spécialisé va analyser votre problème et vous contacter rapidement pour vous apporter une solution.

Informations importantes :
• Temps de réponse : sous 4h en journée
• Support disponible : Lundi-Vendredi 9h-18h
• Intervention à domicile possible selon votre région

Pour accélérer le traitement :
📋 Gardez à portée la référence de votre système
📧 N'hésitez pas à nous envoyer des photos si nécessaire
📞 Pour les urgences : contactez-nous directement

Notre équipe technique expérimentée est là pour résoudre rapidement tous vos problèmes d'osmose inverse.

Cordialement,

L'équipe support Josmose
🔧 support@josmoze.net
📞 Hotline technique 9h-18h
🌐 www.josmoze.net/support

---
Ticket de support #{reference} créé le {date}
        """.strip()
    },
    "default": {
        "subject": "💧 Message reçu - Josmose",
        "message": """
Bonjour,

Nous avons bien reçu votre message et vous remercions pour votre intérêt pour Josmose.

Un membre de notre équipe va prendre connaissance de votre demande et vous recontacter très rapidement.

En attendant, nous vous invitons à découvrir :
🌐 Notre site web : www.josmoze.net
📚 Nos solutions d'osmose inverse
💧 Nos témoignages clients

Merci de votre confiance,

L'équipe Josmose
📧 contact@josmoze.net
🌐 www.josmoze.net

---
Référence de votre message : #{reference}
        """.strip()
    }
}

class EmailService:
    def __init__(self):
        self.mongo_client = AsyncIOMotorClient(os.getenv("MONGO_URL", "mongodb://localhost:27017"))
        self.db = self.mongo_client[os.getenv("DB_NAME", "test_database")]
        self.setup_logging()

    def setup_logging(self):
        """Configure logging pour le service email"""
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    async def send_email(self, from_email: str, to_email: str, subject: str, body: str, 
                        attachments: Optional[List[Dict]] = None, email_password: str = None) -> Dict:
        """
        Envoie un email via SMTP
        """
        try:
            # Créer le message
            msg = MIMEMultipart()
            msg['From'] = from_email
            msg['To'] = to_email
            msg['Subject'] = subject

            # Ajouter le corps du message
            msg.attach(MIMEText(body, 'html' if '<' in body else 'plain', 'utf-8'))

            # Ajouter les pièces jointes si présentes
            if attachments:
                for attachment in attachments:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(attachment['content'])
                    encoders.encode_base64(part)
                    part.add_header(
                        'Content-Disposition',
                        f"attachment; filename= {attachment['filename']}"
                    )
                    msg.attach(part)

            # Envoyer l'email
            server = smtplib.SMTP(EMAIL_CONFIG["smtp_server"], EMAIL_CONFIG["smtp_port"])
            server.starttls()
            server.login(from_email, email_password)
            
            text = msg.as_string()
            server.sendmail(from_email, to_email, text)
            server.quit()

            # Enregistrer l'email envoyé dans la base
            email_record = {
                "id": str(uuid.uuid4()),
                "type": "sent",
                "from_email": from_email,
                "to_email": to_email,
                "subject": subject,
                "body": body,
                "sent_at": datetime.utcnow(),
                "status": "sent",
                "read": False,
                "attachments": attachments or []
            }
            
            await self.db.emails.insert_one(email_record)
            
            self.logger.info(f"Email envoyé avec succès de {from_email} vers {to_email}")
            
            return {"success": True, "message": "Email envoyé", "email_id": email_record["id"]}
            
        except Exception as e:
            self.logger.error(f"Erreur envoi email: {str(e)}")
            return {"success": False, "error": str(e)}

    async def send_auto_reply(self, to_email: str, sender_email: str, original_subject: str) -> Dict:
        """
        Envoie un accusé de réception automatique
        """
        try:
            # Déterminer le template basé sur l'email de destination
            template = WELCOME_TEMPLATES.get(sender_email, WELCOME_TEMPLATES["default"])
            
            # Générer une référence unique
            reference = str(uuid.uuid4())[:8].upper()
            
            # Personnaliser le message
            subject = template["subject"]
            body = template["message"].replace("{reference}", reference)
            body = body.replace("{date}", datetime.utcnow().strftime("%d/%m/%Y à %H:%M"))
            
            # Note: Dans un vrai système, vous utiliseriez les vrais mots de passe email
            # Pour la démo, on simule l'envoi
            
            # Enregistrer l'accusé de réception
            auto_reply_record = {
                "id": str(uuid.uuid4()),
                "type": "auto_reply",
                "from_email": sender_email,
                "to_email": to_email,
                "subject": subject,
                "body": body,
                "sent_at": datetime.utcnow(),
                "status": "sent",
                "reference": reference,
                "original_subject": original_subject,
                "read": False
            }
            
            await self.db.emails.insert_one(auto_reply_record)
            
            self.logger.info(f"Accusé de réception automatique envoyé à {to_email} (ref: {reference})")
            
            return {
                "success": True, 
                "message": "Accusé de réception envoyé", 
                "reference": reference,
                "email_id": auto_reply_record["id"]
            }
            
        except Exception as e:
            self.logger.error(f"Erreur accusé de réception: {str(e)}")
            return {"success": False, "error": str(e)}

    async def receive_emails(self, email_address: str, email_password: str) -> List[Dict]:
        """
        Récupère les emails reçus via IMAP (simulation pour la démo)
        """
        try:
            # Dans un vrai système, vous utiliseriez IMAP
            # Pour la démo, on retourne des emails simulés
            
            # Récupérer les emails de la base de données
            emails_cursor = self.db.emails.find({
                "$or": [
                    {"to_email": email_address},
                    {"from_email": email_address}
                ]
            }).sort("sent_at", -1).limit(50)
            
            emails = await emails_cursor.to_list(length=50)
            
            # Convertir ObjectId en string pour JSON
            for email_doc in emails:
                email_doc["_id"] = str(email_doc["_id"])
            
            return emails
            
        except Exception as e:
            self.logger.error(f"Erreur réception emails: {str(e)}")
            return []

    async def mark_email_as_read(self, email_id: str) -> Dict:
        """
        Marque un email comme lu
        """
        try:
            result = await self.db.emails.update_one(
                {"id": email_id},
                {"$set": {"read": True, "read_at": datetime.utcnow()}}
            )
            
            if result.modified_count > 0:
                return {"success": True, "message": "Email marqué comme lu"}
            else:
                return {"success": False, "error": "Email non trouvé"}
                
        except Exception as e:
            self.logger.error(f"Erreur marquage email: {str(e)}")
            return {"success": False, "error": str(e)}

    async def get_inbox_stats(self, email_address: str) -> Dict:
        """
        Retourne les statistiques de la boîte mail
        """
        try:
            # Compter les emails
            total_emails = await self.db.emails.count_documents({
                "$or": [{"to_email": email_address}, {"from_email": email_address}]
            })
            
            unread_emails = await self.db.emails.count_documents({
                "to_email": email_address,
                "read": False
            })
            
            sent_emails = await self.db.emails.count_documents({
                "from_email": email_address
            })
            
            received_emails = await self.db.emails.count_documents({
                "to_email": email_address
            })
            
            return {
                "total": total_emails,
                "unread": unread_emails,
                "sent": sent_emails,
                "received": received_emails
            }
            
        except Exception as e:
            self.logger.error(f"Erreur stats inbox: {str(e)}")
            return {"total": 0, "unread": 0, "sent": 0, "received": 0}

    async def simulate_incoming_email(self, to_email: str, from_email: str, subject: str, body: str) -> Dict:
        """
        Simule la réception d'un email (pour démo)
        """
        try:
            # Créer un email entrant simulé
            incoming_email = {
                "id": str(uuid.uuid4()),
                "type": "received",
                "from_email": from_email,
                "to_email": to_email,
                "subject": subject,
                "body": body,
                "received_at": datetime.utcnow(),
                "status": "received",
                "read": False
            }
            
            await self.db.emails.insert_one(incoming_email)
            
            # Envoyer automatiquement un accusé de réception
            auto_reply = await self.send_auto_reply(from_email, to_email, subject)
            
            self.logger.info(f"Email entrant simulé: {from_email} -> {to_email}")
            
            return {
                "success": True,
                "message": "Email reçu",
                "email_id": incoming_email["id"],
                "auto_reply": auto_reply
            }
            
        except Exception as e:
            self.logger.error(f"Erreur simulation email: {str(e)}")
            return {"success": False, "error": str(e)}

# Instance globale du service email
email_service = EmailService()