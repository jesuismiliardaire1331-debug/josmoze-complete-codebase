"""
Native Stripe SDK implementation to replace emergentintegrations
"""
import stripe
import logging
from typing import Dict, Any, Optional
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class CheckoutSessionRequest(BaseModel):
    amount: float
    currency: str
    success_url: str
    cancel_url: str
    metadata: Optional[Dict[str, str]] = None

class CheckoutSessionResponse(BaseModel):
    session_id: str
    url: str

class CheckoutStatusResponse(BaseModel):
    status: str
    payment_status: str
    amount_total: int
    currency: str
    metadata: Dict[str, Any]

class WebhookResponse(BaseModel):
    event_type: str
    event_id: str
    session_id: Optional[str]
    payment_status: Optional[str]

class StripeCheckout:
    """Native Stripe SDK wrapper to replace emergentintegrations"""
    
    def __init__(self, api_key: str, webhook_url: str):
        stripe.api_key = api_key
        self.webhook_url = webhook_url
        self.webhook_endpoint_secret = None
    
    async def create_checkout_session(self, request: CheckoutSessionRequest) -> CheckoutSessionResponse:
        """Create a Stripe checkout session"""
        try:
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': request.currency,
                        'product_data': {
                            'name': 'Josmoze Product'
                        },
                        'unit_amount': int(request.amount * 100),
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=request.success_url,
                cancel_url=request.cancel_url,
                metadata=request.metadata or {}
            )
            
            logger.info(f"✅ Stripe session created: {session.id}")
            return CheckoutSessionResponse(
                session_id=session.id,
                url=session.url
            )
            
        except Exception as e:
            logger.error(f"❌ Error creating Stripe session: {e}")
            raise
    
    async def get_checkout_status(self, session_id: str) -> CheckoutStatusResponse:
        """Get checkout session status from Stripe"""
        try:
            session = stripe.checkout.Session.retrieve(session_id)
            
            return CheckoutStatusResponse(
                status=session.status,
                payment_status=session.payment_status,
                amount_total=session.amount_total or 0,
                currency=session.currency or 'eur',
                metadata=session.metadata or {}
            )
            
        except Exception as e:
            logger.error(f"❌ Error retrieving Stripe session: {e}")
            raise
    
    async def handle_webhook(self, body: bytes, signature: str) -> WebhookResponse:
        """Handle Stripe webhook events"""
        try:
            if self.webhook_endpoint_secret:
                event = stripe.Webhook.construct_event(
                    body, signature, self.webhook_endpoint_secret
                )
            else:
                event = stripe.Event.construct_from(
                    stripe.util.json.loads(body.decode('utf-8')),
                    stripe.api_key
                )
            
            session_id = None
            payment_status = None
            
            if event['data']['object']:
                obj = event['data']['object']
                session_id = obj.get('id')
                payment_status = obj.get('payment_status')
            
            logger.info(f"✅ Stripe webhook processed: {event['type']}")
            
            return WebhookResponse(
                event_type=event['type'],
                event_id=event['id'],
                session_id=session_id,
                payment_status=payment_status
            )
            
        except Exception as e:
            logger.error(f"❌ Error processing Stripe webhook: {e}")
            raise
