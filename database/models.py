from datetime import datetime

from app.extensions import db, bcrypt
from flask_login import UserMixin


class User(UserMixin, db.Model):
    """User model with bcrypt password hashing and creation timestamp.

    Fields:
    - id: primary key
    - username: unique login name
    - password_hash: bcrypt hashed password
    - created_at: timestamp when user was created
    """

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def set_password(self, password: str):
        """Hash and store password using Flask-Bcrypt."""
        self.password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    def check_password(self, password: str) -> bool:
        if not self.password_hash:
            return False
        return bcrypt.check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.username}>"


class Post(db.Model):
    """Represents a scheduled or posted item.

    status: one of 'pending', 'running', 'success', 'failed'
    """

    __tablename__ = "posts"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), nullable=True)
    content = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(32), default="pending", nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<Post {self.id} {self.status}>"


class Job(db.Model):
    """Represents a background job that processes posts."""

    __tablename__ = "jobs"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    status = db.Column(db.String(32), default="pending", nullable=False)  # e.g. running, completed
    started_at = db.Column(db.DateTime, nullable=True)
    finished_at = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f"<Job {self.name} {self.status}>"


class Log(db.Model):
    """Simple log model to surface recent entries in the dashboard."""

    __tablename__ = "logs"

    id = db.Column(db.Integer, primary_key=True)
    level = db.Column(db.String(32), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<Log {self.level} {self.created_at}>"
