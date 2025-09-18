"""
Josmoze.com - Inventory & Order Management System
Gestion des stocks, facturation PDF et suivi des commandes
"""

import os
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
import logging
from motor.motor_asyncio import AsyncIOMotorDatabase

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from io import BytesIO
import base64
import asyncio


# ========== MODELS ==========

class StockItem(BaseModel):
    """Modèle pour gérer les stocks"""
    product_id: str
    name: str
    current_stock: int = 50  # Stock initial par défaut
    reserved_stock: int = 0  # Stock réservé (commandes en cours)
    available_stock: int = 50  # Stock disponible
    min_threshold: int = 10  # Seuil minimal (Rouge)
    warning_threshold: int = 20  # Seuil d'alerte (Orange)
    optimal_threshold: int = 30  # Seuil optimal (Vert)
    reorder_point: int = 15  # Point de recommande
    reorder_quantity: int = 50  # Quantité à commander
    supplier: str = "Fournisseur Principal"
    lead_time_days: int = 30  # Délai de livraison (1 mois)
    cost_price: float = 0.0
    last_restocked: Optional[datetime] = None
    next_restock_due: Optional[datetime] = None
    stock_alerts_sent: List[datetime] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class CustomerProfile(BaseModel):
    """Profil client avec préférences de communication"""
    customer_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: str
    name: str
    phone: Optional[str] = None
    preferred_communication: str = "email"  # email, sms, whatsapp
    communication_preferences: Dict[str, bool] = {
        "order_confirmations": True,
        "shipping_updates": True,
        "marketing_emails": True,
        "sms_notifications": False,
        "whatsapp_updates": False
    }
    language: str = "fr"
    country_code: str = "FR"
    customer_type: str = "B2C"  # B2C or B2B
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class OrderTracking(BaseModel):
    """Suivi des commandes"""
    order_id: str
    tracking_number: str = Field(default_factory=lambda: f"JOS-{str(uuid.uuid4())[:8].upper()}")
    status: str = "confirmed"  # confirmed, preparing, shipped, delivered, cancelled
    status_history: List[Dict[str, Any]] = []
    estimated_delivery: Optional[datetime] = None
    carrier: Optional[str] = None
    carrier_tracking_id: Optional[str] = None
    shipping_address: Dict[str, str] = {}
    customer_notifications_sent: List[Dict[str, Any]] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class Invoice(BaseModel):
    """Modèle de facture"""
    invoice_id: str = Field(default_factory=lambda: f"FACT-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:6].upper()}")
    order_id: str
    customer_email: str
    customer_name: str
    customer_address: Dict[str, str] = {}
    invoice_date: datetime = Field(default_factory=datetime.utcnow)
    due_date: datetime = Field(default_factory=lambda: datetime.utcnow() + timedelta(days=30))
    items: List[Dict[str, Any]] = []
    subtotal: float = 0.0
    tax_rate: float = 20.0  # TVA française 20%
    tax_amount: float = 0.0
    shipping_cost: float = 0.0
    total: float = 0.0
    currency: str = "EUR"
    payment_status: str = "paid"  # paid, pending, overdue
    pdf_generated: bool = False
    pdf_file_path: Optional[str] = None
    sent_to_customer: bool = False
    sent_to_admins: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)


# ========== INVENTORY MANAGER CLASS ==========

