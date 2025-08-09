#!/bin/bash
# 🚀 JOSMOSE.COM VNC Deployment Script
# ===================================
# Execute this script after connecting to VNC
# IP: 159.198.66.241, Password: Onu7s8lA

echo "🌊 Starting JOSMOSE.COM Production Deployment..."
echo "=================================================="

# Step 1: Download deployment script
echo "📥 Downloading production deployment script..."
cd /root/

# Create the deployment script directly (since we can't download from external repo)
cat > /root/PRODUCTION_DEPLOY_NAMECHEAP.sh << 'EOF'
#!/bin/bash
# Production Deployment Script for Namecheap VPS
set -e

echo "🌊 JOSMOSE.COM Production Setup Starting..."

# Update system
apt update && apt upgrade -y

# Install dependencies
apt install -y curl wget git vim htop supervisor nginx certbot python3-certbot-nginx

# Install Node.js 18
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
apt install -y nodejs

# Install Yarn
npm install -g yarn

# Install Python packages
apt install -y python3 python3-pip python3-venv

# Install MongoDB
wget -qO - https://www.mongodb.org/static/pgp/server-7.0.asc | sudo apt-key add -
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/7.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list
apt update
apt install -y mongodb-org
systemctl start mongod
systemctl enable mongod

# Create application directory
mkdir -p /var/www/josmoze
cd /var/www/josmoze

echo "✅ System setup completed"

