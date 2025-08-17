from src.models import db, Credit, CreditPayment, Customer
from datetime import date, datetime

class CreditService:
    @staticmethod
    def get_credits(user_role, user_id, boss_id):
        if user_role == "boss":
            return Credit.query.join(Customer).filter(Customer.boss_id == user_id).all()
        elif user_role == "seller":
            return Credit.query.join(Customer).filter(Customer.boss_id == boss_id).all()
        return []

    @staticmethod
    def get_credit_by_id(credit_id, user_role, user_id, boss_id):
        if user_role == "boss":
            return Credit.query.join(Customer).filter(Credit.id == credit_id, Customer.boss_id == user_id).first()
        elif user_role == "seller":
            return Credit.query.join(Customer).filter(Credit.id == credit_id, Customer.boss_id == boss_id).first()
        return None

    @staticmethod
    def pay_credit(credit, amount, payment_date_str, local_id):
        try:
            amount = float(amount)
            if amount <= 0:
                return None, "Amount must be positive"
        except ValueError:
            return None, "Invalid amount format"
        
        try:
            payment_date = date.fromisoformat(payment_date_str) if payment_date_str else date.today()
        except ValueError:
            return None, "Invalid date format for payment_date"
        
        if amount > credit.get_remaining_amount():
            amount = credit.get_remaining_amount()
        
        new_payment = CreditPayment(
            credit_id=credit.id,
            amount=amount,
            payment_date=payment_date,
            local_id=local_id,
            sync_status="PENDING" if local_id else "SYNCED"
        )
        db.session.add(new_payment)
        
        credit.amount_paid += amount
        if credit.amount_paid >= credit.amount:
            credit.is_paid = True
            credit.amount_paid = credit.amount
        
        db.session.commit()
        return new_payment, None

    @staticmethod
    def get_credit_payments(credit_id, user_role, user_id, boss_id):
        credit = CreditService.get_credit_by_id(credit_id, user_role, user_id, boss_id)
        if not credit:
            return None
        return credit.payments


