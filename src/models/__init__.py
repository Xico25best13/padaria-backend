from flask_sqlalchemy import SQLAlchemy

# Instância única do SQLAlchemy
db = SQLAlchemy()

# Importar todos os modelos para garantir que são registados
from .boss import Boss
from .seller import Seller
from .product import Product
from .customer import Customer
from .sale import Sale, SaleItem
from .credit import Credit, CreditPayment
from .sync import SyncQueue, SyncLog
from .guide import SalesGuide, GuideItem

# Exportar todos os modelos
__all__ = [
    'db',
    'Boss',
    'Seller', 
    'Product',
    'Customer',
    'Sale',
    'SaleItem',
    'Credit',
    'CreditPayment',
    'SyncQueue',
    'SyncLog',
    'SalesGuide',
    'GuideItem'
]

