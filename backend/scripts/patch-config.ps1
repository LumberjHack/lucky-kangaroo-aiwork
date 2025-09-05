# backend/scripts/patch-config.ps1
$ErrorActionPreference = 'Stop'

# Dossiers/fichiers
$root   = Split-Path -Parent $PSScriptRoot
$config = Join-Path $root 'config.py'
$backup = "$config.$(Get-Date -Format yyyyMMdd-HHmmss).bak"

if (Test-Path $config) { Copy-Item $config $backup -Force }

# NOTE: here-string DOIT se terminer par une ligne contenant uniquement @" (sans espace)
$Content = @"
# -*- coding: utf-8 -*-
import os
from datetime import timedelta
from pathlib import Path

def _env_str(name, default=None):
    v = os.getenv(name)
    return v if (v is not None and v.strip() != "") else default

def _env_int(name, default):
    v = os.getenv(name)
    try:
        return int(v) if (v is not None and v.strip() != "") else default
    except Exception:
        return default

def _env_bool(name, default):
    v = os.getenv(name)
    if v is None or v.strip() == "":
        return default
    return str(v).lower() in ("1","true","yes","on")

class BaseConfig:
    APP_NAME = "Lucky Kangaroo"
    APP_VERSION = "1.0.0"
    DEBUG = False
    TESTING = False

    SECRET_KEY = _env_str("SECRET_KEY","change-me")

    SQLALCHEMY_DATABASE_URI = _env_str(
        "SQLALCHEMY_DATABASE_URI",
        _env_str("DATABASE_URL","postgresql+psycopg2://lk:lkpass@postgres:5432/luckykangaroo")
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
        "pool_size": 10,
        "max_overflow": 10,
    }

    BASE_DIR = Path(__file__).resolve().parent
    UPLOAD_FOLDER = _env_str("UPLOAD_FOLDER", str(BASE_DIR / "uploads"))
    MAX_CONTENT_LENGTH = _env_int("MAX_CONTENT_LENGTH", 16777216)
    ALLOWED_EXTENSIONS = {"pdf","png","jpg","jpeg","gif","webp"}

    REDIS_URL = _env_str("REDIS_URL","redis://redis:6379/0")
    CACHE_TYPE = _env_str("CACHE_TYPE","SimpleCache")
    CACHE_REDIS_URL = _env_str("CACHE_REDIS_URL", REDIS_URL)
    CACHE_DEFAULT_TIMEOUT = _env_int("CACHE_DEFAULT_TIMEOUT", 300)

    RATELIMIT_DEFAULT = _env_str("RATELIMIT_DEFAULT","200 per hour")
    RATELIMIT_STORAGE_URI = REDIS_URL

    JWT_SECRET_KEY = _env_str("JWT_SECRET_KEY","dev-jwt")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(seconds=_env_int("JWT_ACCESS_TOKEN_EXPIRES", 3600))
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=_env_int("JWT_REFRESH_TOKEN_EXPIRES", 30))
    JWT_BLACKLIST_ENABLED = _env_bool("JWT_BLACKLIST_ENABLED", True)
    JWT_BLACKLIST_TOKEN_CHECKS = (_env_str("JWT_BLACKLIST_TOKEN_CHECKS","access,refresh") or "access,refresh").split(",")

    # Valeurs sûres par défaut pour éviter l'erreur MAIL_PORT vide
    MAIL_SERVER = _env_str("MAIL_SERVER","localhost")
    MAIL_PORT   = _env_int("MAIL_PORT", 1025)
    MAIL_USE_TLS = _env_bool("MAIL_USE_TLS", False)
    MAIL_USE_SSL = _env_bool("MAIL_USE_SSL", False)
    MAIL_USERNAME = _env_str("MAIL_USERNAME","")
    MAIL_PASSWORD = _env_str("MAIL_PASSWORD","")
    MAIL_DEFAULT_SENDER = _env_str("MAIL_DEFAULT_SENDER","noreply@local")
    MAIL_DEBUG = _env_bool("MAIL_DEBUG", False)

    SEARCH_URL = _env_str("SEARCH_URL","")
    SEARCH_INDEX_PREFIX = _env_str("SEARCH_INDEX_PREFIX","luckykangaroo")

    STRIPE_SECRET_KEY = _env_str("STRIPE_SECRET_KEY","")
    STRIPE_WEBHOOK_SECRET = _env_str("STRIPE_WEBHOOK_SECRET","")
    STRIPE_PUBLIC_KEY = _env_str("STRIPE_PUBLIC_KEY","")

    REDIS_SOCKETIO_DB = _env_int("REDIS_SOCKETIO_DB", 3)
    SOCKETIO_MESSAGE_QUEUE = _env_str("SOCKETIO_MESSAGE_QUEUE", f"{REDIS_URL}/{REDIS_SOCKETIO_DB}")
    SOCKETIO_ASYNC_MODE = _env_str("SOCKETIO_ASYNC_MODE","gevent")
    CORS_ORIGINS = _env_str("CORS_ALLOWED_ORIGINS","*")

    LOG_LEVEL = _env_str("LOG_LEVEL","INFO")
    LOG_FORMAT = _env_str("LOG_FORMAT","%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    LOG_FILE = _env_str("LOG_FILE","logs/app.log")

class DevelopmentConfig(BaseConfig):
    DEBUG = True
    SQLALCHEMY_ECHO = True

class TestingConfig(BaseConfig):
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "sqlite://"

class ProductionConfig(BaseConfig):
    pass

CONFIG_BY_NAME = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}

def get_config(env: str = None):
    env = (env or os.getenv("FLASK_ENV","development")).lower()
    return CONFIG_BY_NAME.get(env, DevelopmentConfig)
"@

# Écrit le fichier en UTF-8 (avec BOM pour ISE/Windows)
[IO.File]::WriteAllText($config, $Content, [Text.UTF8Encoding]::new($true))
Write-Host "✅ Fichier mis à jour: $config" -ForegroundColor Green
if (Test-Path $backup) { Write-Host "🗂️  Backup créé: $backup" -ForegroundColor DarkGray }
