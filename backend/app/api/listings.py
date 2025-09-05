"""
Blueprint des annonces pour Lucky Kangaroo
Gestion des objets et services à échanger
"""

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from marshmallow import Schema, fields, validate, ValidationError
from werkzeug.utils import secure_filename
import os
import uuid

from app import db
from app.models.user import User
from app.models.listing import Listing, ListingStatus, ListingType, ExchangeType, Condition
from app.models.listing import ListingCategory, ListingImage
from app.models.notification import Notification, NotificationType

# Créer le blueprint
listings_bp = Blueprint('listings', __name__)

# Limiter de taux
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100 per hour"]
)

# Schémas de validation
class CreateListingSchema(Schema):
    title = fields.Str(required=True, validate=validate.Length(min=5, max=200))
    description = fields.Str(required=True, validate=validate.Length(min=20, max=2000))
    category_id = fields.UUID(required=True)
    listing_type = fields.Str(required=True, validate=validate.OneOf(['good', 'service']))
    condition = fields.Str(validate=validate.OneOf(['excellent', 'very_good', 'good', 'fair', 'poor', 'new']))
    brand = fields.Str(validate=validate.Length(max=100))
    model = fields.Str(validate=validate.Length(max=100))
    year = fields.Int(validate=validate.Range(min=1900, max=2030))
    estimated_value = fields.Float(validate=validate.Range(min=0))
    price_range_min = fields.Float(validate=validate.Range(min=0))
    price_range_max = fields.Float(validate=validate.Range(min=0))
    currency = fields.Str(validate=validate.OneOf(['CHF', 'EUR', 'USD']))
    city = fields.Str(validate=validate.Length(max=100))
    postal_code = fields.Str(validate=validate.Length(max=20))
    country = fields.Str(validate=validate.Length(max=100))
    latitude = fields.Float(validate=validate.Range(min=-90, max=90))
    longitude = fields.Float(validate=validate.Range(min=-180, max=180))
    exchange_type = fields.Str(validate=validate.OneOf(['direct', 'chain', 'both']))
    desired_items = fields.List(fields.Str())
    excluded_items = fields.List(fields.Str())
    tags = fields.List(fields.Str())

class UpdateListingSchema(Schema):
    title = fields.Str(validate=validate.Length(min=5, max=200))
    description = fields.Str(validate=validate.Length(min=20, max=2000))
    category_id = fields.UUID()
    condition = fields.Str(validate=validate.OneOf(['excellent', 'very_good', 'good', 'fair', 'poor', 'new']))
    brand = fields.Str(validate=validate.Length(max=100))
    model = fields.Str(validate=validate.Length(max=100))
    year = fields.Int(validate=validate.Range(min=1900, max=2030))
    estimated_value = fields.Float(validate=validate.Range(min=0))
    price_range_min = fields.Float(validate=validate.Range(min=0))
    price_range_max = fields.Float(validate=validate.Range(min=0))
    currency = fields.Str(validate=validate.OneOf(['CHF', 'EUR', 'USD']))
    city = fields.Str(validate=validate.Length(max=100))
    postal_code = fields.Str(validate=validate.Length(max=20))
    country = fields.Str(validate=validate.Length(max=100))
    latitude = fields.Float(validate=validate.Range(min=-90, max=90))
    longitude = fields.Float(validate=validate.Range(min=-180, max=180))
    exchange_type = fields.Str(validate=validate.OneOf(['direct', 'chain', 'both']))
    desired_items = fields.List(fields.Str())
    excluded_items = fields.List(fields.Str())
    tags = fields.List(fields.Str())

# Instancier les schémas
create_listing_schema = CreateListingSchema()
update_listing_schema = UpdateListingSchema()

