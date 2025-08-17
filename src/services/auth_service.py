from src.models import db, Boss, Seller
from werkzeug.security import generate_password_hash, check_password_hash

class AuthService:
    @staticmethod
    def register_boss(name, email, password):
        if Boss.query.filter_by(email=email).first():
            return None, "Boss with this email already exists"
        
        new_boss = Boss(name=name, email=email)
        new_boss.set_password(password)
        
        db.session.add(new_boss)
        db.session.commit()
        return new_boss, None
    
    @staticmethod
    def login_boss(email, password):
        boss = Boss.query.filter_by(email=email).first()
        if not boss or not boss.check_password(password):
            return None
        return boss
    
    @staticmethod
    def login_seller(token):
        seller = Seller.query.filter_by(token=token, is_active=True).first()
        return seller


