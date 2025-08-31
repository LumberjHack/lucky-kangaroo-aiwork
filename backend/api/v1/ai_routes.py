"""
AI routes for the Lucky Kangaroo API v1.
Handles AI-powered features like recommendations and content moderation.
"""

from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restx import Resource, fields, reqparse, Namespace
import openai
import os

from ...extensions import db, limiter
from ...models.user import User, UserPreferences
from ...models.listing import Listing, Favorite, ViewHistory
from ...models.chat import ChatMessage
from ...utils.decorators import validate_json

# Create AI namespace
ns = Namespace('ai', description='AI-powered features')

# Request parsers
recommend_parser = reqparse.RequestParser()
recommend_parser.add_argument('limit', type=int, default=10, help='Number of recommendations to return')

moderate_parser = reqparse.RequestParser()
moderate_parser.add_argument('content', type=str, required=True, help='Content to moderate')
moderate_parser.add_argument('content_type', type=str, required=True, 
                           choices=['listing', 'message', 'profile'],
                           help='Type of content being moderated')

# Response models
recommendation_model = ns.model('Recommendation', {
    'id': fields.Integer(description='Listing ID'),
    'title': fields.String,
    'description': fields.String,
    'price': fields.Float,
    'currency': fields.String,
    'image': fields.String(description='Primary image URL'),
    'score': fields.Float(description='Recommendation score (0-1)')
})

moderation_result_model = ns.model('ModerationResult', {
    'is_approved': fields.Boolean,
    'reason': fields.String,
    'flags': fields.List(fields.String, description='Content policy violations')
})

# Initialize OpenAI client
openai.api_key = os.getenv('OPENAI_API_KEY')

@ns.route('/recommendations')
class AIRecommendations(Resource):
    ""AI-powered recommendations endpoint."""
    
    @jwt_required()
    @ns.expect(recommend_parser)
    @ns.marshal_list_with(recommendation_model)
    @limiter.limit("100/day;10/minute")
    def get(self):
        ""Get personalized listing recommendations."""
        user_id = get_jwt_identity()
        args = recommend_parser.parse_args()
        limit = min(args['limit'], 50)  # Max 50 recommendations
        
        # Get user preferences
        preferences = UserPreferences.query.filter_by(user_id=user_id).first()
        
        # Get user's favorite categories
        favorite_categories = db.session.query(
            Listing.category_id,
            db.func.count(Listing.category_id).label('count')
        ).join(
            Favorite, Favorite.listing_id == Listing.id
        ).filter(
            Favorite.user_id == user_id
        ).group_by(
            Listing.category_id
        ).order_by(
            db.desc('count')
        ).limit(3).all()
        
        # Get user's viewed items
        viewed_items = ViewHistory.query.filter_by(
            user_id=user_id
        ).order_by(
            ViewHistory.viewed_at.desc()
        ).limit(10).all()
        
        # Build base query
        query = Listing.query.filter(
            Listing.status == 'active',
            Listing.user_id != user_id  # Don't recommend own listings
        )
        
        # Filter by favorite categories if available
        if favorite_categories:
            category_ids = [cat[0] for cat in favorite_categories]
            query = query.filter(Listing.category_id.in_(category_ids))
        
        # Exclude already viewed items
        if viewed_items:
            viewed_ids = [item.listing_id for item in viewed_items]
            query = query.filter(~Listing.id.in_(viewed_ids))
        
        # Order by relevance (simplified for example)
        query = query.order_by(
            Listing.created_at.desc()
        ).limit(limit)
        
        # Format results with dummy scores
        results = []
        for listing in query.all():
            results.append({
                'id': listing.id,
                'title': listing.title,
                'description': listing.description,
                'price': float(listing.price) if listing.price else None,
                'currency': listing.currency,
                'image': listing.images[0].url if listing.images else None,
                'score': 0.8  # Dummy score
            })
        
        return results, 200

