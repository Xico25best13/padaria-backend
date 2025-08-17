from src.models import db, Seller

class SellerService:
    @staticmethod
    def create_seller(boss_id, name):
        new_seller = Seller(boss_id=boss_id, name=name)
        db.session.add(new_seller)
        db.session.commit()
        return new_seller
    
    @staticmethod
    def get_sellers_by_boss(boss_id):
        return Seller.query.filter_by(boss_id=boss_id).all()
    
    @staticmethod
    def get_seller_by_id(seller_id, boss_id=None):
        if boss_id:
            return Seller.query.filter_by(id=seller_id, boss_id=boss_id).first()
        return Seller.query.filter_by(id=seller_id).first()
    
    @staticmethod
    def update_seller(seller, name=None, is_active=None):
        if name is not None:
            seller.name = name
        if is_active is not None:
            seller.is_active = is_active
        db.session.commit()
        return seller
    
    @staticmethod
    def regenerate_seller_token(seller):
        seller.regenerate_token()
        db.session.commit()
        return seller
    
    @staticmethod
    def delete_seller(seller):
        db.session.delete(seller)
        db.session.commit()
        return True


