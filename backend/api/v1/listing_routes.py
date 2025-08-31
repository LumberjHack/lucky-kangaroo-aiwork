"""
Listing routes for the Lucky Kangaroo API v1.
Handles creation, retrieval, updating, and deletion of listings.
"""

from flask import request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from flask_restx import Resource, fields, reqparse, marshal
from werkzeug.datastructures import FileStorage
from sqlalchemy import or_, and_, func
from datetime import datetime, timedelta
import uuid
import os

from ...models.listing import Listing, ListingImage, Category, Favorite, Report, ExchangeRequest, Review
from ...models.user import User, TrustScore
from ...models.exchange import Exchange
from ...extensions import db, limiter, s3_client
from ...utils.decorators import validate_json, upload_file, admin_required
from ...utils.rate_limits import get_limiter_key
from ...utils.geo import get_coordinates, calculate_distance
from . import ns

# Request parsers
create_listing_parser = reqparse.RequestParser()
create_listing_parser.add_argument('title', type=str, required=True, help='Listing title')
create_listing_parser.add_argument('description', type=str, required=True, help='Listing description')
create_listing_parser.add_argument('category_id', type=int, required=True, help='Category ID')
create_listing_parser.add_argument('condition', type=str, required=True, help='Item condition', 
                                  choices=('new', 'like_new', 'good', 'fair', 'poor'))
create_listing_parser.add_argument('value', type=float, required=True, help='Estimated value in EUR')
create_listing_parser.add_argument('preferred_exchange', type=str, required=False, 
                                  help='Preferred exchange type', 
                                  choices=('direct', 'auction', 'both'))
create_listing_parser.add_argument('tags', type=str, action='append', help='Listing tags')
create_listing_parser.add_argument('location', type=dict, required=False, help='Location information')

update_listing_parser = reqparse.RequestParser()
update_listing_parser.add_argument('title', type=str, required=False, help='Listing title')
update_listing_parser.add_argument('description', type=str, required=False, help='Listing description')
update_listing_parser.add_argument('category_id', type=int, required=False, help='Category ID')
update_listing_parser.add_argument('condition', type=str, required=False, help='Item condition', 
                                  choices=('new', 'like_new', 'good', 'fair', 'poor'))
update_listing_parser.add_argument('value', type=float, required=False, help='Estimated value in EUR')
update_listing_parser.add_argument('status', type=str, required=False, help='Listing status',
                                  choices=('draft', 'active', 'pending', 'completed', 'cancelled'))
update_listing_parser.add_argument('preferred_exchange', type=str, required=False, 
                                  help='Preferred exchange type', 
                                  choices=('direct', 'auction', 'both'))
update_listing_parser.add_argument('tags', type=str, action='append', help='Listing tags')
update_listing_parser.add_argument('location', type=dict, required=False, help='Location information')

search_parser = reqparse.RequestParser()
search_parser.add_argument('query', type=str, required=False, help='Search query')
search_parser.add_argument('category_id', type=int, required=False, help='Filter by category ID')
search_parser.add_argument('min_value', type=float, required=False, help='Minimum value')
search_parser.add_argument('max_value', type=float, required=False, help='Maximum value')
search_parser.add_argument('condition', type=str, required=False, help='Item condition',
                          choices=('new', 'like_new', 'good', 'fair', 'poor'))
search_parser.add_argument('distance', type=float, required=False, default=50, 
                          help='Maximum distance in kilometers')
search_parser.add_argument('lat', type=float, required=False, help='Latitude for distance filtering')
search_parser.add_argument('lng', type=float, required=False, help='Longitude for distance filtering')
search_parser.add_argument('sort_by', type=str, required=False, default='recent',
                          choices=('recent', 'value_asc', 'value_desc', 'distance'),
                          help='Sort order')
search_parser.add_argument('page', type=int, required=False, default=1, help='Page number')
search_parser.add_argument('per_page', type=int, required=False, default=20, 
                          help='Items per page (max 100)')

