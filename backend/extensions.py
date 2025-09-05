from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_caching import Cache
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_socketio import SocketIO
from celery import Celery
from redis import Redis
from flask import current_app

db = SQLAlchemy()
migrate = Migrate()
cache = Cache()
jwt = JWTManager()
mail = Mail()
cors = CORS()
limiter = Limiter(key_func=get_remote_address)
socketio = SocketIO(async_mode="gevent", cors_allowed_origins="*")
celery = Celery(__name__)

def init_extensions(app):
    db.init_app(app)
    migrate.init_app(app, db)
    cache.init_app(app)
    jwt.init_app(app)
    mail.init_app(app)
    cors.init_app(app, resources={
        r"/api/*": {"origins": app.config.get("CORS_ALLOWED_ORIGINS", "*").split(",")}
    })
    limiter.init_app(app)
    socketio.init_app(app, message_queue=app.config.get("SOCKETIO_MESSAGE_QUEUE"))

def init_celery(app):
    celery.conf.update(
        broker_url=app.config.get("CELERY_BROKER_URL"),
        result_backend=app.config.get("CELERY_RESULT_BACKEND"),
        task_serializer="json",
        accept_content=["json"],
        result_serializer="json",
        timezone="UTC",
        enable_utc=True,
        task_track_started=True,
    )
    class AppContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return super().__call__(*args, **kwargs)
    celery.Task = AppContextTask
    return celery

def redis_connection():
    url = current_app.config.get("REDIS_URL")
    if not url:
        return None
    return Redis.from_url(url, decode_responses=True)
