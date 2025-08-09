#!/usr/bin/env python3
"""
🔧 CORRECTION DOMAINE GLOBALE
============================
Remplace tous les "josmose.com" par "josmoze.com" dans le système
"""

import os
import re
from pathlib import Path

def fix_domain_in_file(file_path):
    """Corriger le domaine dans un fichier"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Remplacements
        replacements = [
            ('josmose.com', 'josmoze.com'),
            ('josmose.fr', 'josmoze.com'),  # Au cas où
            ('@josmose.', '@josmoze.'),
            ('JOSMOSE.COM', 'JOSMOZE.COM'),
            ('Josmose.com', 'Josmoze.com'),
        ]
        
        original_content = content
        
        for old, new in replacements:
            content = content.replace(old, new)
        
        # Sauvegarder seulement si changements
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        
        return False
        
    except Exception as e:
        print(f"❌ Erreur {file_path}: {str(e)}")
        return False

def main():
    """Correction globale du domaine"""
    
    print("🔧 CORRECTION DOMAINE GLOBALE")
    print("josmose.com → josmoze.com")
    print("=" * 40)
    
    # Répertoires à traiter
    directories = [
        "/app/backend",
        "/app/frontend/src",
    ]
    
    # Extensions de fichiers à traiter
    extensions = ['.py', '.js', '.jsx', '.md', '.txt', '.json']
    
    files_modified = 0
    total_files = 0
    
    for directory in directories:
        if os.path.exists(directory):
            print(f"\n📂 Traitement {directory}...")
            
            for root, dirs, files in os.walk(directory):
                for file in files:
                    file_path = os.path.join(root, file)
                    
                    # Vérifier extension
                    if any(file.endswith(ext) for ext in extensions):
                        total_files += 1
                        
                        if fix_domain_in_file(file_path):
                            files_modified += 1
                            rel_path = os.path.relpath(file_path, "/app")
                            print(f"✅ {rel_path}")
    
    print(f"\n📊 RÉSULTAT:")
    print(f"   Fichiers traités: {total_files}")
    print(f"   Fichiers modifiés: {files_modified}")
    print(f"   Correction: josmose.com → josmoze.com")
    
    if files_modified > 0:
        print(f"\n✅ Correction domaine terminée!")
        print("🔄 Redémarrage des services recommandé")
    else:
        print(f"\n✅ Aucune correction nécessaire")

if __name__ == "__main__":
    main()