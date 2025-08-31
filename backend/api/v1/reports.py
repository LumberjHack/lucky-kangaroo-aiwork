"""
Report routes for handling user reports and analytics.
"""
from flask import request, jsonify, current_app
from flask_restx import Resource, Namespace, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from ...models import db, Report, User, Listing
from ...utils import admin_required

api = Namespace('reports', description='Reporting operations')

# Request models
report_model = api.model('Report', {
    'report_type': fields.String(required=True, enum=['user', 'listing', 'message', 'other']),
    'reported_id': fields.String(required=True, description='ID of the reported item'),
    'reason': fields.String(required=True, description='Reason for the report'),
    'description': fields.String(description='Additional details'),
    'evidence': fields.String(description='URL to evidence if available')
})

@api.route('')
class ReportList(Resource):
    @jwt_required()
    @api.doc('create_report')
    @api.expect(report_model)
    def post(self):
        ""Create a new report."""
        data = request.get_json()
        user_id = get_jwt_identity()
        
        # Check if user already reported this item
        existing = Report.query.filter_by(
            reporter_id=user_id,
            report_type=data['report_type'],
            reported_id=data['reported_id']
        ).first()
        
        if existing:
            return {'message': 'You have already reported this item'}, 400
        
        # Create new report
        report = Report(
            reporter_id=user_id,
            report_type=data['report_type'],
            reported_id=data['reported_id'],
            reason=data['reason'],
            description=data.get('description'),
            evidence=data.get('evidence'),
            status='pending'
        )
        
        db.session.add(report)
        db.session.commit()
        
        return {'message': 'Report submitted successfully', 'id': report.id}, 201

@api.route('/user/<string:user_id>')
class UserReports(Resource):
    @jwt_required()
    def get(self, user_id):
        ""Get reports for a specific user (admin or reporter only)."""
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        if not current_user.is_admin and str(current_user_id) != user_id:
            return {'message': 'Not authorized'}, 403
            
        reports = Report.query.filter_by(
            reporter_id=user_id
        ).order_by(Report.created_at.desc()).all()
        
        return jsonify([{
            'id': r.id,
            'report_type': r.report_type,
            'reported_id': r.reported_id,
            'reason': r.reason,
            'status': r.status,
            'created_at': r.created_at.isoformat(),
            'resolved_at': r.resolved_at.isoformat() if r.resolved_at else None,
            'admin_notes': r.admin_notes if current_user.is_admin else None
        } for r in reports])

@api.route('/admin/pending')
class PendingReports(Resource):
    @admin_required
    def get(self):
        ""Get all pending reports (admin only)."""
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        reports = Report.query.filter_by(
            status='pending'
        ).order_by(
            Report.created_at.desc()
        ).paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'items': [{
                'id': r.id,
                'report_type': r.report_type,
                'reported_id': r.reported_id,
                'reason': r.reason,
                'created_at': r.created_at.isoformat(),
                'reporter_id': r.reporter_id
            } for r in reports.items],
            'total': reports.total,
            'pages': reports.pages,
            'page': page
        })

@api.route('/admin/<int:report_id>/resolve', methods=['POST'])
class ResolveReport(Resource):
    @admin_required
    @api.doc(params={
        'action': 'Action taken (warn, suspend, ban, dismiss)',
        'notes': 'Admin notes about the resolution'
    })
    def post(self, report_id):
        ""Resolve a report (admin only)."""
        report = Report.query.get_or_404(report_id)
        
        if report.status != 'pending':
            return {'message': 'Report already processed'}, 400
            
        action = request.args.get('action', 'dismiss')
        notes = request.args.get('notes', '')
        
        # Update report status
        report.status = 'resolved'
        report.admin_id = get_jwt_identity()
        report.admin_notes = notes
        report.action_taken = action
        
        # Take appropriate action based on report type
        if action in ['warn', 'suspend', 'ban'] and report.report_type == 'user':
            user = User.query.get(report.reported_id)
            if user:
                if action == 'warn':
                    # Send warning
                    pass
                elif action == 'suspend':
                    user.is_suspended = True
                    # Set suspension end date
                elif action == 'ban':
                    user.is_banned = True
        
        db.session.commit()
        return {'message': f'Report {report_id} resolved with action: {action}'}

# Export the blueprint
reports_bp = api
