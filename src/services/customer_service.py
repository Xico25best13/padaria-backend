from src.models import db, Customer

class CustomerService:
    @staticmethod
    def create_customer(boss_id, name, address=None, phone=None):
        new_customer = Customer(boss_id=boss_id, name=name, address=address, phone=phone)
        db.session.add(new_customer)
        db.session.commit()
        return new_customer
    
    @staticmethod
    def get_customers_by_boss(boss_id):
        return Customer.query.filter_by(boss_id=boss_id).all()
    
    @staticmethod
    def get_customer_by_id(customer_id, boss_id=None):
        if boss_id:
            return Customer.query.filter_by(id=customer_id, boss_id=boss_id).first()
        return Customer.query.filter_by(id=customer_id).first()
    
    @staticmethod
    def update_customer(customer, name=None, address=None, phone=None):
        if name is not None:
            customer.name = name
        if address is not None:
            customer.address = address
        if phone is not None:
            customer.phone = phone
        db.session.commit()
        return customer
    
    @staticmethod
    def delete_customer(customer):
        db.session.delete(customer)
        db.session.commit()
        return True


