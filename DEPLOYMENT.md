# 🚀 Guide de Déploiement Lucky Kangaroo

## 📋 Prérequis
- **Serveur Web** : Apache/Nginx avec PHP 8.2+ ou Python 3.11+
- **Base de données** : SQLite (incluse) ou PostgreSQL pour production
- **Hébergement** : Compatible Infomaniak, OVH, AWS, etc.

## 🌐 Déploiement Frontend

### Option 1 : Hébergement Statique (Recommandé)
1. **Upload** le fichier `index.html` sur votre serveur web
2. **Configurer** le domaine pour pointer vers le fichier
3. **Activer HTTPS** (Let's Encrypt recommandé)

### Option 2 : CDN
1. **Upload** sur Netlify, Vercel, ou GitHub Pages
2. **Configuration** automatique HTTPS et CDN
3. **Déploiement** instantané

## 🔧 Déploiement Backend

### Hébergement Infomaniak
```bash
# 1. Upload des fichiers backend/
# 2. Installer les dépendances
pip install -r requirements.txt

# 3. Configurer les variables d'environnement
export FLASK_ENV=production
export SECRET_KEY=votre-clé-secrète-unique

# 4. Lancer l'application
python app.py
```

### Hébergement OVH
```bash
# 1. Utiliser Python 3.11+ sur VPS
# 2. Installer les dépendances
pip3 install -r requirements.txt

# 3. Configurer Nginx/Apache reverse proxy
# 4. Utiliser systemd pour le service
sudo systemctl enable lucky-kangaroo
sudo systemctl start lucky-kangaroo
```

## 🗄️ Configuration Base de Données

### SQLite (Développement)
- **Automatique** : Base créée au premier lancement
- **Fichier** : `lucky_kangaroo.db` dans le répertoire backend

### PostgreSQL (Production)
```python
# Dans app.py, remplacer :
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:password@localhost/lucky_kangaroo'
```

## 🔐 Configuration Sécurité

### Variables d'Environnement
```bash
export SECRET_KEY="votre-clé-secrète-très-longue-et-unique"
export DATABASE_URL="postgresql://..."
export UPLOAD_FOLDER="/var/www/uploads"
export MAX_CONTENT_LENGTH="16777216"  # 16MB
```

### HTTPS Obligatoire
```nginx
# Configuration Nginx
server {
    listen 443 ssl;
    server_name votre-domaine.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 📊 Monitoring & Maintenance

### Logs
```bash
# Logs d'application
tail -f /var/log/lucky-kangaroo/app.log

# Logs d'erreur
tail -f /var/log/lucky-kangaroo/error.log
```

### Backup Base de Données
```bash
# SQLite
cp lucky_kangaroo.db backup_$(date +%Y%m%d).db

# PostgreSQL
pg_dump lucky_kangaroo > backup_$(date +%Y%m%d).sql
```

### Mise à Jour
```bash
# 1. Backup de la base de données
# 2. Upload des nouveaux fichiers
# 3. Redémarrage du service
sudo systemctl restart lucky-kangaroo
```

## 🎯 Optimisations Production

### Performance
- **CDN** : CloudFlare pour les assets statiques
- **Cache** : Redis pour les sessions et cache
- **Compression** : Gzip activé sur le serveur web
- **Minification** : CSS/JS minifiés

### Scalabilité
- **Load Balancer** : Nginx pour répartir la charge
- **Database Pooling** : Connexions optimisées
- **Auto-scaling** : Basé sur CPU/mémoire

### Sécurité
- **Firewall** : Ports 80/443 uniquement
- **Rate Limiting** : Protection anti-spam
- **SSL/TLS** : Certificats A+ rating
- **Backup** : Automatique quotidien

## 📞 Support

### Vérifications Post-Déploiement
1. ✅ Frontend accessible via HTTPS
2. ✅ Backend API répond sur `/api/health`
3. ✅ Upload d'images fonctionnel
4. ✅ Base de données connectée
5. ✅ Authentification opérationnelle

### Troubleshooting
- **500 Error** : Vérifier les logs d'application
- **Database Error** : Vérifier la connexion DB
- **Upload Error** : Vérifier les permissions du dossier uploads
- **CORS Error** : Vérifier la configuration CORS

---

**Lucky Kangaroo est maintenant prêt pour la production !** 🦘🚀

