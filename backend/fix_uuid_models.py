#!/usr/bin/env python3
"""
Script pour corriger les UUID dans tous les modèles pour SQLite
"""

import os
import re

def fix_uuid_in_file(file_path):
    """Corriger les UUID dans un fichier"""
    print(f"Correction de {file_path}...")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remplacer default=uuid.uuid4 par default=lambda: str(uuid.uuid4())
    old_pattern = r'default=uuid\.uuid4'
    new_pattern = 'default=lambda: str(uuid.uuid4())'
    
    new_content = re.sub(old_pattern, new_pattern, content)
    
    if new_content != content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"✅ {file_path} corrigé")
        return True
    else:
        print(f"ℹ️  {file_path} pas de changement nécessaire")
        return False

def main():
    """Fonction principale"""
    models_dir = "app/models"
    
    if not os.path.exists(models_dir):
        print(f"❌ Répertoire {models_dir} non trouvé")
        return
    
    files_to_fix = [
        "listing.py",
        "exchange.py", 
        "chat.py",
        "notification.py",
        "badge.py",
        "review.py",
        "payment.py",
        "location.py",
        "ai_analysis.py"
    ]
    
    fixed_count = 0
    
    for filename in files_to_fix:
        file_path = os.path.join(models_dir, filename)
        if os.path.exists(file_path):
            if fix_uuid_in_file(file_path):
                fixed_count += 1
        else:
            print(f"⚠️  Fichier {file_path} non trouvé")
    
    print(f"\n🎉 Correction terminée: {fixed_count} fichiers modifiés")

if __name__ == '__main__':
    main()
