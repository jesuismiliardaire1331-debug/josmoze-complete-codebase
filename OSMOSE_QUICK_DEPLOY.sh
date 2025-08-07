#!/bin/bash
# 🌊 OSMOSE QUICK DEPLOY - Déploiement Express
# =====================================================
# Script de déploiement ultra-rapide pour système OSMOSE
# Usage: ./OSMOSE_QUICK_DEPLOY.sh [nom_projet] [secteur]
# 
# Auteur: Système OSMOSE v1.0
# Date: 2025

set -e  # Arrêt sur erreur

# Couleurs pour les messages
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration par défaut
PROJECT_NAME="${1:-OSMOSE_DEMO}"
SECTOR="${2:-water_purification}"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

echo -e "${CYAN}"
echo "🌊🌊🌊🌊🌊🌊🌊🌊🌊🌊🌊🌊🌊🌊🌊🌊🌊🌊🌊🌊🌊🌊🌊🌊🌊"
echo "🌊                                                   🌊"
echo "🌊          OSMOSE QUICK DEPLOY v1.0                 🌊"
echo "🌊    Système d'Agents IA Philosophiques            🌊"
echo "🌊                                                   🌊"
echo "🌊🌊🌊🌊🌊🌊🌊🌊🌊🌊🌊🌊🌊🌊🌊🌊🌊🌊🌊🌊🌊🌊🌊🌊🌊"
echo -e "${NC}"

echo -e "${BLUE}📋 Configuration:${NC}"
echo -e "   Projet: ${GREEN}${PROJECT_NAME}${NC}"
echo -e "   Secteur: ${GREEN}${SECTOR}${NC}"
echo -e "   Timestamp: ${GREEN}${TIMESTAMP}${NC}"
echo

# Vérification des prérequis
echo -e "${YELLOW}🔍 Vérification des prérequis...${NC}"

check_command() {
    if ! command -v $1 &> /dev/null; then
        echo -e "${RED}❌ $1 n'est pas installé${NC}"
        return 1
    else
        echo -e "${GREEN}✅ $1 disponible${NC}"
        return 0
    fi
}

MISSING_DEPS=false

check_command "python3" || MISSING_DEPS=true
check_command "node" || MISSING_DEPS=true
check_command "yarn" || MISSING_DEPS=true
check_command "docker" || MISSING_DEPS=true
check_command "docker-compose" || MISSING_DEPS=true

if [ "$MISSING_DEPS" = true ]; then
    echo -e "${RED}❌ Des dépendances sont manquantes. Installation requise.${NC}"
    exit 1
fi

# Génération du système si nécessaire
if [ ! -d "generated_systems/${PROJECT_NAME}_${TIMESTAMP}" ]; then
    echo -e "${PURPLE}🏗️ Génération du système personnalisé...${NC}"
    
    if [ -f "OSMOSE_SYSTEM_PORTABLE.py" ]; then
        python3 OSMOSE_SYSTEM_PORTABLE.py --project "${PROJECT_NAME}" --sector "${SECTOR}"
        PROJECT_DIR="generated_systems/${PROJECT_NAME}_${TIMESTAMP}"
    else
        echo -e "${YELLOW}⚠️  Générateur non trouvé, utilisation du système actuel${NC}"
        PROJECT_DIR="."
    fi
else
    PROJECT_DIR="generated_systems/${PROJECT_NAME}_${TIMESTAMP}"
    echo -e "${GREEN}✅ Système déjà généré: ${PROJECT_DIR}${NC}"
fi

cd "${PROJECT_DIR}"

# Configuration des variables d'environnement
echo -e "${PURPLE}⚙️ Configuration des variables d'environnement...${NC}"

# Backend .env
if [ ! -f "backend/.env" ]; then
    echo -e "${YELLOW}📝 Création backend/.env...${NC}"
    cat > backend/.env << EOF
# ${PROJECT_NAME} - Configuration Backend
# Généré automatiquement le ${TIMESTAMP}

# Base de données
MONGO_URL="mongodb://localhost:27017"
DB_NAME="${PROJECT_NAME,,}_database"

# APIs IA (À CONFIGURER)
OPENAI_API_KEY="sk-YOUR_OPENAI_KEY_HERE"
ANTHROPIC_API_KEY="sk-ant-YOUR_ANTHROPIC_KEY_HERE"
GOOGLE_API_KEY="AIza-YOUR_GOOGLE_KEY_HERE"

