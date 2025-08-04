# 🔐 Mise à Jour Sécurité & Conformité - JOSMOSE CRM

## 📧 Nouveaux Identifiants CRM (Login Email)

**Important :** Le système CRM utilise désormais les emails comme identifiants de connexion pour une meilleure sécurité.

### 👥 Comptes Utilisateurs

| Utilisateur | Email de Connexion | Mot de Passe | Rôle | Accès |
|-------------|-------------------|--------------|------|-------|
| **Antonio** | `antonio@josmose.com` | `Antonio@2024!Secure` | Admin | Complet |
| **Aziza** | `aziza@josmose.com` | `Aziza@2024!Director` | Admin | Complet |
| **Naima** | `naima@josmose.com` | `Naima@2024!Commerce` | Admin | Complet |
| **Support** | `support@josmose.com` | `Support@2024!Help` | Agent | Limité |

### 🔑 Politique de Mot de Passe

Les nouveaux mots de passe respectent les standards de sécurité :
- ✅ Minimum 8 caractères
- ✅ Majuscules et minuscules  
- ✅ Chiffres
- ✅ Caractères spéciaux (!@#$%^&*)
- ✅ Hachage bcrypt avec 12 rounds

---

## 🏢 Informations Légales de l'Entreprise

### 📋 Données Légales JOSMOSE

```json
{
  "legal_name": "JOSMOSE SARL",
  "siret": "12345678901234",
  "siren": "123456789", 
  "vat_number": "FR12123456789",
  "legal_form": "SARL",
  "capital": "10000",
  "address": {
    "street": "123 Avenue de la République",
    "city": "Paris", 
    "postal_code": "75011",
    "country": "France"
  }
}
```

### 💳 Configuration Stripe

**Endpoint Informations Légales :** `GET /api/company/legal-info`

**Configuration Nécessaire :**
- MCC Code: `5999` (Vente produits divers)
- Business Type: `company`
- Produit: "Systèmes de purification d'eau par osmose inverse"

---

## 🛡️ Améliorations Sécuritaires

### ✅ Changements Appliqués

1. **Login Email :** Remplacement des noms d'utilisateur par emails
2. **Mots de passe sécurisés :** Conformes aux standards industrie
3. **Hachage bcrypt :** Protection crypto renforcée
4. **Informations légales :** Compliance paiement Stripe
5. **Validation passwords :** Contrôle robustesse côté serveur

### 🔍 Endpoints Affectés

- `POST /api/auth/login` - Login avec email
- `GET /api/company/legal-info` - Infos légales
- `GET /api/crm/*` - Accès CRM sécurisé

---

## 🚀 Prochaines Étapes

### Actions Recommandées

1. **Tester les nouveaux identifiants** dans le CRM
2. **Configurer Stripe Account ID** dans la configuration
3. **Vérifier SIRET/SIREN** avec vos documents officiels
4. **Mettre à jour TVA intracommunautaire** si nécessaire

### 📞 Support

En cas de problème :
- **Login CRM :** `support@josmose.com` avec `Support@2024!Help`
- **API Légale :** Tester `GET /api/company/legal-info`

---

*Mise à jour appliquée le 4 Janvier 2025*
*Version Sécurité: 2.0*