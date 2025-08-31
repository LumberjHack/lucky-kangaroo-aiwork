"""
Admin routes for the Lucky Kangaroo API v1.
Requires admin privileges to access these endpoints.
"""

from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restx import Resource, fields, reqparse, Namespace
from sqlalchemy import or_

from ...models.user import User, UserRole, UserStatus
from ...models.listing import Listing, ListingStatus
from ...models.report import Report, ReportStatus
from ...extensions import db
from ...utils.decorators import admin_required

# Create admin namespace
ns = Namespace('admin', description='Admin operations')

# Request parsers
pagination_parser = reqparse.RequestParser()
pagination_parser.add_argument('page', type=int, default=1, help='Page number')
pagination_parser.add_argument('per_page', type=int, default=20, help='Items per page')

# Response models
user_model = ns.model('AdminUser', {
    'id': fields.Integer,
    'username': fields.String,
    'email': fields.String,
    'role': fields.String(enum=[r.value for r in UserRole]),
    'status': fields.String(enum=[s.value for s in UserStatus]),
    'created_at': fields.DateTime
})

listing_model = ns.model('AdminListing', {
    'id': fields.Integer,
    'title': fields.String,
    'status': fields.String(enum=[s.value for s in ListingStatus]),
    'user_id': fields.Integer,
    'created_at': fields.DateTime
})

report_model = ns.model('AdminReport', {
    'id': fields.Integer,
    'reason': fields.String,
    'status': fields.String(enum=[s.value for s in ReportStatus]),
    'created_at': fields.DateTime
})

@ns.route('/users')
class AdminUserList(Resource):
    @jwt_required()
    @admin_required()
    @ns.expect(pagination_parser)
    def get(self):
        ""Get paginated list of users."""
        args = pagination_parser.parse_args()
        page = args['page']
        per_page = args['per_page']
        
        users = User.query.paginate(page=page, per_page=per_page, error_out=False)
        
        return {
            'items': [user.as_dict() for user in users.items],
            'total': users.total,
            'pages': users.pages,
            'current_page': page,
            'per_page': per_page
        }, 200

@ns.route('/users/<int:user_id>')
class AdminUserResource(Resource):
    @jwt_required()
    @admin_required()
    @ns.marshal_with(user_model)
    def get(self, user_id):
        ""Get user details."""
        user = User.query.get_or_404(user_id)
        return user, 200
    
    @jwt_required()
    @admin_required()
    def delete(self, user_id):
        ""Delete a user (soft delete)."""
        user = User.query.get_or_404(user_id)
        
        # Prevent deleting self
        current_user_id = get_jwt_identity()
        if user.id == current_user_id:
            return {'message': 'Cannot delete your own account'}, 403
        
        # Soft delete
        user.status = UserStatus.DELETED
        user.email = f"deleted_{user.id}_{user.email}"
        user.username = f"deleted_{user.id}_{user.username}"
        user.token_version += 1
        
        db.session.commit()
        return {'message': 'User deleted successfully'}, 200

@ns.route('/listings')
class AdminListingList(Resource):
    @jwt_required()
    @admin_required()
    @ns.expect(pagination_parser)
    def get(self):
        ""Get paginated list of listings."""
        args = pagination_parser.parse_args()
        page = args['page']
        per_page = args['per_page']
        
        listings = Listing.query.paginate(page=page, per_page=per_page, error_out=False)
        
        return {
            'items': [listing.as_dict() for listing in listings.items],
            'total': listings.total,
            'pages': listings.pages,
            'current_page': page,
            'per_page': per_page
        }, 200

@ns.route('/reports')
class AdminReportList(Resource):
    @jwt_required()
    @admin_required()
    @ns.expect(pagination_parser)
    def get(self):
        ""Get paginated list of reports."""
        args = pagination_parser.parse_args()
        page = args['page']
        per_page = args['per_page']
        
        reports = Report.query.paginate(page=page, per_page=per_page, error_out=False)
        
        return {
            'items': [report.as_dict() for report in reports.items],
            'total': reports.total,
            'pages': reports.pages,
            'current_page': page,
            'per_page': per_page
        }, 200

@ns.route('/stats')
class AdminStats(Resource):
    @jwt_required()
    @admin_required()
    def get(self):
        ""Get platform statistics."""
        from sqlalchemy import func, desc
        from datetime import datetime, timedelta
        
        now = datetime.utcnow()
        today = now.date()
        week_ago = today - timedelta(days=7)
        
        # User stats
        total_users = User.query.count()
        new_users_today = User.query.filter(
            func.date(User.created_at) == today
        ).count()
        
        # Listing stats
        total_listings = Listing.query.count()
        active_listings = Listing.query.filter_by(status=ListingStatus.ACTIVE).count()
        
        # Report stats
        total_reports = Report.query.count()
        open_reports = Report.query.filter_by(status=ReportStatus.OPEN).count()
        
        return {
            'users': {
                'total': total_users,
                'new_today': new_users_today,
                'by_role': dict(
                    db.session.query(User.role, func.count(User.id))
                    .group_by(User.role)
                    .all()
                )
            },
            'listings': {
                'total': total_listings,
                'active': active_listings,
                'by_status': dict(
                    db.session.query(Listing.status, func.count(Listing.id))
                    .group_by(Listing.status)
                    .all()
                )
            },
            'reports': {
                'total': total_reports,
                'open': open_reports,
                'by_status': dict(
                    db.session.query(Report.status, func.count(Report.id))
                    .group_by(Report.status)
                    .all()
                )
            }
        }, 200