@listings_bp.route('/', methods=['GET'])
def get_listings():
    """Obtenir la liste des annonces avec filtres"""
    try:
        # Paramètres de pagination
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        
        # Filtres
        category_id = request.args.get('category_id')
        listing_type = request.args.get('listing_type')
        condition = request.args.get('condition')
        city = request.args.get('city')
        postal_code = request.args.get('postal_code')
        min_price = request.args.get('min_price', type=float)
        max_price = request.args.get('max_price', type=float)
        exchange_type = request.args.get('exchange_type')
        search = request.args.get('search')
        sort_by = request.args.get('sort_by', 'created_at')
        sort_order = request.args.get('sort_order', 'desc')
        
        # Construire la requête
        query = Listing.query.filter_by(status=ListingStatus.ACTIVE.value)
        
        # Appliquer les filtres
        if category_id:
            query = query.filter_by(category_id=category_id)
        if listing_type:
            query = query.filter_by(listing_type=listing_type)
        if condition:
            query = query.filter_by(condition=condition)
        if city:
            query = query.filter_by(city=city)
        if postal_code:
            query = query.filter_by(postal_code=postal_code)
        if min_price is not None:
            query = query.filter(Listing.estimated_value >= min_price)
        if max_price is not None:
            query = query.filter(Listing.estimated_value <= max_price)
        if exchange_type:
            query = query.filter(Listing.exchange_type.in_(['both', exchange_type]))
        if search:
            query = query.filter(
                db.or_(
                    Listing.title.ilike(f'%{search}%'),
                    Listing.description.ilike(f'%{search}%'),
                    Listing.brand.ilike(f'%{search}%'),
                    Listing.model.ilike(f'%{search}%')
                )
            )
        
        # Tri
        if sort_by == 'price':
            if sort_order == 'asc':
                query = query.order_by(Listing.estimated_value.asc())
            else:
                query = query.order_by(Listing.estimated_value.desc())
        elif sort_by == 'views':
            if sort_order == 'asc':
                query = query.order_by(Listing.views_count.asc())
            else:
                query = query.order_by(Listing.views_count.desc())
        else:  # created_at
            if sort_order == 'asc':
                query = query.order_by(Listing.created_at.asc())
            else:
                query = query.order_by(Listing.created_at.desc())
        
        # Pagination
        pagination = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'listings': [listing.to_dict() for listing in pagination.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erreur lors de la récupération des annonces: {str(e)}")
        return jsonify({'error': 'Erreur interne du serveur'}), 500

@listings_bp.route('/<listing_id>', methods=['GET'])
def get_listing(listing_id):
    """Obtenir une annonce spécifique"""
    try:
        listing = Listing.query.get(listing_id)
        
        if not listing:
            return jsonify({'error': 'Annonce non trouvée'}), 404
        
        if listing.status != ListingStatus.ACTIVE.value:
            return jsonify({'error': 'Annonce non disponible'}), 404
        
        # Incrémenter le compteur de vues
        listing.increment_views()
        
        return jsonify({
            'listing': listing.to_dict()
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erreur lors de la récupération de l'annonce: {str(e)}")
        return jsonify({'error': 'Erreur interne du serveur'}), 500

@listings_bp.route('/', methods=['POST'])
@jwt_required()
@limiter.limit("10 per hour")
def create_listing():
    """Créer une nouvelle annonce"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'Utilisateur non trouvé'}), 404
        
        # Valider les données
        data = create_listing_schema.load(request.json)
        
        # Vérifier que la catégorie existe
        category = ListingCategory.query.get(data['category_id'])
        if not category:
            return jsonify({'error': 'Catégorie non trouvée'}), 400
        
        # Créer l'annonce
        listing = Listing(
            user_id=user.id,
            category_id=category.id,
            title=data['title'],
            description=data['description'],
            listing_type=data['listing_type'],
            condition=data.get('condition'),
            brand=data.get('brand'),
            model=data.get('model'),
            year=data.get('year'),
            estimated_value=data.get('estimated_value'),
            price_range_min=data.get('price_range_min'),
            price_range_max=data.get('price_range_max'),
            currency=data.get('currency', 'CHF'),
            city=data.get('city'),
            postal_code=data.get('postal_code'),
            country=data.get('country', 'Switzerland'),
            latitude=data.get('latitude'),
            longitude=data.get('longitude'),
            exchange_type=data.get('exchange_type', 'both'),
            desired_items=data.get('desired_items'),
            excluded_items=data.get('excluded_items'),
            tags=data.get('tags')
        )
        
        db.session.add(listing)
        db.session.commit()
        
        # Mettre à jour les statistiques de l'utilisateur
        user.total_listings += 1
        user.active_listings += 1
        db.session.commit()
        
        return jsonify({
            'message': 'Annonce créée avec succès',
            'listing': listing.to_dict()
        }), 201
        
    except ValidationError as e:
        return jsonify({'error': 'Données invalides', 'details': e.messages}), 400
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Erreur lors de la création de l'annonce: {str(e)}")
        return jsonify({'error': 'Erreur interne du serveur'}), 500

@listings_bp.route('/<listing_id>', methods=['PUT'])
@jwt_required()
@limiter.limit("10 per hour")
def update_listing(listing_id):
    """Mettre à jour une annonce"""
    try:
        current_user_id = get_jwt_identity()
        listing = Listing.query.get(listing_id)
        
        if not listing:
            return jsonify({'error': 'Annonce non trouvée'}), 404
        
        if listing.user_id != current_user_id:
            return jsonify({'error': 'Non autorisé'}), 403
        
        # Valider les données
        data = update_listing_schema.load(request.json, partial=True)
        
        # Mettre à jour les champs
        for field, value in data.items():
            if hasattr(listing, field):
                setattr(listing, field, value)
        
        # Mettre à jour le vecteur de recherche
        listing.update_search_vector()
        
        db.session.commit()
        
        return jsonify({
            'message': 'Annonce mise à jour avec succès',
            'listing': listing.to_dict()
        }), 200
        
    except ValidationError as e:
        return jsonify({'error': 'Données invalides', 'details': e.messages}), 400
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Erreur lors de la mise à jour de l'annonce: {str(e)}")
        return jsonify({'error': 'Erreur interne du serveur'}), 500

@listings_bp.route('/<listing_id>', methods=['DELETE'])
@jwt_required()
@limiter.limit("10 per hour")
def delete_listing(listing_id):
    """Supprimer une annonce"""
    try:
        current_user_id = get_jwt_identity()
        listing = Listing.query.get(listing_id)
        
        if not listing:
            return jsonify({'error': 'Annonce non trouvée'}), 404
        
        if listing.user_id != current_user_id:
            return jsonify({'error': 'Non autorisé'}), 403
        
        # Marquer comme supprimée
        listing.status = ListingStatus.DELETED.value
        
        # Mettre à jour les statistiques de l'utilisateur
        listing.user.active_listings -= 1
        if listing.user.active_listings < 0:
            listing.user.active_listings = 0
        
        db.session.commit()
        
        return jsonify({'message': 'Annonce supprimée avec succès'}), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Erreur lors de la suppression de l'annonce: {str(e)}")
        return jsonify({'error': 'Erreur interne du serveur'}), 500

@listings_bp.route('/<listing_id>/publish', methods=['POST'])
@jwt_required()
@limiter.limit("10 per hour")
def publish_listing(listing_id):
    """Publier une annonce"""
    try:
        current_user_id = get_jwt_identity()
        listing = Listing.query.get(listing_id)
        
        if not listing:
            return jsonify({'error': 'Annonce non trouvée'}), 404
        
        if listing.user_id != current_user_id:
            return jsonify({'error': 'Non autorisé'}), 403
        
        if listing.status != ListingStatus.DRAFT.value:
            return jsonify({'error': 'Annonce déjà publiée'}), 400
        
        # Publier l'annonce
        listing.publish()
        
        return jsonify({
            'message': 'Annonce publiée avec succès',
            'listing': listing.to_dict()
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erreur lors de la publication de l'annonce: {str(e)}")
        return jsonify({'error': 'Erreur interne du serveur'}), 500

@listings_bp.route('/<listing_id>/pause', methods=['POST'])
@jwt_required()
@limiter.limit("10 per hour")
def pause_listing(listing_id):
    """Mettre en pause une annonce"""
    try:
        current_user_id = get_jwt_identity()
        listing = Listing.query.get(listing_id)
        
        if not listing:
            return jsonify({'error': 'Annonce non trouvée'}), 404
        
        if listing.user_id != current_user_id:
            return jsonify({'error': 'Non autorisé'}), 403
        
        if listing.status != ListingStatus.ACTIVE.value:
            return jsonify({'error': 'Annonce non active'}), 400
        
        # Mettre en pause
        listing.pause()
        
        # Mettre à jour les statistiques
        listing.user.active_listings -= 1
        if listing.user.active_listings < 0:
            listing.user.active_listings = 0
        
        db.session.commit()
        
        return jsonify({
            'message': 'Annonce mise en pause avec succès',
            'listing': listing.to_dict()
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erreur lors de la mise en pause: {str(e)}")
        return jsonify({'error': 'Erreur interne du serveur'}), 500

@listings_bp.route('/<listing_id>/resume', methods=['POST'])
@jwt_required()
@limiter.limit("10 per hour")
def resume_listing(listing_id):
    """Reprendre une annonce"""
    try:
        current_user_id = get_jwt_identity()
        listing = Listing.query.get(listing_id)
        
        if not listing:
            return jsonify({'error': 'Annonce non trouvée'}), 404
        
        if listing.user_id != current_user_id:
            return jsonify({'error': 'Non autorisé'}), 403
        
        if listing.status != ListingStatus.PAUSED.value:
            return jsonify({'error': 'Annonce non en pause'}), 400
        
        # Reprendre
        listing.resume()
        
        # Mettre à jour les statistiques
        listing.user.active_listings += 1
        
        db.session.commit()
        
        return jsonify({
            'message': 'Annonce reprise avec succès',
            'listing': listing.to_dict()
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erreur lors de la reprise: {str(e)}")
        return jsonify({'error': 'Erreur interne du serveur'}), 500

@listings_bp.route('/<listing_id>/boost', methods=['POST'])
@jwt_required()
@limiter.limit("5 per hour")
def boost_listing(listing_id):
    """Booster une annonce"""
    try:
        current_user_id = get_jwt_identity()
        listing = Listing.query.get(listing_id)
        
        if not listing:
            return jsonify({'error': 'Annonce non trouvée'}), 404
        
        if listing.user_id != current_user_id:
            return jsonify({'error': 'Non autorisé'}), 403
        
        if listing.status != ListingStatus.ACTIVE.value:
            return jsonify({'error': 'Annonce non active'}), 400
        
        # Durée du boost (en jours)
        days = request.json.get('days', 7)
        
        # Booster l'annonce
        listing.boost(days)
        
        return jsonify({
            'message': 'Annonce boostée avec succès',
            'listing': listing.to_dict()
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erreur lors du boost: {str(e)}")
        return jsonify({'error': 'Erreur interne du serveur'}), 500

@listings_bp.route('/<listing_id>/images', methods=['POST'])
@jwt_required()
@limiter.limit("10 per hour")
def upload_listing_image(listing_id):
    """Uploader une image pour une annonce"""
    try:
        current_user_id = get_jwt_identity()
        listing = Listing.query.get(listing_id)
        
        if not listing:
            return jsonify({'error': 'Annonce non trouvée'}), 404
        
        if listing.user_id != current_user_id:
            return jsonify({'error': 'Non autorisé'}), 403
        
        if 'image' not in request.files:
            return jsonify({'error': 'Aucun fichier fourni'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'Aucun fichier sélectionné'}), 400
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # Générer un nom unique
            unique_filename = f"{listing.id}_{uuid.uuid4().hex}_{filename}"
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'listings', unique_filename)
            
            # Créer le dossier s'il n'existe pas
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Sauvegarder le fichier
            file.save(file_path)
            
            # Créer l'enregistrement d'image
            listing_image = ListingImage(
                listing_id=listing.id,
                filename=unique_filename,
                original_filename=filename,
                file_path=f"/uploads/listings/{unique_filename}",
                file_size=os.path.getsize(file_path),
                mime_type=file.content_type,
                is_main=len(listing.images) == 0  # Première image = image principale
            )
            
            db.session.add(listing_image)
            db.session.commit()
            
            return jsonify({
                'message': 'Image uploadée avec succès',
                'image': listing_image.to_dict()
            }), 200
        else:
            return jsonify({'error': 'Type de fichier non autorisé'}), 400
        
    except Exception as e:
        current_app.logger.error(f"Erreur lors de l'upload de l'image: {str(e)}")
        return jsonify({'error': 'Erreur interne du serveur'}), 500

@listings_bp.route('/categories', methods=['GET'])
def get_categories():
    """Obtenir la liste des catégories"""
    try:
        categories = ListingCategory.query.filter_by(is_active=True).order_by(ListingCategory.sort_order).all()
        
        return jsonify({
            'categories': [category.to_dict() for category in categories]
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erreur lors de la récupération des catégories: {str(e)}")
        return jsonify({'error': 'Erreur interne du serveur'}), 500

# Fonctions utilitaires
def allowed_file(filename):
    """Vérifier si le type de fichier est autorisé"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']
