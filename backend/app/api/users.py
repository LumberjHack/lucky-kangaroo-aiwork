"""
Blueprint des utilisateurs pour Lucky Kangaroo
Gestion des profils utilisateur
"""

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from marshmallow import Schema, fields, validate, ValidationError
from werkzeug.utils import secure_filename
import os

from app import db
from app.models.user import User, UserStatus, UserRole
from app.models.notification import Notification, NotificationType

# Créer le blueprint
users_bp = Blueprint('users', __name__)

# Limiter de taux
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100 per hour"]
)

# Schémas de validation
class UpdateProfileSchema(Schema):
    first_name = fields.Str(validate=validate.Length(min=2, max=100))
    last_name = fields.Str(validate=validate.Length(min=2, max=100))
    bio = fields.Str(validate=validate.Length(max=500))
    city = fields.Str(validate=validate.Length(max=100))
    postal_code = fields.Str(validate=validate.Length(max=20))
    country = fields.Str(validate=validate.Length(max=100))
    language = fields.Str(validate=validate.OneOf(['fr', 'de', 'en', 'it']))
    currency = fields.Str(validate=validate.OneOf(['CHF', 'EUR', 'USD']))
    preferences = fields.Dict()
    notification_settings = fields.Dict()
    privacy_settings = fields.Dict()

class UpdateLocationSchema(Schema):
    latitude = fields.Float(validate=validate.Range(min=-90, max=90))
    longitude = fields.Float(validate=validate.Range(min=-180, max=180))
    city = fields.Str(validate=validate.Length(max=100))
    postal_code = fields.Str(validate=validate.Length(max=20))
    country = fields.Str(validate=validate.Length(max=100))

# Instancier les schémas
update_profile_schema = UpdateProfileSchema()
update_location_schema = UpdateLocationSchema()

