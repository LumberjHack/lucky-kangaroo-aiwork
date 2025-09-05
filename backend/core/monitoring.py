"""
Lucky Kangaroo - Système de monitoring et observabilité
Monitoring des performances, métriques et santé de l'application
"""

import time
import psutil
import threading
from datetime import datetime, timedelta
from flask import request, g, current_app
from functools import wraps
import logging

logger = logging.getLogger(__name__)

class PerformanceMonitor:
    """Moniteur de performance pour l'application"""
    
    def __init__(self):
        self.request_times = []
        self.error_counts = {}
        self.database_operations = []
        self.start_time = datetime.utcnow()
        self._lock = threading.Lock()
    
    def record_request_time(self, path, method, duration, status_code):
        """Enregistre le temps de réponse d'une requête"""
        with self._lock:
            self.request_times.append({
                'timestamp': datetime.utcnow(),
                'path': path,
                'method': method,
                'duration': duration,
                'status_code': status_code
            })
            
            # Garder seulement les 1000 dernières requêtes
            if len(self.request_times) > 1000:
                self.request_times.pop(0)
    
    def record_error(self, error_type, path, method):
        """Enregistre une erreur"""
        with self._lock:
            key = f"{error_type}:{path}:{method}"
            self.error_counts[key] = self.error_counts.get(key, 0) + 1
    
    def record_database_operation(self, operation, table, duration, success):
        """Enregistre une opération de base de données"""
        with self._lock:
            self.database_operations.append({
                'timestamp': datetime.utcnow(),
                'operation': operation,
                'table': table,
                'duration': duration,
                'success': success
            })
            
            # Garder seulement les 500 dernières opérations
            if len(self.database_operations) > 500:
                self.database_operations.pop(0)
    
    def get_statistics(self, time_window_minutes=60):
        """Récupère les statistiques sur une fenêtre de temps"""
        now = datetime.utcnow()
        cutoff = now - timedelta(minutes=time_window_minutes)
        
        with self._lock:
            # Requêtes récentes
            recent_requests = [r for r in self.request_times if r['timestamp'] > cutoff]
            
            # Erreurs récentes
            recent_errors = sum(self.error_counts.values())
            
            # Opérations DB récentes
            recent_db_ops = [op for op in self.database_operations if op['timestamp'] > cutoff]
            
            if recent_requests:
                avg_response_time = sum(r['duration'] for r in recent_requests) / len(recent_requests)
                min_response_time = min(r['duration'] for r in recent_requests)
                max_response_time = max(r['duration'] for r in recent_requests)
            else:
                avg_response_time = min_response_time = max_response_time = 0
            
            if recent_db_ops:
                avg_db_time = sum(op['duration'] for op in recent_db_ops) / len(recent_db_ops)
                db_success_rate = sum(1 for op in recent_db_ops if op['success']) / len(recent_db_ops) * 100
            else:
                avg_db_time = 0
                db_success_rate = 100
            
            return {
                'time_window_minutes': time_window_minutes,
                'total_requests': len(recent_requests),
                'avg_response_time_ms': round(avg_response_time * 1000, 2),
                'min_response_time_ms': round(min_response_time * 1000, 2),
                'max_response_time_ms': round(max_response_time * 1000, 2),
                'total_errors': recent_errors,
                'error_rate_percent': round((recent_errors / len(recent_requests) * 100) if recent_requests else 0, 2),
                'total_db_operations': len(recent_db_ops),
                'avg_db_time_ms': round(avg_db_time * 1000, 2),
                'db_success_rate_percent': round(db_success_rate, 2),
                'uptime_minutes': round((now - self.start_time).total_seconds() / 60, 2)
            }
    
    def get_system_metrics(self):
        """Récupère les métriques système"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'memory_available_gb': round(memory.available / (1024**3), 2),
                'disk_percent': disk.percent,
                'disk_free_gb': round(disk.free / (1024**3), 2)
            }
        except Exception as e:
            logger.warning(f"Impossible de récupérer les métriques système: {e}")
            return {}

# Instance globale du moniteur
performance_monitor = PerformanceMonitor()

def monitor_request(f):
    """Décorateur pour monitorer les requêtes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        start_time = time.time()
        
        # Stocker le temps de début dans g
        g.start_time = start_time
        
        try:
            response = f(*args, **kwargs)
            duration = time.time() - start_time
            
            # Enregistrer la métrique
            performance_monitor.record_request_time(
                request.path,
                request.method,
                duration,
                response.status_code if hasattr(response, 'status_code') else 200
            )
            
            return response
        except Exception as e:
            duration = time.time() - start_time
            
            # Enregistrer l'erreur
            performance_monitor.record_error(
                type(e).__name__,
                request.path,
                request.method
            )
            
            # Enregistrer la métrique avec statut d'erreur
            performance_monitor.record_request_time(
                request.path,
                request.method,
                duration,
                500
            )
            
            raise
    
    return decorated_function

