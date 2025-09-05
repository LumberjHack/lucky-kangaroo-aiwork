#!/usr/bin/env python3
"""
Lucky Kangaroo - Backend Flask Application
Plateforme d'échange d'objets et services
"""

import os
import logging
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Importer l'application
from app import create_app, create_celery, db, socketio

# Créer l'application
app = create_app()
celery = create_celery(app)

if __name__ == '__main__':
    # Démarrer l'application
    socketio.run(
        app,
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000)),
        debug=app.config['DEBUG']
    )




