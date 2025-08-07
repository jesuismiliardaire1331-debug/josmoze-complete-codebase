# 🔑 GUIDE COMPLET - Création Comptes APIs
## Twilio + OpenAI pour Système OSMOSE

---

## 🤖 **1. COMPTE OPENAI (Pour l'IA Conversationnelle)**

### **Étape 1 : Création du compte**
1. **Allez sur :** https://platform.openai.com/signup
2. **Cliquez sur :** "Sign up"
3. **Choisissez :** "Create account" ou connectez-vous avec Google/Microsoft
4. **Saisissez :**
   - Email professionnel
   - Mot de passe sécurisé
   - Nom et prénom
5. **Vérifiez votre email** (lien de confirmation)

### **Étape 2 : Vérification du téléphone**
1. **OpenAI demande un numéro de téléphone** pour vérification
2. **Saisissez votre numéro** (format international : +33...)
3. **Entrez le code SMS** reçu

### **Étape 3 : Configuration du compte**
1. **Questions sur l'usage :**
   - "What do you plan to use OpenAI for?" → Sélectionnez "I'm exploring personal use"
   - "How did you hear about us?" → Choisissez ce qui vous convient
2. **Cliquez :** "Continue"

### **Étape 4 : Obtenir la clé API**
1. **Allez dans :** https://platform.openai.com/api-keys
2. **Cliquez :** "Create new secret key"
3. **Donnez un nom :** "OSMOSE_System"
4. **Copiez immédiatement la clé** (format : sk-...)
   ⚠️ **IMPORTANT :** Elle ne sera plus affichée après fermeture !
5. **Sauvegardez-la précieusement**

### **Étape 5 : Ajouter des crédits**
1. **Allez dans :** https://platform.openai.com/account/billing/overview
2. **Cliquez :** "Add to credit balance"
3. **Choisissez :** $5 minimum (suffisant pour les tests)
4. **Entrez vos informations de paiement**
5. **Confirmez l'achat**

### **📊 Coûts estimés OpenAI :**
```
Tests OSMOSE (100 interactions) :
- GPT-4o : ~$0.50 
- Analyse personnalité : ~$0.20
- Total estimé : $0.70 pour tests complets
```

---

## 📱 **2. COMPTE TWILIO (Pour SMS et Appels)**

### **Étape 1 : Création du compte**
1. **Allez sur :** https://www.twilio.com/try-twilio
2. **Cliquez :** "Start your free trial"
3. **Remplissez le formulaire :**
   - First Name (Prénom)
   - Last Name (Nom)
   - Email professionnel
   - Password (mot de passe sécurisé)
   - Company (nom de votre entreprise ou "OSMOSE Test")
4. **Cochez :** "I'm not a robot"
5. **Cliquez :** "Start your free trial"

### **Étape 2 : Vérification du téléphone**
1. **Twilio demande votre numéro** de téléphone
2. **Saisissez :** +33 puis votre numéro sans le 0
   - Exemple : +33123456789
3. **Choisissez :** "Text me" (SMS) ou "Call me" (appel)
4. **Entrez le code de vérification** reçu

### **Étape 3 : Questionnaire d'usage**
1. **"Which Twilio product do you plan to try first?"**
   → Sélectionnez "SMS"
2. **"What do you plan to build with Twilio?"**
   → Choisissez "Customer engagement/communication"
3. **"Are you a developer?"**
   → Sélectionnez "Yes" ou "No" selon votre profil
4. **"How do you want to use Twilio?"**
   → "I want to use Twilio in a programming language"
   → Sélectionnez "Python"

### **Étape 4 : Obtenir les identifiants**
1. **Une fois connecté, allez dans :** Console → Dashboard
2. **Notez ces informations cruciales :**
   ```
   Account SID : AC... (commence par AC)
   Auth Token : ... (cliquez sur "Show" pour l'afficher)
   ```
3. **Sauvegardez-les précieusement !**

### **Étape 5 : Obtenir un numéro de téléphone**
1. **Dans le menu, cliquez :** "Phone Numbers" → "Manage" → "Buy a number"
2. **Sélectionnez le pays :** France (+33)
3. **Capacités requises :**
   ✅ Voice (pour les appels)
   ✅ SMS (pour les messages)
4. **Cliquez :** "Search" 
5. **Choisissez un numéro disponible** (prix ~$1/mois)
6. **Cliquez :** "Buy" puis confirmez
7. **Notez votre nouveau numéro Twilio**

### **Étape 6 : Configuration pour la France**
1. **Allez dans :** "Messaging" → "Settings" → "Geo permissions"
2. **Vérifiez que "France" est activé** pour l'envoi de SMS
3. **Pour les appels internationaux :**
   - Allez dans "Voice" → "Settings" → "Geo permissions"
   - Activez la France si nécessaire

### **💰 Crédits Twilio gratuits :**
```
Nouveau compte Twilio :
- $15.00 de crédit gratuit 
- Suffisant pour ~150 SMS ou ~100 minutes d'appel
- Numéro français : ~$1/mois
```

---

## 🔧 **3. CONFIGURATION DANS OSMOSE**

### **Variables d'environnement à ajouter :**

