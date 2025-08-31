"""
Notification routes for the Lucky Kangaroo API v1.
Handles user notifications and preferences.
"""

from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restx import Resource, fields, reqparse
from sqlalchemy import desc

from ...models.user import Notification, NotificationType, UserPreferences
from ...extensions import db
from ...utils.decorators import validate_json
from . import ns

# Request parsers
mark_as_read_parser = reqparse.RequestParser()
mark_as_read_parser.add_argument('notification_ids', type=list, location='json', required=True,
                               help='List of notification IDs to mark as read')

update_preferences_parser = reqparse.RequestParser()
update_preferences_parser.add_argument('email_notifications', type=bool, required=False)
update_preferences_parser.add_argument('push_notifications', type=bool, required=False)
update_preferences_parser.add_argument('in_app_notifications', type=bool, required=False)
update_preferences_parser.add_argument('marketing_emails', type=bool, required=False)

# Response models
notification_model = ns.model('Notification', {
    'id': fields.Integer(description='Notification ID'),
    'user_id': fields.Integer(description='Recipient user ID'),
    'type': fields.String(description='Notification type', enum=[t.value for t in NotificationType]),
    'title': fields.String(description='Notification title'),
    'message': fields.String(description='Notification message'),
    'is_read': fields.Boolean(description='Whether the notification has been read'),
    'data': fields.Raw(description='Additional data related to the notification'),
    'created_at': fields.DateTime(description='Creation timestamp'),
    'read_at': fields.DateTime(description='When the notification was read')
})

preferences_model = ns.model('NotificationPreferences', {
    'email_notifications': fields.Boolean(description='Whether email notifications are enabled'),
    'push_notifications': fields.Boolean(description='Whether push notifications are enabled'),
    'in_app_notifications': fields.Boolean(description='Whether in-app notifications are enabled'),
    'marketing_emails': fields.Boolean(description='Whether marketing emails are enabled')
})

@ns.route('/notifications')
class NotificationList(Resource):
    ""Notification collection endpoint."""
    
    @jwt_required()
    @ns.marshal_list_with(notification_model)
    def get(self):
        ""Get all notifications for the current user."""
        user_id = get_jwt_identity()
        
        # Get query parameters
        limit = min(int(request.args.get('limit', 20)), 100)  # Max 100 notifications
        unread_only = request.args.get('unread_only', 'false').lower() == 'true'
        
        query = Notification.query.filter_by(user_id=user_id)
        
        if unread_only:
            query = query.filter_by(is_read=False)
            
        notifications = query.order_by(desc(Notification.created_at)).limit(limit).all()
        
        return notifications, 200
    
    @jwt_required()
    @ns.expect(mark_as_read_parser)
    def post(self):
        ""Mark notifications as read."""
        user_id = get_jwt_identity()
        args = mark_as_read_parser.parse_args()
        
        # Mark specified notifications as read
        updated = Notification.query.filter(
            Notification.id.in_(args['notification_ids']),
            Notification.user_id == user_id,
            Notification.is_read == False
        ).update({
            'is_read': True,
            'read_at': db.func.now()
        }, synchronize_session=False)
        
        db.session.commit()
        
        return {'message': f'Marked {updated} notifications as read'}, 200

@ns.route('/notifications/<int:notification_id>')
class NotificationResource(Resource):
    ""Individual notification endpoint."""
    
    @jwt_required()
    @ns.marshal_with(notification_model)
    def get(self, notification_id):
        ""Get a specific notification."""
        user_id = get_jwt_identity()
        notification = Notification.query.filter_by(
            id=notification_id,
            user_id=user_id
        ).first_or_404()
        
        # Mark as read if not already
        if not notification.is_read:
            notification.is_read = True
            notification.read_at = db.func.now()
            db.session.commit()
        
        return notification, 200
    
    @jwt_required()
    def delete(self, notification_id):
        ""Delete a notification."""
        user_id = get_jwt_identity()
        notification = Notification.query.filter_by(
            id=notification_id,
            user_id=user_id
        ).first_or_404()
        
        db.session.delete(notification)
        db.session.commit()
        
        return {'message': 'Notification deleted successfully'}, 200

@ns.route('/notifications/preferences')
class NotificationPreferences(Resource):
    ""Notification preferences endpoint."""
    
    @jwt_required()
    @ns.marshal_with(preferences_model)
    def get(self):
        ""Get the current user's notification preferences."""
        user_id = get_jwt_identity()
        preferences = UserPreferences.query.filter_by(user_id=user_id).first()
        
        # Return default preferences if none exist
        if not preferences:
            return {
                'email_notifications': True,
                'push_notifications': True,
                'in_app_notifications': True,
                'marketing_emails': False
            }, 200
            
        return {
            'email_notifications': preferences.email_notifications,
            'push_notifications': preferences.push_notifications,
            'in_app_notifications': preferences.in_app_notifications,
            'marketing_emails': preferences.marketing_emails
        }, 200
    
    @jwt_required()
    @ns.expect(update_preferences_parser)
    @ns.marshal_with(preferences_model)
    def put(self):
        ""Update the current user's notification preferences."""
        user_id = get_jwt_identity()
        args = update_preferences_parser.parse_args()
        
        # Get or create preferences
        preferences = UserPreferences.query.filter_by(user_id=user_id).first()
        if not preferences:
            preferences = UserPreferences(user_id=user_id)
            db.session.add(preferences)
        
        # Update provided fields
        for key, value in args.items():
            if value is not None:
                setattr(preferences, key, value)
        
        db.session.commit()
        
        return {
            'email_notifications': preferences.email_notifications,
            'push_notifications': preferences.push_notifications,
            'in_app_notifications': preferences.in_app_notifications,
            'marketing_emails': preferences.marketing_emails
        }, 200

@ns.route('/notifications/unread-count')
class UnreadNotificationCount(Resource):
    ""Unread notification count endpoint."""
    
    @jwt_required()
    def get(self):
        ""Get the count of unread notifications for the current user."""
        user_id = get_jwt_identity()
        
        count = Notification.query.filter_by(
            user_id=user_id,
            is_read=False
        ).count()
        
        return {'count': count}, 200

@ns.route('/notifications/mark-all-read')
class MarkAllNotificationsRead(Resource):
    ""Mark all notifications as read endpoint."""
    
    @jwt_required()
    def post(self):
        ""Mark all notifications as read for the current user."""
        user_id = get_jwt_identity()
        
        updated = Notification.query.filter_by(
            user_id=user_id,
            is_read=False
        ).update({
            'is_read': True,
            'read_at': db.func.now()
        }, synchronize_session=False)
        
        db.session.commit()
        
        return {'message': f'Marked {updated} notifications as read'}, 200
