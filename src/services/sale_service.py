from src.models import db, Sale, SaleItem, Product, Customer, Credit, SalesGuide
from datetime import date, datetime

class SaleService:
    @staticmethod
    def create_sale(seller_id, customer_id, payment_type, sale_date_str, items_data, local_id, guide_id, boss_id):
        try:
            sale_date = date.fromisoformat(sale_date_str) if sale_date_str else date.today()
        except ValueError:
            return None, "Invalid date format for sale_date"

        if customer_id:
            customer = Customer.query.filter_by(id=customer_id, boss_id=boss_id).first()
            if not customer:
                return None, "Customer not found"
        else:
            customer = None

        if guide_id:
            sales_guide = SalesGuide.query.filter_by(id=guide_id, seller_id=seller_id).first()
            if not sales_guide:
                return None, "Sales Guide not found or does not belong to this seller"

        new_sale = Sale(
            seller_id=seller_id,
            customer_id=customer_id,
            payment_type=payment_type,
            sale_date=sale_date,
            local_id=local_id,
            sync_status="PENDING" if local_id else "SYNCED",
            guide_id=guide_id
        )
        db.session.add(new_sale)
        db.session.flush() # Para ter acesso ao ID da venda antes do commit
        
        total_amount = 0
        for item_data in items_data:
            product_id = item_data.get("product_id")
            quantity = item_data.get("quantity")
            
            product = Product.query.filter_by(id=product_id, boss_id=boss_id, is_active=True).first()
            if not product:
                db.session.rollback()
                return None, f"Product with ID {product_id} not found or inactive"
            
            try:
                quantity = int(quantity)
                if quantity <= 0:
                    raise ValueError("Quantity must be positive")
            except ValueError:
                db.session.rollback()
                return None, "Invalid quantity format"
            
            new_sale_item = SaleItem(
                sale_id=new_sale.id,
                product_id=product_id,
                quantity=quantity,
                unit_price=product.price
            )
            new_sale_item.calculate_subtotal()
            db.session.add(new_sale_item)
            total_amount += new_sale_item.subtotal
        
        new_sale.total_amount = total_amount
        
        if payment_type == "credit":
            if not customer_id:
                db.session.rollback()
                return None, "Customer is required for credit sales"
            new_credit = Credit(
                sale_id=new_sale.id,
                customer_id=customer_id,
                amount=total_amount,
                local_id=local_id, # Usar o mesmo local_id da venda para o crédito
                sync_status="PENDING" if local_id else "SYNCED"
            )
            db.session.add(new_credit)
        
        db.session.commit()
        return new_sale, None

    @staticmethod
    def get_sales(user_role, user_id, boss_id):
        if user_role == "boss":
            return Sale.query.join(Seller).filter(Seller.boss_id == user_id).all()
        elif user_role == "seller":
            return Sale.query.filter_by(seller_id=user_id).all()
        return []

    @staticmethod
    def get_sale_by_id(sale_id, user_role, user_id, boss_id):
        if user_role == "boss":
            return Sale.query.join(Seller).filter(Sale.id == sale_id, Seller.boss_id == user_id).first()
        elif user_role == "seller":
            return Sale.query.filter_by(id=sale_id, seller_id=user_id).first()
        return None

    @staticmethod
    def delete_sale(sale):
        db.session.delete(sale)
        db.session.commit()
        return True


