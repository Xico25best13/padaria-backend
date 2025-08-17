from datetime import datetime, date
from . import db


class Sale(db.Model):
    __tablename__ = 'sale'
    
    id = db.Column(db.Integer, primary_key=True)
    seller_id = db.Column(db.Integer, db.ForeignKey('seller.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=True)
    guide_id = db.Column(db.Integer, db.ForeignKey('sales_guide.id'), nullable=True)  # Novo campo
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    payment_type = db.Column(db.Enum('cash', 'credit', name='payment_type'), nullable=False)
    sale_date = db.Column(db.Date, nullable=False, default=date.today)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Campos para sincronização offline
    local_id = db.Column(db.String(255), nullable=True)
    sync_status = db.Column(db.Enum('SYNCED', 'PENDING', 'CONFLICT', name='sync_status'), default='SYNCED')
    last_modified = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    sale_items = db.relationship('SaleItem', backref='sale', lazy=True, cascade='all, delete-orphan')
    credit = db.relationship('Credit', backref='sale', uselist=False, cascade='all, delete-orphan')
    
    def to_dict(self):
        """Converte o objeto para dicionário"""
        return {
            'id': self.id,
            'seller_id': self.seller_id,
            'customer_id': self.customer_id,
            'guide_id': self.guide_id,
            'total_amount': float(self.total_amount),
            'payment_type': self.payment_type,
            'sale_date': self.sale_date.isoformat() if self.sale_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'local_id': self.local_id,
            'sync_status': self.sync_status,
            'last_modified': self.last_modified.isoformat() if self.last_modified else None,
            'items': [item.to_dict() for item in self.sale_items],
            'customer_name': self.customer.name if self.customer else None
        }
    
    def calculate_total(self):
        """Calcula o total da venda baseado nos itens"""
        total = sum(float(item.subtotal) for item in self.sale_items)
        self.total_amount = total
        return total
    
    def __repr__(self):
        return f'<Sale {self.id} - {self.total_amount}>'


class SaleItem(db.Model):
    __tablename__ = 'sale_item'
    
    id = db.Column(db.Integer, primary_key=True)
    sale_id = db.Column(db.Integer, db.ForeignKey('sale.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)
    subtotal = db.Column(db.Numeric(10, 2), nullable=False)
    
    def to_dict(self):
        """Converte o objeto para dicionário"""
        return {
            'id': self.id,
            'sale_id': self.sale_id,
            'product_id': self.product_id,
            'quantity': self.quantity,
            'unit_price': float(self.unit_price),
            'subtotal': float(self.subtotal),
            'product_name': self.product.name if self.product else None
        }
    
    def calculate_subtotal(self):
        """Calcula o subtotal do item"""
        self.subtotal = self.quantity * self.unit_price
        return self.subtotal
    
    def __repr__(self):
        return f'<SaleItem {self.id} - {self.quantity}x {self.product.name if self.product else "Unknown"}>'

