"""
Exchange routes for the Lucky Kangaroo API v1.
Handles exchange requests, offers, and management.
"""

from flask import request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from flask_restx import Resource, fields, reqparse, marshal
from sqlalchemy import or_
from datetime import datetime

from ...models.exchange import Exchange, ExchangeMessage
from ...models.listing import Listing
from ...models.user import Notification, NotificationType
from ...extensions import db, socketio
from . import ns

# Request parsers
create_exchange_parser = reqparse.RequestParser()
create_exchange_parser.add_argument('listing_id', type=int, required=True)
create_exchange_parser.add_argument('offered_listing_id', type=int, required=False)
create_exchange_parser.add_argument('message', type=str, required=False)

update_exchange_parser = reqparse.RequestParser()
update_exchange_parser.add_argument('status', type=str, required=False, 
                                   choices=('pending', 'accepted', 'rejected', 'cancelled'))

# Response models
exchange_model = ns.model('Exchange', {
    'id': fields.Integer,
    'status': fields.String,
    'created_at': fields.DateTime,
    'listing': fields.Nested(ns.model('ExchangeListing', {
        'id': fields.Integer,
        'title': fields.String,
        'primary_image': fields.String
    })),
    'buyer': fields.Nested(ns.model('ExchangeUser', {
        'id': fields.Integer,
        'username': fields.String
    })),
    'seller': fields.Nested(ns.model('ExchangeUser', {
        'id': fields.Integer,
        'username': fields.String
    }))
})

@ns.route('/exchanges')
class ExchangeList(Resource):
    ""Exchange collection endpoint."""
    
    @jwt_required()
    @ns.marshal_list_with(exchange_model)
    def get(self):
        ""Get all exchanges involving the current user."""
        user_id = get_jwt_identity()
        exchanges = Exchange.query.filter(
            or_(
                Exchange.buyer_id == user_id,
                Exchange.seller_id == user_id
            )
        ).order_by(Exchange.updated_at.desc()).all()
        return exchanges, 200
    
    @jwt_required()
    @ns.expect(create_exchange_parser)
    @ns.marshal_with(exchange_model, code=201)
    def post(self):
        ""Create a new exchange request."""
        user_id = get_jwt_identity()
        args = create_exchange_parser.parse_args()
        
        listing = Listing.query.get_or_404(args['listing_id'])
        
        if listing.status != 'active':
            return {'message': 'Listing not available'}, 400
            
        if listing.user_id == user_id:
            return {'message': 'Cannot request your own listing'}, 400
            
        existing = Exchange.query.filter(
            Exchange.listing_id == listing.id,
            Exchange.status.in_(['pending', 'accepted'])
        ).first()
        
        if existing:
            return {'message': 'Active exchange exists'}, 400
        
        exchange = Exchange(
            listing_id=listing.id,
            offered_listing_id=args.get('offered_listing_id'),
            buyer_id=user_id,
            seller_id=listing.user_id,
            status='pending'
        )
        
        db.session.add(exchange)
        
        if args.get('message'):
            message = ExchangeMessage(
                exchange_id=exchange.id,
                sender_id=user_id,
                content=args['message']
            )
            db.session.add(message)
        
        listing.status = 'pending'
        
        notification = Notification(
            user_id=listing.user_id,
            type=NotificationType.EXCHANGE_REQUEST,
            title='New Exchange Request',
            message=f'New exchange request for "{listing.title}"',
            data={'exchange_id': exchange.id}
        )
        db.session.add(notification)
        
        db.session.commit()
        
        socketio.emit('exchange_created', {
            'exchange_id': exchange.id,
            'seller_id': listing.user_id,
            'buyer_id': user_id
        }, room=f'user_{listing.user_id}')
        
        return exchange, 201

@ns.route('/exchanges/<int:exchange_id>')
class ExchangeResource(Resource):
    ""Individual exchange endpoint."""
    
    @jwt_required()
    @ns.marshal_with(exchange_model)
    def get(self, exchange_id):
        ""Get exchange details."""
        user_id = get_jwt_identity()
        exchange = Exchange.query.get_or_404(exchange_id)
        
        if exchange.buyer_id != user_id and exchange.seller_id != user_id:
            return {'message': 'Unauthorized'}, 403
            
        return exchange, 200
    
    @jwt_required()
    @ns.expect(update_exchange_parser)
    @ns.marshal_with(exchange_model)
    def put(self, exchange_id):
        ""Update an exchange."""
        user_id = get_jwt_identity()
        exchange = Exchange.query.get_or_404(exchange_id)
        
        if exchange.seller_id != user_id:
            return {'message': 'Unauthorized'}, 403
            
        args = update_exchange_parser.parse_args()
        
        if args.get('status'):
            exchange.status = args['status']
            exchange.updated_at = datetime.utcnow()
            
            if args['status'] == 'accepted':
                self._handle_accept(exchange)
            elif args['status'] == 'rejected':
                self._handle_reject(exchange)
            
            db.session.commit()
        
        return exchange, 200
    
    def _handle_accept(self, exchange):
        ""Handle exchange acceptance."""
        exchange.listing.status = 'pending'
        
        notification = Notification(
            user_id=exchange.buyer_id,
            type=NotificationType.EXCHANGE_ACCEPTED,
            title='Exchange Accepted',
            message=f'Your exchange for "{exchange.listing.title}" was accepted',
            data={'exchange_id': exchange.id}
        )
        db.session.add(notification)
        
        socketio.emit('exchange_updated', {
            'exchange_id': exchange.id,
            'status': 'accepted',
            'buyer_id': exchange.buyer_id
        }, room=f'user_{exchange.buyer_id}')
    
    def _handle_reject(self, exchange):
        ""Handle exchange rejection."""
        exchange.listing.status = 'active'
        
        notification = Notification(
            user_id=exchange.buyer_id,
            type=NotificationType.EXCHANGE_REJECTED,
            title='Exchange Declined',
            message=f'Your exchange for "{exchange.listing.title}" was declined',
            data={'exchange_id': exchange.id}
        )
        db.session.add(notification)
        
        socketio.emit('exchange_updated', {
            'exchange_id': exchange.id,
            'status': 'rejected',
            'buyer_id': exchange.buyer_id
        }, room=f'user_{exchange.buyer_id}')
