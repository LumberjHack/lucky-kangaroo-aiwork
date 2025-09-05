"""
Blueprint IA pour Lucky Kangaroo
Services d'intelligence artificielle
"""

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from marshmallow import Schema, fields, validate, ValidationError
from werkzeug.utils import secure_filename
import os
import uuid
from datetime import datetime

from app import db
from app.models.user import User
from app.models.listing import Listing, ListingStatus
from app.models.ai_analysis import AIAnalysis, AnalysisType, AnalysisStatus, ObjectDetection, ValueEstimation

# Créer le blueprint
ai_bp = Blueprint('ai', __name__)

# Limiter de taux
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["50 per hour"]
)

# Schémas de validation
class AnalyzeImageSchema(Schema):
    listing_id = fields.UUID(required=True)
    analysis_type = fields.Str(required=True, validate=validate.OneOf(['object_detection', 'value_estimation', 'condition_analysis']))

class AnalyzeTextSchema(Schema):
    text = fields.Str(required=True, validate=validate.Length(min=10, max=2000))
    analysis_type = fields.Str(required=True, validate=validate.OneOf(['content_moderation', 'sentiment_analysis', 'category_classification']))

# Instancier les schémas
analyze_image_schema = AnalyzeImageSchema()
analyze_text_schema = AnalyzeTextSchema()

@ai_bp.route('/analyze/image', methods=['POST'])
@jwt_required()
@limiter.limit("10 per hour")
def analyze_image():
    """Analyser une image avec l'IA"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'Utilisateur non trouvé'}), 404
        
        # Valider les données
        data = analyze_image_schema.load(request.json)
        
        # Vérifier que l'annonce existe et appartient à l'utilisateur
        listing = Listing.query.get(str(data['listing_id']))
        if not listing:
            return jsonify({'error': 'Annonce non trouvée'}), 404
        
        if listing.user_id != current_user_id:
            return jsonify({'error': 'Non autorisé'}), 403
        
        # Vérifier qu'il y a des images
        if not listing.images:
            return jsonify({'error': 'Aucune image trouvée'}), 400
        
        # Créer l'analyse
        analysis = AIAnalysis(
            listing_id=listing.id,
            user_id=user.id,
            analysis_type=data['analysis_type'],
            input_data={
                'listing_id': str(listing.id),
                'image_count': len(listing.images)
            },
            input_files=[img.file_path for img in listing.images]
        )
        
        db.session.add(analysis)
        db.session.commit()
        
        # Démarrer l'analyse (simulation)
        analysis.start_processing()
        
        # Simuler l'analyse
        if data['analysis_type'] == 'object_detection':
            results = simulate_object_detection(listing.images[0])
        elif data['analysis_type'] == 'value_estimation':
            results = simulate_value_estimation(listing)
        elif data['analysis_type'] == 'condition_analysis':
            results = simulate_condition_analysis(listing.images[0])
        else:
            results = {}
        
        # Marquer comme terminé
        analysis.complete(
            results=results,
            confidence_score=0.85,
            processing_time=2.5
        )
        
        return jsonify({
            'message': 'Analyse d\'image terminée',
            'analysis': analysis.to_dict(include_private=True)
        }), 200
        
    except ValidationError as e:
        return jsonify({'error': 'Données invalides', 'details': e.messages}), 400
    except Exception as e:
        current_app.logger.error(f"Erreur lors de l'analyse d'image: {str(e)}")
        return jsonify({'error': 'Erreur interne du serveur'}), 500

@ai_bp.route('/analyze/text', methods=['POST'])
@jwt_required()
@limiter.limit("20 per hour")
def analyze_text():
    """Analyser un texte avec l'IA"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'Utilisateur non trouvé'}), 404
        
        # Valider les données
        data = analyze_text_schema.load(request.json)
        
        # Créer l'analyse
        analysis = AIAnalysis(
            user_id=user.id,
            analysis_type=data['analysis_type'],
            input_data={
                'text': data['text'],
                'text_length': len(data['text'])
            }
        )
        
        db.session.add(analysis)
        db.session.commit()
        
        # Démarrer l'analyse
        analysis.start_processing()
        
        # Simuler l'analyse
        if data['analysis_type'] == 'content_moderation':
            results = simulate_content_moderation(data['text'])
        elif data['analysis_type'] == 'sentiment_analysis':
            results = simulate_sentiment_analysis(data['text'])
        elif data['analysis_type'] == 'category_classification':
            results = simulate_category_classification(data['text'])
        else:
            results = {}
        
        # Marquer comme terminé
        analysis.complete(
            results=results,
            confidence_score=0.90,
            processing_time=1.2
        )
        
        return jsonify({
            'message': 'Analyse de texte terminée',
            'analysis': analysis.to_dict(include_private=True)
        }), 200
        
    except ValidationError as e:
        return jsonify({'error': 'Données invalides', 'details': e.messages}), 400
    except Exception as e:
        current_app.logger.error(f"Erreur lors de l'analyse de texte: {str(e)}")
        return jsonify({'error': 'Erreur interne du serveur'}), 500

