#!/usr/bin/env python3
"""
Script pour adapter les modèles pour SQLite
"""

import os
import re

def fix_sqlite_compatibility():
    """Remplacer les types PostgreSQL par des types compatibles SQLite"""
    
    # Dossier des modèles
    models_dir = "app/models"
    
    # Types à remplacer
    replacements = [
        # UUID -> String
        (r'UUID\(as_uuid=True\)', 'String(36)'),
        (r'UUID\(as_uuid=False\)', 'String(36)'),
        (r'UUID', 'String(36)'),
        
        # ARRAY -> Text (JSON string)
        (r'ARRAY\(String\)', 'Text'),
        (r'ARRAY\(Integer\)', 'Text'),
        (r'ARRAY\(Float\)', 'Text'),
        
        # TSVECTOR -> Text
        (r'TSVECTOR', 'Text'),
        
        # Imports PostgreSQL
        (r'from sqlalchemy.dialects.postgresql import UUID, ARRAY', 'from sqlalchemy import String'),
        (r'from sqlalchemy.dialects.postgresql import UUID, ARRAY, TSVECTOR', 'from sqlalchemy import String'),
    ]
    
    # Fichiers à traiter
    model_files = [
        'user.py',
        'listing.py', 
        'exchange.py',
        'chat.py',
        'notification.py',
        'badge.py',
        'review.py',
        'payment.py',
        'location.py',
        'ai_analysis.py'
    ]
    
    for filename in model_files:
        filepath = os.path.join(models_dir, filename)
        if os.path.exists(filepath):
            print(f"🔄 Traitement de {filename}...")
            
            # Lire le fichier
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Appliquer les remplacements
            original_content = content
            for pattern, replacement in replacements:
                content = re.sub(pattern, replacement, content)
            
            # Écrire le fichier modifié
            if content != original_content:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"✅ {filename} modifié")
            else:
                print(f"ℹ️  {filename} inchangé")
    
    print("🎉 Adaptation SQLite terminée !")

if __name__ == '__main__':
    fix_sqlite_compatibility()
