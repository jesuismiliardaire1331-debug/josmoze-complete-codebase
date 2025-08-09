#!/bin/bash
# 🚀 JOSMOSE.COM - Production Deployment Script for Namecheap VPS
# ==============================================================
# Deployment script for Namecheap VPS (159.198.66.241)
# Domain: josmoze.com
# 
# Prerequisites:
# - Root SSH/VNC access to Namecheap VPS
# - Domain DNS pointing to VPS IP
# - Professional emails configured
#
# Author: OSMOSE AI System
# Date: June 2025

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}"
echo "🌊🌊🌊🌊🌊🌊🌊🌊🌊🌊🌊🌊🌊🌊🌊🌊🌊🌊🌊🌊🌊🌊🌊🌊🌊"
echo "🌊                                                   🌊"
echo "🌊          JOSMOSE.COM PRODUCTION DEPLOY             🌊"
echo "🌊              Namecheap VPS Setup                  🌊"
echo "🌊                                                   🌊"
echo "🌊🌊🌊🌊🌊🌊🌊🌊🌊🌊🌊🌊🌊🌊🌊🌊🌊🌊🌊🌊🌊🌊🌊🌊🌊"
echo -e "${NC}"

echo -e "${BLUE}📋 Server Information:${NC}"
echo -e "   VPS IP: ${GREEN}159.198.66.241${NC}"
echo -e "   Domain: ${GREEN}josmoze.com${NC}"
echo -e "   Server: ${GREEN}Namecheap VPS Quasar${NC}"
echo

# Step 1: System Updates and Dependencies
echo -e "${YELLOW}🔄 Step 1: Updating system and installing dependencies...${NC}"

# Update system
apt update && apt upgrade -y

# Install essential packages
apt install -y curl wget git vim htop supervisor nginx certbot python3-certbot-nginx

# Install Node.js 18+
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
apt install -y nodejs

# Install Yarn
npm install -g yarn

# Install Python 3.10+ and pip
apt install -y python3 python3-pip python3-venv

# Install MongoDB
wget -qO - https://www.mongodb.org/static/pgp/server-7.0.asc | sudo apt-key add -
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/7.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list
apt update
apt install -y mongodb-org
systemctl start mongod
systemctl enable mongod

echo -e "${GREEN}✅ System dependencies installed${NC}"

# Step 2: Clone Application
echo -e "${YELLOW}🔄 Step 2: Setting up application directory...${NC}"

# Create application directory
mkdir -p /var/www/josmoze
cd /var/www/josmoze

# Create application structure (this will be uploaded/copied)
echo -e "${BLUE}📁 Application will be copied to: /var/www/josmoze${NC}"

# Step 3: Environment Configuration
echo -e "${YELLOW}🔄 Step 3: Configuring environment variables...${NC}"

# Backend environment
mkdir -p backend
cat > backend/.env << EOF
# JOSMOSE.COM Production Environment
MONGO_URL="mongodb://localhost:27017"
DB_NAME="josmoze_production"

# OpenAI API (Production)
OPENAI_API_KEY="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"

# Twilio Configuration (Production)
TWILIO_ACCOUNT_SID="AC5d537c46401a27a845402a8c6fca69fa"
TWILIO_AUTH_TOKEN="ead5696cac732121a4f448942845517c"
TWILIO_PHONE_NUMBER="+16592518805"

# DeepL Translation
DEEPL_API_KEY="4d7cbaf9-b3c2-4a0a-a947-acb7ebbad2ff:fx"

# Company Legal Information
COMPANY_SIRET="12345678901234"
COMPANY_SIREN="123456789"
COMPANY_VAT_NUMBER="FR12123456789"
COMPANY_LEGAL_NAME="JOSMOSE SARL"
COMPANY_CAPITAL="10000"

