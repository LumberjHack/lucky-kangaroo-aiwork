"""
Payment routes for handling transactions and subscriptions.
"""
from flask import request, jsonify, current_app
from flask_restx import Resource, Namespace, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from ...models import db, User, Payment, SubscriptionPlan
from ...utils import admin_required

api = Namespace('payments', description='Payment operations')

# Request models
payment_model = api.model('Payment', {
    'amount': fields.Float(required=True, description='Payment amount'),
    'currency': fields.String(required=True, description='Currency code (e.g., CHF, EUR)'),
    'payment_method': fields.String(required=True, description='Payment method ID'),
    'description': fields.String(description='Payment description')
})

subscription_model = api.model('Subscription', {
    'plan_id': fields.String(required=True, description='Subscription plan ID'),
    'payment_method': fields.String(required=True, description='Payment method ID'),
    'trial_period_days': fields.Integer(description='Trial period in days')
})

@api.route('/methods')
class PaymentMethods(Resource):
    @jwt_required()
    def get(self):
        ""Get user's payment methods."""
        user_id = get_jwt_identity()
        # In a real app, fetch from payment provider
        return jsonify({
            'methods': [
                {'id': 'pm_123', 'brand': 'visa', 'last4': '4242', 'exp_month': 12, 'exp_year': 2025}
            ]
        })

@api.route('/create-payment-intent', methods=['POST'])
class CreatePaymentIntent(Resource):
    @jwt_required()
    @api.expect(payment_model)
    def post(self):
        ""Create a payment intent."""
        data = request.get_json()
        user_id = get_jwt_identity()
        
        # In a real app, create a PaymentIntent with a payment provider
        return jsonify({
            'client_secret': 'pi_123_secret_456',
            'amount': data['amount'],
            'currency': data['currency']
        })

@api.route('/subscription/plans')
class SubscriptionPlans(Resource):
    def get(self):
        ""Get available subscription plans."""
        plans = SubscriptionPlan.query.filter_by(is_active=True).all()
        return jsonify([{
            'id': plan.id,
            'name': plan.name,
            'description': plan.description,
            'price': float(plan.price),
            'currency': plan.currency,
            'billing_interval': plan.billing_interval,
            'features': plan.features
        } for plan in plans])

@api.route('/subscription/subscribe', methods=['POST'])
class Subscribe(Resource):
    @jwt_required()
    @api.expect(subscription_model)
    def post(self):
        ""Subscribe to a plan."""
        data = request.get_json()
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        # In a real app, create subscription with payment provider
        return jsonify({
            'status': 'success',
            'subscription_id': 'sub_123',
            'current_period_end': '2025-12-31T23:59:59Z'
        })

@api.route('/subscription/cancel', methods=['POST'])
class CancelSubscription(Resource):
    @jwt_required()
    def post(self):
        ""Cancel subscription."""
        user_id = get_jwt_identity()
        # In a real app, cancel with payment provider
        return jsonify({'status': 'cancelled'})

# Admin endpoints
@api.route('/admin/transactions')
class AdminTransactions(Resource):
    @admin_required
    def get(self):
        ""Get all transactions (admin only)."""
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        transactions = Payment.query.order_by(
            Payment.created_at.desc()
        ).paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'items': [{
                'id': txn.id,
                'user_id': txn.user_id,
                'amount': float(txn.amount),
                'currency': txn.currency,
                'status': txn.status,
                'created_at': txn.created_at.isoformat(),
                'description': txn.description
            } for txn in transactions.items],
            'total': transactions.total,
            'pages': transactions.pages,
            'page': page
        })

# Export the blueprint
payments_bp = api
