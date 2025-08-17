from datetime import datetime, date
from . import db


class Credit(db.Model):
    __tablename__ = 'credit'
    
    id = db.Column(db.Integer, primary_key=True)
    sale_id = db.Column(db.Integer, db.ForeignKey('sale.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    amount_paid = db.Column(db.Numeric(10, 2), default=0)
    is_paid = db.Column(db.Boolean, default=False)
    due_date = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Campos para sincronização offline
    local_id = db.Column(db.String(255), nullable=True)
    sync_status = db.Column(db.Enum('SYNCED', 'PENDING', 'CONFLICT', name='sync_status'), default='SYNCED')
    last_modified = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    payments = db.relationship('CreditPayment', backref='credit', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        """Converte o objeto para dicionário"""
        return {
            'id': self.id,
            'sale_id': self.sale_id,
            'customer_id': self.customer_id,
            'amount': float(self.amount),
            'amount_paid': float(self.amount_paid),
            'amount_remaining': float(self.amount - self.amount_paid),
            'is_paid': self.is_paid,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'local_id': self.local_id,
            'sync_status': self.sync_status,
            'last_modified': self.last_modified.isoformat() if self.last_modified else None,
            'customer_name': self.customer.name if self.customer else None,
            'payments': [payment.to_dict() for payment in self.payments]
        }
    
    def add_payment(self, amount, payment_date=None):
        """Adiciona um pagamento ao crédito"""
        if payment_date is None:
            payment_date = date.today()
        
        payment = CreditPayment(
            credit_id=self.id,
            amount=amount,
            payment_date=payment_date
        )
        
        self.amount_paid += amount
        if self.amount_paid >= self.amount:
            self.is_paid = True
            self.amount_paid = self.amount  # Evitar pagamentos excessivos
        
        return payment
    
    def get_remaining_amount(self):
        """Calcula o valor restante do crédito"""
        return float(self.amount - self.amount_paid)
    
    def __repr__(self):
        return f'<Credit {self.id} - {self.amount} ({self.customer.name if self.customer else "Unknown"})>'


class CreditPayment(db.Model):
    __tablename__ = 'credit_payment'
    
    id = db.Column(db.Integer, primary_key=True)
    credit_id = db.Column(db.Integer, db.ForeignKey('credit.id'), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    payment_date = db.Column(db.Date, nullable=False, default=date.today)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Campos para sincronização offline
    local_id = db.Column(db.String(255), nullable=True)
    sync_status = db.Column(db.Enum('SYNCED', 'PENDING', 'CONFLICT', name='sync_status'), default='SYNCED')
    last_modified = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Converte o objeto para dicionário"""
        return {
            'id': self.id,
            'credit_id': self.credit_id,
            'amount': float(self.amount),
            'payment_date': self.payment_date.isoformat() if self.payment_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'local_id': self.local_id,
            'sync_status': self.sync_status,
            'last_modified': self.last_modified.isoformat() if self.last_modified else None
        }
    
    def __repr__(self):
        return f'<CreditPayment {self.id} - {self.amount}>'

