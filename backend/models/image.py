"""
Lucky Kangaroo - Modèle Image Complet
Modèle pour la gestion des images et photos
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from enum import Enum
import uuid
import os

db = SQLAlchemy()

class ImageType(Enum):
    """Types d'images"""
    PROFILE = "profile"
    LISTING = "listing"
    CHAT = "chat"
    SYSTEM = "system"

class ImageStatus(Enum):
    """Statuts d'images"""
    UPLOADING = "uploading"
    PROCESSING = "processing"
    ACTIVE = "active"
    DELETED = "deleted"
    FAILED = "failed"

class Image(db.Model):
    """Modèle pour les images et photos"""
    
    __tablename__ = 'images'
    
    # Identifiants
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    listing_id = db.Column(db.Integer, db.ForeignKey('listings.id'), nullable=True, index=True)
    
    # Informations de base
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=True)
    file_path = db.Column(db.String(500), nullable=False)
    url = db.Column(db.String(500), nullable=False)
    
    # Métadonnées techniques
    file_size = db.Column(db.Integer, nullable=False)  # Taille en bytes
    mime_type = db.Column(db.String(100), nullable=False)
    width = db.Column(db.Integer, nullable=True)
    height = db.Column(db.Integer, nullable=True)
    format = db.Column(db.String(20), nullable=True)  # JPEG, PNG, WebP, etc.
    
    # Type et statut
    image_type = db.Column(db.Enum(ImageType), nullable=False, default=ImageType.LISTING)
    status = db.Column(db.Enum(ImageStatus), nullable=False, default=ImageStatus.UPLOADING)
    is_main = db.Column(db.Boolean, nullable=False, default=False)  # Image principale pour une annonce
    
    # Versions et optimisations
    thumbnail_url = db.Column(db.String(500), nullable=True)
    medium_url = db.Column(db.String(500), nullable=True)
    large_url = db.Column(db.String(500), nullable=True)
    webp_url = db.Column(db.String(500), nullable=True)  # Version WebP optimisée
    
    # Analyse IA
    ai_analyzed = db.Column(db.Boolean, nullable=False, default=False)
    ai_tags = db.Column(db.Text, nullable=True)  # Tags générés par l'IA (JSON)
    ai_objects = db.Column(db.Text, nullable=True)  # Objets détectés (JSON)
    ai_confidence = db.Column(db.Float, nullable=True)  # Confiance de l'analyse
    ai_category = db.Column(db.String(100), nullable=True)  # Catégorie suggérée par l'IA
    ai_condition = db.Column(db.String(50), nullable=True)  # Condition évaluée par l'IA
    ai_value_estimate = db.Column(db.Float, nullable=True)  # Estimation de valeur par l'IA
    
    # Métadonnées EXIF
    exif_data = db.Column(db.Text, nullable=True)  # Données EXIF (JSON)
    camera_make = db.Column(db.String(100), nullable=True)
    camera_model = db.Column(db.String(100), nullable=True)
    taken_at = db.Column(db.DateTime, nullable=True)  # Date de prise de vue
    
    # Géolocalisation (si disponible dans EXIF)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    
    # Modération
    is_moderated = db.Column(db.Boolean, nullable=False, default=False)
    moderation_status = db.Column(db.String(50), nullable=True)  # approved, rejected, pending
    moderation_reason = db.Column(db.Text, nullable=True)
    moderated_at = db.Column(db.DateTime, nullable=True)
    moderated_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    # Statistiques
    view_count = db.Column(db.Integer, nullable=False, default=0)
    download_count = db.Column(db.Integer, nullable=False, default=0)
    
    # Timestamps
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    processed_at = db.Column(db.DateTime, nullable=True)
    
    def __init__(self, user_id, filename, file_path, url, file_size, mime_type, **kwargs):
        self.user_id = user_id
        self.filename = filename
        self.file_path = file_path
        self.url = url
        self.file_size = file_size
        self.mime_type = mime_type
        
        # Définir les autres attributs depuis kwargs
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def mark_as_processed(self):
        """Marque l'image comme traitée"""
        self.status = ImageStatus.ACTIVE
        self.processed_at = datetime.utcnow()
    
    def mark_as_failed(self, reason=None):
        """Marque l'image comme échouée"""
        self.status = ImageStatus.FAILED
        if reason:
            self.moderation_reason = reason
    
    def set_as_main(self):
        """Définit cette image comme image principale"""
        if self.listing_id:
            # Retirer le statut principal des autres images de cette annonce
            Image.query.filter(
                Image.listing_id == self.listing_id,
                Image.id != self.id
            ).update({'is_main': False})
            
        self.is_main = True
    
    def get_file_size_human(self):
        """Retourne la taille du fichier en format lisible"""
        size = self.file_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
    
    def get_dimensions_string(self):
        """Retourne les dimensions sous forme de chaîne"""
        if self.width and self.height:
            return f"{self.width}x{self.height}"
        return "Dimensions inconnues"
    
    def get_aspect_ratio(self):
        """Calcule le ratio d'aspect"""
        if self.width and self.height and self.height > 0:
            return round(self.width / self.height, 2)
        return None
    
    def is_landscape(self):
        """Vérifie si l'image est en format paysage"""
        return self.width and self.height and self.width > self.height
    
    def is_portrait(self):
        """Vérifie si l'image est en format portrait"""
        return self.width and self.height and self.height > self.width
    
    def is_square(self):
        """Vérifie si l'image est carrée"""
        return self.width and self.height and self.width == self.height
    
    def get_ai_tags_list(self):
        """Retourne les tags IA sous forme de liste"""
        if self.ai_tags:
            import json
            try:
                return json.loads(self.ai_tags)
            except:
                return []
        return []
    
    def set_ai_tags(self, tags_list):
        """Définit les tags IA depuis une liste"""
        import json
        self.ai_tags = json.dumps(tags_list) if tags_list else None
    
    def get_ai_objects_list(self):
        """Retourne les objets détectés sous forme de liste"""
        if self.ai_objects:
            import json
            try:
                return json.loads(self.ai_objects)
            except:
                return []
        return []
    
    def set_ai_objects(self, objects_list):
        """Définit les objets détectés depuis une liste"""
        import json
        self.ai_objects = json.dumps(objects_list) if objects_list else None
    
    def get_exif_data_dict(self):
        """Retourne les données EXIF sous forme de dictionnaire"""
        if self.exif_data:
            import json
            try:
                return json.loads(self.exif_data)
            except:
                return {}
        return {}
    
    def set_exif_data(self, exif_dict):
        """Définit les données EXIF depuis un dictionnaire"""
        import json
        self.exif_data = json.dumps(exif_dict) if exif_dict else None
    
    def get_best_url(self, size='original'):
        """Retourne la meilleure URL selon la taille demandée"""
        size_mapping = {
            'thumbnail': self.thumbnail_url,
            'medium': self.medium_url,
            'large': self.large_url,
            'webp': self.webp_url,
            'original': self.url
        }
        
        return size_mapping.get(size) or self.url
    
    def increment_view(self):
        """Incrémente le compteur de vues"""
        self.view_count += 1
    
    def increment_download(self):
        """Incrémente le compteur de téléchargements"""
        self.download_count += 1
    
    def delete_files(self):
        """Supprime les fichiers physiques"""
        files_to_delete = [
            self.file_path,
            self.thumbnail_url,
            self.medium_url,
            self.large_url,
            self.webp_url
        ]
        
        for file_path in files_to_delete:
            if file_path and os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except OSError:
                    pass  # Ignorer les erreurs de suppression
    
    def soft_delete(self):
        """Suppression logique de l'image"""
        self.status = ImageStatus.DELETED
        self.updated_at = datetime.utcnow()
    
    def to_dict(self, include_ai=False, include_exif=False, include_stats=False):
        """Convertit l'image en dictionnaire"""
        data = {
            'id': self.id,
            'uuid': self.uuid,
            'filename': self.filename,
            'original_filename': self.original_filename,
            'url': self.url,
            'thumbnail_url': self.thumbnail_url,
            'medium_url': self.medium_url,
            'large_url': self.large_url,
            'webp_url': self.webp_url,
            'file_size': self.file_size,
            'file_size_human': self.get_file_size_human(),
            'mime_type': self.mime_type,
            'width': self.width,
            'height': self.height,
            'dimensions': self.get_dimensions_string(),
            'aspect_ratio': self.get_aspect_ratio(),
            'format': self.format,
            'image_type': self.image_type.value if self.image_type else None,
            'status': self.status.value if self.status else None,
            'is_main': self.is_main,
            'is_landscape': self.is_landscape(),
            'is_portrait': self.is_portrait(),
            'is_square': self.is_square(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'processed_at': self.processed_at.isoformat() if self.processed_at else None
        }
        
        if include_ai:
            data['ai'] = {
                'analyzed': self.ai_analyzed,
                'tags': self.get_ai_tags_list(),
                'objects': self.get_ai_objects_list(),
                'confidence': self.ai_confidence,
                'category': self.ai_category,
                'condition': self.ai_condition,
                'value_estimate': self.ai_value_estimate
            }
        
        if include_exif:
            data['exif'] = {
                'data': self.get_exif_data_dict(),
                'camera_make': self.camera_make,
                'camera_model': self.camera_model,
                'taken_at': self.taken_at.isoformat() if self.taken_at else None,
                'latitude': self.latitude,
                'longitude': self.longitude
            }
        
        if include_stats:
            data['stats'] = {
                'view_count': self.view_count,
                'download_count': self.download_count
            }
        
        return data
    
    def to_simple_dict(self):
        """Convertit en dictionnaire simplifié pour les listes"""
        return {
            'id': self.id,
            'url': self.url,
            'thumbnail_url': self.thumbnail_url,
            'is_main': self.is_main,
            'width': self.width,
            'height': self.height,
            'file_size': self.file_size
        }
    
    def __repr__(self):
        return f'<Image {self.filename} by User {self.user_id}>'

    @staticmethod
    def get_by_listing(listing_id, include_deleted=False):
        """Récupère toutes les images d'une annonce"""
        query = Image.query.filter(Image.listing_id == listing_id)
        
        if not include_deleted:
            query = query.filter(Image.status != ImageStatus.DELETED)
        
        return query.order_by(Image.is_main.desc(), Image.created_at.asc()).all()
    
    @staticmethod
    def get_main_image(listing_id):
        """Récupère l'image principale d'une annonce"""
        return Image.query.filter(
            Image.listing_id == listing_id,
            Image.is_main == True,
            Image.status == ImageStatus.ACTIVE
        ).first()
    
    @staticmethod
    def get_user_images(user_id, image_type=None, limit=50):
        """Récupère les images d'un utilisateur"""
        query = Image.query.filter(
            Image.user_id == user_id,
            Image.status == ImageStatus.ACTIVE
        )
        
        if image_type:
            query = query.filter(Image.image_type == image_type)
        
        return query.order_by(Image.created_at.desc()).limit(limit).all()
    
    @staticmethod
    def cleanup_orphaned_images():
        """Nettoie les images orphelines (sans annonce associée)"""
        from datetime import timedelta
        
        # Images de plus de 24h sans annonce associée
        cutoff_date = datetime.utcnow() - timedelta(hours=24)
        
        orphaned_images = Image.query.filter(
            Image.listing_id.is_(None),
            Image.image_type == ImageType.LISTING,
            Image.created_at < cutoff_date,
            Image.status != ImageStatus.DELETED
        ).all()
        
        for image in orphaned_images:
            image.soft_delete()
            image.delete_files()
        
        return len(orphaned_images)
    
    @staticmethod
    def get_storage_stats():
        """Retourne les statistiques de stockage"""
        total_images = Image.query.filter(Image.status != ImageStatus.DELETED).count()
        total_size = db.session.query(db.func.sum(Image.file_size)).filter(
            Image.status != ImageStatus.DELETED
        ).scalar() or 0
        
        by_type = db.session.query(
            Image.image_type,
            db.func.count(Image.id),
            db.func.sum(Image.file_size)
        ).filter(
            Image.status != ImageStatus.DELETED
        ).group_by(Image.image_type).all()
        
        return {
            'total_images': total_images,
            'total_size_bytes': total_size,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'by_type': {
                image_type.value: {
                    'count': count,
                    'size_bytes': size or 0,
                    'size_mb': round((size or 0) / (1024 * 1024), 2)
                }
                for image_type, count, size in by_type
            }
        }

