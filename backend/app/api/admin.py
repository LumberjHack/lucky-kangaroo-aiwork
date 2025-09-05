"""
Blueprint d'administration pour Lucky Kangaroo
Gestion administrative de la plateforme
"""

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from marshmallow import Schema, fields, validate, ValidationError
from datetime import datetime, timedelta
from sqlalchemy import func, desc

from app import db
from app.models.user import User, UserStatus, UserRole
from app.models.listing import Listing, ListingStatus, ListingCategory
from app.models.exchange import Exchange, ExchangeStatus
from app.models.chat import Chat
from app.models.notification import Notification, NotificationType
from app.models.review import Review

# Créer le blueprint
admin_bp = Blueprint('admin', __name__)

# Limiter de taux
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100 per hour"]
)

# Schémas de validation
class UpdateUserStatusSchema(Schema):
    status = fields.Str(required=True, validate=validate.OneOf(['active', 'inactive', 'suspended', 'banned']))
    reason = fields.Str(validate=validate.Length(max=500))

class UpdateUserRoleSchema(Schema):
    role = fields.Str(required=True, validate=validate.OneOf(['user', 'moderator', 'admin', 'super_admin']))

class CreateCategorySchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=2, max=100))
    description = fields.Str(validate=validate.Length(max=500))
    icon = fields.Str(validate=validate.Length(max=100))
    parent_id = fields.UUID()
    sort_order = fields.Int(validate=validate.Range(min=0))

class UpdateCategorySchema(Schema):
    name = fields.Str(validate=validate.Length(min=2, max=100))
    description = fields.Str(validate=validate.Length(max=500))
    icon = fields.Str(validate=validate.Length(max=100))
    parent_id = fields.UUID()
    sort_order = fields.Int(validate=validate.Range(min=0))
    is_active = fields.Bool()

# Instancier les schémas
update_user_status_schema = UpdateUserStatusSchema()
update_user_role_schema = UpdateUserRoleSchema()
create_category_schema = CreateCategorySchema()
update_category_schema = UpdateCategorySchema()

# Middleware pour vérifier les permissions admin
def require_admin(f):
    """Décorateur pour vérifier les permissions administrateur"""
    def decorated_function(*args, **kwargs):
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or not user.is_admin:
            return jsonify({'error': 'Accès refusé'}), 403
        
        return f(*args, **kwargs)
    
    decorated_function.__name__ = f.__name__
    return decorated_function

