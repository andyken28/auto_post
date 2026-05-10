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
