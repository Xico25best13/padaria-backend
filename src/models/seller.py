from datetime import datetime
import secrets
from . import db

class Seller(db.Model):
    __tablename__ = 'seller'
    
    id = db.Column(db.Integer, primary_key=True)
    boss_id = db.Column(db.Integer, db.ForeignKey('boss.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    token = db.Column(db.String(255), unique=True, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    sales = db.relationship('Sale', backref='seller', lazy=True)
    sync_queue = db.relationship('SyncQueue', backref='seller', lazy=True, cascade='all, delete-orphan')
    sync_logs = db.relationship('SyncLog', backref='seller', lazy=True, cascade='all, delete-orphan')
    
    def __init__(self, **kwargs):
        super(Seller, self).__init__(**kwargs)
        if not self.token:
            self.generate_token()
    
    def generate_token(self):
        """Gera um token único para o vendedor"""
        self.token = secrets.token_urlsafe(32)
    
    def regenerate_token(self):
        """Regenera o token do vendedor"""
        self.generate_token()
    
    def to_dict(self):
        """Converte o objeto para dicionário"""
        return {
            'id': self.id,
            'boss_id': self.boss_id,
            'name': self.name,
            'token': self.token,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def to_dict_public(self):
        """Converte o objeto para dicionário sem informações sensíveis"""
        return {
            'id': self.id,
            'name': self.name,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<Seller {self.name}>'

