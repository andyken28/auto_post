from flask import Flask, request, flash, redirect, url_for
from config import Config
from .extensions import db, login_manager, csrf
from .routes import main as main_bp
from .auth import auth as auth_bp
import logger


def create_app(config_class=Config):
    """Application factory. Initializes Flask, extensions and blueprints."""
    app = Flask(__name__, static_folder="../uploads")
    app.config.from_object(config_class)

    # Setup logging early
    logger.setup_logging(app.config)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    # Warn when running with default SECRET_KEY
    if app.config.get('SECRET_KEY', '').startswith('change-me'):
        app.logger.warning('Using default SECRET_KEY; set SECRET_KEY env var for production')

    # CSRF error handler to avoid raw 400 responses and provide useful logs
    try:
        from flask_wtf.csrf import CSRFError

        @app.errorhandler(CSRFError)
        def handle_csrf(e):
            app.logger.warning('CSRF error on request %s %s: %s', request.method, request.path, getattr(e, 'description', str(e)))
            flash_func = getattr(__import__('flask'), 'flash')
            flash_func('Invalid or missing CSRF token. Please try again.', 'danger')
            from flask import redirect, url_for
            return redirect(url_for('auth.login'))
    except Exception:
        app.logger.debug('CSRFError handler could not be installed')

    # Register blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    # Dashboard admin blueprint
    try:
        from .dashboard import dashboard as dashboard_bp
        app.register_blueprint(dashboard_bp, url_prefix="/dashboard")
    except Exception:
        app.logger.exception("Failed to register dashboard blueprint")
    # Facebook accounts blueprint
    try:
        from .facebook_accounts import fb as facebook_bp
        app.register_blueprint(facebook_bp)
    except Exception:
        app.logger.exception("Failed to register facebook accounts blueprint")
    # Logs viewer blueprint
    try:
        from .logs import logs_bp as logs_blueprint
        app.register_blueprint(logs_blueprint)
    except Exception:
        app.logger.exception("Failed to register logs blueprint")
    # Posts blueprint
    try:
        from .posts import posts_bp as posts_blueprint
        app.register_blueprint(posts_blueprint)
    except Exception:
        app.logger.exception("Failed to register posts blueprint")

    # Ensure database tables exist for simple local dev
    with app.app_context():
        db.create_all()
        # Ensure a default admin account exists for development convenience
        try:
            from .services.auth_service import ensure_default_admin
            ensure_default_admin(app)
        except Exception:
            app.logger.exception("Failed to ensure default admin")
        # Start scheduler for processing scheduled posts
        try:
            from .scheduler_service import start_scheduler
            start_scheduler(app)
        except Exception:
            app.logger.exception("Failed to start scheduler")

    return app
