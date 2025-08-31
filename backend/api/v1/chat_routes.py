"""
Chat routes for the Lucky Kangaroo API v1.
Handles real-time messaging between users.
"""

from datetime import datetime
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restx import Resource, fields, reqparse, Namespace
from flask_socketio import emit, join_room, leave_room

from ...models.chat import ChatRoom, ChatMessage, ChatParticipant, ChatRoomStatus
from ...models.user import User, UserStatus
from ...extensions import db, socketio
from ...utils.decorators import validate_json

# Create chat namespace
ns = Namespace('chat', description='Chat operations')

# Request parsers
chat_parser = reqparse.RequestParser()
chat_parser.add_argument('page', type=int, default=1, help='Page number')
chat_parser.add_argument('per_page', type=int, default=50, help='Messages per page')

# Socket.io events
MESSAGE_EVENT = 'new_message'
TYPING_EVENT = 'user_typing'
READ_EVENT = 'message_read'
ONLINE_EVENT = 'user_online'
OFFLINE_EVENT = 'user_offline'

# Response models
message_model = ns.model('ChatMessage', {
    'id': fields.Integer(description='Message ID'),
    'room_id': fields.Integer(description='Chat room ID'),
    'sender_id': fields.Integer(description='Sender user ID'),
    'content': fields.String(description='Message content'),
    'created_at': fields.DateTime(description='Creation timestamp'),
    'read_at': fields.DateTime(description='When the message was read')
})

room_model = ns.model('ChatRoom', {
    'id': fields.Integer(description='Room ID'),
    'created_at': fields.DateTime(description='Creation timestamp'),
    'updated_at': fields.DateTime(description='Last message timestamp'),
    'unread_count': fields.Integer(description='Number of unread messages'),
    'other_user': fields.Nested(ns.model('ChatUser', {
        'id': fields.Integer,
        'username': fields.String,
        'avatar_url': fields.String,
        'is_online': fields.Boolean
    }), description='The other user in the conversation')
})

# Socket.io event handlers
@socketio.on('connect')
def handle_connect():
    """Handle socket connection."""
    # User must be authenticated via JWT
    user_id = get_jwt_identity()
    if not user_id:
        return False
    
    # Mark user as online
    user = User.query.get(user_id)
    if user:
        user.is_online = True
        user.last_seen = datetime.utcnow()
        db.session.commit()
        
        # Notify user's contacts that they're online
        emit(ONLINE_EVENT, {'user_id': user_id}, broadcast=True, include_self=False)
    
    return True

@socketio.on('disconnect')
def handle_disconnect():
    """Handle socket disconnection."""
    user_id = get_jwt_identity()
    if not user_id:
        return
    
    # Mark user as offline
    user = User.query.get(user_id)
    if user:
        user.is_online = False
        user.last_seen = datetime.utcnow()
        db.session.commit()
        
        # Notify user's contacts that they're offline
        emit(OFFLINE_EVENT, {'user_id': user_id}, broadcast=True, include_self=False)

@socketio.on('join')
def on_join(data):
    """Join a chat room."""
    room_id = data.get('room_id')
    user_id = get_jwt_identity()
    
    if not room_id or not user_id:
        return False
    
    # Verify user has access to this room
    participant = ChatParticipant.query.filter_by(
        room_id=room_id,
        user_id=user_id,
        status=ChatRoomStatus.ACTIVE
    ).first()
    
    if participant:
        join_room(str(room_id))
        return True
    
    return False

@socketio.on('leave')
def on_leave(data):
    """Leave a chat room."""
    room_id = data.get('room_id')
    if room_id:
        leave_room(str(room_id))

@socketio.on('typing')
def on_typing(data):
    """Handle typing indicator."""
    room_id = data.get('room_id')
    user_id = get_jwt_identity()
    
    if room_id and user_id:
        emit(TYPING_EVENT, 
             {'user_id': user_id, 'room_id': room_id}, 
             room=str(room_id), 
             include_self=False)

