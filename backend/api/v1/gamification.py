"""
Gamification features including points, badges, and leaderboards.
"""
from datetime import datetime, timedelta
from flask import request, jsonify, current_app
from flask_restx import Resource, Namespace, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func, desc
from ...models import db, User, UserBadge, Badge, UserPoint, UserLevel, Leaderboard
from ...utils import admin_required

api = Namespace('gamification', description='Gamification features')

# Models
point_transaction_model = api.model('PointTransaction', {
    'points': fields.Integer(required=True, description='Points to add (can be negative)'),
    'action_type': fields.String(required=True, 
                               enum=['listing_created', 'exchange_completed', 'review_received',
                                     'daily_login', 'referral', 'admin_adjustment', 'other']),
    'description': fields.String(description='Description of the transaction')
})

badge_award_model = api.model('BadgeAward', {
    'badge_id': fields.Integer(required=True, description='Badge ID to award'),
    'user_id': fields.Integer(description='User ID (admin only)')
})

@api.route('/points')
class UserPoints(Resource):
    @jwt_required()
    def get(self):
        ""Get current user's points and level."""
        user_id = get_jwt_identity()
        points = UserPoint.query.filter_by(user_id=user_id).first()
        level = UserLevel.query.filter_by(user_id=user_id).first()
        
        if not points:
            points = UserPoint(user_id=user_id, points=0)
            db.session.add(points)
            db.session.commit()
        
        if not level:
            level = UserLevel(user_id=user_id, level=1, experience=0)
            db.session.add(level)
            db.session.commit()
        
        return jsonify({
            'points': points.points,
            'level': level.level,
            'experience': level.experience,
            'next_level_xp': level.xp_for_next_level(),
            'progress': level.level_progress()
        })
    
    @jwt_required()
    @api.expect(point_transaction_model)
    def post(self):
        ""Add or remove points (for internal use, called by other services)."""
        data = request.get_json()
        user_id = get_jwt_identity()
        
        # In a real app, this would be called by internal services, not directly by users
        # So we'll require admin for direct calls
        if not User.query.get(user_id).is_admin:
            return {'message': 'Not authorized'}, 403
            
        points = data['points']
        action_type = data['action_type']
        
        # Update points
        user_points = UserPoint.query.filter_by(user_id=user_id).first()
        if not user_points:
            user_points = UserPoint(user_id=user_id, points=points)
            db.session.add(user_points)
        else:
            user_points.points += points
        
        # Update level based on points
        self._update_user_level(user_id, points)
        
        # Log the transaction
        transaction = UserPoint.Transaction(
            user_id=user_id,
            points=points,
            action_type=action_type,
            description=data.get('description', '')
        )
        db.session.add(transaction)
        db.session.commit()
        
        return {'message': 'Points updated successfully'}
    
    def _update_user_level(self, user_id, points_earned):
        ""Update user level based on points earned."""
        level = UserLevel.query.filter_by(user_id=user_id).first()
        if not level:
            level = UserLevel(user_id=user_id, level=1, experience=0)
            db.session.add(level)
        
        # Add experience (1 point = 1 XP)
        level.experience += points_earned
        
        # Level up if enough XP
        xp_needed = level.xp_for_next_level()
        while level.experience >= xp_needed and level.level < 100:  # Cap at level 100
            level.experience -= xp_needed
            level.level += 1
            
            # Award level badge if exists
            self._award_level_badge(user_id, level.level)
            
            xp_needed = level.xp_for_next_level()
        
        db.session.commit()
    
    def _award_level_badge(self, user_id, level):
        ""Award a badge for reaching a certain level."""
        # Check if badge exists for this level
        badge = Badge.query.filter_by(
            badge_type='level',
            requirement_key=level
        ).first()
        
        if badge and not UserBadge.query.filter_by(user_id=user_id, badge_id=badge.id).first():
            user_badge = UserBadge(user_id=user_id, badge_id=badge.id, awarded_at=datetime.utcnow())
            db.session.add(user_badge)
            db.session.commit()

@api.route('/badges')
class BadgeList(Resource):
    def get(self):
        ""Get all available badges."""
        badges = Badge.query.all()
        return jsonify([{
            'id': b.id,
            'name': b.name,
            'description': b.description,
            'image_url': b.image_url,
            'badge_type': b.badge_type,
            'requirement_key': b.requirement_key
        } for b in badges])

