import os
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "change-me-for-prod"
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or \
        f"sqlite:///{os.path.join(basedir, 'database', 'app.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(basedir, "uploads")
    LOG_DIR = os.path.join(basedir, "logs")
    # Scheduler settings
    SCHEDULER_INTERVAL = int(os.environ.get("SCHEDULER_INTERVAL", 30))
    SCHEDULER_MAX_RETRIES = int(os.environ.get("SCHEDULER_MAX_RETRIES", 3))
    SCHEDULER_RETRY_DELAY = int(os.environ.get("SCHEDULER_RETRY_DELAY", 60))
    PROFILE_ROOT = os.path.join(basedir, "profiles")
    # Session security settings
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'False').lower() in ('1', 'true', 'yes')
    SESSION_COOKIE_SAMESITE = os.environ.get('SESSION_COOKIE_SAMESITE', 'Lax')
    REMEMBER_COOKIE_DURATION = timedelta(days=int(os.environ.get("REMEMBER_DAYS", 7)))
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False