# Communications (Optionnel)
TWILIO_ACCOUNT_SID="AC_YOUR_TWILIO_SID_HERE"
TWILIO_AUTH_TOKEN="YOUR_TWILIO_TOKEN_HERE"

# Configuration secteur
SECTOR="${SECTOR}"
PROJECT_NAME="${PROJECT_NAME}"

# DeepL (si nécessaire)
DEEPL_API_KEY="YOUR_DEEPL_KEY_HERE"
EOF
else
    echo -e "${GREEN}✅ backend/.env existe déjà${NC}"
fi

# Frontend .env
if [ ! -f "frontend/.env" ]; then
    echo -e "${YELLOW}📝 Création frontend/.env...${NC}"
    cat > frontend/.env << EOF
# ${PROJECT_NAME} - Configuration Frontend
REACT_APP_BACKEND_URL="http://localhost:8001"
REACT_APP_PROJECT_NAME="${PROJECT_NAME}"
REACT_APP_SECTOR="${SECTOR}"
EOF
else
    echo -e "${GREEN}✅ frontend/.env existe déjà${NC}"
fi

# Installation des dépendances backend
echo -e "${PURPLE}📦 Installation des dépendances backend...${NC}"
cd backend/
if [ -f "requirements.txt" ]; then
    python3 -m pip install -r requirements.txt
    echo -e "${GREEN}✅ Dépendances backend installées${NC}"
else
    echo -e "${YELLOW}⚠️  requirements.txt non trouvé${NC}"
fi
cd ..

# Installation des dépendances frontend
echo -e "${PURPLE}📦 Installation des dépendances frontend...${NC}"
cd frontend/
if [ -f "package.json" ]; then
    yarn install
    echo -e "${GREEN}✅ Dépendances frontend installées${NC}"
else
    echo -e "${YELLOW}⚠️  package.json non trouvé${NC}"
fi
cd ..

# Vérification MongoDB
echo -e "${PURPLE}🗄️ Vérification MongoDB...${NC}"
if pgrep -x "mongod" > /dev/null; then
    echo -e "${GREEN}✅ MongoDB déjà en cours d'exécution${NC}"
else
    echo -e "${YELLOW}⚠️  Démarrage MongoDB...${NC}"
    if command -v brew &> /dev/null && brew services list | grep -q mongodb; then
        brew services start mongodb-community
    elif command -v systemctl &> /dev/null; then
        sudo systemctl start mongod
    else
        echo -e "${RED}❌ Impossible de démarrer MongoDB automatiquement${NC}"
        echo -e "${YELLOW}💡 Démarrez MongoDB manuellement avant de continuer${NC}"
    fi
fi

# Création des scripts de lancement
echo -e "${PURPLE}🚀 Création des scripts de lancement...${NC}"

# Script start-backend.sh
cat > start-backend.sh << 'EOF'
#!/bin/bash
echo "🔗 Démarrage du backend OSMOSE..."
cd backend/
python3 server.py
EOF
chmod +x start-backend.sh

# Script start-frontend.sh  
cat > start-frontend.sh << 'EOF'
#!/bin/bash
echo "🎨 Démarrage du frontend OSMOSE..."
cd frontend/
yarn start
EOF
chmod +x start-frontend.sh

# Script start-all.sh
cat > start-all.sh << 'EOF'
#!/bin/bash
echo "🌊 Démarrage complet du système OSMOSE..."

# Démarrage backend en arrière-plan
echo "🔗 Lancement backend..."
./start-backend.sh > backend.log 2>&1 &
BACKEND_PID=$!

# Attendre que le backend soit prêt
echo "⏳ Attente du backend (30s)..."
sleep 30

# Démarrage frontend
echo "🎨 Lancement frontend..."
./start-frontend.sh

# Nettoyage au signal d'arrêt
cleanup() {
    echo "🛑 Arrêt des services..."
    kill $BACKEND_PID 2>/dev/null
    exit 0
}
trap cleanup SIGINT SIGTERM

wait
EOF
chmod +x start-all.sh

# Docker Compose si disponible
if command -v docker-compose &> /dev/null; then
    echo -e "${PURPLE}🐳 Création docker-compose.yml...${NC}"
    cat > docker-compose.yml << EOF