@api.route('/badges/me')
class MyBadges(Resource):
    @jwt_required()
    def get(self):
        ""Get current user's badges."""
        user_id = get_jwt_identity()
        
        badges = db.session.query(
            Badge, UserBadge.awarded_at
        ).join(
            UserBadge, UserBadge.badge_id == Badge.id
        ).filter(
            UserBadge.user_id == user_id
        ).all()
        
        return jsonify([{
            'id': badge.id,
            'name': badge.name,
            'description': badge.description,
            'image_url': badge.image_url,
            'awarded_at': awarded_at.isoformat() if awarded_at else None
        } for badge, awarded_at in badges])

@api.route('/badges/award', methods=['POST'])
class AwardBadge(Resource):
    @jwt_required()
    @admin_required
    @api.expect(badge_award_model)
    def post(self):
        ""Award a badge to a user (admin only)."""
        data = request.get_json()
        badge_id = data['badge_id']
        user_id = data.get('user_id', get_jwt_identity())
        
        # Check if badge exists
        badge = Badge.query.get(badge_id)
        if not badge:
            return {'message': 'Badge not found'}, 404
        
        # Check if user already has the badge
        if UserBadge.query.filter_by(user_id=user_id, badge_id=badge_id).first():
            return {'message': 'User already has this badge'}, 400
        
        # Award the badge
        user_badge = UserBadge(
            user_id=user_id,
            badge_id=badge_id,
            awarded_at=datetime.utcnow()
        )
        db.session.add(user_badge)
        db.session.commit()
        
        return {'message': 'Badge awarded successfully'}

@api.route('/leaderboard')
class LeaderboardResource(Resource):
    def get(self):
        ""Get the leaderboard."""
        period = request.args.get('period', 'all')  # all, weekly, monthly
        limit = min(int(request.args.get('limit', 100)), 1000)
        
        # Base query
        query = db.session.query(
            User.id,
            User.username,
            User.avatar_url,
            UserPoint.points,
            UserLevel.level
        ).join(
            UserPoint, UserPoint.user_id == User.id
        ).join(
            UserLevel, UserLevel.user_id == User.id
        ).filter(
            User.is_active == True,
            User.is_banned == False
        )
        
        # Filter by period
        if period == 'weekly':
            start_date = datetime.utcnow() - timedelta(days=7)
            query = query.join(
                UserPoint.Transaction
            ).filter(
                UserPoint.Transaction.created_at >= start_date
            ).group_by(
                User.id, UserPoint.points, UserLevel.level
            ).with_entities(
                User.id,
                User.username,
                User.avatar_url,
                func.sum(UserPoint.Transaction.points).label('points'),
                UserLevel.level
            )
        elif period == 'monthly':
            start_date = datetime.utcnow() - timedelta(days=30)
            query = query.join(
                UserPoint.Transaction
            ).filter(
                UserPoint.Transaction.created_at >= start_date
            ).group_by(
                User.id, UserPoint.points, UserLevel.level
            ).with_entities(
                User.id,
                User.username,
                User.avatar_url,
                func.sum(UserPoint.Transaction.points).label('points'),
                UserLevel.level
            )
        
        # Order and limit
        query = query.order_by(desc('points')).limit(limit)
        
        results = query.all()
        
        return jsonify([{
            'user_id': user_id,
            'username': username,
            'avatar_url': avatar_url,
            'points': float(points) if points else 0,
            'level': level or 1
        } for user_id, username, avatar_url, points, level in results])

# Export the blueprint
gamification_bp = api
