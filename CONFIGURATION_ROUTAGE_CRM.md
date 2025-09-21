# Configuration Routage CRM - Guide Infrastructure

## 🚨 **PROBLÈME IDENTIFIÉ**

Le CRM Josmoze est entièrement développé et fonctionnel (backend + frontend), mais un problème de configuration de routage empêche l'accès aux URLs CRM. Toutes les routes CRM redirigent vers le site principal au lieu de servir l'interface CRM.

## ✅ **STATUT DES COMPOSANTS**

- **Backend API** : ✅ 100% fonctionnel (testé via curl)
- **Frontend CRM** : ✅ Code complet avec Email Sequencer
- **Problème** : ⚠️ Configuration proxy/nginx/ingress

## 🔧 **SOLUTIONS PROPOSÉES**

### **OPTION A - Sous-domaine dédié (RECOMMANDÉ)**

**Avantages :**
- Séparation complète CRM / Site principal
- Pas de conflit de routes
- CORS simplifié
- Scaling indépendant

**Configuration :**
```
HOST: crm.josmoze.com (ou josmoze-crm.preview.emergentagent.com)

Routes:
- /api/** → backend:8001 (FastAPI)
- /unsubscribe → backend:8001/unsubscribe (public)
- /** → frontend CRM React (SPA)
```

**Fichier de config :** `/app/nginx_subdomain_config.conf`

### **OPTION B - Préfixe /crm (Alternative)**

**Avantages :**
- Un seul domaine
- Configuration plus simple

**Configuration :**
```
HOST: josmoze-crm.preview.emergentagent.com

Routes:
- /api/** → backend:8001 (FastAPI)
- /unsubscribe → backend:8001/unsubscribe (public)
- /crm/** → frontend CRM React (avec basename)
- /** → site principal React
```

**Fichier de config :** `/app/nginx_crm_config.conf`

## 📋 **RÈGLES DE ROUTAGE CRITIQUES**

### **1. API Backend (FastAPI)**
```nginx
location ^~ /api/ {
    proxy_pass http://localhost:8001/;
    proxy_set_header Host $host;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header X-Forwarded-For $remote_addr;
}
```

### **2. Page Désinscription Publique**
```nginx
location = /unsubscribe {
    proxy_pass http://localhost:8001/unsubscribe;
    proxy_set_header Host $host;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

### **3. Frontend CRM React**
```nginx
# OPTION A (sous-domaine)
location / {
    root /var/www/crm;
    try_files $uri /index.html;
}

# OPTION B (préfixe /crm)
location ^~ /crm/ {
    root /var/www;
    try_files $uri /crm/index.html;
}
```

## 🛠️ **IMPLEMENTATION STEPS**

### **Pour OPTION A (Sous-domaine) :**

1. **Configurer DNS :**
   ```
   crm.josmoze.com → IP serveur
   ```

2. **Appliquer config nginx :**
   ```bash
   cp /app/nginx_subdomain_config.conf /etc/nginx/sites-available/crm.josmoze.com
   ln -s /etc/nginx/sites-available/crm.josmoze.com /etc/nginx/sites-enabled/
   nginx -t && systemctl reload nginx
   ```

3. **Déployer frontend CRM :**
   ```bash
   cd /app/frontend
   yarn build
   cp -r build/* /var/www/crm/
   ```

### **Pour OPTION B (Préfixe /crm) :**

1. **Modifier React pour basename :**
   ```bash
   cd /app/frontend
   echo "PUBLIC_URL=/crm" > .env.production
   # Modifier BrowserRouter avec basename="/crm"
   yarn build
   ```

2. **Appliquer config nginx :**
   ```bash
   cp /app/nginx_crm_config.conf /etc/nginx/sites-available/default
   nginx -t && systemctl reload nginx
   ```

3. **Déployer sous /crm :**
   ```bash
   mkdir -p /var/www/crm
   cp -r build/* /var/www/crm/
   ```

## 🧪 **TESTS DE VALIDATION**

Après configuration, tester :

1. **API Backend :**
   ```bash
   curl https://crm.josmoze.com/api/auth/login -X POST \
        -H "Content-Type: application/json" \
        -d '{"username":"naima@josmoze.com","password":"Naima@2024!Commerce"}'
   ```

2. **Frontend CRM :**
   ```
   https://crm.josmoze.com/  (Option A)
   https://josmoze.com/crm/  (Option B)
   ```

3. **Désinscription publique :**
   ```
   https://crm.josmoze.com/unsubscribe?token=XXX
   ```

## 🚀 **FONCTIONNALITÉS PRÊTES**

Une fois le routage corrigé, accès immédiat à :

- **Dashboard CRM** complet
- **Email Sequencer Osmoseur** (3 emails automatiques)
- **Gestion Prospects** avec GDPR
- **Liste Suppression** avec opt-out
- **Scraper Agent** pour prospection
- **Conformité CNIL/GDPR** complète

## ⚡ **SOLUTION TEMPORAIRE**

En attendant la correction, utiliser :
- **API directe** : `curl` pour tester endpoints backend
- **Page désinscription** : https://chatbot-debug-2.preview.emergentagent.com/api/public/unsubscribe

## 📞 **CONTACT TECHNIQUE**

Pour questions sur l'implémentation :
- Fichiers config : `/app/nginx_*.conf`
- Code CRM : `/app/frontend/src/CRM*.js`
- Email Sequencer : `/app/backend/email_sequencer_manager.py`

---

**Priorité :** 🔥 **HAUTE** - Bloque l'accès à toutes les fonctionnalités CRM développées