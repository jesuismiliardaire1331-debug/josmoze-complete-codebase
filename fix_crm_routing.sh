#!/bin/bash

# Script pour corriger le routage CRM sur Emergent
echo "🔧 Correction du routage CRM pour josmoze.com..."

# 1. Vérifier les fichiers de configuration créés
echo "✅ Vérification des fichiers de configuration..."
ls -la /app/frontend/public/_redirects
ls -la /app/frontend/public/.htaccess

# 2. Rebuild du frontend avec les nouveaux fichiers
echo "🔄 Reconstruction du frontend avec configuration de routage..."
cd /app/frontend
yarn build

# 3. Vérifier que les fichiers sont bien copiés dans build/
echo "✅ Vérification des fichiers dans build/..."
ls -la /app/frontend/build/_redirects
ls -la /app/frontend/build/.htaccess

# 4. Redémarrer les services
echo "🔄 Redémarrage des services..."
sudo supervisorctl restart frontend
sudo supervisorctl restart backend

# 5. Vérifier le statut
echo "📊 Statut des services..."
sudo supervisorctl status

echo "✅ Correction du routage CRM terminée !"
echo "🌍 Testez maintenant: https://josmoze-admin.preview.emergentagent.com/crm"