@ai_bp.route('/upload', methods=['POST'])
@jwt_required()
@limiter.limit("10 per hour")
def upload_for_analysis():
    """Uploader un fichier pour analyse IA"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'Utilisateur non trouvé'}), 404
        
        if 'file' not in request.files:
            return jsonify({'error': 'Aucun fichier fourni'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'Aucun fichier sélectionné'}), 400
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # Générer un nom unique
            unique_filename = f"{user.id}_{uuid.uuid4().hex}_{filename}"
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'ai_analysis', unique_filename)
            
            # Créer le dossier s'il n'existe pas
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Sauvegarder le fichier
            file.save(file_path)
            
            # Créer l'analyse
            analysis = AIAnalysis(
                user_id=user.id,
                analysis_type='object_detection',
                input_data={
                    'filename': filename,
                    'file_size': os.path.getsize(file_path),
                    'mime_type': file.content_type
                },
                input_files=[f"/uploads/ai_analysis/{unique_filename}"]
            )
            
            db.session.add(analysis)
            db.session.commit()
            
            return jsonify({
                'message': 'Fichier uploadé avec succès',
                'analysis_id': str(analysis.id),
                'file_path': f"/uploads/ai_analysis/{unique_filename}"
            }), 200
        else:
            return jsonify({'error': 'Type de fichier non autorisé'}), 400
        
    except Exception as e:
        current_app.logger.error(f"Erreur lors de l'upload: {str(e)}")
        return jsonify({'error': 'Erreur interne du serveur'}), 500

@ai_bp.route('/analyses', methods=['GET'])
@jwt_required()
def get_analyses():
    """Obtenir les analyses de l'utilisateur"""
    try:
        current_user_id = get_jwt_identity()
        
        # Paramètres de pagination
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        
        # Filtres
        analysis_type = request.args.get('analysis_type')
        status = request.args.get('status')
        sort_by = request.args.get('sort_by', 'created_at')
        sort_order = request.args.get('sort_order', 'desc')
        
        # Construire la requête
        query = AIAnalysis.query.filter_by(user_id=current_user_id)
        
        # Appliquer les filtres
        if analysis_type:
            query = query.filter_by(analysis_type=analysis_type)
        if status:
            query = query.filter_by(status=status)
        
        # Tri
        if sort_by == 'analysis_type':
            if sort_order == 'asc':
                query = query.order_by(AIAnalysis.analysis_type.asc())
            else:
                query = query.order_by(AIAnalysis.analysis_type.desc())
        elif sort_by == 'confidence_score':
            if sort_order == 'asc':
                query = query.order_by(AIAnalysis.confidence_score.asc())
            else:
                query = query.order_by(AIAnalysis.confidence_score.desc())
        else:  # created_at
            if sort_order == 'asc':
                query = query.order_by(AIAnalysis.created_at.asc())
            else:
                query = query.order_by(AIAnalysis.created_at.desc())
        
        # Pagination
        pagination = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'analyses': [analysis.to_dict(include_private=True) for analysis in pagination.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erreur lors de la récupération des analyses: {str(e)}")
        return jsonify({'error': 'Erreur interne du serveur'}), 500

@ai_bp.route('/analyses/<analysis_id>', methods=['GET'])
@jwt_required()
def get_analysis(analysis_id):
    """Obtenir une analyse spécifique"""
    try:
        current_user_id = get_jwt_identity()
        analysis = AIAnalysis.query.get(analysis_id)
        
        if not analysis:
            return jsonify({'error': 'Analyse non trouvée'}), 404
        
        if analysis.user_id != current_user_id:
            return jsonify({'error': 'Non autorisé'}), 403
        
        return jsonify({
            'analysis': analysis.to_dict(include_private=True)
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erreur lors de la récupération de l'analyse: {str(e)}")
        return jsonify({'error': 'Erreur interne du serveur'}), 500

@ai_bp.route('/suggestions/listing', methods=['POST'])
@jwt_required()
@limiter.limit("20 per hour")
def get_listing_suggestions():
    """Obtenir des suggestions d'amélioration pour une annonce"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'Utilisateur non trouvé'}), 404
        
        listing_id = request.json.get('listing_id')
        if not listing_id:
            return jsonify({'error': 'ID d\'annonce requis'}), 400
        
        listing = Listing.query.get(listing_id)
        if not listing:
            return jsonify({'error': 'Annonce non trouvée'}), 404
        
        if listing.user_id != current_user_id:
            return jsonify({'error': 'Non autorisé'}), 403
        
        # Générer des suggestions
        suggestions = generate_listing_suggestions(listing)
        
        return jsonify({
            'suggestions': suggestions
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erreur lors de la génération des suggestions: {str(e)}")
        return jsonify({'error': 'Erreur interne du serveur'}), 500

@ai_bp.route('/chat', methods=['POST'])
@jwt_required()
@limiter.limit("30 per hour")
def chat_with_ai():
    """Chatter avec l'assistant IA"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'Utilisateur non trouvé'}), 404
        
        message = request.json.get('message')
        if not message:
            return jsonify({'error': 'Message requis'}), 400
        
        # Simuler une réponse de l'IA
        response = simulate_ai_chat(message, user)
        
        return jsonify({
            'response': response,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erreur lors du chat IA: {str(e)}")
        return jsonify({'error': 'Erreur interne du serveur'}), 500

# Fonctions utilitaires
def allowed_file(filename):
    """Vérifier si le type de fichier est autorisé"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def simulate_object_detection(image):
    """Simuler la détection d'objets"""
    return {
        'objects': [
            {
                'name': 'smartphone',
                'confidence': 0.95,
                'bounding_box': {'x': 100, 'y': 50, 'width': 200, 'height': 300}
            },
            {
                'name': 'table',
                'confidence': 0.87,
                'bounding_box': {'x': 0, 'y': 250, 'width': 400, 'height': 150}
            }
        ],
        'tags': ['smartphone', 'mobile', 'technology', 'electronics'],
        'brand_detected': 'Apple',
        'model_detected': 'iPhone 13'
    }

def simulate_value_estimation(listing):
    """Simuler l'estimation de valeur"""
    return {
        'estimated_value': 800.0,
        'min_value': 700.0,
        'max_value': 900.0,
        'confidence': 0.85,
        'factors': {
            'condition': 0.9,
            'brand': 0.95,
            'market_demand': 0.8,
            'rarity': 0.7
        },
        'market_comparison': [
            {'price': 750, 'condition': 'good', 'source': 'marketplace1'},
            {'price': 850, 'condition': 'excellent', 'source': 'marketplace2'}
        ]
    }

def simulate_condition_analysis(image):
    """Simuler l'analyse de l'état"""
    return {
        'condition': 'very_good',
        'confidence': 0.88,
        'issues_detected': [
            {'type': 'scratch', 'severity': 'minor', 'location': 'back'},
            {'type': 'wear', 'severity': 'minor', 'location': 'edges'}
        ],
        'overall_score': 8.5
    }

def simulate_content_moderation(text):
    """Simuler la modération de contenu"""
    return {
        'is_appropriate': True,
        'confidence': 0.95,
        'issues': [],
        'sentiment': 'positive',
        'language': 'french'
    }

def simulate_sentiment_analysis(text):
    """Simuler l'analyse de sentiment"""
    return {
        'sentiment': 'positive',
        'confidence': 0.87,
        'scores': {
            'positive': 0.75,
            'neutral': 0.20,
            'negative': 0.05
        },
        'emotions': ['satisfaction', 'happiness']
    }

def simulate_category_classification(text):
    """Simuler la classification de catégorie"""
    return {
        'category': 'Electronics',
        'subcategory': 'Smartphones',
        'confidence': 0.92,
        'alternative_categories': [
            {'name': 'Technology', 'confidence': 0.85},
            {'name': 'Mobile Devices', 'confidence': 0.78}
        ]
    }

def generate_listing_suggestions(listing):
    """Générer des suggestions d'amélioration pour une annonce"""
    suggestions = []
    
    # Vérifier la longueur du titre
    if len(listing.title) < 20:
        suggestions.append({
            'type': 'title',
            'message': 'Le titre pourrait être plus descriptif',
            'suggestion': 'Ajoutez plus de détails sur l\'objet'
        })
    
    # Vérifier la description
    if len(listing.description) < 100:
        suggestions.append({
            'type': 'description',
            'message': 'La description pourrait être plus détaillée',
            'suggestion': 'Décrivez l\'état, l\'historique et les caractéristiques'
        })
    
    # Vérifier les images
    if len(listing.images) < 3:
        suggestions.append({
            'type': 'images',
            'message': 'Ajoutez plus de photos',
            'suggestion': 'Montrez l\'objet sous différents angles'
        })
    
    # Vérifier le prix
    if not listing.estimated_value:
        suggestions.append({
            'type': 'price',
            'message': 'Ajoutez une estimation de prix',
            'suggestion': 'Cela aide les utilisateurs à évaluer l\'échange'
        })
    
    return suggestions

def simulate_ai_chat(message, user):
    """Simuler une conversation avec l'IA"""
    responses = {
        'bonjour': f"Bonjour {user.first_name} ! Comment puis-je vous aider aujourd'hui ?",
        'aide': "Je peux vous aider avec vos annonces, les échanges, ou répondre à vos questions sur Lucky Kangaroo.",
        'prix': "Pour estimer le prix d'un objet, je peux analyser vos photos et vous donner une estimation basée sur le marché.",
        'échange': "Les échanges sur Lucky Kangaroo peuvent être directs (A ↔ B) ou en chaîne (A → B → C → A).",
        'sécurité': "Nous utilisons un système de notation de confiance et des évaluations mutuelles pour assurer la sécurité."
    }
    
    message_lower = message.lower()
    for key, response in responses.items():
        if key in message_lower:
            return response
    
    return "Je comprends votre question. Pouvez-vous être plus spécifique ? Je peux vous aider avec les annonces, les échanges, ou les fonctionnalités de la plateforme."
