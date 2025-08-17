from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models import db, Seller, Boss
from src.services.seller_service import SellerService

seller_bp = Blueprint("seller", __name__)

@seller_bp.route("/sellers", methods=["POST"])
@jwt_required()
def create_seller():
    current_user = get_jwt_identity()
    if current_user["role"] != "boss":
        return jsonify({"message": "Unauthorized"}), 403
    
    data = request.get_json()
    name = data.get("name")
    
    if not name:
        return jsonify({"message": "Missing seller name"}), 400
    
    new_seller = SellerService.create_seller(current_user["id"], name)
    
    return jsonify({"message": "Seller created successfully", "seller": new_seller.to_dict()}), 201

@seller_bp.route("/sellers", methods=["GET"])
@jwt_required()
def get_sellers():
    current_user = get_jwt_identity()
    if current_user["role"] != "boss":
        return jsonify({"message": "Unauthorized"}), 403
    
    sellers = SellerService.get_sellers_by_boss(current_user["id"])
    return jsonify([seller.to_dict() for seller in sellers]), 200

@seller_bp.route("/sellers/<int:seller_id>", methods=["GET"])
@jwt_required()
def get_seller(seller_id):
    current_user = get_jwt_identity()
    if current_user["role"] != "boss":
        return jsonify({"message": "Unauthorized"}), 403
    
    seller = SellerService.get_seller_by_id(seller_id, current_user["id"])
    if not seller:
        return jsonify({"message": "Seller not found"}), 404
    
    return jsonify(seller.to_dict()), 200

@seller_bp.route("/sellers/<int:seller_id>", methods=["PUT"])
@jwt_required()
def update_seller(seller_id):
    current_user = get_jwt_identity()
    if current_user["role"] != "boss":
        return jsonify({"message": "Unauthorized"}), 403
    
    seller = SellerService.get_seller_by_id(seller_id, current_user["id"])
    if not seller:
        return jsonify({"message": "Seller not found"}), 404
    
    data = request.get_json()
    updated_seller = SellerService.update_seller(seller, name=data.get("name"), is_active=data.get("is_active"))
    
    return jsonify({"message": "Seller updated successfully", "seller": updated_seller.to_dict()}), 200

@seller_bp.route("/sellers/<int:seller_id>/regenerate_token", methods=["PUT"])
@jwt_required()
def regenerate_seller_token(seller_id):
    current_user = get_jwt_identity()
    if current_user["role"] != "boss":
        return jsonify({"message": "Unauthorized"}), 403
    
    seller = SellerService.get_seller_by_id(seller_id, current_user["id"])
    if not seller:
        return jsonify({"message": "Seller not found"}), 404
    
    regenerated_seller = SellerService.regenerate_seller_token(seller)
    
    return jsonify({"message": "Seller token regenerated successfully", "seller": regenerated_seller.to_dict()}), 200

@seller_bp.route("/sellers/<int:seller_id>", methods=["DELETE"])
@jwt_required()
def delete_seller(seller_id):
    current_user = get_jwt_identity()
    if current_user["role"] != "boss":
        return jsonify({"message": "Unauthorized"}), 403
    
    seller = SellerService.get_seller_by_id(seller_id, current_user["id"])
    if not seller:
        return jsonify({"message": "Seller not found"}), 404
    
    SellerService.delete_seller(seller)
    
    return jsonify({"message": "Seller deleted successfully"}), 204