```bash
# Dans /app/backend/.env

# OpenAI Configuration
OPENAI_API_KEY="sk-votre-clé-openai-ici"

# Twilio Configuration  
TWILIO_ACCOUNT_SID="ACvotre-account-sid-ici"
TWILIO_AUTH_TOKEN="votre-auth-token-ici"
TWILIO_PHONE_NUMBER="+33123456789"  # Votre numéro Twilio

# Configuration France
DEFAULT_COUNTRY_CODE="+33"
TIMEZONE="Europe/Paris"
```

### **Test de connectivité :**
```python
# Script de test (test_apis.py)
import openai
from twilio.rest import Client
import os

# Test OpenAI
openai.api_key = "sk-votre-clé"
try:
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": "Test OSMOSE"}],
        max_tokens=10
    )
    print("✅ OpenAI fonctionne !")
except Exception as e:
    print(f"❌ Erreur OpenAI: {e}")

# Test Twilio
try:
    client = Client("votre-sid", "votre-token")
    message = client.messages.create(
        body="Test OSMOSE - SMS fonctionnel !",
        from_="+33123456789",  # Votre numéro Twilio
        to="+33987654321"      # Votre numéro personnel
    )
    print("✅ Twilio SMS fonctionne !")
except Exception as e:
    print(f"❌ Erreur Twilio: {e}")
```

---

## 💡 **4. CONSEILS ET BONNES PRATIQUES**

### **Sécurité des clés API :**
```bash
# ❌ JAMAIS dans le code :
openai.api_key = "sk-123456789"

# ✅ TOUJOURS dans .env :
openai.api_key = os.environ.get('OPENAI_API_KEY')
```

### **Gestion des coûts OpenAI :**
1. **Définissez une limite :** https://platform.openai.com/account/billing/limits
   - Usage limit : $10 (par exemple)
   - Email alerts : Activées à 75% et 100%

### **Gestion des coûts Twilio :**
1. **Notifications de seuil :**
   - Console → Account → Notifications
   - Définir alerte à $5 restants
   - Email de notification

### **Numéros autorisés (Phase de test) :**
1. **Twilio en mode "Trial" limite les destinations**
2. **Ajoutez votre numéro dans "Verified Caller IDs" :**
   - Console → Phone Numbers → Manage → Verified Caller IDs
   - Add a new number → Votre numéro personnel
   - Vérification par SMS/appel

---

## 🚀 **5. EXEMPLE COMPLET D'INTÉGRATION**

```python
# Exemple d'agent OSMOSE avec APIs réelles
import openai
from twilio.rest import Client
import os

class RealOSMOSEAgent:
    def __init__(self):
        # Configuration APIs
        openai.api_key = os.environ.get('OPENAI_API_KEY')
        self.twilio_client = Client(
            os.environ.get('TWILIO_ACCOUNT_SID'),
            os.environ.get('TWILIO_AUTH_TOKEN')
        )
        self.twilio_number = os.environ.get('TWILIO_PHONE_NUMBER')
    
    def generate_message(self, client_name, personality, strategy):
        """Génère un message personnalisé avec OpenAI"""
        prompt = f"""
        Tu es Socrate, agent commercial philosophique.
        Client: {client_name} (personnalité: {personality})
        Stratégie Schopenhauer: {strategy}
        
        Crée un message SMS de prospection empathique et intelligent.
        """
        
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150,
            temperature=0.7
        )
        
        return response.choices[0].message.content
    
    def send_sms(self, to_number, message):
        """Envoie un SMS via Twilio"""
        try:
            message = self.twilio_client.messages.create(
                body=message,
                from_=self.twilio_number,
                to=to_number
            )
            return True, message.sid
        except Exception as e:
            return False, str(e)
    
    def make_call(self, to_number, message):
        """Effectue un appel avec message vocal"""
        twiml = f"""
        <Response>
            <Say voice="Polly.Celine" language="fr-FR">
                {message}
            </Say>
        </Response>
        """
        
        try:
            call = self.twilio_client.calls.create(
                twiml=twiml,
                to=to_number,
                from_=self.twilio_number
            )
            return True, call.sid
        except Exception as e:
            return False, str(e)

# Test complet
agent = RealOSMOSEAgent()

# Génération message IA
message = agent.generate_message(
    client_name="Marie", 
    personality="ANALYTIQUE",
    strategy="Questionnement socratique"
)

# Envoi SMS réel
success, result = agent.send_sms("+33987654321", message)
print(f"SMS envoyé: {success} - {result}")
```

---

## 📞 **6. RÉCAPITULATIF DES COÛTS**

### **Coûts de démarrage :**
```
OpenAI :
- Compte gratuit : $0
- Crédits minimum : $5
- Tests OSMOSE : ~$1-2

Twilio :
- Compte gratuit : $0  
- Crédits offerts : $15
- Numéro français : $1/mois
- Tests OSMOSE : ~$2-5

TOTAL DÉMARRAGE : ~$8-10 pour tests complets
```

### **Coûts d'usage (mensuel) :**
```
Pour 1000 interactions/mois :
- OpenAI GPT-4o : ~$15
- Twilio SMS : ~$10 
- Twilio appels : ~$20
- Numéro Twilio : $1

TOTAL USAGE : ~$45/mois pour 1000 interactions
```

---

**🎯 Avec ces comptes configurés, votre système OSMOSE pourra envoyer de vrais SMS et effectuer de vrais appels intelligents avec les 5 agents philosophes !** 

**Temps total de configuration : 15-20 minutes maximum**