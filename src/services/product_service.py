from src.models import db, Product

class ProductService:
    @staticmethod
    def create_product(boss_id, name, price):
        new_product = Product(boss_id=boss_id, name=name, price=price)
        db.session.add(new_product)
        db.session.commit()
        return new_product
    
    @staticmethod
    def get_products_by_boss(boss_id, is_active=None):
        query = Product.query.filter_by(boss_id=boss_id)
        if is_active is not None:
            query = query.filter_by(is_active=is_active)
        return query.all()
    
    @staticmethod
    def get_product_by_id(product_id, boss_id=None, is_active=None):
        query = Product.query.filter_by(id=product_id)
        if boss_id:
            query = query.filter_by(boss_id=boss_id)
        if is_active is not None:
            query = query.filter_by(is_active=is_active)
        return query.first()
    
    @staticmethod
    def update_product(product, name=None, price=None, is_active=None):
        if name is not None:
            product.name = name
        if price is not None:
            product.price = price
        if is_active is not None:
            product.is_active = is_active
        db.session.commit()
        return product
    
    @staticmethod
    def delete_product(product):
        db.session.delete(product)
        db.session.commit()
        return True


