from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    key_salt = db.Column(db.LargeBinary, nullable=False)  # For encryption
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship: One user can have many credentials
    credentials = db.relationship('Credential', backref='owner', lazy=True)
    
    def __repr__(self):
        return f'<User {self.username}>'

class Credential(db.Model):
    __tablename__ = 'credentials'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    site = db.Column(db.String(200), nullable=False)
    username = db.Column(db.String(200), nullable=False)
    encrypted_password = db.Column(db.LargeBinary, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Credential {self.site}>'
