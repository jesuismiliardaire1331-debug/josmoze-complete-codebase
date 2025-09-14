"""
Email Sequencer Osmoseur - Système de marketing automation GDPR-compliant
Séquence automatique de 3 emails pour prospects avec respect liste suppression
"""

import os
import uuid
import smtplib
import asyncio
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
from email.mime.base import MimeBase
from jinja2 import Template
import logging

class EmailSequencerManager:
    def __init__(self, db, suppression_manager):
        self.db = db
        self.suppression_manager = suppression_manager
        self.prospects_collection = db.prospects
        self.sequences_collection = db.email_sequences
        self.metrics_collection = db.email_metrics
        self.gdpr_journal = db.gdpr_journal
        
        # Configuration SMTP
        self.smtp_host = os.environ.get('SMTP_HOST', 'smtp.gmail.com')
        self.smtp_port = int(os.environ.get('SMTP_PORT', '587'))
        self.smtp_username = os.environ.get('SMTP_USERNAME', 'contact@josmoze.com')
        self.smtp_password = os.environ.get('SMTP_PASSWORD', '')
        self.from_name = "Josmoze"
        self.from_email = "contact@josmoze.com"
        self.base_url = "https://www.josmoze.com"
        
        # Templates d'emails
        self.email_templates = {
            "email1": {
                "subject": "Votre eau mérite mieux 💧",
                "delay_days": 0,
                "utm_content": "email1",
                "template": """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ subject }}</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }
        .content { background: white; padding: 30px; border: 1px solid #e0e0e0; }
        .cta-button { display: inline-block; background: #007bff; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; font-weight: bold; margin: 20px 0; }
        .benefits { background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0; }
        .benefit-item { margin: 10px 0; }
        .offer { background: #e7f3ff; border-left: 4px solid #007bff; padding: 20px; margin: 20px 0; }
        .footer { background: #f8f9fa; padding: 20px; text-align: center; font-size: 12px; color: #666; border-radius: 0 0 10px 10px; }
        @media (max-width: 600px) { body { padding: 10px; } .header, .content { padding: 20px; } }
    </style>
</head>
<body>
    <div class="header">
        <h1>💧 Josmoze.com</h1>
        <h2>Votre eau mérite mieux</h2>
    </div>
    
    <div class="content">
        <p>Bonjour {{ first_name or '' }},</p>
        
        <p>Savez-vous que <strong>99 % des contaminants de l'eau du robinet</strong> peuvent être éliminés en quelques minutes ?</p>
        
        <p>Découvrez notre <strong>osmoseur nouvelle génération</strong> :</p>
        
        <div class="benefits">
            <div class="benefit-item">✔️ <strong>Eau plus pure et plus saine</strong> - Élimine chlore, nitrates, calcaire</div>
            <div class="benefit-item">✔️ <strong>Économies importantes</strong> - Jusqu'à 700 €/an vs. eau en bouteille</div>
            <div class="benefit-item">✔️ <strong>Installation simple</strong> - Posé en moins d'1 heure</div>
        </div>
        
        <div class="offer">
            <h3>💧 Offre de lancement</h3>
            <p><strong>549 € TTC</strong> (au lieu de 649 €)</p>
            <p>Ou <strong>3× 183 € sans frais</strong></p>
            <p>🎁 <strong>Filtres année 1 offerts</strong> (valeur 109 €)</p>
        </div>
        
        <div style="text-align: center;">
            <a href="{{ cta_link }}" class="cta-button">Je découvre maintenant</a>
        </div>
        
        <p>Cette offre est limitée dans le temps. Ne laissez pas passer cette opportunité d'améliorer votre qualité de vie !</p>
        
        <p>Cordialement,<br>
        <strong>L'équipe Josmoze</strong><br>
        Spécialiste des systèmes d'osmose inverse</p>
    </div>
    
    <div class="footer">
        <p>Josmoze.com - Spécialiste européen des systèmes d'osmose inverse</p>
        <p>Vos données sont protégées selon le RGPD</p>
        <p><a href="{{ unsubscribe_link }}" style="color: #666;">Se désinscrire</a></p>
    </div>
</body>
</html>
                """
            },
            "email2": {
                "subject": "Et si vous goûtiez la différence ?",
                "delay_days": 2,
                "utm_content": "email2",
                "template": """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ subject }}</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: linear-gradient(135deg, #28a745 0%, #20c997 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }
        .content { background: white; padding: 30px; border: 1px solid #e0e0e0; }
        .cta-button { display: inline-block; background: #28a745; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; font-weight: bold; margin: 20px 0; }
        .testimonial { background: #f8f9fa; border-left: 4px solid #28a745; padding: 20px; margin: 20px 0; font-style: italic; }
        .offer { background: #d4edda; border: 1px solid #c3e6cb; padding: 20px; margin: 20px 0; border-radius: 8px; }
        .footer { background: #f8f9fa; padding: 20px; text-align: center; font-size: 12px; color: #666; border-radius: 0 0 10px 10px; }
        @media (max-width: 600px) { body { padding: 10px; } .header, .content { padding: 20px; } }
    </style>
</head>
<body>
    <div class="header">
        <h1>💧 Josmoze.com</h1>
        <h2>Et si vous goûtiez la différence ?</h2>
    </div>
    
    <div class="content">
        <p>Bonjour {{ first_name or '' }},</p>
        
        <p>Avez-vous déjà goûté <strong>une eau aussi pure qu'en montagne</strong>, directement au robinet ?</p>
        
        <p>Notre osmoseur élimine :</p>
        <ul>
            <li>🚫 <strong>Chlore</strong> - Fini le goût et l'odeur désagréables</li>
            <li>🚫 <strong>Nitrates</strong> - Protection pour toute la famille</li>
            <li>🚫 <strong>Calcaire</strong> - Eau douce et pure</li>
            <li>🚫 <strong>Microplastiques</strong> - Santé préservée</li>
        </ul>
        
        <div class="testimonial">
            "Depuis l'installation de notre osmoseur Josmoze, nous avons redécouvert le plaisir de boire l'eau du robinet. Nos enfants adorent et nous économisons plus de 50€ par mois !"<br>
            <strong>- Marie D., Maman de 3 enfants</strong>
        </div>
        
        <div class="offer">
            <h3>⏰ Offre encore valable</h3>
            <p><strong>549 € TTC</strong> au lieu de 649 €</p>
            <p><strong>Paiement 3× sans frais disponible</strong></p>
            <p>Installation comprise + Garantie 2 ans</p>
        </div>
        
        <div style="text-align: center;">
            <a href="{{ cta_link }}" class="cta-button">Je commande mon osmoseur</a>
        </div>
        
        <p>Confort, santé, économies : rejoignez les milliers de familles qui ont fait le choix de l'eau pure !</p>
        
        <p>Cordialement,<br>
        <strong>L'équipe Josmoze</strong></p>
    </div>
    
    <div class="footer">
        <p>Josmoze.com - Spécialiste européen des systèmes d'osmose inverse</p>
        <p><a href="{{ unsubscribe_link }}" style="color: #666;">Se désinscrire</a></p>
    </div>
</body>
</html>
                """
            },
            "email3": {
                "subject": "Derniers jours pour profiter de l'offre spéciale 🚨",
                "delay_days": 5,
                "utm_content": "email3",
                "template": """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ subject }}</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: linear-gradient(135deg, #dc3545 0%, #fd7e14 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }
        .content { background: white; padding: 30px; border: 1px solid #e0e0e0; }
        .cta-button { display: inline-block; background: #dc3545; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; font-weight: bold; margin: 20px 0; font-size: 18px; }
        .urgency { background: #f8d7da; border: 1px solid #f5c6cb; padding: 20px; margin: 20px 0; border-radius: 8px; text-align: center; }
        .final-offer { background: #fff3cd; border: 1px solid #ffeaa7; padding: 20px; margin: 20px 0; border-radius: 8px; }
        .countdown { background: #dc3545; color: white; padding: 15px; text-align: center; font-weight: bold; font-size: 16px; margin: 20px 0; border-radius: 5px; }
        .footer { background: #f8f9fa; padding: 20px; text-align: center; font-size: 12px; color: #666; border-radius: 0 0 10px 10px; }
        @media (max-width: 600px) { body { padding: 10px; } .header, .content { padding: 20px; } }
    </style>
</head>
<body>
    <div class="header">
        <h1>🚨 Josmoze.com</h1>
        <h2>Dernière chance !</h2>
    </div>
    
    <div class="content">
        <p>Bonjour {{ first_name or '' }},</p>
        
        <div class="urgency">
            <h3>⏰ ATTENTION : Offre expire bientôt</h3>
            <p>Il ne vous reste que quelques jours pour profiter de notre promotion de lancement !</p>
        </div>
        
        <p><strong>Dernière chance</strong> de bénéficier de notre offre exceptionnelle :</p>
        
        <div class="final-offer">
            <h3>🎯 Récapitulatif de l'offre</h3>
            <p>✔️ <strong>Osmoseur à 549 € TTC</strong> au lieu de 649 €</p>
            <p>✔️ <strong>3× sans frais disponible</strong> (183 € x 3)</p>
            <p>✔️ <strong>1 an de filtres offert</strong> (valeur 109 €)</p>
            <p>✔️ <strong>Installation comprise</strong></p>
            <p>✔️ <strong>Garantie 2 ans</strong></p>
        </div>
        
        <div class="countdown">
            ⚠️ Après cette date, le prix repasse à 649 € ⚠️
        </div>
        
        <p>Ne laissez pas passer cette opportunité unique d'équiper votre foyer avec le meilleur de la technologie d'osmose inverse !</p>
        
        <div style="text-align: center;">
            <a href="{{ cta_link }}" class="cta-button">🚀 Commander maintenant</a>
        </div>
        
        <p><strong>Plus de 2000 familles</strong> nous font déjà confiance. Rejoignez-les !</p>
        
        <p>Cordialement,<br>
        <strong>L'équipe Josmoze</strong><br>
        <em>Il était temps de changer votre façon de boire l'eau !</em></p>
    </div>
    
    <div class="footer">
        <p>Josmoze.com - Spécialiste européen des systèmes d'osmose inverse</p>
        <p><a href="{{ unsubscribe_link }}" style="color: #666;">Se désinscrire</a></p>
    </div>
</body>
</html>
                """
            }
        }
    
    async def create_indexes(self):
        """Créer les index pour optimiser les performances"""
        try:
            # Index pour les séquences
            await self.sequences_collection.create_index([("prospect_email", 1)])
            await self.sequences_collection.create_index([("sequence_id", 1)])
            await self.sequences_collection.create_index([("step", 1)])
            await self.sequences_collection.create_index([("scheduled_at", 1)])
            await self.sequences_collection.create_index([("status", 1)])
            
            # Index pour les métriques
            await self.metrics_collection.create_index([("sequence_id", 1)])
            await self.metrics_collection.create_index([("prospect_email", 1)])
            await self.metrics_collection.create_index([("step", 1)])
            await self.metrics_collection.create_index([("event_type", 1)])
            await self.metrics_collection.create_index([("created_at", -1)])
            
            print("✅ Index email_sequences et email_metrics créés")
            
        except Exception as e:
            print(f"⚠️ Erreur lors de la création des index: {e}")
    
    async def start_email_sequence(self, test_mode: bool = False, test_emails: List[str] = None, agent_email: str = "system") -> Dict[str, Any]:
        """Démarrer une nouvelle séquence d'emails"""
        try:
            # Générer un ID unique pour cette séquence
            sequence_id = str(uuid.uuid4())
            
            # Obtenir les prospects éligibles
            if test_mode and test_emails:
                # Mode test avec emails spécifiques
                eligible_prospects = []
                for email in test_emails:
                    prospect = await self.prospects_collection.find_one({"email": email})
                    if prospect:
                        eligible_prospects.append(prospect)
                    else:
                        # Créer un prospect de test temporaire
                        eligible_prospects.append({
                            "email": email,
                            "first_name": "Test",
                            "status": "new",
                            "created_at": datetime.now(timezone.utc)
                        })
            else:
                # Mode production - prospects avec status="new"
                cursor = self.prospects_collection.find({
                    "status": "new",
                    "email": {"$exists": True, "$ne": ""}
                })
                eligible_prospects = await cursor.to_list(length=None)
            
            print(f"📧 Prospects éligibles trouvés: {len(eligible_prospects)}")
            
            # Filtrer les emails supprimés et génériques
            filtered_prospects = []
            skipped_count = 0
            
            for prospect in eligible_prospects:
                email = prospect.get("email", "")
                
                # Vérifier la liste de suppression
                is_suppressed = await self.suppression_manager.is_email_suppressed(email)
                if is_suppressed:
                    skipped_count += 1
                    # Journaliser le skip
                    await self.log_email_event(
                        sequence_id=sequence_id,
                        prospect_email=email,
                        step="email1",
                        event_type="skipped_suppressed",
                        details="Email in suppression list"
                    )
                    continue
                
                # Filtrer les emails génériques
                generic_prefixes = ["info@", "contact@", "sales@", "support@", "admin@", "noreply@"]
                if any(email.lower().startswith(prefix) for prefix in generic_prefixes):
                    skipped_count += 1
                    await self.log_email_event(
                        sequence_id=sequence_id,
                        prospect_email=email,
                        step="email1",
                        event_type="skipped_generic",
                        details="Generic email address"
                    )
                    continue
                
                filtered_prospects.append(prospect)
            
            print(f"📧 Prospects après filtrage: {len(filtered_prospects)} (ignorés: {skipped_count})")
            
            # Créer les entrées de séquence pour chaque prospect
            sequence_entries = []
            current_time = datetime.now(timezone.utc)
            
            for prospect in filtered_prospects:
                for step_name, template_config in self.email_templates.items():
                    # Calculer la date d'envoi
                    delay_days = template_config["delay_days"]
                    scheduled_at = current_time + timedelta(days=delay_days)
                    
                    # Éviter les week-ends pour Email 3 (délai de 5 jours -> 7 jours si weekend)
                    if step_name == "email3" and scheduled_at.weekday() >= 5:  # Samedi (5) ou Dimanche (6)
                        # Reporter au lundi suivant
                        days_to_monday = 7 - scheduled_at.weekday()
                        scheduled_at += timedelta(days=days_to_monday)
                    
                    sequence_entry = {
                        "sequence_id": sequence_id,
                        "prospect_email": prospect.get("email"),
                        "prospect_first_name": prospect.get("first_name", ""),
                        "step": step_name,
                        "status": "scheduled",
                        "scheduled_at": scheduled_at,
                        "created_at": current_time,
                        "test_mode": test_mode
                    }
                    sequence_entries.append(sequence_entry)
            
            # Insérer les entrées de séquence
            if sequence_entries:
                await self.sequences_collection.insert_many(sequence_entries)
            
            # Envoyer immédiatement l'Email 1 (J+0)
            email1_entries = [entry for entry in sequence_entries if entry["step"] == "email1"]
            sent_count = 0
            
            for entry in email1_entries:
                success = await self.send_email(
                    sequence_id=sequence_id,
                    prospect_email=entry["prospect_email"],
                    prospect_first_name=entry["prospect_first_name"],
                    step="email1",
                    test_mode=test_mode
                )
                
                if success:
                    sent_count += 1
                    # Marquer l'entrée comme envoyée
                    await self.sequences_collection.update_one(
                        {"sequence_id": sequence_id, "prospect_email": entry["prospect_email"], "step": "email1"},
                        {"$set": {"status": "sent", "sent_at": datetime.now(timezone.utc)}}
                    )
                    
                    # Mettre à jour le statut du prospect
                    await self.prospects_collection.update_one(
                        {"email": entry["prospect_email"]},
                        {
                            "$set": {
                                "status": "contacted",
                                "last_contacted_at": datetime.now(timezone.utc)
                            }
                        }
                    )
            
            # Journaliser le lancement de séquence
            await self.suppression_manager.log_gdpr_action(
                action_type="email_sequence_started",
                email="",
                details=f"Started sequence {sequence_id}: {sent_count} sent, {skipped_count} skipped",
                agent_email=agent_email
            )
            
            return {
                "success": True,
                "sequence_id": sequence_id,
                "total_prospects": len(eligible_prospects),
                "filtered_prospects": len(filtered_prospects),
                "skipped_count": skipped_count,
                "email1_sent": sent_count,
                "test_mode": test_mode
            }
            
        except Exception as e:
            logging.error(f"Erreur lors du démarrage de séquence: {e}")
            return {"success": False, "error": str(e)}
    
    async def send_email(self, sequence_id: str, prospect_email: str, prospect_first_name: str, step: str, test_mode: bool = False) -> bool:
        """Envoyer un email de la séquence"""
        try:
            # Vérifier une dernière fois la liste de suppression
            is_suppressed = await self.suppression_manager.is_email_suppressed(prospect_email)
            if is_suppressed:
                await self.log_email_event(
                    sequence_id=sequence_id,
                    prospect_email=prospect_email,
                    step=step,
                    event_type="skipped_suppressed",
                    details="Email suppressed at send time"
                )
                return False
            
            # Obtenir le template d'email
            template_config = self.email_templates.get(step)
            if not template_config:
                raise ValueError(f"Template non trouvé pour step: {step}")
            
            # Générer le lien de désinscription
            unsubscribe_link = self.suppression_manager.build_unsubscribe_link(prospect_email)
            
            # Générer le lien CTA avec UTM tracking
            cta_link = f"{self.base_url}/acheter?utm_source=email&utm_campaign=osmozeur_seq1&utm_content={template_config['utm_content']}"
            
            # Rendu du template
            template = Template(template_config["template"])
            html_content = template.render(
                subject=template_config["subject"],
                first_name=prospect_first_name,
                cta_link=cta_link,
                unsubscribe_link=unsubscribe_link
            )
            
            # Créer le message email
            msg = MimeMultipart('alternative')
            msg['Subject'] = template_config["subject"]
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = prospect_email
            
            # Version HTML
            html_part = MimeText(html_content, 'html', 'utf-8')
            msg.attach(html_part)
            
            # Envoyer l'email
            if test_mode:
                # Mode test - simuler l'envoi
                print(f"📧 TEST MODE - Email {step} simulé pour {prospect_email}")
                await self.log_email_event(
                    sequence_id=sequence_id,
                    prospect_email=prospect_email,
                    step=step,
                    event_type="sent",
                    details="Test mode - simulated send"
                )
                return True
            else:
                # Mode production - envoi réel
                try:
                    with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                        server.starttls()
                        if self.smtp_password:
                            server.login(self.smtp_username, self.smtp_password)
                        
                        server.send_message(msg)
                    
                    print(f"📧 Email {step} envoyé avec succès à {prospect_email}")
                    
                    # Journaliser l'envoi
                    await self.log_email_event(
                        sequence_id=sequence_id,
                        prospect_email=prospect_email,
                        step=step,
                        event_type="sent",
                        details="Email sent successfully"
                    )
                    
                    return True
                    
                except smtplib.SMTPException as e:
                    print(f"❌ Erreur SMTP pour {prospect_email}: {e}")
                    
                    # Déterminer le type d'erreur
                    error_str = str(e).lower()
                    if "550" in error_str or "5.1.1" in error_str:
                        event_type = "hard_bounce"
                        # Ajouter automatiquement à la liste de suppression
                        await self.suppression_manager.add_email_to_suppression_list(
                            email=prospect_email,
                            reason="hard_bounce",
                            source="email_sequencer",
                            notes=f"Hard bounce from step {step}: {str(e)}",
                            agent_email="email_sequencer"
                        )
                    else:
                        event_type = "soft_bounce"
                    
                    await self.log_email_event(
                        sequence_id=sequence_id,
                        prospect_email=prospect_email,
                        step=step,
                        event_type=event_type,
                        details=str(e)
                    )
                    
                    return False
            
        except Exception as e:
            print(f"❌ Erreur lors de l'envoi email: {e}")
            await self.log_email_event(
                sequence_id=sequence_id,
                prospect_email=prospect_email,
                step=step,
                event_type="error",
                details=str(e)
            )
            return False
    
    async def process_scheduled_emails(self) -> Dict[str, Any]:
        """Traiter les emails programmés (à appeler périodiquement)"""
        try:
            current_time = datetime.now(timezone.utc)
            
            # Trouver les emails à envoyer
            cursor = self.sequences_collection.find({
                "status": "scheduled",
                "scheduled_at": {"$lte": current_time}
            })
            
            scheduled_emails = await cursor.to_list(length=None)
            print(f"📧 Emails programmés à traiter: {len(scheduled_emails)}")
            
            sent_count = 0
            error_count = 0
            
            for email_entry in scheduled_emails:
                try:
                    success = await self.send_email(
                        sequence_id=email_entry["sequence_id"],
                        prospect_email=email_entry["prospect_email"],
                        prospect_first_name=email_entry["prospect_first_name"],
                        step=email_entry["step"],
                        test_mode=email_entry.get("test_mode", False)
                    )
                    
                    if success:
                        sent_count += 1
                        # Marquer comme envoyé
                        await self.sequences_collection.update_one(
                            {"_id": email_entry["_id"]},
                            {"$set": {"status": "sent", "sent_at": current_time}}
                        )
                    else:
                        error_count += 1
                        # Marquer comme erreur
                        await self.sequences_collection.update_one(
                            {"_id": email_entry["_id"]},
                            {"$set": {"status": "error", "error_at": current_time}}
                        )
                        
                except Exception as e:
                    print(f"❌ Erreur traitement email programmé: {e}")
                    error_count += 1
            
            return {
                "success": True,
                "processed": len(scheduled_emails),
                "sent": sent_count,
                "errors": error_count
            }
            
        except Exception as e:
            print(f"❌ Erreur traitement emails programmés: {e}")
            return {"success": False, "error": str(e)}
    
    async def log_email_event(self, sequence_id: str, prospect_email: str, step: str, event_type: str, details: str = ""):
        """Journaliser un événement email"""
        try:
            event_entry = {
                "sequence_id": sequence_id,
                "prospect_email": prospect_email,
                "step": step,
                "event_type": event_type,  # sent, delivered, opened, clicked, bounced, skipped_suppressed, error
                "details": details,
                "created_at": datetime.now(timezone.utc)
            }
            
            await self.metrics_collection.insert_one(event_entry)
            
        except Exception as e:
            print(f"❌ Erreur journalisation événement: {e}")
    
    async def get_sequence_metrics(self, sequence_id: str = None, limit: int = 100) -> Dict[str, Any]:
        """Obtenir les métriques des séquences"""
        try:
            # Filtres
            match_filter = {}
            if sequence_id:
                match_filter["sequence_id"] = sequence_id
            
            # Métriques générales
            pipeline = [
                {"$match": match_filter},
                {"$group": {
                    "_id": {
                        "sequence_id": "$sequence_id",
                        "step": "$step",
                        "event_type": "$event_type"
                    },
                    "count": {"$sum": 1}
                }}
            ]
            
            metrics_raw = await self.metrics_collection.aggregate(pipeline).to_list(length=None)
            
            # Organiser les métriques
            metrics = {}
            for metric in metrics_raw:
                seq_id = metric["_id"]["sequence_id"]
                step = metric["_id"]["step"]
                event_type = metric["_id"]["event_type"]
                count = metric["count"]
                
                if seq_id not in metrics:
                    metrics[seq_id] = {}
                if step not in metrics[seq_id]:
                    metrics[seq_id][step] = {}
                
                metrics[seq_id][step][event_type] = count
            
            # Séquences actives
            active_sequences = await self.sequences_collection.distinct("sequence_id")
            
            # Métriques détaillées par prospect
            cursor = self.metrics_collection.find(match_filter).sort("created_at", -1).limit(limit)
            recent_events = await cursor.to_list(length=None)
            
            # Supprimer les ObjectId
            for event in recent_events:
                if '_id' in event:
                    del event['_id']
                if 'created_at' in event:
                    event['created_at'] = event['created_at'].isoformat()
            
            return {
                "success": True,
                "metrics": metrics,
                "active_sequences": active_sequences,
                "recent_events": recent_events
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def get_sequence_status(self, sequence_id: str) -> Dict[str, Any]:
        """Obtenir le statut d'une séquence spécifique"""
        try:
            # Statuts des emails de la séquence
            cursor = self.sequences_collection.find({"sequence_id": sequence_id})
            sequence_entries = await cursor.to_list(length=None)
            
            # Métriques de la séquence
            metrics = await self.get_sequence_metrics(sequence_id)
            
            # Organiser par prospect
            prospects_status = {}
            for entry in sequence_entries:
                email = entry["prospect_email"]
                if email not in prospects_status:
                    prospects_status[email] = {
                        "first_name": entry["prospect_first_name"],
                        "steps": {}
                    }
                
                prospects_status[email]["steps"][entry["step"]] = {
                    "status": entry["status"],
                    "scheduled_at": entry["scheduled_at"].isoformat() if entry.get("scheduled_at") else None,
                    "sent_at": entry["sent_at"].isoformat() if entry.get("sent_at") else None
                }
            
            return {
                "success": True,
                "sequence_id": sequence_id,
                "prospects": prospects_status,
                "metrics": metrics.get("metrics", {}).get(sequence_id, {})
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def stop_sequence(self, sequence_id: str, agent_email: str = "system") -> Dict[str, Any]:
        """Arrêter une séquence (annuler les emails non envoyés)"""
        try:
            # Marquer les emails programmés comme annulés
            result = await self.sequences_collection.update_many(
                {"sequence_id": sequence_id, "status": "scheduled"},
                {"$set": {"status": "cancelled", "cancelled_at": datetime.now(timezone.utc)}}
            )
            
            # Journaliser l'arrêt
            await self.suppression_manager.log_gdpr_action(
                action_type="email_sequence_stopped",
                email="",
                details=f"Stopped sequence {sequence_id}: {result.modified_count} emails cancelled",
                agent_email=agent_email
            )
            
            return {
                "success": True,
                "sequence_id": sequence_id,
                "cancelled_emails": result.modified_count
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}