@ns.route('/rooms')
class ChatRoomList(Resource):
    ""Chat room collection endpoint."""
    
    @jwt_required()
    @ns.marshal_list_with(room_model)
    def get(self):
        ""Get all chat rooms for the current user."""
        user_id = get_jwt_identity()
        
        # Get all rooms where the user is an active participant
        participants = ChatParticipant.query.filter_by(
            user_id=user_id,
            status=ChatRoomStatus.ACTIVE
        ).all()
        
        rooms = []
        for p in participants:
            # Get the other participant in the room (for 1-on-1 chats)
            other_participant = ChatParticipant.query.filter(
                ChatParticipant.room_id == p.room_id,
                ChatParticipant.user_id != user_id,
                ChatParticipant.status == ChatRoomStatus.ACTIVE
            ).first()
            
            if not other_participant:
                continue
                
            other_user = User.query.get(other_participant.user_id)
            
            # Get unread message count
            unread_count = ChatMessage.query.filter(
                ChatMessage.room_id == p.room_id,
                ChatMessage.sender_id != user_id,
                ChatMessage.read_at.is_(None)
            ).count()
            
            rooms.append({
                'id': p.room_id,
                'created_at': p.room.created_at,
                'updated_at': p.room.updated_at,
                'unread_count': unread_count,
                'other_user': {
                    'id': other_user.id,
                    'username': other_user.username,
                    'avatar_url': other_user.avatar_url,
                    'is_online': other_user.is_online
                }
            })
        
        # Sort by most recent message
        rooms.sort(key=lambda x: x['updated_at'] or x['created_at'], reverse=True)
        return rooms, 200
    
    @jwt_required()
    @ns.expect(ns.model('NewChatRoom', {
        'user_id': fields.Integer(required=True, description='ID of the user to start a chat with')
    }))
    @ns.marshal_with(room_model)
    def post(self):
        ""Create a new chat room or return existing one."""
        current_user_id = get_jwt_identity()
        target_user_id = request.json.get('user_id')
        
        if not target_user_id:
            return {'message': 'User ID is required'}, 400
        
        if current_user_id == target_user_id:
            return {'message': 'Cannot start a chat with yourself'}, 400
        
        # Check if target user exists and is active
        target_user = User.query.filter_by(
            id=target_user_id,
            status=UserStatus.ACTIVE
        ).first_or_404('User not found or inactive')
        
        # Check if a room already exists between these users
        existing_room = db.session.query(ChatRoom).join(
            ChatParticipant,
            ChatParticipant.room_id == ChatRoom.id
        ).filter(
            ChatParticipant.user_id == current_user_id,
            ChatParticipant.status == ChatRoomStatus.ACTIVE,
            ChatRoom.id.in_(
                db.session.query(ChatParticipant.room_id).filter(
                    ChatParticipant.user_id == target_user_id,
                    ChatParticipant.status == ChatRoomStatus.ACTIVE
                )
            )
        ).first()
        
        if existing_room:
            # Return existing room
            return {
                'id': existing_room.id,
                'created_at': existing_room.created_at,
                'updated_at': existing_room.updated_at,
                'unread_count': 0,
                'other_user': {
                    'id': target_user.id,
                    'username': target_user.username,
                    'avatar_url': target_user.avatar_url,
                    'is_online': target_user.is_online
                }
            }, 200
        
        # Create new room
        room = ChatRoom()
        db.session.add(room)
        db.session.flush()  # Get room ID
        
        # Add participants
        participants = [
            ChatParticipant(
                room_id=room.id,
                user_id=current_user_id,
                status=ChatRoomStatus.ACTIVE
            ),
            ChatParticipant(
                room_id=room.id,
                user_id=target_user_id,
                status=ChatRoomStatus.ACTIVE
            )
        ]
        
        db.session.add_all(participants)
        db.session.commit()
        
        return {
            'id': room.id,
            'created_at': room.created_at,
            'updated_at': room.updated_at,
            'unread_count': 0,
            'other_user': {
                'id': target_user.id,
                'username': target_user.username,
                'avatar_url': target_user.avatar_url,
                'is_online': target_user.is_online
            }
        }, 201

@ns.route('/rooms/<int:room_id>/messages')
class MessageList(Resource):
    ""Message collection endpoint for a specific chat room."""
    
    @jwt_required()
    @ns.expect(chat_parser)
    @ns.marshal_list_with(message_model)
    def get(self, room_id):
        ""Get messages for a specific chat room."""
        user_id = get_jwt_identity()
        
        # Verify user has access to this room
        participant = ChatParticipant.query.filter_by(
            room_id=room_id,
            user_id=user_id,
            status=ChatRoomStatus.ACTIVE
        ).first_or_404('Room not found or access denied')
        
        # Get pagination parameters
        args = chat_parser.parse_args()
        page = args['page']
        per_page = args['per_page']
        
        # Get messages
        messages = ChatMessage.query.filter_by(room_id=room_id)\
            .order_by(ChatMessage.created_at.desc())\
            .paginate(page=page, per_page=per_page, error_out=False)
        
        # Mark messages as read
        unread_messages = ChatMessage.query.filter(
            ChatMessage.room_id == room_id,
            ChatMessage.sender_id != user_id,
            ChatMessage.read_at.is_(None)
        ).all()
        
        if unread_messages:
            for msg in unread_messages:
                msg.read_at = datetime.utcnow()
            db.session.commit()
            
            # Notify sender that messages were read
            emit(READ_EVENT, {
                'room_id': room_id,
                'user_id': user_id,
                'message_ids': [msg.id for msg in unread_messages]
            }, room=str(room_id), include_self=False)
        
        return messages.items, 200
    
    @jwt_required()
    @ns.expect(ns.model('NewMessage', {
        'content': fields.String(required=True, description='Message content')
    }))
    @ns.marshal_with(message_model, code=201)
    def post(self, room_id):
        ""Send a new message to a chat room."""
        user_id = get_jwt_identity()
        content = request.json.get('content', '').strip()
        
        if not content:
            return {'message': 'Message content is required'}, 400
        
        # Verify user has access to this room
        participant = ChatParticipant.query.filter_by(
            room_id=room_id,
            user_id=user_id,
            status=ChatRoomStatus.ACTIVE
        ).first_or_404('Room not found or access denied')
        
        # Create message
        message = ChatMessage(
            room_id=room_id,
            sender_id=user_id,
            content=content
        )
        
        db.session.add(message)
        
        # Update room's updated_at timestamp
        room = ChatRoom.query.get(room_id)
        room.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        # Emit socket event
        message_data = {
            'id': message.id,
            'room_id': message.room_id,
            'sender_id': message.sender_id,
            'content': message.content,
            'created_at': message.created_at.isoformat(),
            'read_at': message.read_at.isoformat() if message.read_at else None
        }
        
        emit(MESSAGE_EVENT, message_data, room=str(room_id))
        
        return message, 201

@ns.route('/messages/<int:message_id>/read')
class MessageRead(Resource):
    ""Mark a message as read."""
    
    @jwt_required()
    def post(self, message_id):
        ""Mark a message as read."""
        user_id = get_jwt_identity()
        
        message = ChatMessage.query.get_or_404(message_id)
        
        # Verify user has access to this message's room
        participant = ChatParticipant.query.filter_by(
            room_id=message.room_id,
            user_id=user_id,
            status=ChatRoomStatus.ACTIVE
        ).first_or_404('Access denied')
        
        # Only mark as read if not already read and not sent by current user
        if not message.read_at and message.sender_id != user_id:
            message.read_at = datetime.utcnow()
            db.session.commit()
            
            # Notify sender that message was read
            emit(READ_EVENT, {
                'room_id': message.room_id,
                'user_id': user_id,
                'message_ids': [message.id]
            }, room=str(message.room_id), include_self=False)
        
        return {'message': 'Message marked as read'}, 200
