from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_mail import Mail
from flask_caching import Cache
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from sentry_sdk.integrations.redis import RedisIntegration


db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
cors = CORS()
mail = Mail()
cache = Cache()
limiter = Limiter(key_func=get_remote_address)

def init_extensions(app):
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    cors.init_app(app)
    mail.init_app(app)
    cache.init_app(app)
    limiter.init_app(app)

    if app.config.get('SENTRY_DSN'):
        sentry_sdk.init(
            dsn=app.config['SENTRY_DSN'],
            integrations=[
                FlaskIntegration(),
                SqlalchemyIntegration(),
                RedisIntegration(),
            ],
            traces_sample_rate=1.0,
            environment=app.config.get('ENV', 'development'),
        )
