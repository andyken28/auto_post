from flask import Blueprint, request, redirect, url_for, flash, render_template, current_app
from flask_login import login_user, logout_user, login_required, current_user
import logging
from app.extensions import db, login_manager
from app.services.auth_service import get_user_by_username, create_user
from database.models import User

logger = logging.getLogger(__name__)

auth = Blueprint("auth", __name__, template_folder="templates")


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@auth.route("/login", methods=["GET", "POST"])
def login():
    """Render login page on GET. Handle credential POST on POST.

    Supports `remember` checkbox for persistent sessions.
    """
    if request.method == "POST":
        # Detailed debug logging for POST login attempts
        try:
            logger.debug('POST /auth/login called')
            logger.debug('request.method=%s', request.method)
            logger.debug('request.headers=%s', {k: v for k, v in request.headers.items() if k.lower()!='cookie'})
            logger.debug('request.form=%s', request.form.to_dict())

            username = request.form.get("username")
            password = request.form.get("password")
            remember = bool(request.form.get("remember"))

            logger.debug('username received=%s', username)

            if not username or not password:
                flash("Username and password are required", "warning")
                logger.warning('Login attempt missing username or password: form=%s', request.form.to_dict())
                return redirect(url_for("auth.login"))

            user = get_user_by_username(username)
            if not user:
                # Create user for convenience in development
                logger.info('Creating development user %s', username)
                user = create_user(username, password)

            if user.check_password(password):
                login_user(user, remember=remember)
                flash("Logged in successfully", "success")
                logger.info('User %s logged in', username)
                next_page = request.args.get("next") or url_for("main.index")
                return redirect(next_page)

            flash("Invalid credentials", "danger")
            logger.warning('Invalid credentials for user %s', username)
            return redirect(url_for("auth.login"))
        except Exception as e:
            # Log traceback and details for debugging
            logger.exception('Exception during login: %s', e)
            flash('An error occurred during login. Check server logs.', 'danger')
            return redirect(url_for('auth.login'))

    return render_template("login.html")


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out", "info")
    return redirect(url_for("main.index"))