@ns.route('/moderate', methods=['POST'])
class AIModeration(Resource):
    ""AI content moderation endpoint."""
    
    @jwt_required()
    @ns.expect(moderate_parser)
    @ns.marshal_with(moderation_result_model)
    @limiter.limit("1000/day;100/minute")
    def post(self):
        ""Check if content violates community guidelines."""
        args = moderate_parser.parse_args()
        content = args['content']
        content_type = args['content_type']
        
        # Simple keyword-based moderation (in production, use a proper ML model or API)
        banned_phrases = [
            # Offensive language
            'hate speech', 'racist', 'sexist', 'homophobic',
            # Scams
            'free money', 'get rich quick', 'work from home',
            # Contact info
            '@gmail.com', '@yahoo.com', '@hotmail.com', 'phone number',
            # External links
            'http://', 'https://', 'www.', '.com'
        ]
        
        flags = []
        for phrase in banned_phrases:
            if phrase.lower() in content.lower():
                flags.append(f"Contains '{phrase}'")
        
        # Check content length
        if content_type == 'listing' and len(content) > 2000:
            flags.append("Content too long")
        elif content_type == 'message' and len(content) > 500:
            flags.append("Message too long")
        
        # Check for excessive capitalization
        if len([c for c in content if c.isupper()]) / max(1, len(content)) > 0.5:
            flags.append("Excessive capitalization")
        
        # Check for repeated characters
        if any(3 * c in content for c in set(content) if c.isalnum()):
            flags.append("Repeated characters detected")
        
        # Make decision
        is_approved = len(flags) == 0
        reason = "Content approved" if is_approved else "Content requires review"
        
        return {
            'is_approved': is_approved,
            'reason': reason,
            'flags': flags
        }, 200

@ns.route('/generate-title')
class AITitleGenerator(Resource):
    ""AI-powered title generator."""
    
    @jwt_required()
    @ns.doc(params={
        'description': 'Listing description',
        'category': 'Category name',
        'price': 'Listing price (optional)'
    })
    @limiter.limit("50/day;10/minute")
    def get(self):
        ""Generate a title for a listing."""
        description = request.args.get('description', '').strip()
        category = request.args.get('category', '').strip()
        price = request.args.get('price', '').strip()
        
        if not description:
            return {'message': 'Description is required'}, 400
        
        # In production, call OpenAI API or another AI service
        prompt = f"Generate a concise, engaging title for a {category} listing. "
        if price:
            prompt += f"Price: {price}. "
        prompt += f"Description: {description[:500]}"
        
        try:
            # Mock response - in production, use actual API call
            # response = openai.ChatCompletion.create(
            #     model="gpt-3.5-turbo",
            #     messages=[{"role": "user", "content": prompt}],
            #     max_tokens=60,
            #     temperature=0.7
            # )
            # title = response.choices[0].message.content.strip('"\'')
            
            # Mock response for demo
            title = f"{category.capitalize()}: {description[:40]}..."
            if len(title) > 60:
                title = title[:57] + "..."
                
            return {'title': title}, 200
            
        except Exception as e:
            return {'message': f'Error generating title: {str(e)}'}, 500

@ns.route('/chat-suggestions')
class AIChatSuggestions(Resource):
    ""AI-powered chat suggestions."""
    
    @jwt_required()
    @ns.doc(params={
        'room_id': 'Chat room ID',
        'message': 'Partial message (optional)'
    })
    @limiter.limit("100/day;20/minute")
    def get(self):
        ""Get AI-suggested responses for a chat."""
        room_id = request.args.get('room_id')
        message = request.args.get('message', '').strip()
        user_id = get_jwt_identity()
        
        if not room_id:
            return {'message': 'Room ID is required'}, 400
        
        # Verify user has access to this chat room
        participant = db.session.query(ChatParticipant).filter_by(
            room_id=room_id,
            user_id=user_id,
            status='active'
        ).first()
        
        if not participant:
            return {'message': 'Access denied'}, 403
        
        # Get recent messages for context
        recent_messages = ChatMessage.query.filter_by(
            room_id=room_id
        ).order_by(
            ChatMessage.created_at.desc()
        ).limit(5).all()
        
        # In production, use AI to generate suggestions
        suggestions = []
        
        if message:
            # Generate completions for the partial message
            suggestions.extend([
                f"{message}?",
                f"{message}!",
                f"I agree, {message.lower()}",
                f"Can you tell me more about {message}?",
                f"Thanks for sharing about {message}"
            ])
        else:
            # Generic suggestions
            suggestions = [
                "Hi there!",
                "How are you?",
                "Is this still available?",
                "Can you send more photos?",
                "What's your best price?"
            ]
        
        return {'suggestions': suggestions[:5]}, 200
