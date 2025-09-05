from app import create_app
from extensions import init_celery

flask_app = create_app()
celery = init_celery(flask_app)

