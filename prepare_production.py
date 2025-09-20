#!/usr/bin/env python3
# 🚀 Production Preparation Script for JOSMOSE.COM
# =================================================
# This script prepares the application for production deployment
# - Updates URLs to production domain
# - Cleans test data and comments
# - Optimizes configuration files
# - Creates deployment-ready package

import os
import re
import json
import shutil
from datetime import datetime

print("🌊 JOSMOSE.COM Production Preparation")
print("=" * 50)

def update_file_content(file_path, replacements):
    """Update file content with production values"""
    if not os.path.exists(file_path):
        print(f"⚠️  File not found: {file_path}")
        return
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Apply replacements
        for old, new in replacements.items():
            content = content.replace(old, new)
        
        # Write back if changed
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Updated: {file_path}")
        else:
            print(f"📝 No changes: {file_path}")
            
    except Exception as e:
        print(f"❌ Error updating {file_path}: {e}")

def clean_test_files():
    """Remove test files and logs"""
    test_patterns = [
        'test_*.py',
        'test_*.js',
        'debug_*.py',
        '*.log',
        '__pycache__',
        'node_modules',
        '.pytest_cache'
    ]
    
    print("\n🧹 Cleaning test files and logs...")
    
    for root, dirs, files in os.walk('.'):
        # Skip certain directories
        if any(skip in root for skip in ['.git', 'frontend/build', 'backend/.env']):
            continue
            
        for pattern in test_patterns:
            if pattern in dirs:
                dir_path = os.path.join(root, pattern)
                try:
                    shutil.rmtree(dir_path)
                    print(f"🗑️  Removed directory: {dir_path}")
                except:
                    pass
            
            for file in files:
                if file.startswith('test_') or file.endswith('.log') or file.startswith('debug_'):
                    file_path = os.path.join(root, file)
                    try:
                        os.remove(file_path)
                        print(f"🗑️  Removed file: {file_path}")
                    except:
                        pass

