"""
Gamification routes for the Lucky Kangaroo API v1.
Handles user points, badges, achievements, and leaderboards.
"""

from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restx import Resource, fields, reqparse, Namespace
from datetime import datetime, timedelta
from sqlalchemy import func, desc, and_

from ...models.user import User, UserPoints, Badge, UserBadge, Achievement, UserAchievement
from ...models.listing import Listing, Exchange
from ...extensions import db
from ...utils.decorators import validate_json

# Create gamification namespace
ns = Namespace('gamification', description='Gamification features')

# Request parsers
leaderboard_parser = reqparse.RequestParser()
leaderboard_parser.add_argument('timeframe', type=str, default='all', 
                              choices=['all', 'daily', 'weekly', 'monthly'],
                              help='Time period for leaderboard')
leaderboard_parser.add_argument('limit', type=int, default=20, help='Number of results to return')

# Response models
points_summary_model = ns.model('PointsSummary', {
    'total_points': fields.Integer(description='Total points earned'),
    'available_points': fields.Integer(description='Points available to spend'),
    'spent_points': fields.Integer(description='Points spent'),
    'level': fields.Integer(description='Current level'),
    'points_to_next_level': fields.Integer(description='Points needed for next level'),
    'level_progress': fields.Float(description='Progress to next level (0-1)')
})

badge_model = ns.model('Badge', {
    'id': fields.Integer,
    'name': fields.String,
    'description': fields.String,
    'icon_url': fields.String,
    'points_value': fields.Integer,
    'earned_at': fields.DateTime(attribute='earned_at', skip_none=True)
})

achievement_model = ns.model('Achievement', {
    'id': fields.Integer,
    'name': fields.String,
    'description': fields.String,
    'icon_url': fields.String,
    'points_value': fields.Integer,
    'progress': fields.Float(description='Progress percentage (0-100)'),
    'is_unlocked': fields.Boolean,
    'unlocked_at': fields.DateTime(attribute='unlocked_at', skip_none=True)
})

leaderboard_entry_model = ns.model('LeaderboardEntry', {
    'rank': fields.Integer,
    'user_id': fields.Integer,
    'username': fields.String,
    'avatar_url': fields.String,
    'points': fields.Integer,
    'level': fields.Integer
})

@ns.route('/points')
class PointsResource(Resource):
    ""User points and level information."""
    
    @jwt_required()
    @ns.marshal_with(points_summary_model)
    def get(self):
        ""Get the current user's points and level information."""
        user_id = get_jwt_identity()
        
        # Get total points
        total_points = db.session.query(
            func.coalesce(func.sum(UserPoints.points), 0)
        ).filter(
            UserPoints.user_id == user_id
        ).scalar() or 0
        
        # Get spent points (simplified - in a real app, track point spending)
        spent_points = 0
        available_points = total_points - spent_points
        
        # Calculate level (simplified formula: level = floor(sqrt(total_points / 100)))
        level = int((total_points / 100) ** 0.5)
        
        # Points needed for next level
        points_for_current_level = (level ** 2) * 100
        points_for_next_level = ((level + 1) ** 2) * 100
        points_to_next_level = max(0, points_for_next_level - total_points)
        
        # Progress to next level (0-1)
        level_progress = min(1.0, (total_points - points_for_current_level) / 
                           (points_for_next_level - points_for_current_level)) if level > 0 else 0.0
        
        return {
            'total_points': total_points,
            'available_points': available_points,
            'spent_points': spent_points,
            'level': level,
            'points_to_next_level': points_to_next_level,
            'level_progress': level_progress
        }, 200

@ns.route('/badges')
class BadgeList(Resource):
    ""User badges and achievements."""
    
    @jwt_required()
    @ns.marshal_list_with(badge_model)
    def get(self):
        ""Get all badges, with earned status for the current user."""
        user_id = get_jwt_identity()
        
        # Get all badges with earned status
        badges = db.session.query(
            Badge,
            UserBadge.earned_at
        ).outerjoin(
            UserBadge, 
            and_(
                UserBadge.badge_id == Badge.id,
                UserBadge.user_id == user_id
            )
        ).all()
        
        result = []
        for badge, earned_at in badges:
            badge_dict = badge.as_dict()
            badge_dict['earned_at'] = earned_at
            result.append(badge_dict)
            
        return result, 200