@admin_bp.route('/dashboard', methods=['GET'])
@jwt_required()
@require_admin
def get_dashboard_stats():
    """Obtenir les statistiques du tableau de bord admin"""
    try:
        # Statistiques générales
        total_users = User.query.count()
        active_users = User.query.filter_by(status=UserStatus.ACTIVE.value).count()
        new_users_today = User.query.filter(
            User.created_at >= datetime.utcnow().date()
        ).count()
        
        total_listings = Listing.query.count()
        active_listings = Listing.query.filter_by(status=ListingStatus.ACTIVE.value).count()
        new_listings_today = Listing.query.filter(
            Listing.created_at >= datetime.utcnow().date()
        ).count()
        
        total_exchanges = Exchange.query.count()
        active_exchanges = Exchange.query.filter(
            Exchange.status.in_([ExchangeStatus.PENDING.value, ExchangeStatus.ACCEPTED.value, ExchangeStatus.IN_PROGRESS.value])
        ).count()
        completed_exchanges = Exchange.query.filter_by(status=ExchangeStatus.COMPLETED.value).count()
        
        total_chats = Chat.query.count()
        active_chats = Chat.query.filter_by(status=ChatStatus.ACTIVE.value).count()
        
        # Statistiques par période
        users_last_7_days = User.query.filter(
            User.created_at >= datetime.utcnow() - timedelta(days=7)
        ).count()
        
        listings_last_7_days = Listing.query.filter(
            Listing.created_at >= datetime.utcnow() - timedelta(days=7)
        ).count()
        
        exchanges_last_7_days = Exchange.query.filter(
            Exchange.created_at >= datetime.utcnow() - timedelta(days=7)
        ).count()
        
        # Top catégories
        top_categories = db.session.query(
            ListingCategory.name,
            func.count(Listing.id).label('count')
        ).join(Listing).filter(
            Listing.status == ListingStatus.ACTIVE.value
        ).group_by(ListingCategory.id, ListingCategory.name).order_by(
            func.count(Listing.id).desc()
        ).limit(10).all()
        
        # Top villes
        top_cities = db.session.query(
            Listing.city,
            func.count(Listing.id).label('count')
        ).filter(
            Listing.city.isnot(None),
            Listing.status == ListingStatus.ACTIVE.value
        ).group_by(Listing.city).order_by(
            func.count(Listing.id).desc()
        ).limit(10).all()
        
        return jsonify({
            'stats': {
                'users': {
                    'total': total_users,
                    'active': active_users,
                    'new_today': new_users_today,
                    'new_last_7_days': users_last_7_days
                },
                'listings': {
                    'total': total_listings,
                    'active': active_listings,
                    'new_today': new_listings_today,
                    'new_last_7_days': listings_last_7_days
                },
                'exchanges': {
                    'total': total_exchanges,
                    'active': active_exchanges,
                    'completed': completed_exchanges,
                    'new_last_7_days': exchanges_last_7_days
                },
                'chats': {
                    'total': total_chats,
                    'active': active_chats
                }
            },
            'top_categories': [
                {'name': cat[0], 'count': cat[1]} for cat in top_categories
            ],
            'top_cities': [
                {'name': city[0], 'count': city[1]} for city in top_cities
            ]
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erreur lors de la récupération des statistiques: {str(e)}")
        return jsonify({'error': 'Erreur interne du serveur'}), 500

@admin_bp.route('/users', methods=['GET'])
@jwt_required()
@require_admin
def get_users():
    """Obtenir la liste des utilisateurs"""
    try:
        # Paramètres de pagination
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        
        # Filtres
        status = request.args.get('status')
        role = request.args.get('role')
        search = request.args.get('search')
        sort_by = request.args.get('sort_by', 'created_at')
        sort_order = request.args.get('sort_order', 'desc')
        
        # Construire la requête
        query = User.query
        
        # Appliquer les filtres
        if status:
            query = query.filter_by(status=status)
        if role:
            query = query.filter_by(role=role)
        if search:
            query = query.filter(
                db.or_(
                    User.email.ilike(f'%{search}%'),
                    User.username.ilike(f'%{search}%'),
                    User.first_name.ilike(f'%{search}%'),
                    User.last_name.ilike(f'%{search}%')
                )
            )
        
        # Tri
        if sort_by == 'email':
            if sort_order == 'asc':
                query = query.order_by(User.email.asc())
            else:
                query = query.order_by(User.email.desc())
        elif sort_by == 'trust_score':
            if sort_order == 'asc':
                query = query.order_by(User.trust_score.asc())
            else:
                query = query.order_by(User.trust_score.desc())
        else:  # created_at
            if sort_order == 'asc':
                query = query.order_by(User.created_at.asc())
            else:
                query = query.order_by(User.created_at.desc())
        
        # Pagination
        pagination = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'users': [user.to_dict(include_private=True) for user in pagination.items],
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
        current_app.logger.error(f"Erreur lors de la récupération des utilisateurs: {str(e)}")
        return jsonify({'error': 'Erreur interne du serveur'}), 500

@admin_bp.route('/users/<user_id>/status', methods=['PUT'])
@jwt_required()
@require_admin
@limiter.limit("10 per minute")
def update_user_status(user_id):
    """Mettre à jour le statut d'un utilisateur"""
    try:
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'Utilisateur non trouvé'}), 404
        
        # Valider les données
        data = update_user_status_schema.load(request.json)
        
        # Mettre à jour le statut
        user.status = data['status']
        
        # Ajouter la raison dans les métadonnées
        if data.get('reason'):
            user.metadata['status_change_reason'] = data['reason']
            user.metadata['status_change_date'] = datetime.utcnow().isoformat()
        
        db.session.commit()
        
        return jsonify({
            'message': 'Statut utilisateur mis à jour avec succès',
            'user': user.to_dict(include_private=True)
        }), 200
        
    except ValidationError as e:
        return jsonify({'error': 'Données invalides', 'details': e.messages}), 400
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Erreur lors de la mise à jour du statut: {str(e)}")
        return jsonify({'error': 'Erreur interne du serveur'}), 500