# File upload parser
image_upload_parser = reqparse.RequestParser()
image_upload_parser.add_argument('image', location='files', type=FileStorage, required=True, 
                               help='Image file')

# Response models
category_model = ns.model('Category', {
    'id': fields.Integer(description='Category ID'),
    'name': fields.String(description='Category name'),
    'slug': fields.String(description='URL-friendly slug'),
    'parent_id': fields.Integer(description='Parent category ID'),
    'icon': fields.String(description='Icon class or URL'),
    'is_active': fields.Boolean(description='Whether the category is active')
})

image_model = ns.model('Image', {
    'id': fields.Integer(description='Image ID'),
    'url': fields.String(description='Image URL'),
    'thumbnail_url': fields.String(description='Thumbnail URL'),
    'is_primary': fields.Boolean(description='Whether this is the primary image')
})

listing_model = ns.model('Listing', {
    'id': fields.Integer(description='Listing ID'),
    'title': fields.String(description='Listing title'),
    'description': fields.String(description='Listing description'),
    'status': fields.String(description='Listing status', 
                          enum=['draft', 'active', 'pending', 'completed', 'cancelled']),
    'condition': fields.String(description='Item condition', 
                              enum=['new', 'like_new', 'good', 'fair', 'poor']),
    'value': fields.Float(description='Estimated value in EUR'),
    'preferred_exchange': fields.String(description='Preferred exchange type',
                                       enum=['direct', 'auction', 'both']),
    'views': fields.Integer(description='Number of views'),
    'favorites_count': fields.Integer(description='Number of times favorited'),
    'created_at': fields.DateTime(description='Creation timestamp'),
    'updated_at': fields.DateTime(description='Last update timestamp'),
    'user': fields.Nested(ns.model('ListingUser', {
        'id': fields.Integer(description='User ID'),
        'username': fields.String(description='Username'),
        'avatar_url': fields.String(description='Profile picture URL'),
        'trust_score': fields.Float(description='User trust score')
    })),
    'category': fields.Nested(category_model, description='Listing category'),
    'images': fields.List(fields.Nested(image_model), description='Listing images'),
    'tags': fields.List(fields.String, description='Listing tags'),
    'location': fields.Raw(description='Location information'),
    'distance': fields.Float(description='Distance in km (only for search results with location)')
})

