"""
Search routes for the Lucky Kangaroo API v1.
Handles searching for users and listings.
"""

from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restx import Resource, fields, reqparse, Namespace
from sqlalchemy import or_, and_

from ...models.user import User, UserStatus
from ...models.listing import Listing, ListingStatus, Category
from ...extensions import db

# Create search namespace
ns = Namespace('search', description='Search operations')

# Request parsers
search_parser = reqparse.RequestParser()
search_parser.add_argument('q', type=str, required=True, help='Search query')
search_parser.add_argument('type', type=str, choices=['all', 'users', 'listings'], default='all')
search_parser.add_argument('page', type=int, default=1, help='Page number')
search_parser.add_argument('per_page', type=int, default=20, help='Items per page')
search_parser.add_argument('category_id', type=int, help='Filter by category ID')

# Response models
search_result_model = ns.model('SearchResult', {
    'type': fields.String(description='Result type: user or listing'),
    'id': fields.Integer(description='Item ID'),
    'title': fields.String(description='Title or username'),
    'description': fields.String(description='Description or user info'),
    'image': fields.String(description='Image URL or avatar'),
    'price': fields.Float(description='Price (for listings)'),
    'currency': fields.String(description='Currency (for listings)'),
    'category': fields.String(description='Category name (for listings)'),
    'user_id': fields.Integer(description='User ID (for listings)'),
    'username': fields.String(description='Username (for listings)'),
    'trust_score': fields.Float(description='User trust score')
})

@ns.route('')
class Search(Resource):
    ""Search endpoint for finding users and listings."""
    
    @jwt_required(optional=True)
    @ns.expect(search_parser)
    @ns.marshal_list_with(search_result_model)
    def get(self):
        ""Search for users and listings."""
        args = search_parser.parse_args()
        query = args['q'].strip()
        search_type = args['type']
        page = args['page']
        per_page = args['per_page']
        
        if not query and not args.get('category_id'):
            return {'message': 'Search query or category filter is required'}, 400
        
        results = []
        
        # Search users
        if search_type in ['all', 'users']:
            user_query = User.query.filter(
                User.status == UserStatus.ACTIVE,
                or_(
                    User.username.ilike(f'%{query}%'),
                    User.display_name.ilike(f'%{query}%')
                )
            )
            
            users = user_query.paginate(page=page, per_page=per_page, error_out=False)
            
            for user in users.items:
                results.append({
                    'type': 'user',
                    'id': user.id,
                    'title': user.username,
                    'description': user.bio or '',
                    'image': user.avatar_url,
                    'trust_score': user.trust_score
                })
        
        # Search listings
        if search_type in ['all', 'listings']:
            listing_query = db.session.query(Listing, Category.name).join(
                Category, Category.id == Listing.category_id
            ).filter(
                Listing.status == ListingStatus.ACTIVE
            )
            
            if query:
                listing_query = listing_query.filter(
                    or_(
                        Listing.title.ilike(f'%{query}%'),
                        Listing.description.ilike(f'%{query}%')
                    )
                )
            
            if args.get('category_id'):
                listing_query = listing_query.filter(Listing.category_id == args['category_id'])
            
            listings = listing_query.paginate(page=page, per_page=per_page, error_out=False)
            
            for listing, category_name in listings.items:
                image_url = listing.images[0].url if listing.images else None
                results.append({
                    'type': 'listing',
                    'id': listing.id,
                    'title': listing.title,
                    'description': listing.description,
                    'image': image_url,
                    'price': float(listing.price) if listing.price else None,
                    'currency': listing.currency,
                    'category': category_name,
                    'user_id': listing.user_id,
                    'username': listing.user.username,
                    'trust_score': listing.user.trust_score
                })
        
        return results, 200

@ns.route('/categories')
class CategoryList(Resource):
    ""Get all categories."""
    
    @ns.marshal_list_with(ns.model('Category', {
        'id': fields.Integer,
        'name': fields.String,
        'parent_id': fields.Integer,
        'icon': fields.String
    }))
    def get(self):
        ""Get all categories."""
        categories = Category.query.all()
        return categories, 200
