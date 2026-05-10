import os
from datetime import timedelta

from flask import current_app
from app.extensions import db
from database.models import User


def create_user(username: str, password: str) -> User:
    """Create a new user with a hashed password. Returns the User instance."""
    user = User(username=username)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return user


def get_user_by_username(username: str):
    return User.query.filter_by(username=username).first()


def ensure_default_admin(app=None):
    """Create a default admin account if none exists.

    Username and password are taken from env vars `ADMIN_USER` and `ADMIN_PASS`.
    If not provided, defaults to `admin` / `admin` (ONLY for dev).
    """
    if app is None:
        app = current_app

    admin_user = os.environ.get("ADMIN_USER", "admin")
    admin_pass = os.environ.get("ADMIN_PASS", "admin")

    with app.app_context():
        if not User.query.filter_by(username=admin_user).first():
            app.logger.info("Creating default admin user: %s", admin_user)
            create_user(admin_user, admin_pass)
        else:
            app.logger.info("Default admin already exists: %s", admin_user)