@users_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Obtenir le profil de l'utilisateur connecté"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'Utilisateur non trouvé'}), 404
        
        return jsonify({
            'user': user.to_dict(include_private=True)
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erreur lors de la récupération du profil: {str(e)}")
        return jsonify({'error': 'Erreur interne du serveur'}), 500

@users_bp.route('/profile', methods=['PUT'])
@jwt_required()
@limiter.limit("10 per minute")
def update_profile():
    """Mettre à jour le profil de l'utilisateur"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'Utilisateur non trouvé'}), 404
        
        # Valider les données
        data = update_profile_schema.load(request.json, partial=True)
        
        # Mettre à jour les champs
        for field, value in data.items():
            if hasattr(user, field):
                setattr(user, field, value)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Profil mis à jour avec succès',
            'user': user.to_dict(include_private=True)
        }), 200
        
    except ValidationError as e:
        return jsonify({'error': 'Données invalides', 'details': e.messages}), 400
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Erreur lors de la mise à jour du profil: {str(e)}")
        return jsonify({'error': 'Erreur interne du serveur'}), 500

@users_bp.route('/location', methods=['PUT'])
@jwt_required()
@limiter.limit("10 per minute")
def update_location():
    """Mettre à jour la localisation de l'utilisateur"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'Utilisateur non trouvé'}), 404
        
        # Valider les données
        data = update_location_schema.load(request.json)
        
        # Mettre à jour la localisation
        user.latitude = data.get('latitude')
        user.longitude = data.get('longitude')
        user.city = data.get('city')
        user.postal_code = data.get('postal_code')
        user.country = data.get('country')
        
        db.session.commit()
        
        return jsonify({
            'message': 'Localisation mise à jour avec succès',
            'location': {
                'latitude': user.latitude,
                'longitude': user.longitude,
                'city': user.city,
                'postal_code': user.postal_code,
                'country': user.country
            }
        }), 200
        
    except ValidationError as e:
        return jsonify({'error': 'Données invalides', 'details': e.messages}), 400
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Erreur lors de la mise à jour de la localisation: {str(e)}")
        return jsonify({'error': 'Erreur interne du serveur'}), 500

@users_bp.route('/avatar', methods=['POST'])
@jwt_required()
@limiter.limit("5 per minute")
def upload_avatar():
    """Uploader une photo de profil"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'Utilisateur non trouvé'}), 404
        
        if 'avatar' not in request.files:
            return jsonify({'error': 'Aucun fichier fourni'}), 400
        
        file = request.files['avatar']
        if file.filename == '':
            return jsonify({'error': 'Aucun fichier sélectionné'}), 400
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # Générer un nom unique
            unique_filename = f"{user.id}_{filename}"
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'avatars', unique_filename)
            
            # Créer le dossier s'il n'existe pas
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Sauvegarder le fichier
            file.save(file_path)
            
            # Mettre à jour le profil
            user.profile_picture = f"/uploads/avatars/{unique_filename}"
            db.session.commit()
            
            return jsonify({
                'message': 'Photo de profil mise à jour avec succès',
                'profile_picture': user.profile_picture
            }), 200
        else:
            return jsonify({'error': 'Type de fichier non autorisé'}), 400
        
    except Exception as e:
        current_app.logger.error(f"Erreur lors de l'upload de l'avatar: {str(e)}")
        return jsonify({'error': 'Erreur interne du serveur'}), 500

@users_bp.route('/cover', methods=['POST'])
@jwt_required()
@limiter.limit("5 per minute")
def upload_cover():
    """Uploader une photo de couverture"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'Utilisateur non trouvé'}), 404
        
        if 'cover' not in request.files:
            return jsonify({'error': 'Aucun fichier fourni'}), 400
        
        file = request.files['cover']
        if file.filename == '':
            return jsonify({'error': 'Aucun fichier sélectionné'}), 400
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # Générer un nom unique
            unique_filename = f"{user.id}_{filename}"
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'covers', unique_filename)
            
            # Créer le dossier s'il n'existe pas
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Sauvegarder le fichier
            file.save(file_path)
            
            # Mettre à jour le profil
            user.cover_picture = f"/uploads/covers/{unique_filename}"
            db.session.commit()
            
            return jsonify({
                'message': 'Photo de couverture mise à jour avec succès',
                'cover_picture': user.cover_picture
            }), 200
        else:
            return jsonify({'error': 'Type de fichier non autorisé'}), 400
        
    except Exception as e:
        current_app.logger.error(f"Erreur lors de l'upload de la couverture: {str(e)}")
        return jsonify({'error': 'Erreur interne du serveur'}), 500

@users_bp.route('/<user_id>', methods=['GET'])
def get_user_profile(user_id):
    """Obtenir le profil public d'un utilisateur"""
    try:
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'Utilisateur non trouvé'}), 404
        
        if user.status != UserStatus.ACTIVE.value:
            return jsonify({'error': 'Profil non disponible'}), 404
        
        return jsonify({
            'user': user.to_dict(include_private=False)
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erreur lors de la récupération du profil: {str(e)}")
        return jsonify({'error': 'Erreur interne du serveur'}), 500

@users_bp.route('/<user_id>/listings', methods=['GET'])
def get_user_listings(user_id):
    """Obtenir les annonces d'un utilisateur"""
    try:
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'Utilisateur non trouvé'}), 404
        
        if user.status != UserStatus.ACTIVE.value:
            return jsonify({'error': 'Profil non disponible'}), 404
        
        # Récupérer les annonces actives
        listings = user.listings.filter_by(status='active').all()
        
        return jsonify({
            'listings': [listing.to_dict() for listing in listings]
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erreur lors de la récupération des annonces: {str(e)}")
        return jsonify({'error': 'Erreur interne du serveur'}), 500

@users_bp.route('/<user_id>/reviews', methods=['GET'])
def get_user_reviews(user_id):
    """Obtenir les avis reçus par un utilisateur"""
    try:
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'Utilisateur non trouvé'}), 404
        
        if user.status != UserStatus.ACTIVE.value:
            return jsonify({'error': 'Profil non disponible'}), 404
        
        # Récupérer les avis publics
        reviews = user.reviews_received.filter_by(is_public=True).all()
        
        return jsonify({
            'reviews': [review.to_dict() for review in reviews]
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erreur lors de la récupération des avis: {str(e)}")
        return jsonify({'error': 'Erreur interne du serveur'}), 500

@users_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_user_stats():
    """Obtenir les statistiques de l'utilisateur"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'Utilisateur non trouvé'}), 404
        
        stats = {
            'total_listings': user.total_listings,
            'active_listings': user.active_listings,
            'total_exchanges': user.total_exchanges,
            'successful_exchanges': user.successful_exchanges,
            'success_rate': user.success_rate,
            'trust_score': user.trust_score,
            'ecological_score': user.ecological_score,
            'badges_count': len([b for b in user.badges if b.is_active])
        }
        
        return jsonify({'stats': stats}), 200
        
    except Exception as e:
        current_app.logger.error(f"Erreur lors de la récupération des statistiques: {str(e)}")
        return jsonify({'error': 'Erreur interne du serveur'}), 500

@users_bp.route('/delete-account', methods=['DELETE'])
@jwt_required()
@limiter.limit("1 per hour")
def delete_account():
    """Supprimer le compte utilisateur"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'Utilisateur non trouvé'}), 404
        
        # Vérifier le mot de passe
        password = request.json.get('password')
        if not password or not user.check_password(password):
            return jsonify({'error': 'Mot de passe incorrect'}), 400
        
        # Marquer le compte comme supprimé
        user.status = UserStatus.INACTIVE.value
        user.email = f"deleted_{user.id}@deleted.com"
        user.username = f"deleted_{user.id}"
        
        db.session.commit()
        
        return jsonify({'message': 'Compte supprimé avec succès'}), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Erreur lors de la suppression du compte: {str(e)}")
        return jsonify({'error': 'Erreur interne du serveur'}), 500

# Fonctions utilitaires
def allowed_file(filename):
    """Vérifier si le type de fichier est autorisé"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']
