from src.models import db, SalesGuide, GuideItem, Product, Seller
from datetime import date, datetime

class GuideService:
    @staticmethod
    def create_guide(seller_id, guide_date_str, notes, items_data, local_id, boss_id):
        try:
            guide_date = date.fromisoformat(guide_date_str) if guide_date_str else date.today()
        except ValueError:
            return None, "Invalid date format for guide_date"
        
        new_guide = SalesGuide(
            seller_id=seller_id,
            guide_date=guide_date,
            notes=notes,
            local_id=local_id,
            sync_status="PENDING" if local_id else "SYNCED"
        )
        db.session.add(new_guide)
        db.session.flush() # Para ter acesso ao ID da guia antes do commit
        
        for item_data in items_data:
            product_id = item_data.get("product_id")
            quantity_taken = item_data.get("quantity_taken")
            
            product = Product.query.filter_by(id=product_id, boss_id=boss_id, is_active=True).first()
            if not product:
                db.session.rollback()
                return None, f"Product with ID {product_id} not found or inactive"
            
            try:
                quantity_taken = int(quantity_taken)
                if quantity_taken <= 0:
                    raise ValueError("Quantity taken must be positive")
            except ValueError:
                db.session.rollback()
                return None, "Invalid quantity_taken format"
            
            new_guide_item = GuideItem(
                guide_id=new_guide.id,
                product_id=product_id,
                quantity_taken=quantity_taken,
                unit_price=product.price
            )
            new_guide_item.calculate_values()
            db.session.add(new_guide_item)
        
        new_guide.calculate_totals()
        db.session.commit()
        return new_guide, None

    @staticmethod
    def get_guides(user_role, user_id, boss_id):
        if user_role == "boss":
            return SalesGuide.query.join(Seller).filter(Seller.boss_id == user_id).all()
        elif user_role == "seller":
            return SalesGuide.query.filter_by(seller_id=user_id).all()
        return []

    @staticmethod
    def get_guide_by_id(guide_id, user_role, user_id, boss_id):
        if user_role == "boss":
            return SalesGuide.query.join(Seller).filter(SalesGuide.id == guide_id, Seller.boss_id == user_id).first()
        elif user_role == "seller":
            return SalesGuide.query.filter_by(id=guide_id, seller_id=user_id).first()
        return None

    @staticmethod
    def close_guide(guide, items_data):
        if guide.status == "CLOSED":
            return None, "Sales Guide is already closed"
        
        for item_data in items_data:
            item_id = item_data.get("id")
            quantity_remaining = item_data.get("quantity_remaining")
            
            guide_item = GuideItem.query.filter_by(id=item_id, guide_id=guide.id).first()
            if not guide_item:
                db.session.rollback()
                return None, f"Guide Item with ID {item_id} not found in this guide"
            
            try:
                quantity_remaining = int(quantity_remaining)
                guide_item.set_remaining_quantity(quantity_remaining)
            except ValueError as e:
                db.session.rollback()
                return None, str(e)
        
        if not guide.can_close():
            db.session.rollback()
            return None, "Cannot close guide: some items do not have remaining quantities registered"
        
        guide.close_guide()
        db.session.commit()
        return guide, None

    @staticmethod
    def update_guide_item(guide, item_id, quantity_remaining):
        if guide.status == "CLOSED":
            return None, "Cannot update item in a closed guide"
        
        guide_item = GuideItem.query.filter_by(id=item_id, guide_id=guide.id).first()
        if not guide_item:
            return None, "Guide Item not found in this guide"
        
        try:
            quantity_remaining = int(quantity_remaining)
            guide_item.set_remaining_quantity(quantity_remaining)
            db.session.commit()
            guide.calculate_totals()
            db.session.commit()
        except ValueError as e:
            return None, str(e)
        
        return guide_item, None

    @staticmethod
    def delete_guide(guide):
        db.session.delete(guide)
        db.session.commit()
        return True