@admin_bp.route('/users/<user_id>/role', methods=['PUT'])
@jwt_required()
@require_admin
@limiter.limit("10 per minute")
def update_user_role(user_id):
    """Mettre à jour le rôle d'un utilisateur"""
    try:
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'Utilisateur non trouvé'}), 404
        
        # Valider les données
        data = update_user_role_schema.load(request.json)
        
        # Mettre à jour le rôle
        user.role = data['role']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Rôle utilisateur mis à jour avec succès',
            'user': user.to_dict(include_private=True)
        }), 200
        
    except ValidationError as e:
        return jsonify({'error': 'Données invalides', 'details': e.messages}), 400
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Erreur lors de la mise à jour du rôle: {str(e)}")
        return jsonify({'error': 'Erreur interne du serveur'}), 500

@admin_bp.route('/listings', methods=['GET'])
@jwt_required()
@require_admin
def get_listings():
    """Obtenir la liste des annonces"""
    try:
        # Paramètres de pagination
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        
        # Filtres
        status = request.args.get('status')
        category_id = request.args.get('category_id')
        search = request.args.get('search')
        sort_by = request.args.get('sort_by', 'created_at')
        sort_order = request.args.get('sort_order', 'desc')
        
        # Construire la requête
        query = Listing.query
        
        # Appliquer les filtres
        if status:
            query = query.filter_by(status=status)
        if category_id:
            query = query.filter_by(category_id=category_id)
        if search:
            query = query.filter(
                db.or_(
                    Listing.title.ilike(f'%{search}%'),
                    Listing.description.ilike(f'%{search}%')
                )
            )
        
        # Tri
        if sort_by == 'title':
            if sort_order == 'asc':
                query = query.order_by(Listing.title.asc())
            else:
                query = query.order_by(Listing.title.desc())
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
            'listings': [listing.to_dict(include_private=True) for listing in pagination.items],
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

@admin_bp.route('/categories', methods=['GET'])
@jwt_required()
@require_admin
def get_categories():
    """Obtenir la liste des catégories"""
    try:
        categories = ListingCategory.query.order_by(ListingCategory.sort_order).all()
        
        return jsonify({
            'categories': [category.to_dict() for category in categories]
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erreur lors de la récupération des catégories: {str(e)}")
        return jsonify({'error': 'Erreur interne du serveur'}), 500

@admin_bp.route('/categories', methods=['POST'])
@jwt_required()
@require_admin
@limiter.limit("10 per hour")
def create_category():
    """Créer une nouvelle catégorie"""
    try:
        # Valider les données
        data = create_category_schema.load(request.json)
        
        # Créer la catégorie
        category = ListingCategory(
            name=data['name'],
            description=data.get('description'),
            icon=data.get('icon'),
            parent_id=data.get('parent_id'),
            sort_order=data.get('sort_order', 0)
        )
        
        db.session.add(category)
        db.session.commit()
        
        return jsonify({
            'message': 'Catégorie créée avec succès',
            'category': category.to_dict()
        }), 201
        
    except ValidationError as e:
        return jsonify({'error': 'Données invalides', 'details': e.messages}), 400
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Erreur lors de la création de la catégorie: {str(e)}")
        return jsonify({'error': 'Erreur interne du serveur'}), 500

@admin_bp.route('/categories/<category_id>', methods=['PUT'])
@jwt_required()
@require_admin
@limiter.limit("10 per hour")
def update_category(category_id):
    """Mettre à jour une catégorie"""
    try:
        category = ListingCategory.query.get(category_id)
        
        if not category:
            return jsonify({'error': 'Catégorie non trouvée'}), 404
        
        # Valider les données
        data = update_category_schema.load(request.json, partial=True)
        
        # Mettre à jour les champs
        for field, value in data.items():
            if hasattr(category, field):
                setattr(category, field, value)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Catégorie mise à jour avec succès',
            'category': category.to_dict()
        }), 200
        
    except ValidationError as e:
        return jsonify({'error': 'Données invalides', 'details': e.messages}), 400
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Erreur lors de la mise à jour de la catégorie: {str(e)}")
        return jsonify({'error': 'Erreur interne du serveur'}), 500

