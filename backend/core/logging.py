"""
Lucky Kangaroo - Système de logging centralisé
Configuration et gestion des logs pour l'application
"""

import logging
import logging.config
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from pathlib import Path
import os
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    """Formateur JSON pour les logs structurés"""
    
    def format(self, record):
        log_entry = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Ajouter les données d'exception si présentes
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
        
        # Ajouter les données extra si présentes
        if hasattr(record, 'extra_data'):
            log_entry['extra'] = record.extra_data
        
        return json.dumps(log_entry, ensure_ascii=False)

class ColoredFormatter(logging.Formatter):
    """Formateur coloré pour la console"""
    
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'        # Reset
    }
    
    def format(self, record):
        color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        reset = self.COLORS['RESET']
        
        # Formater le message avec couleur
        record.levelname = f"{color}{record.levelname}{reset}"
        record.name = f"{color}{record.name}{reset}"
        
        return super().format(record)

def setup_logging(app):
    """Configure le système de logging pour l'application"""
    
    # Créer le répertoire de logs s'il n'existe pas
    log_dir = Path(app.config.get('LOG_DIR', 'logs'))
    log_dir.mkdir(exist_ok=True, parents=True)
    
    # Configuration de base
    log_level = app.config.get('LOG_LEVEL', 'INFO')
    log_format = app.config.get('LOG_FORMAT', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Configuration détaillée du logging
    log_config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'default': {
                'format': log_format,
                'datefmt': '%Y-%m-%d %H:%M:%S'
            },
            'json': {
                '()': JSONFormatter
            },
            'colored': {
                '()': ColoredFormatter,
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S'
            },
            'detailed': {
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(lineno)d - %(funcName)s - %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S'
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'colored' if app.config.get('DEBUG', False) else 'default',
                'stream': 'ext://sys.stdout',
                'level': 'DEBUG' if app.config.get('DEBUG', False) else 'INFO'
            },
            'file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'formatter': 'detailed',
                'filename': str(log_dir / 'app.log'),
                'maxBytes': 10 * 1024 * 1024,  # 10MB
                'backupCount': 5,
                'encoding': 'utf8',
                'level': log_level
            },
            'error_file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'formatter': 'json',
                'filename': str(log_dir / 'error.log'),
                'maxBytes': 10 * 1024 * 1024,  # 10MB
                'backupCount': 5,
                'level': 'ERROR',
                'encoding': 'utf8'
            },
            'access_file': {
                'class': 'logging.handlers.TimedRotatingFileHandler',
                'formatter': 'json',
                'filename': str(log_dir / 'access.log'),
                'when': 'midnight',
                'interval': 1,
                'backupCount': 30,
                'encoding': 'utf8',
                'level': 'INFO'
            },
            'security_file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'formatter': 'json',
                'filename': str(log_dir / 'security.log'),
                'maxBytes': 5 * 1024 * 1024,  # 5MB
                'backupCount': 10,
                'encoding': 'utf8',
                'level': 'WARNING'
            }
        },
        'loggers': {
            '': {
                'handlers': ['console', 'file', 'error_file'],
                'level': log_level,
                'propagate': True
            },
            'werkzeug': {
                'handlers': ['console', 'access_file'],
                'level': 'INFO',
                'propagate': False
            },
            'sqlalchemy.engine': {
                'handlers': ['console', 'file'],
                'level': 'WARNING',
                'propagate': False
            },
            'sqlalchemy.pool': {
                'handlers': ['console', 'file'],
                'level': 'WARNING',
                'propagate': False
            },
            'flask_cors': {
                'handlers': ['console', 'file'],
                'level': 'INFO',
                'propagate': False
            },
            'flask_jwt_extended': {
                'handlers': ['console', 'security_file'],
                'level': 'INFO',
                'propagate': False
            },
            'flask_limiter': {
                'handlers': ['console', 'security_file'],
                'level': 'INFO',
                'propagate': False
            },
            'celery': {
                'handlers': ['console', 'file'],
                'level': 'INFO',
                'propagate': False
            },
            'redis': {
                'handlers': ['console', 'file'],
                'level': 'WARNING',
                'propagate': False
            },
            'opensearch': {
                'handlers': ['console', 'file'],
                'level': 'WARNING',
                'propagate': False
            }
        }
    }
    
    try:
        # Appliquer la configuration
        logging.config.dictConfig(log_config)
        
        # Configurer le logger principal de l'application
        app.logger = logging.getLogger('lucky_kangaroo')
        app.logger.setLevel(log_level)
        
        # Log de démarrage
        app.logger.info(f"Lucky Kangaroo - Configuration du logging terminée (niveau: {log_level})")
        app.logger.info(f"Logs disponibles: console, fichier, erreurs, accès, sécurité")
        
    except Exception as e:
        # Fallback en cas d'erreur
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        app.logger = logging.getLogger('lucky_kangaroo')
        app.logger.error(f"Erreur lors de la configuration du logging: {e}")
        app.logger.warning("Utilisation de la configuration de base")

def get_logger(name):
    """Retourne un logger configuré pour le nom donné"""
    return logging.getLogger(name)

def log_security_event(event_type, details, user_id=None, ip_address=None, severity='INFO'):
    """Log un événement de sécurité"""
    logger = logging.getLogger('security')
    
    extra_data = {
        'event_type': event_type,
        'details': details,
        'user_id': user_id,
        'ip_address': ip_address,
        'timestamp': datetime.utcnow().isoformat()
    }
    
    if severity == 'ERROR':
        logger.error(f"Security event: {event_type}", extra={'extra_data': extra_data})
    elif severity == 'WARNING':
        logger.warning(f"Security event: {event_type}", extra={'extra_data': extra_data})
    else:
        logger.info(f"Security event: {event_type}", extra={'extra_data': extra_data})

def log_api_request(method, path, status_code, response_time, user_id=None, ip_address=None):
    """Log une requête API"""
    logger = logging.getLogger('api')
    
    extra_data = {
        'method': method,
        'path': path,
        'status_code': status_code,
        'response_time': response_time,
        'user_id': user_id,
        'ip_address': ip_address,
        'timestamp': datetime.utcnow().isoformat()
    }
    
    if status_code >= 400:
        logger.warning(f"API request: {method} {path} - {status_code}", extra={'extra_data': extra_data})
    else:
        logger.info(f"API request: {method} {path} - {status_code}", extra={'extra_data': extra_data})

def log_database_operation(operation, table, duration, success=True, error=None):
    """Log une opération de base de données"""
    logger = logging.getLogger('database')
    
    extra_data = {
        'operation': operation,
        'table': table,
        'duration': duration,
        'success': success,
        'error': str(error) if error else None,
        'timestamp': datetime.utcnow().isoformat()
    }
    
    if success:
        logger.debug(f"DB operation: {operation} on {table}", extra={'extra_data': extra_data})
    else:
        logger.error(f"DB operation failed: {operation} on {table}", extra={'extra_data': extra_data})
