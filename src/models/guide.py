from datetime import datetime, date
from . import db


class SalesGuide(db.Model):
    __tablename__ = 'sales_guide'
    
    id = db.Column(db.Integer, primary_key=True)
    seller_id = db.Column(db.Integer, db.ForeignKey('seller.id'), nullable=False)
    guide_date = db.Column(db.Date, nullable=False, default=date.today)
    status = db.Column(db.Enum('OPEN', 'CLOSED', name='guide_status'), default='OPEN')
    total_taken_value = db.Column(db.Numeric(10, 2), default=0)
    total_sold_value = db.Column(db.Numeric(10, 2), default=0)
    total_remaining_value = db.Column(db.Numeric(10, 2), default=0)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    closed_at = db.Column(db.DateTime, nullable=True)
    
    # Campos para sincronização offline
    local_id = db.Column(db.String(255), nullable=True)
    sync_status = db.Column(db.Enum('SYNCED', 'PENDING', 'CONFLICT', name='sync_status'), default='SYNCED')
    last_modified = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    guide_items = db.relationship('GuideItem', backref='guide', lazy=True, cascade='all, delete-orphan')
    sales = db.relationship('Sale', backref='guide', lazy=True)
    
    def to_dict(self):
        """Converte o objeto para dicionário"""
        return {
            'id': self.id,
            'seller_id': self.seller_id,
            'guide_date': self.guide_date.isoformat() if self.guide_date else None,
            'status': self.status,
            'total_taken_value': float(self.total_taken_value),
            'total_sold_value': float(self.total_sold_value),
            'total_remaining_value': float(self.total_remaining_value),
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'closed_at': self.closed_at.isoformat() if self.closed_at else None,
            'local_id': self.local_id,
            'sync_status': self.sync_status,
            'last_modified': self.last_modified.isoformat() if self.last_modified else None,
            'items': [item.to_dict() for item in self.guide_items],
            'seller_name': self.seller.name if self.seller else None
        }
    
    def calculate_totals(self):
        """Calcula os totais da guia baseado nos itens"""
        self.total_taken_value = sum(float(item.total_taken_value) for item in self.guide_items)
        self.total_sold_value = sum(float(item.total_sold_value) for item in self.guide_items)
        self.total_remaining_value = sum(float(item.total_remaining_value) for item in self.guide_items)
    
    def close_guide(self):
        """Fecha a guia"""
        self.status = 'CLOSED'
        self.closed_at = datetime.utcnow()
        self.calculate_totals()
    
    def can_close(self):
        """Verifica se a guia pode ser fechada (todas as sobras registadas)"""
        for item in self.guide_items:
            if item.quantity_remaining is None:
                return False
        return True
    
    def get_sales_summary(self):
        """Retorna resumo das vendas associadas à guia"""
        total_sales_registered = sum(float(sale.total_amount) for sale in self.sales)
        expected_sales_value = float(self.total_sold_value)
        difference = total_sales_registered - expected_sales_value
        
        return {
            'total_sales_registered': total_sales_registered,
            'expected_sales_value': expected_sales_value,
            'difference': difference,
            'difference_percentage': (difference / expected_sales_value * 100) if expected_sales_value > 0 else 0
        }
    
    def __repr__(self):
        return f'<SalesGuide {self.id} - {self.guide_date} ({self.status})>'


class GuideItem(db.Model):
    __tablename__ = 'guide_item'
    
    id = db.Column(db.Integer, primary_key=True)
    guide_id = db.Column(db.Integer, db.ForeignKey('sales_guide.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity_taken = db.Column(db.Integer, nullable=False)
    quantity_remaining = db.Column(db.Integer, nullable=True)  # Null até ser registado
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)
    
    # Campos calculados (serão calculados pela aplicação, não pela BD)
    total_taken_value = db.Column(db.Numeric(10, 2), nullable=False)
    total_sold_value = db.Column(db.Numeric(10, 2), default=0)
    total_remaining_value = db.Column(db.Numeric(10, 2), default=0)
    
    def to_dict(self):
        """Converte o objeto para dicionário"""
        quantity_sold = self.get_quantity_sold()
        return {
            'id': self.id,
            'guide_id': self.guide_id,
            'product_id': self.product_id,
            'quantity_taken': self.quantity_taken,
            'quantity_remaining': self.quantity_remaining,
            'quantity_sold': quantity_sold,
            'unit_price': float(self.unit_price),
            'total_taken_value': float(self.total_taken_value),
            'total_sold_value': float(self.total_sold_value),
            'total_remaining_value': float(self.total_remaining_value),
            'product_name': self.product.name if self.product else None
        }
    
    def get_quantity_sold(self):
        """Calcula a quantidade vendida"""
        if self.quantity_remaining is not None:
            return self.quantity_taken - self.quantity_remaining
        return 0
    
    def calculate_values(self):
        """Calcula os valores baseado nas quantidades"""
        self.total_taken_value = self.quantity_taken * self.unit_price
        
        if self.quantity_remaining is not None:
            quantity_sold = self.get_quantity_sold()
            self.total_sold_value = quantity_sold * self.unit_price
            self.total_remaining_value = self.quantity_remaining * self.unit_price
        else:
            self.total_sold_value = 0
            self.total_remaining_value = 0
    
    def set_remaining_quantity(self, quantity):
        """Define a quantidade que sobrou e recalcula os valores"""
        if quantity > self.quantity_taken:
            raise ValueError("Quantidade restante não pode ser maior que a quantidade levada")
        
        self.quantity_remaining = quantity
        self.calculate_values()
    
    def get_waste_percentage(self):
        """Calcula a percentagem de desperdício"""
        if self.quantity_taken == 0:
            return 0
        return (self.quantity_remaining / self.quantity_taken * 100) if self.quantity_remaining else 0
    
    def __repr__(self):
        return f'<GuideItem {self.id} - {self.quantity_taken}x {self.product.name if self.product else "Unknown"}>'

