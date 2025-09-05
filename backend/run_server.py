#!/usr/bin/env python3
"""
Script de démarrage du serveur Flask Lucky Kangaroo
"""

import os
import sys

# Ajouter le répertoire courant au path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Forcer l'utilisation de SQLite
os.environ['DATABASE_URL'] = 'sqlite:///lucky_kangaroo.db'
os.environ['FLASK_ENV'] = 'development'

if __name__ == '__main__':
    from app import create_app
    
    app = create_app()
    
    print("🚀 Démarrage du serveur Lucky Kangaroo...")
    print("📱 Frontend: http://localhost:3000")
    print("🔧 Backend API: http://localhost:5000")
    print("📚 Documentation: http://localhost:5000/api/")
    print("=" * 50)
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        use_reloader=False  # Éviter les redémarrages automatiques
    )
