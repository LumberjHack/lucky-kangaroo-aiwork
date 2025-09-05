"""
Blueprint des échanges pour Lucky Kangaroo
Gestion des échanges directs et en chaîne
"""

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from marshmallow import Schema, fields, validate, ValidationError
from datetime import datetime, timedelta

from app import db
from app.models.user import User
from app.models.listing import Listing, ListingStatus
from app.models.exchange import Exchange, ExchangeStatus, ExchangeType, ExchangeParticipantRole
from app.models.notification import Notification, NotificationType

# Créer le blueprint
exchanges_bp = Blueprint('exchanges', __name__)

# Limiter de taux
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100 per hour"]
)

# Schémas de validation
class CreateExchangeSchema(Schema):
    listing_id = fields.UUID(required=True)
    title = fields.Str(required=True, validate=validate.Length(min=5, max=200))
    description = fields.Str(validate=validate.Length(max=1000))
    proposed_items = fields.List(fields.Str())
    proposed_value = fields.Float(validate=validate.Range(min=0))
    currency = fields.Str(validate=validate.OneOf(['CHF', 'EUR', 'USD']))
    exchange_type = fields.Str(validate=validate.OneOf(['direct', 'chain']))

class UpdateExchangeSchema(Schema):
    title = fields.Str(validate=validate.Length(min=5, max=200))
    description = fields.Str(validate=validate.Length(max=1000))
    proposed_items = fields.List(fields.Str())
    proposed_value = fields.Float(validate=validate.Range(min=0))
    currency = fields.Str(validate=validate.OneOf(['CHF', 'EUR', 'USD']))

class ScheduleMeetingSchema(Schema):
    meeting_date = fields.DateTime(required=True)
    location = fields.Str(validate=validate.Length(max=200))
    address = fields.Str(validate=validate.Length(max=500))
    instructions = fields.Str(validate=validate.Length(max=1000))

class RateExchangeSchema(Schema):
    rating = fields.Int(required=True, validate=validate.Range(min=1, max=5))
    review = fields.Str(validate=validate.Length(max=500))
    communication_rating = fields.Int(validate=validate.Range(min=1, max=5))
    item_condition_rating = fields.Int(validate=validate.Range(min=1, max=5))
    meeting_rating = fields.Int(validate=validate.Range(min=1, max=5))
    overall_experience_rating = fields.Int(validate=validate.Range(min=1, max=5))

# Instancier les schémas
create_exchange_schema = CreateExchangeSchema()
update_exchange_schema = UpdateExchangeSchema()
schedule_meeting_schema = ScheduleMeetingSchema()
rate_exchange_schema = RateExchangeSchema()

@exchanges_bp.route('/', methods=['GET'])
@jwt_required()
def get_exchanges():
    """Obtenir la liste des échanges de l'utilisateur"""
    try:
        current_user_id = get_jwt_identity()
        
        # Paramètres de pagination
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        
        # Filtres
        status = request.args.get('status')
        exchange_type = request.args.get('exchange_type')
        sort_by = request.args.get('sort_by', 'created_at')
        sort_order = request.args.get('sort_order', 'desc')
        
        # Construire la requête
        query = Exchange.query.filter(
            db.or_(
                Exchange.owner_id == current_user_id,
                Exchange.participants.any(user_id=current_user_id)
            )
        )
        
        # Appliquer les filtres
        if status:
            query = query.filter_by(status=status)
        if exchange_type:
            query = query.filter_by(exchange_type=exchange_type)
        
        # Tri
        if sort_by == 'updated_at':
            if sort_order == 'asc':
                query = query.order_by(Exchange.updated_at.asc())
            else:
                query = query.order_by(Exchange.updated_at.desc())
        else:  # created_at
            if sort_order == 'asc':
                query = query.order_by(Exchange.created_at.asc())
            else:
                query = query.order_by(Exchange.created_at.desc())
        
        # Pagination
        pagination = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'exchanges': [exchange.to_dict(include_private=True) for exchange in pagination.items],
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
        current_app.logger.error(f"Erreur lors de la récupération des échanges: {str(e)}")
        return jsonify({'error': 'Erreur interne du serveur'}), 500

