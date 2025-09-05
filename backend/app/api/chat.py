"""
API de chat temps réel avec WebSockets
"""
from flask import Blueprint, request, jsonify, current_app
from flask_socketio import emit, join_room, leave_room, disconnect
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.orm import joinedload
from datetime import datetime
import uuid

from app import db, socketio
from app.models.user import User
from app.models.listing import Listing
from app.models.chat import Chat, ChatParticipant, ChatMessage
from app.models.exchange import Exchange

# Créer le blueprint
chat_bp = Blueprint('chat', __name__)

# ============================================================================
# ROUTES API REST
# ============================================================================

@chat_bp.route('/chats', methods=['GET'])
@jwt_required()
def get_user_chats():
    """Récupérer les chats de l'utilisateur connecté"""
    try:
        user_id = get_jwt_identity()
        
        # Récupérer les chats de l'utilisateur avec les participants
        chats = db.session.query(Chat).join(ChatParticipant).filter(
            ChatParticipant.user_id == user_id,
            ChatParticipant.is_active == True
        ).options(
            joinedload(Chat.participants),
            joinedload(Chat.listing),
            joinedload(Chat.exchange)
        ).order_by(Chat.last_message_at.desc()).all()
        
        # Formater les données
        chats_data = []
        for chat in chats:
            # Récupérer le dernier message
            last_message = db.session.query(ChatMessage).filter(
                ChatMessage.chat_id == chat.id
            ).order_by(ChatMessage.created_at.desc()).first()
            
            # Compter les messages non lus
            unread_count = db.session.query(ChatMessage).join(ChatParticipant).filter(
                ChatMessage.chat_id == chat.id,
                ChatParticipant.user_id == user_id,
                ChatMessage.created_at > ChatParticipant.last_read_at
            ).count()
            
            chat_data = {
                'id': chat.id,
                'type': chat.chat_type,
                'name': chat.name,
                'description': chat.description,
                'avatar_url': chat.avatar_url,
                'status': chat.status,
                'participants_count': len(chat.participants),
                'last_message': {
                    'id': last_message.id if last_message else None,
                    'message': last_message.message if last_message else None,
                    'message_type': last_message.message_type if last_message else None,
                    'created_at': last_message.created_at.isoformat() if last_message else None,
                    'user': {
                        'id': last_message.user.id,
                        'username': last_message.user.username,
                        'first_name': last_message.user.first_name
                    } if last_message else None
                },
                'unread_count': unread_count,
                'created_at': chat.created_at.isoformat(),
                'updated_at': chat.updated_at.isoformat()
            }
            
            # Ajouter les informations spécifiques selon le type de chat
            if chat.listing:
                chat_data['listing'] = {
                    'id': chat.listing.id,
                    'title': chat.listing.title,
                    'images': [img.file_path for img in chat.listing.images[:1]]
                }
            
            if chat.exchange:
                chat_data['exchange'] = {
                    'id': chat.exchange.id,
                    'title': chat.exchange.title,
                    'status': chat.exchange.status
                }
            
            chats_data.append(chat_data)
        
        return jsonify({
            'success': True,
            'chats': chats_data,
            'total': len(chats_data)
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erreur lors de la récupération des chats: {e}")
        return jsonify({
            'success': False,
            'error': 'Erreur lors de la récupération des chats'
        }), 500

@chat_bp.route('/chats/<chat_id>', methods=['GET'])
@jwt_required()
def get_chat_details(chat_id):
    """Récupérer les détails d'un chat spécifique"""
    try:
        user_id = get_jwt_identity()
        
        # Vérifier que l'utilisateur participe au chat
        participant = db.session.query(ChatParticipant).filter(
            ChatParticipant.chat_id == chat_id,
            ChatParticipant.user_id == user_id,
            ChatParticipant.is_active == True
        ).first()
        
        if not participant:
            return jsonify({
                'success': False,
                'error': 'Chat non trouvé ou accès non autorisé'
            }), 404
        
        # Récupérer le chat avec tous les détails
        chat = db.session.query(Chat).filter(Chat.id == chat_id).options(
            joinedload(Chat.participants).joinedload(ChatParticipant.user),
            joinedload(Chat.listing),
            joinedload(Chat.exchange)
        ).first()
        
        if not chat:
            return jsonify({
                'success': False,
                'error': 'Chat non trouvé'
            }), 404
        
        # Formater les participants
        participants_data = []
        for participant in chat.participants:
            if participant.is_active:
                participants_data.append({
                    'id': participant.user.id,
                    'username': participant.user.username,
                    'first_name': participant.user.first_name,
                    'last_name': participant.user.last_name,
                    'profile_picture': participant.user.profile_picture,
                    'role': participant.role,
                    'is_admin': participant.is_admin,
                    'joined_at': participant.joined_at.isoformat(),
                    'last_activity_at': participant.last_activity_at.isoformat()
                })
        
        chat_data = {
            'id': chat.id,
            'type': chat.chat_type,
            'name': chat.name,
            'description': chat.description,
            'avatar_url': chat.avatar_url,
            'status': chat.status,
            'participants': participants_data,
            'created_at': chat.created_at.isoformat(),
            'updated_at': chat.updated_at.isoformat()
        }
        
        # Ajouter les informations spécifiques
        if chat.listing:
            chat_data['listing'] = {
                'id': chat.listing.id,
                'title': chat.listing.title,
                'description': chat.listing.description,
                'images': [img.file_path for img in chat.listing.images[:3]]
            }
        
        if chat.exchange:
            chat_data['exchange'] = {
                'id': chat.exchange.id,
                'title': chat.exchange.title,
                'status': chat.exchange.status,
                'proposed_value': chat.exchange.proposed_value
            }
        
        return jsonify({
            'success': True,
            'chat': chat_data
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erreur lors de la récupération du chat: {e}")
        return jsonify({
            'success': False,
            'error': 'Erreur lors de la récupération du chat'
        }), 500

@chat_bp.route('/chats/<chat_id>/messages', methods=['GET'])
@jwt_required()
def get_chat_messages(chat_id):
    """Récupérer les messages d'un chat"""
    try:
        user_id = get_jwt_identity()
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        
        # Vérifier que l'utilisateur participe au chat
        participant = db.session.query(ChatParticipant).filter(
            ChatParticipant.chat_id == chat_id,
            ChatParticipant.user_id == user_id,
            ChatParticipant.is_active == True
        ).first()
        
        if not participant:
            return jsonify({
                'success': False,
                'error': 'Chat non trouvé ou accès non autorisé'
            }), 404
        
        # Récupérer les messages avec pagination
        messages = db.session.query(ChatMessage).filter(
            ChatMessage.chat_id == chat_id,
            ChatMessage.is_deleted == False
        ).options(
            joinedload(ChatMessage.user)
        ).order_by(ChatMessage.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # Formater les messages
        messages_data = []
        for message in messages.items:
            message_data = {
                'id': message.id,
                'message': message.message,
                'message_type': message.message_type,
                'attachment_url': message.attachment_url,
                'attachment_filename': message.attachment_filename,
                'location': {
                    'latitude': message.location_latitude,
                    'longitude': message.location_longitude,
                    'name': message.location_name
                } if message.location_latitude else None,
                'reply_to': message.reply_to_id,
                'is_edited': message.is_edited,
                'edited_at': message.edited_at.isoformat() if message.edited_at else None,
                'user': {
                    'id': message.user.id,
                    'username': message.user.username,
                    'first_name': message.user.first_name,
                    'last_name': message.user.last_name,
                    'profile_picture': message.user.profile_picture
                },
                'created_at': message.created_at.isoformat()
            }
            messages_data.append(message_data)
        
        return jsonify({
            'success': True,
            'messages': messages_data,
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
        current_app.logger.error(f"Erreur lors de la récupération des messages: {e}")
        return jsonify({
            'success': False,
            'error': 'Erreur lors de la récupération des messages'
        }), 500

@chat_bp.route('/chats/<chat_id>/messages', methods=['POST'])
@jwt_required()
def send_message(chat_id):
    """Envoyer un message dans un chat"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Vérifier que l'utilisateur participe au chat
        participant = db.session.query(ChatParticipant).filter(
            ChatParticipant.chat_id == chat_id,
            ChatParticipant.user_id == user_id,
            ChatParticipant.is_active == True
        ).first()
        
        if not participant:
            return jsonify({
                'success': False,
                'error': 'Chat non trouvé ou accès non autorisé'
            }), 404
        
        # Créer le message
        message = ChatMessage(
            id=str(uuid.uuid4()),
            chat_id=chat_id,
            user_id=user_id,
            message=data.get('message', '').strip(),
            message_type=data.get('message_type', 'text'),
            attachment_url=data.get('attachment_url'),
            attachment_filename=data.get('attachment_filename'),
            location_latitude=data.get('location', {}).get('latitude'),
            location_longitude=data.get('location', {}).get('longitude'),
            location_name=data.get('location', {}).get('name'),
            reply_to_id=data.get('reply_to_id'),
            is_edited=False,
            is_deleted=False,
            chat_metadata={}
        )
        
        db.session.add(message)
        
        # Mettre à jour le timestamp du dernier message du chat
        chat = db.session.query(Chat).filter(Chat.id == chat_id).first()
        if chat:
            chat.last_message_at = datetime.utcnow()
            chat.updated_at = datetime.utcnow()
        
        # Mettre à jour l'activité du participant
        participant.last_activity_at = datetime.utcnow()
        
        db.session.commit()
        
        # Émettre le message via WebSocket
        socketio.emit('new_message', {
            'id': message.id,
            'chat_id': chat_id,
            'message': message.message,
            'message_type': message.message_type,
            'attachment_url': message.attachment_url,
            'attachment_filename': message.attachment_filename,
            'location': {
                'latitude': message.location_latitude,
                'longitude': message.location_longitude,
                'name': message.location_name
            } if message.location_latitude else None,
            'reply_to': message.reply_to_id,
            'user': {
                'id': message.user.id,
                'username': message.user.username,
                'first_name': message.user.first_name,
                'last_name': message.user.last_name,
                'profile_picture': message.user.profile_picture
            },
            'created_at': message.created_at.isoformat()
        }, room=chat_id)
        
        return jsonify({
            'success': True,
            'message': {
                'id': message.id,
                'message': message.message,
                'message_type': message.message_type,
                'created_at': message.created_at.isoformat()
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Erreur lors de l'envoi du message: {e}")
        return jsonify({
            'success': False,
            'error': 'Erreur lors de l\'envoi du message'
        }), 500

@chat_bp.route('/chats/<chat_id>/read', methods=['POST'])
@jwt_required()
def mark_chat_as_read(chat_id):
    """Marquer un chat comme lu"""
    try:
        user_id = get_jwt_identity()
        
        # Mettre à jour le timestamp de lecture
        participant = db.session.query(ChatParticipant).filter(
            ChatParticipant.chat_id == chat_id,
            ChatParticipant.user_id == user_id
        ).first()
        
        if participant:
            participant.last_read_at = datetime.utcnow()
            participant.last_activity_at = datetime.utcnow()
            db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Chat marqué comme lu'
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erreur lors du marquage du chat comme lu: {e}")
        return jsonify({
            'success': False,
            'error': 'Erreur lors du marquage du chat comme lu'
        }), 500

# ============================================================================
# ÉVÉNEMENTS WEBSOCKET
# ============================================================================

@socketio.on('connect')
@jwt_required()
def handle_connect():
    """Gérer la connexion WebSocket"""
    user_id = get_jwt_identity()
    current_app.logger.info(f"Utilisateur {user_id} connecté via WebSocket")
    
    # Récupérer les chats de l'utilisateur
    chats = db.session.query(Chat).join(ChatParticipant).filter(
        ChatParticipant.user_id == user_id,
        ChatParticipant.is_active == True
    ).all()
    
    # Rejoindre les rooms des chats
    for chat in chats:
        join_room(chat.id)
    
    emit('connected', {
        'user_id': user_id,
        'chats_count': len(chats)
    })

@socketio.on('disconnect')
@jwt_required()
def handle_disconnect():
    """Gérer la déconnexion WebSocket"""
    user_id = get_jwt_identity()
    current_app.logger.info(f"Utilisateur {user_id} déconnecté via WebSocket")

@socketio.on('join_chat')
@jwt_required()
def handle_join_chat(data):
    """Rejoindre un chat spécifique"""
    user_id = get_jwt_identity()
    chat_id = data.get('chat_id')
    
    # Vérifier que l'utilisateur participe au chat
    participant = db.session.query(ChatParticipant).filter(
        ChatParticipant.chat_id == chat_id,
        ChatParticipant.user_id == user_id,
        ChatParticipant.is_active == True
    ).first()
    
    if participant:
        join_room(chat_id)
        emit('joined_chat', {'chat_id': chat_id})
        
        # Notifier les autres participants
        emit('user_joined', {
            'user_id': user_id,
            'chat_id': chat_id
        }, room=chat_id, include_self=False)

@socketio.on('leave_chat')
@jwt_required()
def handle_leave_chat(data):
    """Quitter un chat spécifique"""
    user_id = get_jwt_identity()
    chat_id = data.get('chat_id')
    
    leave_room(chat_id)
    emit('left_chat', {'chat_id': chat_id})
    
    # Notifier les autres participants
    emit('user_left', {
        'user_id': user_id,
        'chat_id': chat_id
    }, room=chat_id, include_self=False)

@socketio.on('typing_start')
@jwt_required()
def handle_typing_start(data):
    """Indiquer que l'utilisateur commence à taper"""
    user_id = get_jwt_identity()
    chat_id = data.get('chat_id')
    
    # Vérifier que l'utilisateur participe au chat
    participant = db.session.query(ChatParticipant).filter(
        ChatParticipant.chat_id == chat_id,
        ChatParticipant.user_id == user_id,
        ChatParticipant.is_active == True
    ).first()
    
    if participant:
        emit('user_typing', {
            'user_id': user_id,
            'chat_id': chat_id,
            'is_typing': True
        }, room=chat_id, include_self=False)

@socketio.on('typing_stop')
@jwt_required()
def handle_typing_stop(data):
    """Indiquer que l'utilisateur arrête de taper"""
    user_id = get_jwt_identity()
    chat_id = data.get('chat_id')
    
    emit('user_typing', {
        'user_id': user_id,
        'chat_id': chat_id,
        'is_typing': False
    }, room=chat_id, include_self=False)

@socketio.on('message_read')
@jwt_required()
def handle_message_read(data):
    """Marquer un message comme lu"""
    user_id = get_jwt_identity()
    message_id = data.get('message_id')
    chat_id = data.get('chat_id')
    
    # Mettre à jour le timestamp de lecture
    participant = db.session.query(ChatParticipant).filter(
        ChatParticipant.chat_id == chat_id,
        ChatParticipant.user_id == user_id
    ).first()
    
    if participant:
        participant.last_read_at = datetime.utcnow()
        db.session.commit()
        
        emit('message_read', {
            'message_id': message_id,
            'user_id': user_id,
            'chat_id': chat_id
        }, room=chat_id, include_self=False)