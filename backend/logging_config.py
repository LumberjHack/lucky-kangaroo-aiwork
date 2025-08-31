"""
Configuration de la journalisation pour l'application Lucky Kangaroo.
"""
import logging
import logging.handlers
from logging.config import dictConfig
from pathlib import Path
from typing import Dict, Any

def configure_logging(app) -> None:
    """
    Configure la journalisation pour l'application.
    
    Args:
        app: L'instance de l'application Flask
    """
    # Créer le répertoire de logs s'il n'existe pas
    log_dir = Path(app.config.get('LOG_DIR', 'logs'))
    log_dir.mkdir(exist_ok=True, parents=True)
    
    # Configuration du format des logs
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    log_level = app.config.get('LOG_LEVEL', 'INFO')
    
    # Configuration du dictionnaire de logging
    log_config: Dict[str, Any] = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'default': {
                'format': log_format,
                'datefmt': '%Y-%m-%d %H:%M:%S',
            },
            'json': {
                '()': 'pythonjsonlogger.jsonlogger.JsonFormatter',
                'format': '%(asctime)s %(name)s %(levelname)s %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S',
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'default',
                'stream': 'ext://sys.stdout',
            },
            'file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'formatter': 'default',
                'filename': str(log_dir / 'app.log'),
                'maxBytes': 10485760,  # 10MB
                'backupCount': 5,
                'encoding': 'utf8',
            },
            'error_file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'formatter': 'json',
                'filename': str(log_dir / 'error.log'),
                'maxBytes': 10485760,  # 10MB
                'backupCount': 5,
                'level': 'ERROR',
                'encoding': 'utf8',
            }
        },
        'loggers': {
            '': {  # root logger
                'handlers': ['console', 'file', 'error_file'],
                'level': log_level,
                'propagate': True,
            },
            'werkzeug': {
                'handlers': ['console', 'file'],
                'level': 'INFO',  # Évite les logs trop verbeux de Werkzeug
                'propagate': False,
            },
            'sqlalchemy.engine': {
                'handlers': ['console', 'file'],
                'level': 'WARNING',  # Réduit la verbosité de SQLAlchemy
                'propagate': False,
            },
        }
    }
    
    # Appliquer la configuration
    dictConfig(log_config)
    
    # Configurer le logger de l'application
    app.logger = logging.getLogger(__name__)
    app.logger.setLevel(log_level)
    
    # Désactiver le logger de requêtes HTTP de Werkzeug en production
    if not app.debug:
        logging.getLogger('werkzeug').setLevel(logging.WARNING)
    
    app.logger.info('Configuration de la journalisation terminée')


def get_logger(name: str = None) -> logging.Logger:
    """
    Obtient un logger configuré.
    
    Args:
        name: Nom du logger (utilise le nom du module appelant si non spécifié)
        
    Returns:
        logging.Logger: Instance de logger configurée
    """
    if name is None:
        import inspect
        name = inspect.currentframe().f_back.f_globals.get('__name__') or 'root'
    return logging.getLogger(name)
