from flask import Flask
from config import Config
from .extensions import db, login_manager
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

    # Register blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")

    # Ensure database tables exist for simple local dev
    with app.app_context():
        db.create_all()
        # Ensure a default admin account exists for development convenience
        try:
            from .services.auth_service import ensure_default_admin
            ensure_default_admin(app)
        except Exception:
            app.logger.exception("Failed to ensure default admin")

    return app
