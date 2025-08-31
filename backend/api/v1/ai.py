"""
AI-powered features for the application.
"""
import os
import openai
from flask import request, jsonify, current_app
from flask_restx import Resource, Namespace, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from ...models import db, User, Listing, ChatMessage
from ...utils import rate_limited

api = Namespace('ai', description='AI-powered features')

# Initialize OpenAI client
openai.api_key = os.getenv('OPENAI_API_KEY')

# Request models
chat_completion_model = api.model('ChatCompletion', {
    'message': fields.String(required=True, description='User message'),
    'conversation_id': fields.String(description='Conversation ID for context'),
    'context': fields.Raw(description='Additional context for the AI')
})

content_moderation_model = api.model('ContentModeration', {
    'text': fields.String(required=True, description='Text to moderate'),
    'content_type': fields.String(required=True, enum=['listing', 'message', 'profile'])
})

listing_suggestion_model = api.model('ListingSuggestion', {
    'title': fields.String(description='Current listing title'),
    'description': fields.String(description='Current listing description'),
    'category': fields.String(description='Listing category'),
    'price': fields.Float(description='Listing price')
})

@api.route('/chat')
class AIChat(Resource):
    @jwt_required()
    @api.expect(chat_completion_model)
    @rate_limited('ai_chat', limit=30, period=300)  # 30 requests per 5 minutes
    def post(self):
        ""Chat with the AI assistant."""
        data = request.get_json()
        user_id = get_jwt_identity()
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant for the Lucky Kangaroo marketplace. "
                                                "Help users with their questions about buying, selling, and trading items."},
                    {"role": "user", "content": data['message']}
                ]
            )
            
            # Save the conversation to the database
            if data.get('conversation_id'):
                conversation = ChatMessage.query.get(data['conversation_id'])
                if conversation and conversation.user_id == user_id:
                    # Update existing conversation
                    pass  # Implementation depends on your chat model
            
            return {
                'response': response.choices[0].message['content'],
                'conversation_id': data.get('conversation_id')
            }
            
        except Exception as e:
            current_app.logger.error(f"AI chat error: {str(e)}")
            return {'error': 'Failed to process your request'}, 500

@api.route('/moderate', methods=['POST'])
class ContentModeration(Resource):
    @jwt_required()
    @api.expect(content_moderation_model)
    def post(self):
        ""Moderate content using AI."""
        data = request.get_json()
        
        try:
            # Use OpenAI's moderation endpoint
            response = openai.Moderation.create(input=data['text'])
            
            # Process results
            result = response["results"][0]
            
            return {
                'flagged': result['flagged'],
                'categories': result['categories'],
                'category_scores': result['category_scores'],
                'moderation_id': response["id"]
            }
            
        except Exception as e:
            current_app.logger.error(f"Content moderation error: {str(e)}")
            return {'error': 'Failed to moderate content'}, 500

@api.route('/suggest-listing')
class ListingSuggestion(Resource):
    @jwt_required()
    @api.expect(listing_suggestion_model)
    @rate_limited('listing_suggestions', limit=20, period=3600)  # 20 requests per hour
    def post(self):
        ""Get AI suggestions for improving a listing."""
        data = request.get_json()
        
        try:
            prompt = f"""Analyze this marketplace listing and provide suggestions for improvement.
            
            Current Title: {data.get('title', '')}
            Current Description: {data.get('description', '')}
            Category: {data.get('category', 'Not specified')}
            Price: {data.get('price', 'Not specified')}
            
            Please provide:
            1. A more engaging title
            2. An improved description
            3. Relevant tags
            4. Pricing suggestions if applicable
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a marketplace optimization expert. Provide clear, actionable suggestions."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            return {'suggestions': response.choices[0].message['content']}
            
        except Exception as e:
            current_app.logger.error(f"Listing suggestion error: {str(e)}")
            return {'error': 'Failed to generate suggestions'}, 500

@api.route('/recommendations')
class Recommendations(Resource):
    @jwt_required()
    @rate_limited('recommendations', limit=10, period=60)  # 10 requests per minute
    def get(self):
        ""Get personalized listing recommendations."""
        user_id = get_jwt_identity()
        
        # In a real implementation, this would use collaborative filtering or other ML techniques
        # For now, we'll return popular listings
        popular_listings = Listing.query.filter_by(
            is_active=True
        ).order_by(
            Listing.view_count.desc()
        ).limit(10).all()
        
        return jsonify([{
            'id': listing.id,
            'title': listing.title,
            'price': float(listing.price) if listing.price else None,
            'currency': listing.currency,
            'image_url': listing.primary_image_url,
            'location': listing.location
        } for listing in popular_listings])

# Export the blueprint
ai_bp = api