class InventoryManager:
    """Gestionnaire de stock et facturation pour Josmoze.com"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.logger = logging.getLogger(__name__)
        
        # Stock par défaut pour les nouveaux produits finalisés  
        self.default_stock_items = [
            {"product_id": "osmoseur-essentiel", "name": "Osmoseur Essentiel", "current_stock": 50},
            {"product_id": "osmoseur-premium", "name": "Osmoseur Premium", "current_stock": 40},
            {"product_id": "osmoseur-prestige", "name": "Osmoseur Prestige", "current_stock": 30},
            {"product_id": "purificateur-portable-hydrogene", "name": "Purificateur Portable H2", "current_stock": 60},
            {"product_id": "fontaine-eau-animaux", "name": "Fontaine Animaux", "current_stock": 45},
            {"product_id": "osmoseur-pro", "name": "Système Osmose Inverse Pro", "current_stock": 25},
            {"product_id": "filtres-rechange", "name": "Kit Filtres de Rechange", "current_stock": 100},
            {"product_id": "filtres-pro", "name": "Filtres Professionnels", "current_stock": 50}
        ]
    
    async def initialize_stock(self):
        """Initialiser les stocks par défaut"""
        try:
            for item in self.default_stock_items:
                existing = await self.db.stock_items.find_one({"product_id": item["product_id"]})
                if not existing:
                    stock_item = StockItem(
                        product_id=item["product_id"],
                        name=item["name"],
                        current_stock=item["current_stock"],
                        available_stock=item["current_stock"]
                    )
                    await self.db.stock_items.insert_one(stock_item.dict())
            
            self.logger.info("Stock initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Stock initialization failed: {e}")
    
    async def get_stock_status(self, product_id: str) -> Dict[str, Any]:
        """Obtenir le statut du stock d'un produit"""
        try:
            stock_item = await self.db.stock_items.find_one({"product_id": product_id})
            if not stock_item:
                return {"error": "Product not found", "stock_level": "unknown"}
            
            available = stock_item.get("available_stock", 0)
            
            # Déterminer le niveau d'alerte
            if available < stock_item.get("min_threshold", 10):
                alert_level = "critical"  # Rouge
                alert_message = "Stock critique - Réapprovisionnement urgent"
                color = "red"
            elif available < stock_item.get("warning_threshold", 20):
                alert_level = "warning"  # Orange
                alert_message = "Stock faible - Préparer commande"
                color = "orange"
            elif available >= stock_item.get("optimal_threshold", 30):
                alert_level = "optimal"  # Vert
                alert_message = "Stock optimal"
                color = "green"
            else:
                alert_level = "normal"
                alert_message = "Stock normal"
                color = "blue"
            
            # Pour l'affichage public du site
            show_stock_warning = available < 20  # "stock limité" si < 20
            
            return {
                "product_id": product_id,
                "current_stock": stock_item.get("current_stock", 0),
                "available_stock": available,
                "reserved_stock": stock_item.get("reserved_stock", 0),
                "alert_level": alert_level,
                "alert_message": alert_message,
                "alert_color": color,
                "show_stock_warning": show_stock_warning,
                "stock_warning_text": "Stock limité ⚠️" if show_stock_warning else None,
                "reorder_needed": available <= stock_item.get("reorder_point", 15),
                "days_until_restock": self._calculate_restock_days(stock_item)
            }
            
        except Exception as e:
            self.logger.error(f"Error getting stock status: {e}")
            return {"error": str(e), "stock_level": "unknown"}
    
    async def get_all_stock_status(self) -> List[Dict[str, Any]]:
        """Obtenir le statut de tous les stocks (pour le CRM)"""
        try:
            stock_items = await self.db.stock_items.find().to_list(100)
            stock_status = []
            
            for item in stock_items:
                status = await self.get_stock_status(item["product_id"])
                stock_status.append(status)
            
            # Trier par niveau d'alerte (critique en premier)
            priority_order = {"critical": 0, "warning": 1, "normal": 2, "optimal": 3}
            stock_status.sort(key=lambda x: priority_order.get(x.get("alert_level", "normal"), 2))
            
            return stock_status
            
        except Exception as e:
            self.logger.error(f"Error getting all stock status: {e}")
            return []
    
    async def reserve_stock(self, product_id: str, quantity: int) -> Dict[str, Any]:
        """Réserver du stock pour une commande"""
        try:
            stock_item = await self.db.stock_items.find_one({"product_id": product_id})
            if not stock_item:
                return {"success": False, "error": "Product not found"}
            
            available = stock_item.get("available_stock", 0)
            if available < quantity:
                return {
                    "success": False, 
                    "error": f"Stock insuffisant. Disponible: {available}, Demandé: {quantity}"
                }
            
            # Réserver le stock
            new_reserved = stock_item.get("reserved_stock", 0) + quantity
            new_available = available - quantity
            
            await self.db.stock_items.update_one(
                {"product_id": product_id},
                {
                    "$set": {
                        "reserved_stock": new_reserved,
                        "available_stock": new_available,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            self.logger.info(f"Reserved {quantity} units of {product_id}")
            
            return {
                "success": True,
                "reserved_quantity": quantity,
                "new_available_stock": new_available,
                "new_reserved_stock": new_reserved
            }
            
        except Exception as e:
            self.logger.error(f"Error reserving stock: {e}")
            return {"success": False, "error": str(e)}
    
    async def confirm_stock_usage(self, product_id: str, quantity: int) -> Dict[str, Any]:
        """Confirmer l'utilisation du stock (après paiement)"""
        try:
            stock_item = await self.db.stock_items.find_one({"product_id": product_id})
            if not stock_item:
                return {"success": False, "error": "Product not found"}
            
            # Diminuer le stock physique et les réservations
            new_current = stock_item.get("current_stock", 0) - quantity
            new_reserved = max(0, stock_item.get("reserved_stock", 0) - quantity)
            
            await self.db.stock_items.update_one(
                {"product_id": product_id},
                {
                    "$set": {
                        "current_stock": new_current,
                        "reserved_stock": new_reserved,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            # Vérifier si une alerte de réapprovisionnement est nécessaire
            await self._check_restock_alert(product_id, new_current)
            
            self.logger.info(f"Confirmed usage of {quantity} units of {product_id}")
            
            return {
                "success": True,
                "new_current_stock": new_current,
                "new_reserved_stock": new_reserved
            }
            
        except Exception as e:
            self.logger.error(f"Error confirming stock usage: {e}")
            return {"success": False, "error": str(e)}
    
    async def generate_invoice_pdf(self, invoice_data: Dict[str, Any]) -> str:
        """Générer une facture PDF professionnelle"""
        try:
            # Créer le buffer pour le PDF
            buffer = BytesIO()
            
            # Créer le document PDF
            doc = SimpleDocTemplate(buffer, pagesize=A4)
            styles = getSampleStyleSheet()
            story = []
            
            # Styles personnalisés
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=20,
                textColor=colors.HexColor('#1E40AF'),
                alignment=TA_CENTER,
                spaceAfter=30
            )
            
            header_style = ParagraphStyle(
                'CustomHeader',
                parent=styles['Heading2'],
                fontSize=14,
                textColor=colors.HexColor('#1F2937'),
                spaceBefore=20,
                spaceAfter=10
            )
            
            # En-tête avec logo (texte pour l'instant)
            story.append(Paragraph("🌊 JOSMOZE.COM", title_style))
            story.append(Paragraph("Spécialiste européen des systèmes d'osmose inverse", styles['Normal']))
            story.append(Paragraph("Solutions pour particuliers et professionnels", styles['Normal']))
            story.append(Spacer(1, 20))
            
            # Informations de facturation
            story.append(Paragraph("FACTURE", header_style))
            
            # Tableau des informations
            invoice_info = [
                ['Numéro de facture:', invoice_data.get('invoice_id', 'N/A')],
                ['Date de facture:', invoice_data.get('invoice_date', datetime.now()).strftime('%d/%m/%Y')],
                ['Date d\'échéance:', invoice_data.get('due_date', datetime.now()).strftime('%d/%m/%Y')],
                ['Commande N°:', invoice_data.get('order_id', 'N/A')],
            ]
            
            info_table = Table(invoice_info, colWidths=[4*cm, 6*cm])
            info_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F3F4F6')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            
            story.append(info_table)
            story.append(Spacer(1, 20))
            
            # Informations client
            story.append(Paragraph("FACTURATION À:", header_style))
            customer_info = f"""
            {invoice_data.get('customer_name', 'N/A')}<br/>
            {invoice_data.get('customer_email', 'N/A')}<br/>
            """
            
            if invoice_data.get('customer_address'):
                addr = invoice_data['customer_address']
                customer_info += f"""
                {addr.get('street', '')}<br/>
                {addr.get('postal_code', '')} {addr.get('city', '')}<br/>
                {addr.get('country', '')}
                """
            
            story.append(Paragraph(customer_info, styles['Normal']))
            story.append(Spacer(1, 20))
            
            # Détails des articles
            story.append(Paragraph("DÉTAIL DES ARTICLES:", header_style))
            
            # En-tête du tableau
            items_data = [['Article', 'Quantité', 'Prix unitaire', 'Total']]
            
            # Ajouter les articles
            for item in invoice_data.get('items', []):
                items_data.append([
                    item.get('name', 'Article'),
                    str(item.get('quantity', 1)),
                    f"€{item.get('unit_price', 0.0):.2f}",
                    f"€{item.get('total', 0.0):.2f}"
                ])
            
            # Ajouter les totaux
            items_data.append(['', '', 'Sous-total:', f"€{invoice_data.get('subtotal', 0.0):.2f}"])
            
            if invoice_data.get('shipping_cost', 0.0) > 0:
                items_data.append(['', '', 'Frais de port:', f"€{invoice_data.get('shipping_cost', 0.0):.2f}"])
            
            items_data.append(['', '', f"TVA ({invoice_data.get('tax_rate', 20.0)}%):", f"€{invoice_data.get('tax_amount', 0.0):.2f}"])
            items_data.append(['', '', 'TOTAL TTC:', f"€{invoice_data.get('total', 0.0):.2f}"])
            
            # Créer le tableau des articles
            items_table = Table(items_data, colWidths=[7*cm, 2*cm, 3*cm, 3*cm])
            items_table.setStyle(TableStyle([
                # En-tête
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E40AF')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                
                # Corps du tableau
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                
                # Ligne de sous-total
                ('BACKGROUND', (0, -4), (-1, -4), colors.HexColor('#F3F4F6')),
                ('FONTNAME', (2, -4), (-1, -4), 'Helvetica-Bold'),
                
                # Ligne de total final
                ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#1E40AF')),
                ('TEXTCOLOR', (0, -1), (-1, -1), colors.whitesmoke),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, -1), (-1, -1), 12),
            ]))
            
            story.append(items_table)
            story.append(Spacer(1, 30))
            
            # Conditions de vente
            story.append(Paragraph("CONDITIONS DE VENTE:", header_style))
            conditions = """
            • Paiement effectué par carte bancaire via Stripe<br/>
            • Garantie constructeur incluse selon les termes du produit<br/>
            • Support technique disponible par email : support@josmoze.com<br/>
            • Service client : +33 (0)1 XX XX XX XX<br/>
            • TVA intracommunautaire : FR XX XXX XXX XXX<br/><br/>
            <b>Merci pour votre confiance ! 🌊</b>
            """
            story.append(Paragraph(conditions, styles['Normal']))
            
            # Construire le PDF
            doc.build(story)
            buffer.seek(0)
            
            # Convertir en base64 pour stockage
            pdf_base64 = base64.b64encode(buffer.read()).decode('utf-8')
            buffer.close()
            
            self.logger.info(f"Invoice PDF generated for {invoice_data.get('invoice_id')}")
            
            return pdf_base64
            
        except Exception as e:
            self.logger.error(f"Error generating invoice PDF: {e}")
            return None
    
    async def create_invoice_for_order(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """Créer une facture pour une commande"""
        try:
            # Calculer les montants
            subtotal = sum(item.get('price', 0) * item.get('quantity', 1) for item in order_data.get('items', []))
            shipping_cost = order_data.get('shipping_cost', 0.0)
            tax_rate = 20.0  # TVA française
            tax_amount = (subtotal + shipping_cost) * tax_rate / 100
            total = subtotal + shipping_cost + tax_amount
            
            # Créer la facture
            invoice = Invoice(
                order_id=order_data.get('id'),
                customer_email=order_data.get('customer_email'),
                customer_name=order_data.get('customer_name'),
                customer_address=order_data.get('customer_address', {}),
                items=[
                    {
                        'name': item.get('product_id', 'Article'),
                        'quantity': item.get('quantity', 1),
                        'unit_price': item.get('price', 0.0),
                        'total': item.get('price', 0.0) * item.get('quantity', 1)
                    }
                    for item in order_data.get('items', [])
                ],
                subtotal=subtotal,
                tax_amount=tax_amount,
                shipping_cost=shipping_cost,
                total=total,
                currency=order_data.get('currency', 'EUR'),
                payment_status='paid'
            )
            
            # Générer le PDF
            pdf_content = await self.generate_invoice_pdf(invoice.dict())
            if pdf_content:
                invoice.pdf_generated = True
            
            # Sauvegarder la facture
            await self.db.invoices.insert_one(invoice.dict())
            
            # Envoyer la facture par email (à implémenter avec l'API d'email)
            await self._send_invoice_email(invoice, pdf_content)
            
            self.logger.info(f"Invoice created for order {order_data.get('id')}")
            
            return {
                "success": True,
                "invoice_id": invoice.invoice_id,
                "invoice": invoice.dict(),
                "pdf_generated": bool(pdf_content)
            }
            
        except Exception as e:
            self.logger.error(f"Error creating invoice: {e}")
            return {"success": False, "error": str(e)}
    
    async def create_order_tracking(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """Créer le suivi pour une commande"""
        try:
            # Estimation de livraison (7-10 jours ouvrés)
            estimated_delivery = datetime.utcnow() + timedelta(days=8)
            
            tracking = OrderTracking(
                order_id=order_data.get('id'),
                status="confirmed",
                status_history=[{
                    "status": "confirmed",
                    "timestamp": datetime.utcnow(),
                    "message": "Commande confirmée et paiement accepté",
                    "location": "Centre de traitement Josmose"
                }],
                estimated_delivery=estimated_delivery,
                shipping_address=order_data.get('customer_address', {})
            )
            
            # Sauvegarder le suivi
            await self.db.order_tracking.insert_one(tracking.dict())
            
            # Envoyer notification de confirmation
            await self._send_tracking_notification(
                order_data.get('customer_email'),
                order_data.get('customer_name'),
                tracking.tracking_number,
                "confirmed",
                "Votre commande a été confirmée ! 📦"
            )
            
            self.logger.info(f"Order tracking created for {order_data.get('id')}")
            
            return {
                "success": True,
                "tracking_number": tracking.tracking_number,
                "tracking": tracking.dict()
            }
            
        except Exception as e:
            self.logger.error(f"Error creating order tracking: {e}")
            return {"success": False, "error": str(e)}
    
    async def update_order_status(self, order_id: str, new_status: str, message: str = "") -> Dict[str, Any]:
        """Mettre à jour le statut d'une commande"""
        try:
            tracking = await self.db.order_tracking.find_one({"order_id": order_id})
            if not tracking:
                return {"success": False, "error": "Tracking not found"}
            
            # Ajouter à l'historique
            status_update = {
                "status": new_status,
                "timestamp": datetime.utcnow(),
                "message": message or f"Commande {new_status}",
                "location": "Centre logistique Josmose"
            }
            
            # Mettre à jour le tracking
            await self.db.order_tracking.update_one(
                {"order_id": order_id},
                {
                    "$set": {
                        "status": new_status,
                        "updated_at": datetime.utcnow()
                    },
                    "$push": {"status_history": status_update}
                }
            )
            
            # Envoyer notification au client
            await self._send_tracking_notification(
                tracking.get('customer_email', ''),
                tracking.get('customer_name', ''),
                tracking.get('tracking_number', ''),
                new_status,
                message
            )
            
            self.logger.info(f"Order {order_id} status updated to {new_status}")
            
            return {"success": True, "new_status": new_status}
            
        except Exception as e:
            self.logger.error(f"Error updating order status: {e}")
            return {"success": False, "error": str(e)}
    
    def _calculate_restock_days(self, stock_item: Dict) -> int:
        """Calculer les jours restants avant réapprovisionnement"""
        if stock_item.get('next_restock_due'):
            days = (stock_item['next_restock_due'] - datetime.utcnow()).days
            return max(0, days)
        return stock_item.get('lead_time_days', 30)
    
    async def _check_restock_alert(self, product_id: str, current_stock: int):
        """Vérifier et envoyer des alertes de réapprovisionnement"""
        try:
            stock_item = await self.db.stock_items.find_one({"product_id": product_id})
            if not stock_item:
                return
            
            reorder_point = stock_item.get('reorder_point', 15)
            if current_stock <= reorder_point:
                # Envoyer alerte aux admins
                alert_message = f"⚠️ ALERTE STOCK: {stock_item.get('name')} - Stock actuel: {current_stock}"
                
                # Sauvegarder l'alerte
                await self.db.stock_alerts.insert_one({
                    "product_id": product_id,
                    "alert_type": "restock_needed",
                    "current_stock": current_stock,
                    "reorder_point": reorder_point,
                    "message": alert_message,
                    "created_at": datetime.utcnow(),
                    "resolved": False
                })
                
                self.logger.warning(alert_message)
                
        except Exception as e:
            self.logger.error(f"Error checking restock alert: {e}")
    
    async def _send_invoice_email(self, invoice: Invoice, pdf_content: str):
        """Envoyer la facture par email (placeholder pour intégration email)"""
        try:
            # TODO: Intégrer avec service d'email (SendGrid, etc.)
            email_record = {
                "recipient": invoice.customer_email,
                "recipient_admin": ["admin@josmoze.com", "naima@josmoze.com", "aziza@josmoze.com"],
                "subject": f"Votre facture Josmoze.com - {invoice.invoice_id}",
                "content": f"Merci pour votre commande ! Voici votre facture en pièce jointe.",
                "type": "invoice",
                "status": "sent",
                "pdf_attachment": pdf_content[:100] + "..." if pdf_content else None,  # Truncated for log
                "sent_at": datetime.utcnow()
            }
            
            await self.db.email_logs.insert_one(email_record)
            self.logger.info(f"Invoice email sent for {invoice.invoice_id}")
            
        except Exception as e:
            self.logger.error(f"Error sending invoice email: {e}")
    
    async def _send_tracking_notification(self, email: str, name: str, tracking_number: str, status: str, message: str):
        """Envoyer notification de suivi (placeholder pour intégration multi-canal)"""
        try:
            # TODO: Intégrer WhatsApp/SMS selon préférences client
            notification_record = {
                "customer_email": email,
                "customer_name": name,
                "tracking_number": tracking_number,
                "status": status,
                "message": message,
                "channel": "email",  # Par défaut, à adapter selon préférences
                "sent_at": datetime.utcnow()
            }
            
            await self.db.tracking_notifications.insert_one(notification_record)
            self.logger.info(f"Tracking notification sent for {tracking_number}")
            
        except Exception as e:
            self.logger.error(f"Error sending tracking notification: {e}")


# ========== HELPER FUNCTIONS ==========

def get_inventory_manager(db: AsyncIOMotorDatabase) -> InventoryManager:
    """Factory function pour créer une instance d'InventoryManager"""
    return InventoryManager(db)