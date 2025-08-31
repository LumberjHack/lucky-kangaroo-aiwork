from backend.extensions import db
"""Gamification models for Lucky Kangaroo."""
from datetime import datetime
from ...extensions import db
from sqlalchemy.ext.hybrid import hybrid_property

class Badge(db.Model):
    """Badges that users can earn."""
    __tablename__ = 'badges'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    image_url = db.Column(db.String(255))
    badge_type = db.Column(db.String(50), nullable=False)  # level, achievement, special
    requirement_key = db.Column(db.String(50))  # e.g., level number, achievement ID
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    def __repr__(self):
        return f'<Badge {self.name}>'


class UserBadge(db.Model):
    """Association table for users and badges they've earned."""
    __tablename__ = 'user_badges'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    badge_id = db.Column(db.Integer, db.ForeignKey('badges.id'), nullable=False)
    awarded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    badge = db.relationship('Badge', backref='user_badges')
    
    def __repr__(self):
        return f'<UserBadge user:{self.user_id} badge:{self.badge_id}>'


class UserPoint(db.Model):
    """Tracks user points and transactions."""
    __tablename__ = 'user_points'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    points = db.Column(db.Integer, default=0, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    transactions = db.relationship('PointTransaction', backref='user_points', lazy='dynamic')
    
    def __repr__(self):
        return f'<UserPoints user:{self.user_id} points:{self.points}>'
    
    class Transaction(db.Model):
        """Records of point transactions."""
        __tablename__ = 'point_transactions'
        
        id = db.Column(db.Integer, primary_key=True)
        user_points_id = db.Column(db.Integer, db.ForeignKey('user_points.id'), nullable=False)
        points = db.Column(db.Integer, nullable=False)
        action_type = db.Column(db.String(50), nullable=False)  # listing_created, exchange_completed, etc.
        description = db.Column(db.Text)
        reference_id = db.Column(db.String(100))  # ID of related entity
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        
        def __repr__(self):
            return f'<PointTransaction {self.id} points:{self.points}>'


class UserLevel(db.Model):
    """Tracks user levels and experience points."""
    __tablename__ = 'user_levels'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    level = db.Column(db.Integer, default=1, nullable=False)
    experience = db.Column(db.Integer, default=0, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def xp_for_next_level(self):
        ""Calculate XP needed for next level."""
        # Simple formula: 1000 * (level ^ 1.5)
        return int(1000 * (self.level ** 1.5))
    
    def level_progress(self):
        ""Get progress to next level (0-100)."""
        current_level_xp = self.xp_for_level(self.level)
        next_level_xp = self.xp_for_level(self.level + 1)
        xp_needed = next_level_xp - current_level_xp
        xp_earned = self.experience - current_level_xp
        
        return min(100, int((xp_earned / xp_needed) * 100)) if xp_needed > 0 else 100
    
    @classmethod
    def xp_for_level(cls, level):
        ""Get total XP needed for a specific level."""
        if level <= 1:
            return 0
        return int(sum(1000 * (l ** 1.5) for l in range(1, level)))
    
    def __repr__(self):
        return f'<UserLevel user:{self.user_id} level:{self.level} xp:{self.experience}>'


class Achievement(db.Model):
    """Achievements that users can unlock."""
    __tablename__ = 'achievements'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    icon_url = db.Column(db.String(255))
    points = db.Column(db.Integer, default=0)
    criteria = db.Column(db.JSON)  # Criteria for unlocking
    is_secret = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Achievement {self.name}>'


class UserAchievement(db.Model):
    """Tracks which users have unlocked which achievements."""
    __tablename__ = 'user_achievements'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    achievement_id = db.Column(db.Integer, db.ForeignKey('achievements.id'), nullable=False)
    unlocked_at = db.Column(db.DateTime, default=datetime.utcnow)
    progress = db.Column(db.Integer, default=100)  # 0-100%
    
    # Relationships
    achievement = db.relationship('Achievement', backref='user_achievements')
    
    def __repr__(self):
        return f'<UserAchievement user:{self.user_id} achievement:{self.achievement_id}>'
