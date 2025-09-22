#!/usr/bin/env python3
"""
📞 Test uniquement l'appel Sophie
"""

import openai
from twilio.rest import Client
import os

# Configuration
openai.api_key = "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"
TWILIO_ACCOUNT_SID = "AC5d37fc46401a27a84540203820d680ca"
TWILIO_AUTH_TOKEN = "ead5696cac732121a4f448942845517c"
TWILIO_PHONE_NUMBER = "+16592518805"
TEST_CLIENT_NUMBER = "+15068893760"

def test_sophie_call():
    """Test uniquement l'appel de Sophie"""
    
    twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    
    print("📞 LANCEMENT APPEL SOPHIE...")
    print(f"📱 Destination: {TEST_CLIENT_NUMBER}")
    
    # Message commercial de Sophie
    message = """
    Bonjour Monsieur Dubois,
    
    Je suis Sophie, votre conseillère en purification d'eau. 
    
    J'aimerais vous présenter trois bénéfices essentiels qui peuvent transformer votre quotidien :
    
    Premièrement, une eau parfaitement pure pour votre santé et celle de votre famille.
    Deuxièmement, des économies substantielles en éliminant l'achat de bouteilles.
    Troisièmement, un geste écologique majeur pour préserver notre environnement.
    """
    
    # TwiML pour conversation interactive
    twiml_content = f"""
    <Response>
        <Say voice="Polly.Celine" language="fr-FR">
            {message}
            
            Si ces bénéfices vous intéressent, appuyez sur 1.
            Pour programmer un rendez-vous, appuyez sur 2.
            Pour parler directement à un conseiller, appuyez sur 3.
            Pour ne plus être contacté, appuyez sur 9.
        </Say>
        
        <Gather numDigits="1" timeout="15">
            <Say voice="Polly.Celine" language="fr-FR">
                J'attends votre choix.
            </Say>
        </Gather>
        
        <Say voice="Polly.Celine" language="fr-FR">
            Merci pour votre écoute Monsieur Dubois. 
            Nous vous recontacterons très prochainement. 
            Excellente journée !
        </Say>
    </Response>
    """
    
    try:
        call = twilio_client.calls.create(
            twiml=twiml_content,
            to=TEST_CLIENT_NUMBER,
            from_=TWILIO_PHONE_NUMBER,
            record=False,
            timeout=30
        )
        
        print(f"✅ APPEL SOPHIE LANCÉ AVEC SUCCÈS !")
        print(f"📋 Call SID: {call.sid}")
        print(f"📞 Sophie va appeler {TEST_CLIENT_NUMBER} dans quelques secondes...")
        print(f"🔔 Assurez-vous que votre téléphone n'est plus en 'Do Not Disturb' !")
        
        return True
        
    except Exception as e:
        print(f"❌ ERREUR APPEL: {str(e)}")
        return False

if __name__ == "__main__":
    test_sophie_call()