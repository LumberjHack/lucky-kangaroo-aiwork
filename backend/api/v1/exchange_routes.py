"""
Exchange routes for the Lucky Kangaroo API v1.
Handles exchange requests, offers, and management.
"""

from flask import request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restx import Resource, reqparse
from sqlalchemy import or_
from datetime import datetime

from ...models.exchange import Exchange, ExchangeStatus
from ...models.listing import Listing, ListingStatus
from ...models.notification import Notification, NotificationType
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

# We return plain dicts using model to_dict() methods to avoid schema drift.

@ns.route('/exchanges')
class ExchangeList(Resource):
    """Exchange collection endpoint."""
    
    @jwt_required()
    def get(self):
        """Get all exchanges involving the current user."""
        user_id = get_jwt_identity()
        exchanges = Exchange.query.filter(
            or_(
                Exchange.requester_id == user_id,
                Exchange.owner_id == user_id
            )
        ).order_by(Exchange.updated_at.desc()).all()
        return [e.to_dict() for e in exchanges], 200
    
    @jwt_required()
    @ns.expect(create_exchange_parser)
    def post(self):
        """Create a new exchange request."""
        user_id = get_jwt_identity()
        args = create_exchange_parser.parse_args()

        listing = Listing.query.get_or_404(args['listing_id'])

        if listing.status != ListingStatus.ACTIVE:
            return {'message': 'Listing not available'}, 400

        if listing.user_id == user_id:
            return {'message': 'Cannot request your own listing'}, 400

        offered_listing_id = args.get('offered_listing_id')
        if not offered_listing_id:
            return {'message': 'offered_listing_id is required'}, 400

        existing = Exchange.query.filter(
            Exchange.requested_listing_id == listing.id,
            Exchange.status.in_([
                ExchangeStatus.REQUESTED,
                ExchangeStatus.ACCEPTED,
                ExchangeStatus.CONFIRMED,
                ExchangeStatus.IN_PROGRESS,
            ])
        ).first()

        if existing:
            return {'message': 'Active exchange exists'}, 400

        exchange = Exchange(
            requester_id=user_id,
            owner_id=listing.user_id,
            offered_listing_id=offered_listing_id,
            requested_listing_id=listing.id,
            message=args.get('message'),
            status=ExchangeStatus.REQUESTED,
        )

        db.session.add(exchange)

        notif = Notification.create_exchange_notification(
            user_id=listing.user_id,
            exchange=exchange,
            notification_type=NotificationType.EXCHANGE_REQUEST,
            additional_data={'requester_id': user_id},
        )
        db.session.add(notif)

        db.session.commit()

        socketio.emit(
            'exchange_created',
            {
                'exchange_id': exchange.id,
                'owner_id': listing.user_id,
                'requester_id': user_id,
            },
            room=f'user_{listing.user_id}',
        )

        return exchange.to_dict(), 201

@ns.route('/exchanges/<int:exchange_id>')
class ExchangeResource(Resource):
    """Individual exchange endpoint."""
    
    @jwt_required()
    def get(self, exchange_id):
        """Get exchange details."""
        user_id = get_jwt_identity()
        exchange = Exchange.query.get_or_404(exchange_id)

        if exchange.requester_id != user_id and exchange.owner_id != user_id:
            return {'message': 'Unauthorized'}, 403

        return exchange.to_dict(), 200
    
    @jwt_required()
    @ns.expect(update_exchange_parser)
    def put(self, exchange_id):
        """Update an exchange."""
        user_id = get_jwt_identity()
        exchange = Exchange.query.get_or_404(exchange_id)

        if exchange.owner_id != user_id:
            return {'message': 'Unauthorized'}, 403

        args = update_exchange_parser.parse_args()

        if args.get('status'):
            new_status = args['status']
            if new_status == 'accepted':
                exchange.accept()
                self._handle_accept(exchange)
            elif new_status == 'rejected':
                exchange.cancel()
                self._handle_reject(exchange)
            exchange.updated_at = datetime.utcnow()
            db.session.commit()

        return exchange.to_dict(), 200
    
    def _handle_accept(self, exchange):
        """Handle exchange acceptance."""
        notif = Notification.create_exchange_notification(
            user_id=exchange.requester_id,
            exchange=exchange,
            notification_type=NotificationType.EXCHANGE_ACCEPTED,
        )
        db.session.add(notif)

        socketio.emit(
            'exchange_updated',
            {
                'exchange_id': exchange.id,
                'status': 'accepted',
                'requester_id': exchange.requester_id,
            },
            room=f'user_{exchange.requester_id}',
        )
    
    def _handle_reject(self, exchange):
        """Handle exchange rejection."""
        notif = Notification.create_exchange_notification(
            user_id=exchange.requester_id,
            exchange=exchange,
            notification_type=NotificationType.EXCHANGE_CANCELLED,
        )
        db.session.add(notif)

        socketio.emit(
            'exchange_updated',
            {
                'exchange_id': exchange.id,
                'status': 'rejected',
                'requester_id': exchange.requester_id,
            },
            room=f'user_{exchange.requester_id}',
        )