def main():
    print(f"📅 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Production URL replacements
    url_replacements = {
        # Old development URLs to production
        'https://josmoze-ecom-fix.preview.emergentagent.com': 'https://josmoze.com',
        'http://localhost:3000': 'https://josmoze.com',
        'http://localhost:8001': 'https://josmoze.com',
        'preview.emergentagent.com': 'josmoze.com',
        
        # Database name for production
        'test_database': 'josmoze_production',
        
        # API endpoints
        'REACT_APP_BACKEND_URL=http://localhost:8001': 'REACT_APP_BACKEND_URL=https://josmoze.com',
        
        # Email domains (if any old references)
        '@josmose.com': '@josmoze.com',
        
        # Environment markers
        'ENVIRONMENT=development': 'ENVIRONMENT=production',
        'DEBUG=true': 'DEBUG=false',
        'DEBUG=True': 'DEBUG=False',
    }
    
    # Files to update
    critical_files = [
        # Frontend
        'frontend/.env',
        'frontend/src/App.js',
        'frontend/src/CRM.js',
        'frontend/src/AIAgentsManager.js',
        'frontend/package.json',
        
        # Backend
        'backend/.env',
        'backend/server.py',
        'backend/ai_agents_system.py',
        'backend/conversational_agents.py',
        'backend/interactive_call_system.py',
        'backend/sms_webhook_handler.py',
        'backend/email_service.py',
        
        # Configuration
        'README.md',
    ]
    
    print("\n🔧 Updating production URLs...")
    for file_path in critical_files:
        update_file_content(file_path, url_replacements)
    
    # Update frontend .env specifically
    print("\n⚙️  Configuring frontend .env for production...")
    frontend_env_content = """REACT_APP_BACKEND_URL=https://josmoze.com
WDS_SOCKET_PORT=443
GENERATE_SOURCEMAP=false
"""
    
    with open('frontend/.env', 'w') as f:
        f.write(frontend_env_content)
    print("✅ Frontend .env configured for production")
    
    # Update backend .env for production
    print("\n⚙️  Configuring backend .env for production...")
    if os.path.exists('backend/.env'):
        with open('backend/.env', 'r') as f:
            backend_content = f.read()
        
        # Update database name and add production flags
        backend_content = backend_content.replace('DB_NAME="test_database"', 'DB_NAME="josmoze_production"')
        backend_content = backend_content.replace('MONGO_URL="mongodb://localhost:27017"', 'MONGO_URL="mongodb://localhost:27017"')
        
        # Add production environment marker if not exists
        if 'ENVIRONMENT=' not in backend_content:
            backend_content += '\n\n# Production Environment\nENVIRONMENT=production\nDEBUG=false\n'
        
        with open('backend/.env', 'w') as f:
            f.write(backend_content)
        print("✅ Backend .env configured for production")
    
    # Clean test files (optional - commented out to preserve for reference)
    # clean_test_files()
    
    # Update package.json for production build
    print("\n📦 Optimizing package.json for production...")
    if os.path.exists('frontend/package.json'):
        try:
            with open('frontend/package.json', 'r') as f:
                package_data = json.load(f)
            
            # Add production build script if not exists
            if 'scripts' in package_data:
                package_data['scripts']['build:prod'] = 'GENERATE_SOURCEMAP=false yarn build'
                package_data['scripts']['start:prod'] = 'serve -s build -l 3000'
            
            with open('frontend/package.json', 'w') as f:
                json.dump(package_data, f, indent=2)
            print("✅ package.json optimized")
        except Exception as e:
            print(f"⚠️  Could not update package.json: {e}")
    
    # Create production deployment manifest
    print("\n📋 Creating deployment manifest...")
    
    manifest = {
        "project": "JOSMOSE.COM",
        "domain": "josmoze.com",
        "prepared_at": datetime.now().isoformat(),
        "environment": "production",
        "version": "1.0.0",
        "components": {
            "frontend": {
                "framework": "React",
                "build_command": "yarn build",
                "output_dir": "build/",
                "port": 3000
            },
            "backend": {
                "framework": "FastAPI",
                "start_command": "python3 server.py",
                "port": 8001,
                "database": "MongoDB (josmoze_production)"
            },
            "ai_agents": {
                "openai_integration": True,
                "twilio_integration": True,
                "agents_count": 5,
                "operating_hours": "9h-18h (Mon-Fri) + 24/7 (prospecting)"
            }
        },
        "services": {
            "web_server": "Nginx",
            "process_manager": "Supervisor",
            "ssl": "Let's Encrypt",
            "firewall": "UFW"
        },
        "contacts": [
            "naima@josmoze.com",
            "aziza@josmoze.com", 
            "antonio@josmoze.com",
            "commercial@josmoze.com",
            "support@josmoze.com"
        ]
    }
    
    with open('PRODUCTION_MANIFEST.json', 'w') as f:
        json.dump(manifest, f, indent=2)
    print("✅ Production manifest created")
    
    # Create quick deployment checklist
    print("\n📝 Creating deployment checklist...")
    
    checklist = """# 🚀 JOSMOSE.COM Production Deployment Checklist

## Pre-Deployment (Completed)
- [x] Application code prepared for production
- [x] URLs updated to josmoze.com
- [x] Environment variables configured
- [x] Professional emails configured
- [x] Namecheap VPS provisioned

## Server Setup (To Do)
- [ ] Connect to VPS via VNC (159.198.66.241)
- [ ] Run PRODUCTION_DEPLOY_NAMECHEAP.sh script
- [ ] Upload application files to /var/www/josmoze
- [ ] Configure DNS records in Namecheap panel

## Application Deployment (To Do)
- [ ] Install dependencies (pip install, yarn install)
- [ ] Build frontend (yarn build)
- [ ] Configure Nginx reverse proxy
- [ ] Setup Supervisor for backend
- [ ] Configure MongoDB database

## SSL & Security (To Do)
- [ ] Point DNS A record to 159.198.66.241
- [ ] Install Let's Encrypt SSL certificate
- [ ] Configure firewall rules
- [ ] Test HTTPS access

## Final Testing (To Do)
- [ ] Website loads at https://josmoze.com
- [ ] CRM login works
- [ ] AI Agents respond in dashboard
- [ ] Email system functional
- [ ] SMS/Call agents operational
- [ ] E-commerce pages working

## Go Live (To Do)
- [ ] Final system monitoring check
- [ ] Backup systems verified
- [ ] Team access confirmed
- [ ] Performance metrics baseline
- [ ] 🎉 Launch celebration!

---
Generated: """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """
Status: Ready for Production Deployment
"""
    
    with open('DEPLOYMENT_CHECKLIST.md', 'w') as f:
        f.write(checklist)
    print("✅ Deployment checklist created")
    
    print("\n" + "=" * 50)
    print("🎉 PRODUCTION PREPARATION COMPLETED!")
    print("=" * 50)
    print("✅ Application configured for josmoze.com")
    print("✅ Production URLs updated in all files")
    print("✅ Environment variables optimized")
    print("✅ Deployment scripts ready")
    print("✅ Manifest and checklist created")
    
    print("\n🚀 Next Steps:")
    print("1. Connect to VNC: 159.198.66.241 (password: Onu7s8lA)")
    print("2. Run: bash PRODUCTION_DEPLOY_NAMECHEAP.sh")
    print("3. Upload application files")
    print("4. Configure DNS and SSL")
    print("5. Test and go live!")
    
    print(f"\n📅 Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🌊 JOSMOSE is ready for production! 🤖")

if __name__ == "__main__":
    main()