@ns.route('/listings')
class ListingList(Resource):
    ""Listings collection endpoint."""
    
    @jwt_required(optional=True)
    @ns.expect(search_parser)
    @ns.marshal_list_with(listing_model)
    def get(self):
        ""Search and filter listings."""
        args = search_parser.parse_args()
        
        # Base query for active listings
        query = Listing.query.filter_by(status='active')
        
        # Apply filters
        if args.get('query'):
            search = f"%{args['query']}%"
            query = query.filter(
                or_(
                    Listing.title.ilike(search),
                    Listing.description.ilike(search),
                    Listing.tags.any(search)
                )
            )
            
        if args.get('category_id'):
            # Include subcategories
            category = Category.query.get_or_404(args['category_id'])
            category_ids = [c.id for c in category.get_all_children()] + [category.id]
            query = query.filter(Listing.category_id.in_(category_ids))
            
        if args.get('min_value') is not None:
            query = query.filter(Listing.value >= args['min_value'])
            
        if args.get('max_value') is not None:
            query = query.filter(Listing.value <= args['max_value'])
            
        if args.get('condition'):
            query = query.filter(Listing.condition == args['condition'])
        
        # Handle location-based filtering
        if args.get('lat') and args.get('lng') and args.get('distance'):
            # This is a simplified approach - in production, use PostGIS for better performance
            user_lat = args['lat']
            user_lng = args['lng']
            max_distance = args['distance']
            
            # Get listings with location data
            listings_with_location = []
            for listing in query.all():
                if listing.location and 'lat' in listing.location and 'lng' in listing.location:
                    distance = calculate_distance(
                        user_lat, user_lng,
                        listing.location['lat'], listing.location['lng']
                    )
                    if distance <= max_distance:
                        listing.distance = distance
                        listings_with_location.append(listing)
            
            # Sort by distance
            listings_with_location.sort(key=lambda x: x.distance)
            
            # Apply pagination
            page = args['page']
            per_page = min(args['per_page'], 100)  # Max 100 per page
            start = (page - 1) * per_page
            end = start + per_page
            paginated_listings = listings_with_location[start:end]
            
            return paginated_listings, 200
        
        # Apply sorting
        if args.get('sort_by') == 'recent':
            query = query.order_by(Listing.created_at.desc())
        elif args.get('sort_by') == 'value_asc':
            query = query.order_by(Listing.value.asc())
        elif args.get('sort_by') == 'value_desc':
            query = query.order_by(Listing.value.desc())
        
        # Pagination
        page = args['page']
        per_page = min(args['per_page'], 100)  # Max 100 per page
        paginated_listings = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return paginated_listings.items, 200
    
    @jwt_required()
    @ns.expect(create_listing_parser)
    @ns.marshal_with(listing_model, code=201)
    def post(self):
        ""Create a new listing."""
        user_id = get_jwt_identity()
        args = create_listing_parser.parse_args()
        
        # Check if category exists
        category = Category.query.get(args['category_id'])
        if not category or not category.is_active:
            return {'message': 'Invalid or inactive category'}, 400
        
        # Create the listing
        listing = Listing(
            user_id=user_id,
            title=args['title'],
            description=args['description'],
            category_id=args['category_id'],
            condition=args['condition'],
            value=args['value'],
            preferred_exchange=args.get('preferred_exchange', 'direct'),
            status='draft',  # Start as draft, require images to activate
            tags=args.get('tags', []),
            location=args.get('location')
        )
        
        db.session.add(listing)
        db.session.commit()
        
        # Return the created listing
        return listing, 201

@ns.route('/listings/<int:listing_id>')
class ListingResource(Resource):
    ""Individual listing endpoint."""
    
    @jwt_required(optional=True)
    @ns.marshal_with(listing_model)
    def get(self, listing_id):
        ""Get a single listing by ID."""
        listing = Listing.query.get_or_404(listing_id)
        
        # Increment view count (only for non-owners and non-draft listings)
        current_user_id = get_jwt_identity()
        if current_user_id != listing.user_id and listing.status != 'draft':
            listing.views += 1
            db.session.commit()
        
        return listing
    
    @jwt_required()
    @ns.expect(update_listing_parser)
    @ns.marshal_with(listing_model)
    def put(self, listing_id):
        ""Update a listing."""
        user_id = get_jwt_identity()
        listing = Listing.query.get_or_404(listing_id)
        
        # Check ownership
        if listing.user_id != user_id:
            return {'message': 'Not authorized to update this listing'}, 403
        
        # Prevent updates to completed or cancelled listings
        if listing.status in ['completed', 'cancelled']:
            return {'message': 'Cannot update a completed or cancelled listing'}, 400
        
        args = update_listing_parser.parse_args()
        
        # Update fields if provided
        if args.get('title') is not None:
            listing.title = args['title']
        if args.get('description') is not None:
            listing.description = args['description']
        if args.get('category_id') is not None:
            category = Category.query.get(args['category_id'])
            if not category or not category.is_active:
                return {'message': 'Invalid or inactive category'}, 400
            listing.category_id = args['category_id']
        if args.get('condition') is not None:
            listing.condition = args['condition']
        if args.get('value') is not None:
            listing.value = args['value']
        if args.get('status') is not None:
            # Additional validation for status changes
            if args['status'] not in ['draft', 'active', 'pending', 'completed', 'cancelled']:
                return {'message': 'Invalid status'}, 400
            listing.status = args['status']
        if args.get('preferred_exchange') is not None:
            listing.preferred_exchange = args['preferred_exchange']
        if args.get('tags') is not None:
            listing.tags = args['tags']
        if args.get('location') is not None:
            listing.location = args['location']
        
        listing.updated_at = datetime.utcnow()
        db.session.commit()
        
        return listing
    
    @jwt_required()
    def delete(self, listing_id):
        ""Delete a listing."""
        user_id = get_jwt_identity()
        listing = Listing.query.get_or_404(listing_id)
        
        # Check ownership or admin
        if listing.user_id != user_id and not get_jwt().get('is_admin', False):
            return {'message': 'Not authorized to delete this listing'}, 403
        
        # Don't allow deletion of listings with active exchanges
        active_exchanges = Exchange.query.filter(
            or_(
                Exchange.listing_id == listing_id,
                Exchange.offered_listing_id == listing_id
            ),
            Exchange.status.in_(['pending', 'accepted', 'in_progress'])
        ).count()
        
        if active_exchanges > 0:
            return {'message': 'Cannot delete a listing with active exchanges'}, 400
        
        # Soft delete
        listing.status = 'deleted'
        listing.deleted_at = datetime.utcnow()
        db.session.commit()
        
        return {'message': 'Listing deleted successfully'}, 200

@ns.route('/listings/<int:listing_id>/images')
class ListingImages(Resource):
    ""Listing images management endpoint."""
    
    @jwt_required()
    @ns.expect(image_upload_parser)
    @ns.marshal_with(image_model, code=201)
    @upload_file(allowed_extensions={'png', 'jpg', 'jpeg', 'gif'}, max_size=5*1024*1024)  # 5MB max
    def post(self, listing_id, uploaded_file):
        ""Upload an image for a listing."""
        user_id = get_jwt_identity()
        listing = Listing.query.get_or_404(listing_id)
        
        # Check ownership
        if listing.user_id != user_id:
            return {'message': 'Not authorized to add images to this listing'}, 403
            
        # Check if listing can be modified
        if listing.status in ['completed', 'cancelled', 'deleted']:
            return {'message': 'Cannot add images to a completed, cancelled, or deleted listing'}, 400
        
        # Generate a unique filename
        file_ext = os.path.splitext(uploaded_file.filename)[1].lower()
        filename = f"listings/{listing_id}/{uuid.uuid4()}{file_ext}"
        
        # Upload to S3
        try:
            s3_client.upload_fileobj(
                uploaded_file,
                current_app.config['S3_BUCKET'],
                filename,
                ExtraArgs={
                    'ACL': 'public-read',
                    'ContentType': uploaded_file.content_type
                }
            )
            
            # Create image record
            image = ListingImage(
                listing_id=listing_id,
                url=f"https://{current_app.config['S3_BUCKET']}.s3.{current_app.config['S3_REGION']}.amazonaws.com/{filename}",
                filename=filename,
                content_type=uploaded_file.content_type,
                file_size=uploaded_file.content_length,
                is_primary=False  # First image will be set as primary
            )
            
            # If this is the first image, set it as primary
            if not listing.images:
                image.is_primary = True
            
            db.session.add(image)
            
            # If listing was a draft with no images, activate it
            if listing.status == 'draft' and len(listing.images) == 0:
                listing.status = 'active'
            
            listing.updated_at = datetime.utcnow()
            db.session.commit()
            
            return image, 201
            
        except Exception as e:
            current_app.logger.error(f"Failed to upload listing image: {str(e)}")
            return {'message': 'Failed to upload image'}, 500
    
    @jwt_required()
    @ns.param('image_id', 'ID of the image to set as primary')
    def put(self, listing_id):
        ""Set an image as the primary image for a listing."""
        user_id = get_jwt_identity()
        listing = Listing.query.get_or_404(listing_id)
        
        # Check ownership
        if listing.user_id != user_id:
            return {'message': 'Not authorized to modify this listing'}, 403
            
        image_id = request.args.get('image_id')
        if not image_id:
            return {'message': 'image_id parameter is required'}, 400
            
        # Find the image
        image = ListingImage.query.filter_by(
            id=image_id,
            listing_id=listing_id
        ).first()
        
        if not image:
            return {'message': 'Image not found'}, 404
            
        # Reset all primary flags
        ListingImage.query.filter_by(listing_id=listing_id).update({'is_primary': False})
        
        # Set the selected image as primary
        image.is_primary = True
        listing.updated_at = datetime.utcnow()
        db.session.commit()
        
        return {'message': 'Primary image updated successfully'}, 200
    
    @jwt_required()
    @ns.param('image_id', 'ID of the image to delete')
    def delete(self, listing_id):
        ""Delete an image from a listing."""
        user_id = get_jwt_identity()
        listing = Listing.query.get_or_404(listing_id)
        
        # Check ownership
        if listing.user_id != user_id:
            return {'message': 'Not authorized to modify this listing'}, 403
            
        image_id = request.args.get('image_id')
        if not image_id:
            return {'message': 'image_id parameter is required'}, 400
            
        # Find the image
        image = ListingImage.query.filter_by(
            id=image_id,
            listing_id=listing_id
        ).first()
        
        if not image:
            return {'message': 'Image not found'}, 404
            
        # Don't allow deletion if it's the only image
        if len(listing.images) <= 1:
            return {'message': 'Cannot delete the only image of a listing'}, 400
            
        # If it's the primary image, set another one as primary
        if image.is_primary:
            # Find another image to set as primary
            another_image = ListingImage.query.filter(
                ListingImage.listing_id == listing_id,
                ListingImage.id != image_id
            ).first()
            
            if another_image:
                another_image.is_primary = True
        
        # Delete from S3
        try:
            s3_client.delete_object(
                Bucket=current_app.config['S3_BUCKET'],
                Key=image.filename
            )
        except Exception as e:
            current_app.logger.error(f"Failed to delete image from S3: {str(e)}")
        
        # Delete from database
        db.session.delete(image)
        
        # If no images left, set listing back to draft
        if len(listing.images) == 1:  # Current image is not deleted yet
            listing.status = 'draft'
        
        listing.updated_at = datetime.utcnow()
        db.session.commit()
        
        return {'message': 'Image deleted successfully'}, 200

@ns.route('/listings/<int:listing_id>/favorite')
class FavoriteListing(Resource):
    ""Favorite/unfavorite a listing."""
    
    @jwt_required()
    def post(self, listing_id):
        ""Add a listing to favorites."""
        user_id = get_jwt_identity()
        listing = Listing.query.get_or_404(listing_id)
        
        # Check if already favorited
        favorite = Favorite.query.filter_by(
            user_id=user_id,
            listing_id=listing_id
        ).first()
        
        if favorite:
            return {'message': 'Listing already in favorites'}, 200
        
        # Create favorite
        favorite = Favorite(
            user_id=user_id,
            listing_id=listing_id
        )
        
        db.session.add(favorite)
        listing.favorites_count += 1
        db.session.commit()
        
        return {'message': 'Listing added to favorites'}, 201
    
    @jwt_required()
    def delete(self, listing_id):
        ""Remove a listing from favorites."""
        user_id = get_jwt_identity()
        
        # Find and delete favorite
        favorite = Favorite.query.filter_by(
            user_id=user_id,
            listing_id=listing_id
        ).first()
        
        if not favorite:
            return {'message': 'Listing not in favorites'}, 404
        
        db.session.delete(favorite)
        
        # Update favorites count
        listing = Listing.query.get(listing_id)
        if listing and listing.favorites_count > 0:
            listing.favorites_count -= 1
        
        db.session.commit()
        
        return {'message': 'Listing removed from favorites'}, 200

