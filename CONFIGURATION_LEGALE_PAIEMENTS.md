# 💳 Configuration Légale et Paiements - JOSMOSE

## 🏢 Informations Légales Actualisées

### 📋 Données à Mettre à Jour (IMPORTANT)

> ⚠️ **Action Requise :** Remplacez les valeurs d'exemple par vos vrais numéros officiels

```bash
# Dans /app/backend/.env
COMPANY_SIRET="12345678901234"      # ← Remplacer par votre SIRET réel
COMPANY_SIREN="123456789"           # ← Remplacer par votre SIREN réel  
COMPANY_VAT_NUMBER="FR12123456789"  # ← Remplacer par votre TVA réelle
```

### 🔍 Où Trouver vos Numéros Officiels

| Document | Contient | Où le trouver |
|----------|----------|---------------|
| **SIRET** (14 chiffres) | Système d'Identification du Répertoire des Etablissements | INSEE, Kbis, Factures |
| **SIREN** (9 chiffres) | Système d'Identification du Répertoire des Entreprises | INSEE, Kbis |
| **TVA Intracommunautaire** | Numéro TVA européen | Service des Impôts, Kbis récent |

---

## 💳 Configuration Stripe pour Conformité

### 🎯 Paramètres Obligatoires

```json
{
  "mcc": "5999",                    // Code marchand pour produits divers
  "business_type": "company",       // Type entreprise
  "country": "FR",                  // France
  "product_description": "Systèmes de purification d'eau par osmose inverse"
}
```

### 🔧 Étapes de Configuration Stripe

1. **Compte Stripe :**
   - Créer un compte professionnel sur [stripe.com](https://stripe.com)
   - Vérifier votre identité avec documents officiels

2. **Informations Légales :**
   - Renseigner SIRET/SIREN dans les paramètres Stripe
   - Ajouter votre numéro TVA intracommunautaire
   - Confirmer l'adresse d'entreprise

3. **Configuration Technique :**
   ```bash
   # Remplacer dans .env
   STRIPE_API_KEY="sk_live_votre_clé_réelle"
   ```

---

## 🏦 Configuration des Retraits

### 💰 Paramètres Bancaires

Pour retirer facilement vos fonds Stripe :

1. **Compte Bancaire Entreprise :**
   - IBAN français au nom de "JOSMOSE SARL"
   - BIC/SWIFT de votre banque
   - RIB avec mention du SIRET

2. **Fréquence de Versement :**
   ```json
   {
     "interval": "daily",           // Versements quotidiens
     "delay_days": 2               // Délai de 2 jours ouvrés
   }
   ```

3. **Configuration Stripe Dashboard :**
   - Paramètres → Versements
   - Ajouter le compte bancaire vérifié
   - Configurer la fréquence automatique

---

## ⚖️ Conformité Légale e-Commerce

### 📄 Mentions Obligatoires

Votre site dispose déjà de :
- ✅ Conditions Générales de Vente (CGV)
- ✅ Mentions Légales avec SIRET
- ✅ Politique de Confidentialité RGPD
- ✅ Droit de Rétractation 14 jours

### 🧾 Facturation Automatique

Le système génère automatiquement :
- Factures PDF avec numéros séquentiels
- Mentions légales complètes (SIRET, TVA)
- Archivage électronique 10 ans

---

## 📊 Monitoring des Paiements

### 🔍 API d'Information Légale

```bash
# Tester l'endpoint
GET /api/company/legal-info

# Retourne toutes vos données légales
{
  "siret": "votre_siret",
  "siren": "votre_siren", 
  "vat_number": "votre_tva",
  "stripe": { ... }
}
```

### 📈 Dashboard CRM

Suivi temps réel dans le CRM :
- 💰 Chiffre d'affaires journalier/mensuel
- 📊 Conversion par canal
- 🧾 Export factures pour comptabilité
- 📋 Rapports TVA trimestriels

---

## 🚀 Actions Prioritaires

### ✅ Checklist Complétude

- [ ] **Récupérer SIRET/SIREN officiel** depuis votre Kbis
- [ ] **Obtenir numéro TVA intracommunautaire** (impôts.gouv.fr)
- [ ] **Créer compte Stripe professionnel** avec documents
- [ ] **Configurer compte bancaire** pour retraits automatiques
- [ ] **Tester paiement complet** avec vrais identifiants
- [ ] **Vérifier factures générées** (mentions légales)

### 🎯 Configuration Recommandée

1. **Phase 1 :** Mettre à jour numéros légaux
2. **Phase 2 :** Configurer Stripe en mode live
3. **Phase 3 :** Tester cycle complet commande→facturation→retrait

---

## 📞 Support & Ressources

### 🆘 En Cas de Problème

- **SIRET/SIREN :** [insee.fr](https://sirene.fr) (vérification gratuite)
- **TVA Intracommunautaire :** Service Impôts Entreprises
- **Stripe :** Support technique [support.stripe.com](https://support.stripe.com)
- **Conformité :** Chambre de Commerce locale

### 📋 Documentation Complémentaire

- Guide Stripe France : [stripe.com/fr/guides](https://stripe.com/fr/guides)
- Obligations e-commerce : [economie.gouv.fr](https://economie.gouv.fr)
- RGPD : [cnil.fr](https://cnil.fr)

---

*Configuration mise à jour le 4 Janvier 2025*  
*Version Légale: 2.0 - Stripe Ready*