# Stripe Configuration (TO BE UPDATED)
STRIPE_API_KEY="sk_test_emergent"
STRIPE_MCC="5999"
STRIPE_BUSINESS_TYPE="company"
STRIPE_ACCOUNT_COUNTRY="FR"

# Test Configuration
TEST_CLIENT_NUMBER="+15068893760"
TEST_CLIENT_NAME="Client Test OSMOSE"
EOF

# Frontend environment
mkdir -p frontend
cat > frontend/.env << EOF
REACT_APP_BACKEND_URL=https://josmoze.com
WDS_SOCKET_PORT=443
EOF

echo -e "${GREEN}✅ Environment configured${NC}"

# Step 4: Nginx Configuration
echo -e "${YELLOW}🔄 Step 4: Configuring Nginx...${NC}"

cat > /etc/nginx/sites-available/josmoze.com << 'EOF'
server {
    listen 80;
    server_name josmoze.com www.josmoze.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name josmoze.com www.josmoze.com;
    
    # SSL Configuration (will be configured by certbot)
    ssl_certificate /etc/letsencrypt/live/josmoze.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/josmoze.com/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;
    
    # Frontend (React)
    location / {
        root /var/www/josmoze/frontend/build;
        try_files $uri $uri/ /index.html;
        
        # Security headers
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;
    }
    
    # Backend API
    location /api {
        proxy_pass http://127.0.0.1:8001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }
    
    # Static files caching
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
EOF

# Enable site
ln -sf /etc/nginx/sites-available/josmoze.com /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t

echo -e "${GREEN}✅ Nginx configured${NC}"

# Step 5: Supervisor Configuration
echo -e "${YELLOW}🔄 Step 5: Configuring Supervisor for backend...${NC}"

cat > /etc/supervisor/conf.d/josmoze-backend.conf << 'EOF'
[program:josmoze-backend]
command=python3 server.py
directory=/var/www/josmoze/backend
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/supervisor/josmoze-backend.log
environment=PATH="/usr/bin"
EOF

echo -e "${GREEN}✅ Supervisor configured${NC}"

# Step 6: Firewall Configuration
echo -e "${YELLOW}🔄 Step 6: Configuring UFW firewall...${NC}"

ufw --force enable
ufw allow ssh
ufw allow 'Nginx Full'
ufw allow 80
ufw allow 443

echo -e "${GREEN}✅ Firewall configured${NC}"

# Step 7: SSL Certificate Setup (will run after DNS is configured)
echo -e "${YELLOW}🔄 Step 7: Preparing SSL certificate setup...${NC}"

cat > /root/setup_ssl.sh << 'EOF'
#!/bin/bash
echo "🔒 Setting up SSL certificate for josmoze.com..."

# Test if domain points to this server
if ! nslookup josmoze.com | grep -q "159.198.66.241"; then
    echo "❌ Domain josmoze.com does not point to this server"
    echo "Please configure DNS first"
    exit 1
fi

# Obtain SSL certificate
certbot --nginx -d josmoze.com -d www.josmoze.com --non-interactive --agree-tos --email support@josmoze.com

# Restart services
systemctl reload nginx
echo "✅ SSL certificate installed successfully"
EOF

chmod +x /root/setup_ssl.sh

echo -e "${GREEN}✅ SSL setup script created${NC}"

# Step 8: Create deployment helper scripts
echo -e "${YELLOW}🔄 Step 8: Creating helper scripts...${NC}"

# Application deployment script
cat > /root/deploy_application.sh << 'EOF'
#!/bin/bash
echo "🚀 Deploying JOSMOSE application..."

cd /var/www/josmoze

# Install backend dependencies
if [ -f "backend/requirements.txt" ]; then
    cd backend
    pip3 install -r requirements.txt
    cd ..
fi

# Build frontend
if [ -f "frontend/package.json" ]; then
    cd frontend
    yarn install
    yarn build
    cd ..
fi

# Set permissions
chown -R www-data:www-data /var/www/josmoze
chmod -R 755 /var/www/josmoze

# Restart services
supervisorctl reread
supervisorctl update
supervisorctl restart josmoze-backend
systemctl restart nginx

echo "✅ Application deployed successfully"
EOF

chmod +x /root/deploy_application.sh

# Status check script
cat > /root/check_status.sh << 'EOF'
#!/bin/bash
echo "📊 JOSMOSE System Status"
echo "========================"

echo "🌐 Nginx Status:"
systemctl status nginx --no-pager -l

echo ""
echo "🗄️ MongoDB Status:"
systemctl status mongod --no-pager -l

echo ""
echo "🔗 Backend Status:"
supervisorctl status josmoze-backend

echo ""
echo "🔥 Firewall Status:"
ufw status

echo ""
echo "🔒 SSL Certificate Status:"
if [ -f "/etc/letsencrypt/live/josmoze.com/fullchain.pem" ]; then
    echo "✅ SSL Certificate exists"
    openssl x509 -in /etc/letsencrypt/live/josmoze.com/cert.pem -text -noout | grep "Not After"
else
    echo "❌ SSL Certificate not found"
fi

echo ""
echo "📋 System Resources:"
free -h
df -h /
EOF

chmod +x /root/check_status.sh

# Create systemctl aliases for easy management
cat > /root/.bashrc_josmoze << 'EOF'
# JOSMOSE Management Aliases
alias josmoze-status='bash /root/check_status.sh'
alias josmoze-deploy='bash /root/deploy_application.sh'
alias josmoze-ssl='bash /root/setup_ssl.sh'
alias josmoze-logs-backend='tail -f /var/log/supervisor/josmoze-backend.log'
alias josmoze-logs-nginx='tail -f /var/log/nginx/access.log'
alias josmoze-restart='supervisorctl restart josmoze-backend && systemctl reload nginx'
EOF

echo "source /root/.bashrc_josmoze" >> /root/.bashrc

echo -e "${GREEN}✅ Helper scripts created${NC}"

# Final Instructions
echo
echo -e "${GREEN}🎉 NAMECHEAP VPS SETUP COMPLETED! 🎉${NC}"
echo
echo -e "${CYAN}📋 Next Steps:${NC}"
echo -e "${BLUE}1.${NC} Upload/copy your application files to ${GREEN}/var/www/josmoze${NC}"
echo -e "${BLUE}2.${NC} Configure DNS: josmoze.com A record → ${GREEN}159.198.66.241${NC}"
echo -e "${BLUE}3.${NC} Run: ${GREEN}bash /root/deploy_application.sh${NC}"
echo -e "${BLUE}4.${NC} Run: ${GREEN}bash /root/setup_ssl.sh${NC} (after DNS)"
echo -e "${BLUE}5.${NC} Check status: ${GREEN}bash /root/check_status.sh${NC}"

echo
echo -e "${PURPLE}🔧 Management Commands:${NC}"
echo -e "   ${GREEN}josmoze-status${NC}      - Check system status"
echo -e "   ${GREEN}josmoze-deploy${NC}      - Deploy application"
echo -e "   ${GREEN}josmoze-ssl${NC}         - Setup SSL certificate"
echo -e "   ${GREEN}josmoze-restart${NC}     - Restart services"
echo -e "   ${GREEN}josmoze-logs-backend${NC} - View backend logs"

echo
echo -e "${YELLOW}⚠️  Important Notes:${NC}"
echo -e "   • Domain DNS must point to ${GREEN}159.198.66.241${NC}"
echo -e "   • SSL certificate requires DNS configuration first"
echo -e "   • Professional emails: aziza@, naima@, antonio@, commercial@, support@josmoze.com"
echo -e "   • CRM access: ${GREEN}https://josmoze.com/crm${NC}"

echo
echo -e "${CYAN}🌊 JOSMOSE is ready for production deployment! 🤖${NC}"