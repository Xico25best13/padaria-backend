from datetime import datetime
from . import db


class Customer(db.Model):
    __tablename__ = 'customer'
    
    id = db.Column(db.Integer, primary_key=True)
    boss_id = db.Column(db.Integer, db.ForeignKey('boss.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.Text, nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    sales = db.relationship('Sale', backref='customer', lazy=True)
    credits = db.relationship('Credit', backref='customer', lazy=True)
    
    def to_dict(self):
        """Converte o objeto para dicionário"""
        return {
            'id': self.id,
            'boss_id': self.boss_id,
            'name': self.name,
            'address': self.address,
            'phone': self.phone,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def get_total_credit(self):
        """Calcula o total de crédito pendente do cliente"""
        total = 0
        for credit in self.credits:
            if not credit.is_paid:
                total += float(credit.amount - credit.amount_paid)
        return total
    
    def __repr__(self):
        return f'<Customer {self.name}>'