@ns.route('/listings/<int:listing_id>/report', methods=['POST'])
class ReportListing(Resource):
    ""Report a listing."""
    
    @jwt_required()
    @ns.expect(ns.model('ReportData', {
        'reason': fields.String(required=True, description='Reason for reporting'),
        'description': fields.String(required=False, description='Additional details')
    }))
    def post(self, listing_id):
        ""Report a listing."""
        user_id = get_jwt_identity()
        listing = Listing.query.get_or_404(listing_id)
        
        # Check if already reported by this user
        existing_report = Report.query.filter_by(
            reporter_id=user_id,
            listing_id=listing_id
        ).first()
        
        if existing_report:
            return {'message': 'You have already reported this listing'}, 400
        
        data = request.get_json()
        
        # Create report
        report = Report(
            reporter_id=user_id,
            listing_id=listing_id,
            reason=data['reason'],
            description=data.get('description'),
            status='pending'
        )
        
        db.session.add(report)
        db.session.commit()
        
        # TODO: Notify admins about the report
        
        return {'message': 'Listing reported successfully'}, 201

@ns.route('/categories')
class CategoryList(Resource):
    ""Categories endpoint."""
    
    @ns.marshal_list_with(category_model)
    def get(self):
        ""Get all active categories."""
        categories = Category.query.filter_by(is_active=True).all()
        return categories, 200