# Configure Nginx
cat > /etc/nginx/sites-available/josmoze.com << 'NGINXEOF'
server {
    listen 80;
    server_name josmoze.com www.josmoze.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name josmoze.com www.josmoze.com;
    
    ssl_certificate /etc/letsencrypt/live/josmoze.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/josmoze.com/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;
    
    location / {
        root /var/www/josmoze/frontend/build;
        try_files $uri $uri/ /index.html;
        
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;
    }
    
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
    
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
NGINXEOF

ln -sf /etc/nginx/sites-available/josmoze.com /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t

# Configure Supervisor
cat > /etc/supervisor/conf.d/josmoze-backend.conf << 'SUPEOF'
[program:josmoze-backend]
command=python3 server.py
directory=/var/www/josmoze/backend
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/supervisor/josmoze-backend.log
environment=PATH="/usr/bin"
SUPEOF

# Configure UFW firewall
ufw --force enable
ufw allow ssh
ufw allow 'Nginx Full'
ufw allow 80
ufw allow 443

echo "🎉 Server configuration completed!"
echo "Ready for application files and SSL setup"
EOF

chmod +x /root/PRODUCTION_DEPLOY_NAMECHEAP.sh

# Step 2: Run the deployment script
echo "🚀 Running production deployment script..."
bash /root/PRODUCTION_DEPLOY_NAMECHEAP.sh

# Step 3: Create application files structure
echo "📁 Creating application structure..."
cd /var/www/josmoze

# Create basic structure
mkdir -p backend frontend

# Backend environment
cat > backend/.env << 'ENVEOF'
MONGO_URL="mongodb://localhost:27017"
DB_NAME="josmoze_production"
STRIPE_API_KEY=sk_test_emergent

# DEEPL TRANSLATION API
DEEPL_API_KEY="4d7cbaf9-b3c2-4a0a-a947-acb7ebbad2ff:fx"

# INFORMATIONS LÉGALES ENTREPRISE
COMPANY_SIRET="12345678901234"
COMPANY_SIREN="123456789"
COMPANY_VAT_NUMBER="FR12123456789"
COMPANY_LEGAL_NAME="JOSMOSE SARL"
COMPANY_CAPITAL="10000"

# CONFIGURATION STRIPE
STRIPE_MCC="5999"
STRIPE_BUSINESS_TYPE="company"
STRIPE_ACCOUNT_COUNTRY="FR"

# APIs IA
OPENAI_API_KEY="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"
ANTHROPIC_API_KEY="sk-ant-YOUR_ANTHROPIC_KEY_HERE"
GOOGLE_API_KEY="AIza-YOUR_GOOGLE_KEY_HERE"

# Communications
TWILIO_ACCOUNT_SID="AC5d537c46401a27a845402a8c6fca69fa"
TWILIO_AUTH_TOKEN="ead5696cac732121a4f448942845517c"
TWILIO_PHONE_NUMBER="+16592518805"

# Test Configuration
TEST_CLIENT_NUMBER="+15068893760"
TEST_CLIENT_NAME="Client Test OSMOSE"

# Production Environment
ENVIRONMENT=production
DEBUG=false
ENVEOF

# Frontend environment
cat > frontend/.env << 'FRONTEOF'
REACT_APP_BACKEND_URL=https://josmoze.com
WDS_SOCKET_PORT=443
GENERATE_SOURCEMAP=false
FRONTEOF

echo "✅ Environment files created"

# Step 4: Create management scripts
echo "🛠️  Creating management scripts..."

# Status check script
cat > /root/josmoze-status.sh << 'STATUSEOF'
#!/bin/bash
echo "📊 JOSMOSE System Status"
echo "========================"

echo "🌐 Nginx Status:"
systemctl status nginx --no-pager -l | head -5

echo ""
echo "🗄️  MongoDB Status:"
systemctl status mongod --no-pager -l | head -5

echo ""
echo "🔗 Backend Status:"
supervisorctl status josmoze-backend

echo ""
echo "🔥 Firewall Status:"
ufw status numbered

echo ""
echo "💾 Disk Usage:"
df -h / | tail -1

echo ""
echo "🧠 Memory Usage:"
free -h | head -2
STATUSEOF

chmod +x /root/josmoze-status.sh

# SSL setup script
cat > /root/setup-ssl.sh << 'SSLEOF'
#!/bin/bash
echo "🔒 Setting up SSL for josmoze.com..."

# Check DNS
if nslookup josmoze.com | grep -q "159.198.66.241"; then
    echo "✅ DNS correctly points to this server"
    
    # Get SSL certificate
    certbot --nginx -d josmoze.com -d www.josmoze.com \
        --non-interactive --agree-tos --email support@josmoze.com
    
    systemctl reload nginx
    echo "✅ SSL certificate installed"
else
    echo "❌ DNS does not point to this server yet"
    echo "Please configure DNS first"
fi
SSLEOF

chmod +x /root/setup-ssl.sh

# Deployment script
cat > /root/deploy-app.sh << 'DEPLOYEOF'
#!/bin/bash
echo "🚀 Deploying JOSMOSE application..."

cd /var/www/josmoze

# Install backend dependencies
if [ -f "backend/requirements.txt" ]; then
    cd backend
    pip3 install -r requirements.txt
    cd ..
fi

# Install and build frontend
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
systemctl reload nginx

echo "✅ Application deployed successfully"
DEPLOYEOF

chmod +x /root/deploy-app.sh

echo "✅ Management scripts created"

# Step 5: Create helpful aliases
echo "⚙️  Setting up command aliases..."

cat >> /root/.bashrc << 'ALIASEOF'

# JOSMOSE Management Aliases
alias js-status='/root/josmoze-status.sh'
alias js-ssl='/root/setup-ssl.sh'  
alias js-deploy='/root/deploy-app.sh'
alias js-logs='tail -f /var/log/supervisor/josmoze-backend.log'
alias js-nginx='tail -f /var/log/nginx/access.log'
alias js-restart='supervisorctl restart josmoze-backend && systemctl reload nginx'
ALIASEOF

# Load aliases
source /root/.bashrc

echo ""
echo "🎉 VNC DEPLOYMENT SETUP COMPLETED!"
echo "================================="
echo ""
echo "📋 Next Manual Steps:"
echo "1. Upload application files to /var/www/josmoze"
echo "2. Configure DNS: josmoze.com A record → 159.198.66.241"  
echo "3. Run: /root/deploy-app.sh"
echo "4. Run: /root/setup-ssl.sh"
echo "5. Check: /root/josmoze-status.sh"
echo ""
echo "🔧 Quick Commands:"
echo "   js-status   - Check system status"
echo "   js-deploy   - Deploy application" 
echo "   js-ssl      - Setup SSL certificate"
echo "   js-logs     - View backend logs"
echo "   js-restart  - Restart services"
echo ""
echo "🌐 Once complete:"
echo "   Website: https://josmoze.com"
echo "   CRM: https://josmoze.com/crm"
echo ""
echo "✅ Server is ready for JOSMOSE deployment!"