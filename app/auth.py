from flask import Blueprint, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from .extensions import db, login_manager
from database.models import User

auth = Blueprint("auth", __name__)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@auth.route("/login", methods=["GET", "POST"])
def login():
    """Simple login endpoint for development.

    POST params: `username`, `password`.
    If the user does not exist it will be created (dev convenience).
    """
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if not username or not password:
            return jsonify(error="username and password required"), 400

        user = User.query.filter_by(username=username).first()
        if not user:
            user = User(username=username)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()

        if user.check_password(password):
            login_user(user)
            return jsonify(message="logged in", username=user.username)
        return jsonify(error="invalid credentials"), 401

    # GET -> return simple instruction
    return jsonify(message="POST username & password to login")


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return jsonify(message="logged out")