# Admin-only endpoints for listing management
@ns.route('/admin/listings')
class AdminListingList(Resource):
    ""Admin endpoint for listing management."""
    
    @jwt_required()
    @admin_required
    @ns.expect(search_parser)
    @ns.marshal_list_with(listing_model)
    def get(self):
        ""Get all listings (admin only)."""
        args = search_parser.parse_args()
        query = Listing.query
        
        # Apply filters
        if args.get('query'):
            search = f"%{args['query']}%"
            query = query.filter(
                or_(
                    Listing.title.ilike(search),
                    Listing.description.ilike(search)
                )
            )
            
        if args.get('status'):
            query = query.filter_by(status=args['status'])
        
        # Apply sorting
        if args.get('sort_by') == 'recent':
            query = query.order_by(Listing.created_at.desc())
        elif args.get('sort_by') == 'value_asc':
            query = query.order_by(Listing.value.asc())
        elif args.get('sort_by') == 'value_desc':
            query = query.order_by(Listing.value.desc())
        else:
            query = query.order_by(Listing.created_at.desc())
        
        # Pagination
        page = args['page']
        per_page = min(args['per_page'], 100)  # Max 100 per page
        paginated_listings = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return paginated_listings.items, 200

@ns.route('/admin/listings/<int:listing_id>/status')
class AdminListingStatus(Resource):
    ""Admin endpoint for updating listing status."""
    
    @jwt_required()
    @admin_required
    @ns.expect(ns.model('UpdateListingStatus', {
        'status': fields.String(required=True, description='New status',
                              enum=['active', 'pending', 'completed', 'cancelled', 'banned']),
        'reason': fields.String(required=False, description='Reason for status change')
    }))
    def put(self, listing_id):
        ""Update a listing's status (admin only)."""
        listing = Listing.query.get_or_404(listing_id)
        data = request.get_json()
        
        # Validate status
        if data['status'] not in ['active', 'pending', 'completed', 'cancelled', 'banned']:
            return {'message': 'Invalid status'}, 400
        
        # Update status
        old_status = listing.status
        listing.status = data['status']
        listing.updated_at = datetime.utcnow()
        
        # If banning, record the reason
        if data['status'] == 'banned':
            listing.ban_reason = data.get('reason')
            listing.banned_at = datetime.utcnow()
            listing.banned_by = get_jwt_identity()
        
        db.session.commit()
        
        # TODO: Notify the listing owner about the status change
        
        return {'message': f'Listing status updated to {data["status"]}'}, 200
