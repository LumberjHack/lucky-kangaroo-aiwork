#!/usr/bin/env python3
"""
Script pour adapter les méthodes utilisant des ARRAY en JSON
"""

import os
import re

def fix_array_methods():
    """Adapter les méthodes qui utilisent des ARRAY"""
    
    # Dossier des modèles
    models_dir = "app/models"
    
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
            print(f"🔄 Traitement des méthodes dans {filename}...")
            
            # Lire le fichier
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Ajouter les imports JSON si nécessaire
            if 'import json' not in content and ('ARRAY' in content or 'tags' in content):
                # Trouver la ligne d'import et ajouter json
                import_pattern = r'(from sqlalchemy import.*?)\n'
                match = re.search(import_pattern, content)
                if match:
                    content = content.replace(
                        match.group(0),
                        match.group(0) + 'import json\n'
                    )
            
            # Remplacer les méthodes qui utilisent des listes
            # Exemple: self.tags.append() -> self._get_tags_list().append()
            content = re.sub(
                r'self\.(\w+_tags|\w+_items)\.append\(',
                r'self._get_\1_list().append(',
                content
            )
            
            content = re.sub(
                r'self\.(\w+_tags|\w+_items)\.remove\(',
                r'self._get_\1_list().remove(',
                content
            )
            
            content = re.sub(
                r'self\.(\w+_tags|\w+_items)\.extend\(',
                r'self._get_\1_list().extend(',
                content
            )
            
            # Ajouter des méthodes helper pour gérer les listes JSON
            if 'def _get_' not in content and ('_tags' in content or '_items' in content):
                # Trouver la fin de la classe et ajouter les méthodes helper
                class_end_pattern = r'(\s+def __repr__\(self\):.*?return.*?\n)'
                match = re.search(class_end_pattern, content, re.DOTALL)
                if match:
                    helper_methods = '''
    def _get_tags_list(self):
        """Helper pour gérer les tags comme une liste JSON"""
        if not self.tags:
            return []
        try:
            return json.loads(self.tags) if isinstance(self.tags, str) else self.tags
        except:
            return []
    
    def _set_tags_list(self, tags_list):
        """Helper pour sauvegarder les tags comme JSON"""
        self.tags = json.dumps(tags_list) if tags_list else None
    
    def _get_desired_items_list(self):
        """Helper pour gérer les objets désirés comme une liste JSON"""
        if not self.desired_items:
            return []
        try:
            return json.loads(self.desired_items) if isinstance(self.desired_items, str) else self.desired_items
        except:
            return []
    
    def _set_desired_items_list(self, items_list):
        """Helper pour sauvegarder les objets désirés comme JSON"""
        self.desired_items = json.dumps(items_list) if items_list else None
    
    def _get_excluded_items_list(self):
        """Helper pour gérer les objets exclus comme une liste JSON"""
        if not self.excluded_items:
            return []
        try:
            return json.loads(self.excluded_items) if isinstance(self.excluded_items, str) else self.excluded_items
        except:
            return []
    
    def _set_excluded_items_list(self, items_list):
        """Helper pour sauvegarder les objets exclus comme JSON"""
        self.excluded_items = json.dumps(items_list) if items_list else None
    
    def _get_proposed_items_list(self):
        """Helper pour gérer les objets proposés comme une liste JSON"""
        if not self.proposed_items:
            return []
        try:
            return json.loads(self.proposed_items) if isinstance(self.proposed_items, str) else self.proposed_items
        except:
            return []
    
    def _set_proposed_items_list(self, items_list):
        """Helper pour sauvegarder les objets proposés comme JSON"""
        self.proposed_items = json.dumps(items_list) if items_list else None
    
    def _get_input_files_list(self):
        """Helper pour gérer les fichiers d'entrée comme une liste JSON"""
        if not self.input_files:
            return []
        try:
            return json.loads(self.input_files) if isinstance(self.input_files, str) else self.input_files
        except:
            return []
    
    def _set_input_files_list(self, files_list):
        """Helper pour sauvegarder les fichiers d'entrée comme JSON"""
        self.input_files = json.dumps(files_list) if files_list else None
    
    def _get_ai_tags_list(self):
        """Helper pour gérer les tags IA comme une liste JSON"""
        if not self.ai_tags:
            return []
        try:
            return json.loads(self.ai_tags) if isinstance(self.ai_tags, str) else self.ai_tags
        except:
            return []
    
    def _set_ai_tags_list(self, tags_list):
        """Helper pour sauvegarder les tags IA comme JSON"""
        self.ai_tags = json.dumps(tags_list) if tags_list else None
'''
                    content = content.replace(match.group(0), match.group(0) + helper_methods)
            
            # Écrire le fichier modifié
            if content != original_content:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"✅ {filename} méthodes adaptées")
            else:
                print(f"ℹ️  {filename} méthodes inchangées")
    
    print("🎉 Adaptation des méthodes terminée !")

if __name__ == '__main__':
    fix_array_methods()