@ns.route('/achievements')
class AchievementList(Resource):
    ""User achievements and progress."""
    
    @jwt_required()
    @ns.marshal_list_with(achievement_model)
    def get(self):
        ""Get all achievements with progress for the current user."""
        user_id = get_jwt_identity()
        
        # Get all achievements with progress
        achievements = db.session.query(
            Achievement,
            UserAchievement.unlocked_at
        ).outerjoin(
            UserAchievement,
            and_(
                UserAchievement.achievement_id == Achievement.id,
                UserAchievement.user_id == user_id
            )
        ).all()
        
        # Get user stats for progress calculation
        user = User.query.get(user_id)
        user_stats = self._get_user_stats(user_id)
        
        result = []
        for achievement, unlocked_at in achievements:
            progress = self._calculate_achievement_progress(achievement, user, user_stats)
            is_unlocked = unlocked_at is not None
            
            achievement_dict = achievement.as_dict()
            achievement_dict.update({
                'progress': progress,
                'is_unlocked': is_unlocked,
                'unlocked_at': unlocked_at
            })
            result.append(achievement_dict)
            
        return result, 200
    
    def _get_user_stats(self, user_id):
        ""Get user statistics for achievement progress."""
        stats = {
            'listings_created': Listing.query.filter_by(user_id=user_id).count(),
            'exchanges_completed': Exchange.query.filter(
                Exchange.status == 'completed',
                Exchange.seller_id == user_id
            ).count(),
            'messages_sent': 0,  # Would come from chat model
            'days_active': (datetime.utcnow() - user.created_at).days,
            'trust_score': user.trust_score
        }
        return stats
    
    def _calculate_achievement_progress(self, achievement, user, user_stats):
        ""Calculate progress for an achievement."""
        criteria = achievement.criteria or {}
        progress = 0.0
        
        if achievement.achievement_type == 'listing_count':
            target = criteria.get('count', 1)
            progress = min(100.0, (user_stats['listings_created'] / target) * 100)
            
        elif achievement.achievement_type == 'exchange_count':
            target = criteria.get('count', 1)
            progress = min(100.0, (user_stats['exchanges_completed'] / target) * 100)
            
        elif achievement.achievement_type == 'streak':
            # This is simplified - in a real app, track login streaks
            progress = 0.0
            
        elif achievement.achievement_type == 'trust_score':
            target = criteria.get('score', 100)
            progress = min(100.0, (user_stats['trust_score'] / target) * 100)
        
        return min(100.0, progress)  # Cap at 100%

@ns.route('/leaderboard')
class LeaderboardResource(Resource):
    ""Leaderboard of top users by points."""
    
    @jwt_required()
    @ns.expect(leaderboard_parser)
    @ns.marshal_with(leaderboard_entry_model)
    def get(self):
        ""Get the leaderboard."""
        args = leaderboard_parser.parse_args()
        timeframe = args['timeframe']
        limit = min(args['limit'], 100)
        
        # Calculate time filter based on timeframe
        now = datetime.utcnow()
        if timeframe == 'daily':
            start_date = now - timedelta(days=1)
        elif timeframe == 'weekly':
            start_date = now - timedelta(weeks=1)
        elif timeframe == 'monthly':
            start_date = now - timedelta(days=30)
        else:  # all time
            start_date = None
        
        # Base query for user points
        query = db.session.query(
            User.id.label('user_id'),
            User.username,
            User.avatar_url,
            func.coalesce(func.sum(UserPoints.points), 0).label('total_points')
        ).join(
            UserPoints, UserPoints.user_id == User.id
        ).filter(
            User.status == 'active'
        )
        
        # Apply time filter if specified
        if start_date:
            query = query.filter(UserPoints.awarded_at >= start_date)
        
        # Group and order
        query = query.group_by(User.id).order_by(desc('total_points')).limit(limit)
        
        # Execute query
        results = query.all()
        
        # Format results with ranks
        leaderboard = []
        for i, (user_id, username, avatar_url, points) in enumerate(results, 1):
            # Calculate level
            level = int((points / 100) ** 0.5)
            
            leaderboard.append({
                'rank': i,
                'user_id': user_id,
                'username': username,
                'avatar_url': avatar_url,
                'points': points,
                'level': level
            })
        
        return leaderboard, 200

@ns.route('/recent-activity')
class RecentActivity(Resource):
    ""Recent gamification activity for the current user."""
    
    @jwt_required()
    def get(self):
        ""Get recent points, badges, and achievements."""
        user_id = get_jwt_identity()
        limit = min(int(request.args.get('limit', 10)), 50)
        
        # Get recent points
        recent_points = UserPoints.query.filter_by(
            user_id=user_id
        ).order_by(
            UserPoints.awarded_at.desc()
        ).limit(limit).all()
        
        # Get recent badges
        recent_badges = db.session.query(
            Badge, 
            UserBadge.earned_at
        ).join(
            UserBadge, UserBadge.badge_id == Badge.id
        ).filter(
            UserBadge.user_id == user_id
        ).order_by(
            UserBadge.earned_at.desc()
        ).limit(limit).all()
        
        # Get recent achievements
        recent_achievements = db.session.query(
            Achievement,
            UserAchievement.unlocked_at
        ).join(
            UserAchievement, UserAchievement.achievement_id == Achievement.id
        ).filter(
            UserAchievement.user_id == user_id
        ).order_by(
            UserAchievement.unlocked_at.desc()
        ).limit(limit).all()
        
        # Combine and sort all activities
        activities = []
        
        for points in recent_points:
            activities.append({
                'type': 'points',
                'title': f"Earned {points.points} points",
                'description': points.reason,
                'timestamp': points.awarded_at,
                'data': {
                    'points': points.points,
                    'reason': points.reason
                }
            })
            
        for badge, earned_at in recent_badges:
            activities.append({
                'type': 'badge',
                'title': f"Earned badge: {badge.name}",
                'description': badge.description,
                'timestamp': earned_at,
                'data': {
                    'badge_id': badge.id,
                    'badge_name': badge.name,
                    'icon_url': badge.icon_url,
                    'points_value': badge.points_value
                }
            })
            
        for achievement, unlocked_at in recent_achievements:
            activities.append({
                'type': 'achievement',
                'title': f"Achievement unlocked: {achievement.name}",
                'description': achievement.description,
                'timestamp': unlocked_at,
                'data': {
                    'achievement_id': achievement.id,
                    'achievement_name': achievement.name,
                    'icon_url': achievement.icon_url,
                    'points_value': achievement.points_value
                }
            })
        
        # Sort by timestamp
        activities.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return {'activities': activities[:limit]}, 200
