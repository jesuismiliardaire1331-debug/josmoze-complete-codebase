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
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
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
        
        # Templates d'emails - VERSION V2 OPTIMISEE avec nouveau contenu valide
        self.email_templates = {
            "email1": {
                "subject": "🚨 Sarah, saviez-vous ce que contient VRAIMENT votre eau du robinet ?",
                "delay_days": 0,
                "utm_content": "email1_sensibilisation",
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
        .cta-button { display: inline-block; background: #dc3545; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; font-weight: bold; margin: 20px 0; }
        .danger-alert { background: #f8d7da; border-left: 4px solid #dc3545; padding: 20px; margin: 20px 0; }
        .chiffres-choc { background: #fff3cd; border: 1px solid #ffeaa7; padding: 20px; margin: 20px 0; border-radius: 8px; }
        .footer { background: #f8f9fa; padding: 20px; text-align: center; font-size: 12px; color: #666; border-radius: 0 0 10px 10px; }
        @media (max-width: 600px) { body { padding: 10px; } .header, .content { padding: 20px; } }
    </style>
</head>
<body>
    <div class="header">
        <h1>🚨 JOSMOZE.COM</h1>
        <h2>Alerte Eau du Robinet</h2>
    </div>
    
    <div class="content">
        <p>Bonjour {{ first_name or 'Cher lecteur' }},</p>
        
        <p><strong>Vous buvez de l'eau du robinet en toute confiance ?</strong></p>
        
        <p>Moi aussi, jusqu'à ce que je découvre les résultats de la dernière étude nationale sur la qualité de l'eau en France...</p>
        
        <div class="chiffres-choc">
            <h3>🔍 Les chiffres qui font froid dans le dos :</h3>
            <ul>
                <li>• <strong>68% des points de contrôle</strong> contiennent des pesticides</li>
                <li>• <strong>Plus de 200 molécules chimiques</strong> détectées dans l'eau du robinet</li>
                <li>• <strong>15% des communes</strong> dépassent les seuils de nitrates recommandés</li>
                <li>• <strong>142 cas de syndrome du bébé bleu</strong> recensés depuis 2020</li>
            </ul>
            <p><em>Et ce sont les chiffres OFFICIELS...</em></p>
        </div>
        
        <div class="danger-alert">
            <h3>⚠️ Votre famille boit peut-être un cocktail chimique quotidien sans le savoir</h3>
            <p><strong>Nitrates, pesticides, chlore, métaux lourds</strong> : Ces substances s'accumulent dans votre organisme et celui de vos enfants jour après jour.</p>
        </div>
        
        <p><strong>Le plus troublant ?</strong> La réglementation teste chaque substance individuellement, mais <strong>personne ne connaît l'effet de ce mélange</strong> sur votre santé à long terme.</p>
        
        <div style="text-align: center;">
            <a href="{{ cta_link }}" class="cta-button">🔍 Découvrir toute la vérité</a>
        </div>
        
        <div class="chiffres-choc">
            <h3>🎥 Témoignage choc du Dr. Christine Marseille :</h3>
            <p><em>"En 15 ans d'exercice en Bretagne, j'ai vu exploser les troubles digestifs inexpliqués. Quand mes patients passent à l'eau filtrée, 70% voient leurs symptômes s'améliorer en 2 mois."</em></p>
        </div>
        
        <p><strong>{{ first_name or 'Cher lecteur' }}, votre eau est-elle vraiment sûre ?</strong></p>
        
        <div style="text-align: center; margin: 30px 0;">
            <a href="{{ cta_link }}" class="cta-button">📞 ANALYSE GRATUITE DE VOTRE EAU</a>
        </div>
        
        <p><small>Nos experts se déplacent chez vous et testent 15 paramètres cruciaux</small></p>
        
        <p>Vous méritez de savoir ce que vous buvez.</p>
        
        <p>Cordialement,<br>
        <strong>Pierre Moreau</strong><br>
        <em>Expert Traitement Eau - Josmoze</em></p>
        
        <p><strong>P.S.</strong> : Cette analyse est 100% gratuite et sans engagement. Mais les créneaux disponibles partent vite...</p>
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
                "subject": "Sarah, ces 3 substances dans votre eau inquiètent les médecins...",
                "delay_days": 4,
                "utm_content": "email2_education",
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
        .menace-box { background: #f8d7da; border-left: 4px solid #dc3545; padding: 20px; margin: 20px 0; }
        .zones-box { background: #d4edda; border-left: 4px solid #28a745; padding: 15px; margin: 15px 0; }
        .solutions-box { background: #e2e3e5; border-left: 4px solid #6c757d; padding: 15px; margin: 15px 0; }
        .footer { background: #f8f9fa; padding: 20px; text-align: center; font-size: 12px; color: #666; border-radius: 0 0 10px 10px; }
        @media (max-width: 600px) { body { padding: 10px; } .header, .content { padding: 20px; } }
    </style>
</head>
<body>
    <div class="header">
        <h1>🧪 JOSMOZE.COM</h1>
        <h2>Les 3 Menaces Principales</h2>
    </div>
    
    <div class="content">
        <p>Bonjour {{ first_name or 'Cher lecteur' }},</p>
        
        <p>Suite à mon premier message sur les dangers cachés de l'eau du robinet, vous avez été <strong>nombreux à me poser cette question :</strong></p>
        
        <p><em>"Concrètement, quelles sont les substances les plus dangereuses dans mon eau ?"</em></p>
        
        <p><strong>Excellente question.</strong> Laissez-moi vous parler des <strong>3 menaces principales</strong> que tous les parents devraient connaître :</p>
        
        <div class="menace-box">
            <h3>🚨 MENACE #1 : LES NITRATES</h3>
            <p><strong>D'où viennent-ils ?</strong> Agriculture intensive (78% des cas)</p>
            <p><strong>Pourquoi c'est grave ?</strong></p>
            <ul>
                <li>• <strong>Syndrome du bébé bleu</strong> chez les nourrissons</li>
                <li>• <strong>+18% risque cancer colorectal</strong> chez l'adulte</li>
                <li>• <strong>142 cas recensés</strong> en France depuis 2020</li>
            </ul>
            <p><strong>Zones les plus touchées :</strong> Bretagne (68% des communes), Champagne-Ardenne (52%), Beauce (45%)</p>
        </div>
        
        <div class="menace-box">
            <h3>🌾 MENACE #2 : LES PESTICIDES</h3>
            <p><strong>Le chiffre choc :</strong> <strong>5,7 pesticides différents</strong> dans chaque verre d'eau en moyenne</p>
            <p><strong>Les plus dangereux :</strong></p>
            <ul>
                <li>• <strong>Atrazine</strong> (78% de présence) : Perturbateur endocrinien</li>
                <li>• <strong>Glyphosate</strong> (65% de présence) : Cancérigène probable</li>
                <li>• <strong>Métolachlore</strong> (52% de présence) : Toxique hépatique</li>
            </ul>
            <p><strong>L'effet cocktail :</strong> Personne ne sait ce qui se passe quand ces molécules se mélangent dans votre organisme...</p>
        </div>
        
        <div class="menace-box">
            <h3>💧 MENACE #3 : LE CHLORE</h3>
            <p><strong>Le paradoxe :</strong> Nécessaire pour désinfecter, mais crée des sous-produits cancérigènes</p>
            <p><strong>Les sous-produits toxiques :</strong></p>
            <ul>
                <li>• <strong>Trihalométhanes</strong> : Présents dans 45% des réseaux</li>
                <li>• <strong>Impact sur votre microbiote</strong> : -23% de diversité microbienne après 6 mois</li>
            </ul>
        </div>
        
        <div style="text-align: center;">
            <a href="{{ cta_link }}" class="cta-button">📖 Analyse détaillée + Solutions</a>
        </div>
        
        <div class="zones-box">
            <h3>🗺️ Votre Région est-elle Concernée ?</h3>
            <p><strong>🔴 ZONES ROUGES</strong> (Risque Élevé) : Bretagne, Bassin parisien, Nord-Pas-de-Calais</p>
            <p><strong>🟡 ZONES ORANGE</strong> (Risque Modéré) : Vallée du Rhône, Aquitaine viticole, Est industriel</p>
            <p><strong>🟢 ZONES VERTES</strong> (Risque Faible) : Haute montagne, zones rurales protégées</p>
            <p><strong>Même en zone verte,</strong> le chlore et ses sous-produits restent présents partout en France.</p>
        </div>
        
        <div class="solutions-box">
            <h3>💡 Ce qui NE Marche PAS :</h3>
            <p>❌ <strong>Faire bouillir l'eau</strong> : Concentre les nitrates et pesticides<br>
            ❌ <strong>Carafes basiques</strong> : Inefficaces sur nitrates/pesticides<br>
            ❌ <strong>Eau en bouteille</strong> : Microplastiques + coût environnemental</p>
            
            <h3>✅ Ce qui Marche VRAIMENT :</h3>
            <p><strong>1. Osmose Inverse</strong> : 99,9% d'élimination de TOUT<br>
            <strong>2. Charbon Actif +</strong> : 85-95% selon substances<br>
            <strong>3. Distillation</strong> : 99,9% mais énergivore</p>
        </div>
        
        <div style="text-align: center;">
            <a href="{{ cta_link }}" class="cta-button">📞 CONSEIL PERSONNALISÉ GRATUIT</a>
        </div>
        <p style="text-align: center;"><small>Nos spécialistes analysent votre situation et vous proposent LA solution adaptée</small></p>
        
        <p><strong>{{ first_name or 'Cher lecteur' }}, votre famille mérite une eau parfaitement pure.</strong></p>
        
        <p>Dans 3 jours, je vous dévoilerai <strong>la solution que 95% de nos clients choisissent</strong> et pourquoi elle surpasse toutes les autres.</p>
        
        <p>À très bientôt,</p>
        
        <p><strong>Pierre Moreau</strong><br>
        <em>Expert Traitement Eau - Josmoze</em></p>
        
        <p><strong>P.S.</strong> : Vous avez des questions spécifiques sur votre eau ? <strong>Répondez directement à cet email</strong>, je vous réponds personnellement sous 24h.</p>
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
                "subject": "🎁 Sarah, votre offre famille exclusive (48h seulement)",
                "delay_days": 7,
                "utm_content": "email3_offre_commerciale",
                "template": """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ subject }}</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: linear-gradient(135deg, #6f42c1 0%, #007bff 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }
        .content { background: white; padding: 30px; border: 1px solid #e0e0e0; }
        .cta-button { display: inline-block; background: #dc3545; color: white; padding: 18px 35px; text-decoration: none; border-radius: 5px; font-weight: bold; margin: 20px 0; font-size: 18px; }
        .urgency { background: #f8d7da; border: 1px solid #f5c6cb; padding: 20px; margin: 20px 0; border-radius: 8px; text-align: center; }
        .pack-offer { background: #d4edda; border: 1px solid #c3e6cb; padding: 25px; margin: 20px 0; border-radius: 8px; }
        .bonus-box { background: #fff3cd; border: 1px solid #ffeaa7; padding: 20px; margin: 20px 0; border-radius: 8px; }
        .temoignages { background: #e2e3e5; border-left: 4px solid #6c757d; padding: 15px; margin: 15px 0; }
        .garanties { background: #cce5ff; border: 1px solid #99d3ff; padding: 20px; margin: 20px 0; border-radius: 8px; }
        .footer { background: #f8f9fa; padding: 20px; text-align: center; font-size: 12px; color: #666; border-radius: 0 0 10px 10px; }
        @media (max-width: 600px) { body { padding: 10px; } .header, .content { padding: 20px; } }
    </style>
</head>
<body>
    <div class="header">
        <h1>🎁 JOSMOZE.COM</h1>
        <h2>Offre Famille Exclusive</h2>
    </div>
    
    <div class="content">
        <p>Bonjour {{ first_name or 'Cher lecteur' }},</p>
        
        <p>Vous avez lu mes deux premiers messages sur <strong>les dangers de l'eau du robinet</strong> et <strong>les 3 substances préoccupantes</strong> (nitrates, pesticides, chlore).</p>
        
        <p>Maintenant, parlons <strong>solutions.</strong></p>
        
        <p><strong>Après 15 ans d'expertise</strong> et l'analyse de milliers d'eaux françaises, <strong>UNE technologie domine toutes les autres :</strong></p>
        
        <div class="urgency">
            <h2>🚨 OFFRE FAMILLE EXCLUSIVE - 48H SEULEMENT</h2>
            <p><strong>Plus que 48h</strong> pour profiter de cette offre exclusive</p>
        </div>
        
        <div class="pack-offer">
            <h3>🎁 PACK FAMILLE INTÉGRAL</h3>
            <p><strong>🏆 OSMOSEUR 7 ÉTAPES + INSTALLATION + GARANTIES :</strong></p>
            <p style="font-size: 24px; text-align: center;">
                <del>1 290€</del> → <strong style="color: #dc3545;">890€</strong> <em>(-31% Exclusif)</em>
            </p>
            
            <div class="bonus-box">
                <h4>🎁 BONUS SPÉCIAL NOUVEAUTÉ :</h4>
                <p><strong>Choisissez 1 produit OFFERT</strong> pour vos animaux :</p>
                <ul>
                    <li>• <strong>🐾 Fontaine Eau Pure Animaux</strong> <em>(Valeur 49€)</em></li>
                    <li>• <strong>👜 Sac Transport Premium</strong> <em>(Valeur 29€)</em></li>
                    <li>• <strong>🍽️ Distributeur Nourriture Intelligent</strong> <em>(Valeur 39€)</em></li>
                </ul>
            </div>
            
            <p style="text-align: center; font-size: 18px;">
                <strong>💰 VALEUR TOTALE : 1 378€</strong><br>
                <strong style="color: #dc3545; font-size: 22px;">→ VOTRE PRIX : 890€</strong>
            </p>
        </div>
        
        <div class="pack-offer">
            <h3>✅ TOUT INCLUS - AUCUN FRAIS CACHÉ :</h3>
            <ul>
                <li>✅ <strong>Osmoseur 7 étapes</strong> (Technologie NASA)</li>
                <li>✅ <strong>Installation professionnelle</strong> (Technicien certifié)</li>
                <li>✅ <strong>Analyse eau gratuite</strong> (15 paramètres)</li>
                <li>✅ <strong>Formation famille</strong> (1h avec expert)</li>
                <li>✅ <strong>Kit filtres 1ère année</strong> (150€ économisés)</li>
                <li>✅ <strong>App mobile</strong> IoT (Monitoring qualité)</li>
                <li>✅ <strong>Garantie 5 ans</strong> (Pièces + main d'œuvre)</li>
                <li>✅ <strong>Produit animal OFFERT</strong> (Au choix)</li>
            </ul>
            
            <div style="text-align: center; margin: 25px 0;">
                <p><strong>💳 FINANCEMENT 0% - 24 MOIS</strong></p>
                <p style="font-size: 20px; color: #28a745;"><strong>37€/mois</strong> <em>sans frais - sans apport</em></p>
                <p><strong>Moins cher que votre eau en bouteille actuelle !</strong></p>
            </div>
        </div>
        
        <div class="temoignages">
            <h3>⭐ Témoignages Clients Vérifiés</h3>
            <p><strong>Sophie M. - Lille</strong> ⭐⭐⭐⭐⭐<br>
            <em>"2 ans avec l'osmoseur Josmoze. Mes enfants n'ont plus de problèmes digestifs et le goût de l'eau est incroyable. Je recommande !"</em></p>
            <p><strong>Dr. Claire L. - Nice</strong> ⭐⭐⭐⭐⭐<br>
            <em>"En tant que médecin, je ne peux que saluer la qualité de filtration. Mes patients avec osmoseur Josmoze vont mieux."</em></p>
            <p><strong>📊 Note Moyenne : 4,8/5</strong> <em>(847 avis vérifiés)</em></p>
        </div>
        
        <div class="urgency">
            <h3>⚠️ ATTENTION : STOCK LIMITÉ</h3>
            <p>⏰ <strong>Plus que 48h</strong> pour profiter de cette offre exclusive</p>
            <p>📦 <strong>Seulement 12 osmoseurs</strong> disponibles ce mois-ci</p>
            <p>🎁 <strong>Produits animaux</strong> : Stocks limitées nouveauté</p>
        </div>
        
        <div style="text-align: center;">
            <a href="{{ cta_link }}" class="cta-button">🚀 JE COMMANDE MAINTENANT</a>
        </div>
        
        <div class="garanties">
            <h3>🏆 Garantie Josmoze : Votre Tranquillité</h3>
            <p>✅ <strong>Satisfait ou remboursé 30 jours</strong><br>
            ✅ <strong>Installation garantie 5 ans</strong><br>
            ✅ <strong>Qualité eau certifiée à vie</strong><br>
            ✅ <strong>Service client 7j/7</strong></p>
        </div>
        
        <p><strong>{{ first_name or 'Cher lecteur' }}, votre famille mérite une eau parfaitement pure.</strong></p>
        
        <p><strong>Cette offre exclusive expire dans 48h.</strong> Après, vous paierez le prix normal (1 290€) et les produits animaux ne seront plus offerts.</p>
        
        <div style="text-align: center; margin: 30px 0;">
            <a href="{{ cta_link }}" class="cta-button">🔥 NE LAISSEZ PAS PASSER CETTE OPPORTUNITÉ</a>
        </div>
        
        <p>Votre santé n'a pas de prix, mais une eau pure peut avoir un coût abordable.</p>
        
        <p><strong>À très bientôt dans la famille Josmoze !</strong></p>
        
        <p><strong>Pierre Moreau</strong><br>
        <em>Expert Traitement Eau - Josmoze</em></p>
        
        <p><strong>P.S.</strong> : Vous hésitez encore ? <strong>Répondez à cet email</strong> avec vos questions, je vous réponds personnellement sous 2h. Ou <strong>appelez-moi directement au 06 12 34 56 78</strong>.</p>
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
            msg = MIMEMultipart('alternative')
            msg['Subject'] = template_config["subject"]
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = prospect_email
            
            # Version HTML
            html_part = MIMEText(html_content, 'html', 'utf-8')
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