@exchanges_bp.route('/<exchange_id>', methods=['GET'])
@jwt_required()
def get_exchange(exchange_id):
    """Obtenir un échange spécifique"""
    try:
        current_user_id = get_jwt_identity()
        exchange = Exchange.query.get(exchange_id)
        
        if not exchange:
            return jsonify({'error': 'Échange non trouvé'}), 404
        
        # Vérifier que l'utilisateur est participant
        if exchange.owner_id != current_user_id and not any(p.user_id == current_user_id for p in exchange.participants):
            return jsonify({'error': 'Non autorisé'}), 403
        
        return jsonify({
            'exchange': exchange.to_dict(include_private=True)
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erreur lors de la récupération de l'échange: {str(e)}")
        return jsonify({'error': 'Erreur interne du serveur'}), 500

@exchanges_bp.route('/', methods=['POST'])
@jwt_required()
@limiter.limit("10 per hour")
def create_exchange():
    """Créer un nouvel échange"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'Utilisateur non trouvé'}), 404
        
        # Valider les données
        data = create_exchange_schema.load(request.json)
        
        # Vérifier que l'annonce existe et est active
        listing = Listing.query.get(data['listing_id'])
        if not listing:
            return jsonify({'error': 'Annonce non trouvée'}), 404
        
        if listing.status != ListingStatus.ACTIVE.value:
            return jsonify({'error': 'Annonce non disponible'}), 400
        
        # Vérifier que l'utilisateur n'est pas le propriétaire
        if listing.user_id == current_user_id:
            return jsonify({'error': 'Vous ne pouvez pas échanger avec vous-même'}), 400
        
        # Vérifier qu'il n'y a pas déjà un échange en cours
        existing_exchange = Exchange.query.filter_by(
            listing_id=data['listing_id'],
            status=ExchangeStatus.PENDING.value
        ).filter(
            Exchange.participants.any(user_id=current_user_id)
        ).first()
        
        if existing_exchange:
            return jsonify({'error': 'Un échange est déjà en cours pour cette annonce'}), 400
        
        # Créer l'échange
        exchange = Exchange(
            listing_id=listing.id,
            owner_id=listing.user_id,
            title=data['title'],
            description=data.get('description'),
            proposed_items=data.get('proposed_items'),
            proposed_value=data.get('proposed_value'),
            currency=data.get('currency', 'CHF'),
            exchange_type=data.get('exchange_type', 'direct')
        )
        
        db.session.add(exchange)
        db.session.flush()  # Pour obtenir l'ID
        
        # Ajouter l'initiateur comme participant
        exchange.add_participant(
            user_id=current_user_id,
            role=ExchangeParticipantRole.INITIATOR.value,
            proposed_items=data.get('proposed_items')
        )
        
        db.session.commit()
        
        # Créer une notification pour le propriétaire
        notification = Notification(
            user_id=listing.user_id,
            notification_type=NotificationType.EXCHANGE.value,
            title="Nouvelle demande d'échange",
            message=f"{user.display_name} souhaite échanger avec vous",
            action_url=f"/exchanges/{exchange.id}"
        )
        db.session.add(notification)
        db.session.commit()
        
        return jsonify({
            'message': 'Demande d\'échange créée avec succès',
            'exchange': exchange.to_dict(include_private=True)
        }), 201
        
    except ValidationError as e:
        return jsonify({'error': 'Données invalides', 'details': e.messages}), 400
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Erreur lors de la création de l'échange: {str(e)}")
        return jsonify({'error': 'Erreur interne du serveur'}), 500

@exchanges_bp.route('/<exchange_id>', methods=['PUT'])
@jwt_required()
@limiter.limit("10 per hour")
def update_exchange(exchange_id):
    """Mettre à jour un échange"""
    try:
        current_user_id = get_jwt_identity()
        exchange = Exchange.query.get(exchange_id)
        
        if not exchange:
            return jsonify({'error': 'Échange non trouvé'}), 404
        
        # Vérifier que l'utilisateur est participant
        if exchange.owner_id != current_user_id and not any(p.user_id == current_user_id for p in exchange.participants):
            return jsonify({'error': 'Non autorisé'}), 403
        
        # Valider les données
        data = update_exchange_schema.load(request.json, partial=True)
        
        # Mettre à jour les champs
        for field, value in data.items():
            if hasattr(exchange, field):
                setattr(exchange, field, value)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Échange mis à jour avec succès',
            'exchange': exchange.to_dict(include_private=True)
        }), 200
        
    except ValidationError as e:
        return jsonify({'error': 'Données invalides', 'details': e.messages}), 400
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Erreur lors de la mise à jour de l'échange: {str(e)}")
        return jsonify({'error': 'Erreur interne du serveur'}), 500

@exchanges_bp.route('/<exchange_id>/accept', methods=['POST'])
@jwt_required()
@limiter.limit("10 per hour")
def accept_exchange(exchange_id):
    """Accepter un échange"""
    try:
        current_user_id = get_jwt_identity()
        exchange = Exchange.query.get(exchange_id)
        
        if not exchange:
            return jsonify({'error': 'Échange non trouvé'}), 404
        
        # Vérifier que l'utilisateur est le propriétaire
        if exchange.owner_id != current_user_id:
            return jsonify({'error': 'Non autorisé'}), 403
        
        if exchange.status != ExchangeStatus.PENDING.value:
            return jsonify({'error': 'Échange non en attente'}), 400
        
        # Accepter l'échange
        exchange.accept()
        
        # Créer une notification pour l'initiateur
        initiator = exchange.initiator
        if initiator:
            notification = Notification(
                user_id=initiator.id,
                notification_type=NotificationType.EXCHANGE.value,
                title="Échange accepté",
                message=f"Votre demande d'échange a été acceptée",
                action_url=f"/exchanges/{exchange.id}"
            )
            db.session.add(notification)
            db.session.commit()
        
        return jsonify({
            'message': 'Échange accepté avec succès',
            'exchange': exchange.to_dict(include_private=True)
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erreur lors de l'acceptation de l'échange: {str(e)}")
        return jsonify({'error': 'Erreur interne du serveur'}), 500

@exchanges_bp.route('/<exchange_id>/start', methods=['POST'])
@jwt_required()
@limiter.limit("10 per hour")
def start_exchange(exchange_id):
    """Démarrer un échange"""
    try:
        current_user_id = get_jwt_identity()
        exchange = Exchange.query.get(exchange_id)
        
        if not exchange:
            return jsonify({'error': 'Échange non trouvé'}), 404
        
        # Vérifier que l'utilisateur est participant
        if exchange.owner_id != current_user_id and not any(p.user_id == current_user_id for p in exchange.participants):
            return jsonify({'error': 'Non autorisé'}), 403
        
        if exchange.status != ExchangeStatus.ACCEPTED.value:
            return jsonify({'error': 'Échange non accepté'}), 400
        
        # Démarrer l'échange
        exchange.start()
        
        return jsonify({
            'message': 'Échange démarré avec succès',
            'exchange': exchange.to_dict(include_private=True)
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erreur lors du démarrage de l'échange: {str(e)}")
        return jsonify({'error': 'Erreur interne du serveur'}), 500

@exchanges_bp.route('/<exchange_id>/schedule-meeting', methods=['POST'])
@jwt_required()
@limiter.limit("10 per hour")
def schedule_meeting(exchange_id):
    """Planifier un rendez-vous"""
    try:
        current_user_id = get_jwt_identity()
        exchange = Exchange.query.get(exchange_id)
        
        if not exchange:
            return jsonify({'error': 'Échange non trouvé'}), 404
        
        # Vérifier que l'utilisateur est participant
        if exchange.owner_id != current_user_id and not any(p.user_id == current_user_id for p in exchange.participants):
            return jsonify({'error': 'Non autorisé'}), 403
        
        if exchange.status not in [ExchangeStatus.ACCEPTED.value, ExchangeStatus.IN_PROGRESS.value]:
            return jsonify({'error': 'Échange non en cours'}), 400
        
        # Valider les données
        data = schedule_meeting_schema.load(request.json)
        
        # Planifier le rendez-vous
        exchange.schedule_meeting(
            meeting_date=data['meeting_date'],
            location=data.get('location'),
            address=data.get('address'),
            instructions=data.get('instructions')
        )
        
        return jsonify({
            'message': 'Rendez-vous planifié avec succès',
            'exchange': exchange.to_dict(include_private=True)
        }), 200
        
    except ValidationError as e:
        return jsonify({'error': 'Données invalides', 'details': e.messages}), 400
    except Exception as e:
        current_app.logger.error(f"Erreur lors de la planification du rendez-vous: {str(e)}")
        return jsonify({'error': 'Erreur interne du serveur'}), 500

@exchanges_bp.route('/<exchange_id>/complete', methods=['POST'])
@jwt_required()
@limiter.limit("10 per hour")
def complete_exchange(exchange_id):
    """Marquer un échange comme terminé"""
    try:
        current_user_id = get_jwt_identity()
        exchange = Exchange.query.get(exchange_id)
        
        if not exchange:
            return jsonify({'error': 'Échange non trouvé'}), 404
        
        # Vérifier que l'utilisateur est participant
        if exchange.owner_id != current_user_id and not any(p.user_id == current_user_id for p in exchange.participants):
            return jsonify({'error': 'Non autorisé'}), 403
        
        if exchange.status not in [ExchangeStatus.IN_PROGRESS.value, ExchangeStatus.MEETING_SCHEDULED.value]:
            return jsonify({'error': 'Échange non en cours'}), 400
        
        # Terminer l'échange
        exchange.complete()
        
        # Mettre à jour les statistiques des utilisateurs
        for participant in exchange.participants:
            participant.user.total_exchanges += 1
            participant.user.successful_exchanges += 1
        
        exchange.owner.total_exchanges += 1
        exchange.owner.successful_exchanges += 1
        
        db.session.commit()
        
        return jsonify({
            'message': 'Échange terminé avec succès',
            'exchange': exchange.to_dict(include_private=True)
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erreur lors de la finalisation de l'échange: {str(e)}")
        return jsonify({'error': 'Erreur interne du serveur'}), 500

@exchanges_bp.route('/<exchange_id>/cancel', methods=['POST'])
@jwt_required()
@limiter.limit("10 per hour")
def cancel_exchange(exchange_id):
    """Annuler un échange"""
    try:
        current_user_id = get_jwt_identity()
        exchange = Exchange.query.get(exchange_id)
        
        if not exchange:
            return jsonify({'error': 'Échange non trouvé'}), 404
        
        # Vérifier que l'utilisateur est participant
        if exchange.owner_id != current_user_id and not any(p.user_id == current_user_id for p in exchange.participants):
            return jsonify({'error': 'Non autorisé'}), 403
        
        if exchange.status == ExchangeStatus.COMPLETED.value:
            return jsonify({'error': 'Échange déjà terminé'}), 400
        
        # Raison de l'annulation
        reason = request.json.get('reason', 'Annulé par l\'utilisateur')
        
        # Annuler l'échange
        exchange.cancel(reason)
        
        return jsonify({
            'message': 'Échange annulé avec succès',
            'exchange': exchange.to_dict(include_private=True)
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erreur lors de l'annulation de l'échange: {str(e)}")
        return jsonify({'error': 'Erreur interne du serveur'}), 500

@exchanges_bp.route('/<exchange_id>/rate', methods=['POST'])
@jwt_required()
@limiter.limit("5 per hour")
def rate_exchange(exchange_id):
    """Noter un échange"""
    try:
        current_user_id = get_jwt_identity()
        exchange = Exchange.query.get(exchange_id)
        
        if not exchange:
            return jsonify({'error': 'Échange non trouvé'}), 404
        
        # Vérifier que l'utilisateur est participant
        if exchange.owner_id != current_user_id and not any(p.user_id == current_user_id for p in exchange.participants):
            return jsonify({'error': 'Non autorisé'}), 403
        
        if exchange.status != ExchangeStatus.COMPLETED.value:
            return jsonify({'error': 'Échange non terminé'}), 400
        
        # Valider les données
        data = rate_exchange_schema.load(request.json)
        
        # Noter l'échange
        if exchange.owner_id == current_user_id:
            # Le propriétaire note le participant
            exchange.rate_participant(
                rating=data['rating'],
                review=data.get('review')
            )
        else:
            # Le participant note le propriétaire
            exchange.rate_owner(
                rating=data['rating'],
                review=data.get('review')
            )
        
        return jsonify({
            'message': 'Échange noté avec succès',
            'exchange': exchange.to_dict(include_private=True)
        }), 200
        
    except ValidationError as e:
        return jsonify({'error': 'Données invalides', 'details': e.messages}), 400
    except Exception as e:
        current_app.logger.error(f"Erreur lors de la notation de l'échange: {str(e)}")
        return jsonify({'error': 'Erreur interne du serveur'}), 500

@exchanges_bp.route('/<exchange_id>/messages', methods=['GET'])
@jwt_required()
def get_exchange_messages(exchange_id):
    """Obtenir les messages d'un échange"""
    try:
        current_user_id = get_jwt_identity()
        exchange = Exchange.query.get(exchange_id)
        
        if not exchange:
            return jsonify({'error': 'Échange non trouvé'}), 404
        
        # Vérifier que l'utilisateur est participant
        if exchange.owner_id != current_user_id and not any(p.user_id == current_user_id for p in exchange.participants):
            return jsonify({'error': 'Non autorisé'}), 403
        
        # Paramètres de pagination
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 50, type=int), 100)
        
        # Récupérer les messages
        messages = exchange.messages.order_by(exchange.messages.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'messages': [message.to_dict() for message in messages.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': messages.total,
                'pages': messages.pages,
                'has_next': messages.has_next,
                'has_prev': messages.has_prev
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erreur lors de la récupération des messages: {str(e)}")
        return jsonify({'error': 'Erreur interne du serveur'}), 500

@exchanges_bp.route('/<exchange_id>/messages', methods=['POST'])
@jwt_required()
@limiter.limit("20 per minute")
def send_exchange_message(exchange_id):
    """Envoyer un message dans un échange"""
    try:
        current_user_id = get_jwt_identity()
        exchange = Exchange.query.get(exchange_id)
        
        if not exchange:
            return jsonify({'error': 'Échange non trouvé'}), 404
        
        # Vérifier que l'utilisateur est participant
        if exchange.owner_id != current_user_id and not any(p.user_id == current_user_id for p in exchange.participants):
            return jsonify({'error': 'Non autorisé'}), 403
        
        if exchange.status == ExchangeStatus.CANCELLED.value:
            return jsonify({'error': 'Échange annulé'}), 400
        
        # Contenu du message
        message_content = request.json.get('message')
        message_type = request.json.get('message_type', 'text')
        
        if not message_content:
            return jsonify({'error': 'Message requis'}), 400
        
        # Ajouter le message
        exchange_message = exchange.add_message(
            user_id=current_user_id,
            message=message_content,
            message_type=message_type
        )
        
        return jsonify({
            'message': 'Message envoyé avec succès',
            'exchange_message': exchange_message.to_dict()
        }), 201
        
    except Exception as e:
        current_app.logger.error(f"Erreur lors de l'envoi du message: {str(e)}")
        return jsonify({'error': 'Erreur interne du serveur'}), 500

# Moteur de matching intelligent
@exchanges_bp.route('/matching/suggestions', methods=['GET'])
@jwt_required()
@limiter.limit("30 per minute")
def get_matching_suggestions():
    """Obtenir des suggestions de matching pour un utilisateur"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'Utilisateur non trouvé'}), 404
        
        # Paramètres de recherche
        listing_id = request.args.get('listing_id')
        max_distance = int(request.args.get('max_distance', 50))  # km
        max_suggestions = int(request.args.get('max_suggestions', 10))
        
        if listing_id:
            # Suggestions pour une annonce spécifique
            listing = Listing.query.get(listing_id)
            if not listing or listing.user_id != current_user_id:
                return jsonify({'error': 'Annonce non trouvée'}), 404
            
            suggestions = find_matching_suggestions_for_listing(listing, max_distance, max_suggestions)
        else:
            # Suggestions générales pour l'utilisateur
            suggestions = find_general_matching_suggestions(user, max_distance, max_suggestions)
        
        return jsonify({
            'suggestions': suggestions,
            'total': len(suggestions),
            'filters': {
                'max_distance': max_distance,
                'max_suggestions': max_suggestions
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erreur lors de la recherche de suggestions: {str(e)}")
        return jsonify({'error': 'Erreur interne du serveur'}), 500

@exchanges_bp.route('/matching/chains', methods=['GET'])
@jwt_required()
@limiter.limit("20 per minute")
def get_exchange_chains():
    """Obtenir des chaînes d'échange possibles"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'Utilisateur non trouvé'}), 404
        
        # Paramètres
        listing_id = request.args.get('listing_id')
        max_chain_length = int(request.args.get('max_chain_length', 3))
        max_distance = int(request.args.get('max_distance', 100))  # km
        
        if not listing_id:
            return jsonify({'error': 'ID d\'annonce requis'}), 400
        
        listing = Listing.query.get(listing_id)
        if not listing or listing.user_id != current_user_id:
            return jsonify({'error': 'Annonce non trouvée'}), 404
        
        # Trouver les chaînes d'échange
        chains = find_exchange_chains(listing, max_chain_length, max_distance)
        
        return jsonify({
            'chains': chains,
            'total': len(chains),
            'filters': {
                'max_chain_length': max_chain_length,
                'max_distance': max_distance
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erreur lors de la recherche de chaînes: {str(e)}")
        return jsonify({'error': 'Erreur interne du serveur'}), 500

@exchanges_bp.route('/matching/analyze', methods=['POST'])
@jwt_required()
@limiter.limit("10 per minute")
def analyze_matching_potential():
    """Analyser le potentiel de matching entre deux annonces"""
    try:
        current_user_id = get_jwt_identity()
        data = request.json
        
        listing_id_1 = data.get('listing_id_1')
        listing_id_2 = data.get('listing_id_2')
        
        if not listing_id_1 or not listing_id_2:
            return jsonify({'error': 'Deux IDs d\'annonces requis'}), 400
        
        listing_1 = Listing.query.get(listing_id_1)
        listing_2 = Listing.query.get(listing_id_2)
        
        if not listing_1 or not listing_2:
            return jsonify({'error': 'Une ou plusieurs annonces non trouvées'}), 404
        
        # Vérifier que l'utilisateur est propriétaire d'au moins une des annonces
        if listing_1.user_id != current_user_id and listing_2.user_id != current_user_id:
            return jsonify({'error': 'Non autorisé'}), 403
        
        # Analyser le matching
        analysis = analyze_listing_compatibility(listing_1, listing_2)
        
        return jsonify({
            'analysis': analysis,
            'listing_1': {
                'id': listing_1.id,
                'title': listing_1.title,
                'user_id': listing_1.user_id
            },
            'listing_2': {
                'id': listing_2.id,
                'title': listing_2.title,
                'user_id': listing_2.user_id
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erreur lors de l'analyse de matching: {str(e)}")
        return jsonify({'error': 'Erreur interne du serveur'}), 500

# Fonctions utilitaires pour le matching
def find_matching_suggestions_for_listing(listing, max_distance=50, max_suggestions=10):
    """Trouver des suggestions de matching pour une annonce spécifique"""
    suggestions = []
    
    # Critères de matching
    criteria = {
        'category_id': listing.category_id,
        'exchange_type': listing.exchange_type,
        'status': 'active',
        'user_id': {'$ne': listing.user_id}  # Exclure les annonces du même utilisateur
    }
    
    # Recherche d'annonces compatibles
    compatible_listings = Listing.query.filter(
        Listing.category_id == listing.category_id,
        Listing.exchange_type == listing.exchange_type,
        Listing.status == 'active',
        Listing.user_id != listing.user_id
    ).all()
    
    for candidate in compatible_listings:
        # Calculer le score de compatibilité
        compatibility_score = calculate_compatibility_score(listing, candidate)
        
        # Calculer la distance géographique
        distance = calculate_distance(
            listing.latitude, listing.longitude,
            candidate.latitude, candidate.longitude
        )
        
        if distance <= max_distance and compatibility_score > 0.3:
            suggestions.append({
                'listing': {
                    'id': candidate.id,
                    'title': candidate.title,
                    'description': candidate.description[:200] + '...' if len(candidate.description) > 200 else candidate.description,
                    'estimated_value': candidate.estimated_value,
                    'currency': candidate.currency,
                    'condition': candidate.condition,
                    'city': candidate.city,
                    'user': {
                        'id': candidate.user.id,
                        'username': candidate.user.username,
                        'trust_score': candidate.user.trust_score
                    }
                },
                'compatibility_score': compatibility_score,
                'distance_km': round(distance, 2),
                'match_reasons': get_match_reasons(listing, candidate)
            })
    
    # Trier par score de compatibilité
    suggestions.sort(key=lambda x: x['compatibility_score'], reverse=True)
    
    return suggestions[:max_suggestions]

def find_general_matching_suggestions(user, max_distance=50, max_suggestions=10):
    """Trouver des suggestions générales de matching pour un utilisateur"""
    suggestions = []
    
    # Récupérer les annonces actives de l'utilisateur
    user_listings = Listing.query.filter(
        Listing.user_id == user.id,
        Listing.status == 'active'
    ).all()
    
    for listing in user_listings:
        listing_suggestions = find_matching_suggestions_for_listing(listing, max_distance, 5)
        suggestions.extend(listing_suggestions)
    
    # Dédupliquer et trier
    seen_ids = set()
    unique_suggestions = []
    
    for suggestion in suggestions:
        listing_id = suggestion['listing']['id']
        if listing_id not in seen_ids:
            seen_ids.add(listing_id)
            unique_suggestions.append(suggestion)
    
    # Trier par score de compatibilité
    unique_suggestions.sort(key=lambda x: x['compatibility_score'], reverse=True)
    
    return unique_suggestions[:max_suggestions]

def find_exchange_chains(listing, max_chain_length=3, max_distance=100):
    """Trouver des chaînes d'échange possibles"""
    chains = []
    
    def find_chain_recursive(current_listing, target_listing, visited, chain, max_length):
        if len(chain) >= max_length:
            return
        
        # Trouver des annonces compatibles
        compatible_listings = Listing.query.filter(
            Listing.category_id == current_listing.category_id,
            Listing.exchange_type == current_listing.exchange_type,
            Listing.status == 'active',
            Listing.user_id != current_listing.user_id,
            Listing.id.notin_(visited)
        ).all()
        
        for candidate in compatible_listings:
            # Vérifier la distance
            distance = calculate_distance(
                current_listing.latitude, current_listing.longitude,
                candidate.latitude, candidate.longitude
            )
            
            if distance <= max_distance:
                new_chain = chain + [candidate]
                new_visited = visited + [candidate.id]
                
                # Vérifier si on peut atteindre la cible
                if candidate.user_id == target_listing.user_id:
                    # Chaîne trouvée !
                    chains.append({
                        'chain': [listing] + new_chain + [target_listing],
                        'length': len(new_chain) + 2,
                        'total_distance': sum([
                            calculate_distance(
                                new_chain[i].latitude, new_chain[i].longitude,
                                new_chain[i+1].latitude, new_chain[i+1].longitude
                            ) for i in range(len(new_chain))
                        ]),
                        'feasibility_score': calculate_chain_feasibility(new_chain)
                    })
                else:
                    # Continuer la recherche
                    find_chain_recursive(candidate, target_listing, new_visited, new_chain, max_length)
    
    # Pour l'instant, on simule des chaînes (dans une vraie implémentation, on utiliserait un algorithme plus sophistiqué)
    # Simuler quelques chaînes d'exemple
    chains = [
        {
            'chain': [
                {'id': listing.id, 'title': listing.title, 'user_id': listing.user_id},
                {'id': 'chain-1', 'title': 'Annonce intermédiaire 1', 'user_id': 'user-2'},
                {'id': 'chain-2', 'title': 'Annonce intermédiaire 2', 'user_id': 'user-3'},
                {'id': 'target', 'title': 'Annonce cible', 'user_id': 'user-4'}
            ],
            'length': 4,
            'total_distance': 45.2,
            'feasibility_score': 0.85
        }
    ]
    
    return chains

def analyze_listing_compatibility(listing_1, listing_2):
    """Analyser la compatibilité entre deux annonces"""
    compatibility_score = calculate_compatibility_score(listing_1, listing_2)
    
    # Calculer la distance
    distance = calculate_distance(
        listing_1.latitude, listing_1.longitude,
        listing_2.latitude, listing_2.longitude
    )
    
    # Analyser les facteurs de compatibilité
    factors = {
        'category_match': listing_1.category_id == listing_2.category_id,
        'exchange_type_match': listing_1.exchange_type == listing_2.exchange_type,
        'value_compatibility': abs(listing_1.estimated_value - listing_2.estimated_value) / max(listing_1.estimated_value, listing_2.estimated_value) < 0.3,
        'condition_compatibility': listing_1.condition == listing_2.condition,
        'geographical_proximity': distance <= 50,  # 50km
        'user_trust_compatibility': abs(listing_1.user.trust_score - listing_2.user.trust_score) <= 1.0
    }
    
    # Calculer le score global
    positive_factors = sum(1 for factor in factors.values() if factor)
    total_factors = len(factors)
    
    return {
        'compatibility_score': compatibility_score,
        'distance_km': round(distance, 2),
        'factors': factors,
        'positive_factors': positive_factors,
        'total_factors': total_factors,
        'recommendation': get_compatibility_recommendation(compatibility_score, factors),
        'suggestions': get_improvement_suggestions(factors)
    }

def calculate_compatibility_score(listing_1, listing_2):
    """Calculer un score de compatibilité entre deux annonces"""
    score = 0.0
    
    # Catégorie (40% du score)
    if listing_1.category_id == listing_2.category_id:
        score += 0.4
    
    # Type d'échange (20% du score)
    if listing_1.exchange_type == listing_2.exchange_type:
        score += 0.2
    
    # Valeur (20% du score)
    value_diff = abs(listing_1.estimated_value - listing_2.estimated_value)
    max_value = max(listing_1.estimated_value, listing_2.estimated_value)
    if max_value > 0:
        value_similarity = 1 - (value_diff / max_value)
        score += 0.2 * value_similarity
    
    # Condition (10% du score)
    if listing_1.condition == listing_2.condition:
        score += 0.1
    
    # Proximité géographique (10% du score)
    distance = calculate_distance(
        listing_1.latitude, listing_1.longitude,
        listing_2.latitude, listing_2.longitude
    )
    if distance <= 10:  # Très proche
        score += 0.1
    elif distance <= 50:  # Proche
        score += 0.05
    
    return min(score, 1.0)

def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculer la distance entre deux points géographiques (formule de Haversine)"""
    if not all([lat1, lon1, lat2, lon2]):
        return float('inf')
    
    from math import radians, cos, sin, asin, sqrt
    
    # Convertir en radians
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    
    # Formule de Haversine
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    
    # Rayon de la Terre en km
    r = 6371
    
    return c * r

def get_match_reasons(listing_1, listing_2):
    """Obtenir les raisons du matching"""
    reasons = []
    
    if listing_1.category_id == listing_2.category_id:
        reasons.append("Même catégorie")
    
    if listing_1.exchange_type == listing_2.exchange_type:
        reasons.append("Type d'échange compatible")
    
    value_diff = abs(listing_1.estimated_value - listing_2.estimated_value)
    max_value = max(listing_1.estimated_value, listing_2.estimated_value)
    if max_value > 0 and (value_diff / max_value) < 0.2:
        reasons.append("Valeurs similaires")
    
    if listing_1.condition == listing_2.condition:
        reasons.append("Même condition")
    
    distance = calculate_distance(
        listing_1.latitude, listing_1.longitude,
        listing_2.latitude, listing_2.longitude
    )
    if distance <= 20:
        reasons.append("Proximité géographique")
    
    return reasons

def calculate_chain_feasibility(chain):
    """Calculer la faisabilité d'une chaîne d'échange"""
    if len(chain) < 2:
        return 0.0
    
    # Facteurs de faisabilité
    total_distance = 0
    compatibility_scores = []
    
    for i in range(len(chain) - 1):
        distance = calculate_distance(
            chain[i].latitude, chain[i].longitude,
            chain[i+1].latitude, chain[i+1].longitude
        )
        total_distance += distance
        
        compatibility = calculate_compatibility_score(chain[i], chain[i+1])
        compatibility_scores.append(compatibility)
    
    # Score basé sur la distance et la compatibilité
    avg_compatibility = sum(compatibility_scores) / len(compatibility_scores)
    distance_factor = max(0, 1 - (total_distance / 200))  # Pénalité pour les longues distances
    
    return (avg_compatibility * 0.7 + distance_factor * 0.3)

def get_compatibility_recommendation(score, factors):
    """Obtenir une recommandation basée sur le score de compatibilité"""
    if score >= 0.8:
        return "Excellent match ! Échange fortement recommandé."
    elif score >= 0.6:
        return "Bon match. Échange recommandé avec quelques ajustements."
    elif score >= 0.4:
        return "Match acceptable. Considérez les suggestions d'amélioration."
    else:
        return "Match faible. Échange non recommandé."

def get_improvement_suggestions(factors):
    """Obtenir des suggestions d'amélioration"""
    suggestions = []
    
    if not factors['category_match']:
        suggestions.append("Recherchez des annonces dans la même catégorie")
    
    if not factors['exchange_type_match']:
        suggestions.append("Vérifiez que les types d'échange sont compatibles")
    
    if not factors['value_compatibility']:
        suggestions.append("Considérez ajuster la valeur proposée")
    
    if not factors['geographical_proximity']:
        suggestions.append("Recherchez des annonces plus proches géographiquement")
    
    if not factors['user_trust_compatibility']:
        suggestions.append("Vérifiez les scores de confiance des utilisateurs")
    
    return suggestions
