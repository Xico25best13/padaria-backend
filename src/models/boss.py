from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from . import db

class Boss(db.Model):
    __tablename__ = 'boss'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    sellers = db.relationship('Seller', backref='boss', lazy=True, cascade='all, delete-orphan')
    products = db.relationship('Product', backref='boss', lazy=True, cascade='all, delete-orphan')
    customers = db.relationship('Customer', backref='boss', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Define a palavra-passe com hash"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verifica se a palavra-passe está correta"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """Converte o objeto para dicionário"""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Boss {self.name}>'

