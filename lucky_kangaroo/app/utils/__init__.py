import redis
import os

_redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
redis_connection = redis.from_url(_redis_url) if _redis_url else None