@admin_bp.route('/reports', methods=['GET'])
@jwt_required()
@require_admin
def get_reports():
    """Obtenir les rapports et signalements"""
    try:
        # Paramètres de pagination
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        
        # Filtres
        report_type = request.args.get('type')
        status = request.args.get('status')
        sort_by = request.args.get('sort_by', 'created_at')
        sort_order = request.args.get('sort_order', 'desc')
        
        # Construire la requête
        query = db.session.query(
            Review.id,
            Review.reviewer_id,
            Review.reviewee_id,
            Review.rating,
            Review.comment,
            Review.created_at,
            Review.is_public
        ).filter(
            Review.rating <= 2  # Avis négatifs
        )
        
        # Tri
        if sort_by == 'rating':
            if sort_order == 'asc':
                query = query.order_by(Review.rating.asc())
            else:
                query = query.order_by(Review.rating.desc())
        else:  # created_at
            if sort_order == 'asc':
                query = query.order_by(Review.created_at.asc())
            else:
                query = query.order_by(Review.created_at.desc())
        
        # Pagination
        pagination = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # Formater les résultats
        reports = []
        for report in pagination.items:
            reports.append({
                'id': str(report.id),
                'type': 'negative_review',
                'rating': report.rating,
                'comment': report.comment,
                'created_at': report.created_at.isoformat(),
                'reviewer_id': str(report.reviewer_id),
                'reviewee_id': str(report.reviewee_id)
            })
        
        return jsonify({
            'reports': reports,
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
        current_app.logger.error(f"Erreur lors de la récupération des rapports: {str(e)}")
        return jsonify({'error': 'Erreur interne du serveur'}), 500

@admin_bp.route('/system/health', methods=['GET'])
@jwt_required()
@require_admin
def get_system_health():
    """Obtenir l'état de santé du système"""
    try:
        # Vérifier la base de données
        db_status = 'healthy'
        try:
            db.session.execute('SELECT 1')
        except Exception as e:
            db_status = f'unhealthy: {str(e)}'
        
        # Vérifier Redis (si configuré)
        redis_status = 'not_configured'
        try:
            # Ici, vous pourriez vérifier Redis
            pass
        except Exception as e:
            redis_status = f'unhealthy: {str(e)}'
        
        # Statistiques de performance
        performance_stats = {
            'database_connections': db.session.bind.pool.size(),
            'active_sessions': db.session.bind.pool.checkedout(),
            'available_connections': db.session.bind.pool.checkedin()
        }
        
        return jsonify({
            'status': 'healthy' if db_status == 'healthy' else 'unhealthy',
            'services': {
                'database': db_status,
                'redis': redis_status
            },
            'performance': performance_stats,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erreur lors de la vérification de santé: {str(e)}")
        return jsonify({'error': 'Erreur interne du serveur'}), 500
