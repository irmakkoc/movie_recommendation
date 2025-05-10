from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from flask_login import UserMixin
import secrets
import hashlib

db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    reset_token_hash = db.Column(db.String(128))
    reset_token_expires = db.Column(db.DateTime)
    watched_movies = db.relationship('WatchedMovie', backref='user', lazy=True)
    watch_later = db.relationship('WatchLaterMovie', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_reset_token(self):
        # Generate a secure random token
        token = secrets.token_urlsafe(64)
        # Hash the token before storing
        self.reset_token_hash = hashlib.sha256(token.encode()).hexdigest()
        # Set expiration to 30 minutes from now
        self.reset_token_expires = datetime.utcnow() + timedelta(minutes=30)
        db.session.commit()
        return token

    def verify_reset_token(self, token):
        if not self.reset_token_hash or not self.reset_token_expires:
            return False
        if datetime.utcnow() > self.reset_token_expires:
            return False
        # Hash the provided token and compare with stored hash
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        return secrets.compare_digest(token_hash, self.reset_token_hash)

    def clear_reset_token(self):
        self.reset_token_hash = None
        self.reset_token_expires = None
        db.session.commit()

    def __repr__(self):
        return f'<User {self.username}>'

class WatchedMovie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    movie_title = db.Column(db.String(200), nullable=False)
    watched_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<WatchedMovie {self.movie_title}>'

class WatchLaterMovie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    movie_title = db.Column(db.String(200), nullable=False)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<WatchLaterMovie {self.movie_title}>' 