def monitor_database_operation(operation, table):
    """Décorateur pour monitorer les opérations de base de données"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = f(*args, **kwargs)
                duration = time.time() - start_time
                
                # Enregistrer l'opération réussie
                performance_monitor.record_database_operation(
                    operation, table, duration, True
                )
                
                return result
            except Exception as e:
                duration = time.time() - start_time
                
                # Enregistrer l'opération échouée
                performance_monitor.record_database_operation(
                    operation, table, duration, False
                )
                
                raise
        
        return decorated_function
    return decorator

def setup_monitoring(app):
    """Configure le monitoring pour l'application Flask"""
    
    @app.before_request
    def start_timer():
        """Démarre le chronomètre pour chaque requête"""
        g.start_time = time.time()
    
    @app.after_request
    def log_request_metrics(response):
        """Log les métriques de la requête"""
        if hasattr(g, 'start_time'):
            duration = time.time() - g.start_time
            
            # Log de base
            logger.debug(f"Request: {request.method} {request.path} - {response.status_code} - {duration:.3f}s")
            
            # Enregistrer dans le moniteur
            performance_monitor.record_request_time(
                request.path,
                request.method,
                duration,
                response.status_code
            )
            
            # Log des erreurs
            if response.status_code >= 400:
                logger.warning(f"Error response: {request.method} {request.path} - {response.status_code}")
        
        return response
    
    @app.errorhandler(Exception)
    def handle_exception(e):
        """Gère les exceptions non gérées et les log"""
        if hasattr(g, 'start_time'):
            duration = time.time() - g.start_time
            
            # Enregistrer l'erreur
            performance_monitor.record_error(
                type(e).__name__,
                request.path,
                request.method
            )
            
            # Enregistrer la métrique avec statut d'erreur
            performance_monitor.record_request_time(
                request.path,
                request.method,
                duration,
                500
            )
        
        # Laisser Flask gérer l'erreur normalement
        raise

def get_health_status():
    """Retourne le statut de santé de l'application"""
    try:
        # Vérifier la base de données
        from extensions import db
        db.session.execute('SELECT 1')
        db_healthy = True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_healthy = False
    
    try:
        # Vérifier Redis
        from extensions import redis_connection
        redis = redis_connection()
        if redis:
            redis.ping()
            redis_healthy = True
        else:
            redis_healthy = False
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
        redis_healthy = False
    
    # Métriques système
    system_metrics = performance_monitor.get_system_metrics()
    
    # Statistiques de performance
    perf_stats = performance_monitor.get_statistics(time_window_minutes=5)
    
    return {
        'status': 'healthy' if (db_healthy and redis_healthy) else 'unhealthy',
        'timestamp': datetime.utcnow().isoformat(),
        'components': {
            'database': 'healthy' if db_healthy else 'unhealthy',
            'redis': 'healthy' if redis_healthy else 'unhealthy'
        },
        'system': system_metrics,
        'performance': perf_stats
    }

def get_detailed_metrics():
    """Retourne des métriques détaillées pour le monitoring"""
    return {
        'health': get_health_status(),
        'performance': performance_monitor.get_statistics(time_window_minutes=60),
        'errors': dict(performance_monitor.error_counts),
        'uptime': {
            'start_time': performance_monitor.start_time.isoformat(),
            'uptime_minutes': round((datetime.utcnow() - performance_monitor.start_time).total_seconds() / 60, 2)
        }
    }
