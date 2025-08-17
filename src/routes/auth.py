from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from src.models import db, Boss, Seller
from src.services.auth_service import AuthService

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register/boss", methods=["POST"])
def register_boss():
    data = request.get_json()
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")
    
    if not all([name, email, password]):
        return jsonify({"message": "Missing data"}), 400
    
    new_boss, error = AuthService.register_boss(name, email, password)
    if error:
        return jsonify({"message": error}), 409
    
    return jsonify({"message": "Boss registered successfully", "boss": new_boss.to_dict()}), 201

@auth_bp.route("/login/boss", methods=["POST"])
def login_boss():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    
    boss = AuthService.login_boss(email, password)
    if not boss:
        return jsonify({"message": "Invalid credentials"}), 401
    
    access_token = create_access_token(identity={"id": boss.id, "role": "boss"})
    return jsonify(access_token=access_token, boss=boss.to_dict()), 200

@auth_bp.route("/login/seller", methods=["POST"])
def login_seller():
    data = request.get_json()
    token = data.get("token")
    
    seller = AuthService.login_seller(token)
    if not seller:
        return jsonify({"message": "Invalid or inactive token"}), 401
    
    access_token = create_access_token(identity={"id": seller.id, "role": "seller", "boss_id": seller.boss_id})
    return jsonify(access_token=access_token, seller=seller.to_dict_public()), 200

@auth_bp.route("/protected", methods=["GET"])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200