version: '3.8'
services:
  mongodb:
    image: mongo:7.0
    container_name: ${PROJECT_NAME,,}_mongo
    volumes:
      - mongodb_data:/data/db
    ports:
      - "27017:27017"
    
  backend:
    build: ./backend
    container_name: ${PROJECT_NAME,,}_backend
    depends_on:
      - mongodb
    environment:
      - MONGO_URL=mongodb://mongodb:27017
      - DB_NAME=${PROJECT_NAME,,}_database
    ports:
      - "8001:8001"
    volumes:
      - ./backend:/app
      
  frontend:
    build: ./frontend
    container_name: ${PROJECT_NAME,,}_frontend
    depends_on:
      - backend
    ports:
      - "3000:3000"
    volumes:
      - ./frontend:/app
    environment:
      - REACT_APP_BACKEND_URL=http://localhost:8001

volumes:
  mongodb_data:
EOF

    # Script Docker
    cat > start-docker.sh << 'EOF'
#!/bin/bash
echo "🐳 Démarrage avec Docker Compose..."
docker-compose up --build
EOF
    chmod +x start-docker.sh
fi

# Création du README de démarrage rapide
cat > QUICK_START.md << EOF
# 🚀 ${PROJECT_NAME} - Démarrage Rapide

## 📋 Prérequis
Avant de commencer, assurez-vous d'avoir configuré vos clés API dans:
- \`backend/.env\` (OpenAI, Anthropic, Google, Twilio...)

## 🎯 Méthodes de lancement

### Méthode 1: Scripts individuels
\`\`\`bash
# Terminal 1 - Backend
./start-backend.sh

# Terminal 2 - Frontend  
./start-frontend.sh
\`\`\`

### Méthode 2: Lancement complet
\`\`\`bash
./start-all.sh
\`\`\`

### Méthode 3: Docker (Recommandé pour production)
\`\`\`bash
./start-docker.sh
\`\`\`

## 🌐 URLs d'accès
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8001
- **CRM Login**: http://localhost:3000/crm

## 🔑 Identifiants par défaut
- **Email**: naima@josmose.com
- **Mot de passe**: Naima@2024!Commerce

## 🤖 Agents disponibles
Selon votre secteur (${SECTOR}), vous avez accès aux agents spécialisés.
Rendez-vous dans l'onglet "Agents IA" 🤖 du CRM.

## 📚 Documentation complète
- Consultez \`docs/\` pour la documentation détaillée
- Script vidéo disponible dans \`OSMOSE_VIDEO_SCRIPT.md\`

---
*Système ${PROJECT_NAME} généré le ${TIMESTAMP}*
EOF

# Messages de fin
echo
echo -e "${GREEN}🎉 DÉPLOIEMENT TERMINÉ AVEC SUCCÈS ! 🎉${NC}"
echo
echo -e "${CYAN}📁 Répertoire: $(pwd)${NC}"
echo
echo -e "${YELLOW}🔧 PROCHAINES ÉTAPES:${NC}"
echo -e "${BLUE}1.${NC} Configurez vos clés API dans ${GREEN}backend/.env${NC}"
echo -e "${BLUE}2.${NC} Lancez le système avec ${GREEN}./start-all.sh${NC}"
echo -e "${BLUE}3.${NC} Accédez au CRM: ${GREEN}http://localhost:3000/crm${NC}"
echo -e "${BLUE}4.${NC} Identifiants: ${GREEN}naima@josmose.com / Naima@2024!Commerce${NC}"
echo

echo -e "${PURPLE}📚 RESSOURCES DISPONIBLES:${NC}"
echo -e "   📖 Guide rapide: ${GREEN}QUICK_START.md${NC}"
echo -e "   🎬 Script vidéo: ${GREEN}OSMOSE_VIDEO_SCRIPT.md${NC}"
echo -e "   📋 Documentation: ${GREEN}docs/${NC}"
echo -e "   🐳 Docker: ${GREEN}./start-docker.sh${NC}"

echo
echo -e "${CYAN}🌊 Bienvenue dans l'ère OSMOSE ! 🤖${NC}"
echo -e "${CYAN}   Vos agents philosophes sont prêts à révolutionner${NC}"
echo -e "${CYAN}   votre relation client ! ${NC}"
echo

# Optionnel: Lancement automatique si demandé
read -p "🚀 Voulez-vous lancer le système maintenant ? (y/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${GREEN}🌊 Lancement du système OSMOSE...${NC}"
    ./start-all.sh
fi