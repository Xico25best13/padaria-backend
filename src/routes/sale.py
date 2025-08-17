from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models import db, Sale, SaleItem, Product, Customer, Seller, Credit, SalesGuide
from src.services.sale_service import SaleService
from datetime import date

sale_bp = Blueprint("sale", __name__)

@sale_bp.route("/sales", methods=["POST"])
@jwt_required()
def create_sale():
    current_user = get_jwt_identity()
    if current_user["role"] != "seller":
        return jsonify({"message": "Unauthorized"}), 403
    
    seller_id = current_user["id"]
    boss_id = current_user["boss_id"]
    data = request.get_json()
    
    customer_id = data.get("customer_id")
    payment_type = data.get("payment_type")
    sale_date_str = data.get("sale_date")
    items_data = data.get("items")
    local_id = data.get("local_id")
    guide_id = data.get("guide_id")
    
    if not all([payment_type, items_data]):
        return jsonify({"message": "Missing payment type or items data"}), 400
    
    if payment_type not in ["cash", "credit"]:
        return jsonify({"message": "Invalid payment type"}), 400
    
    new_sale, error = SaleService.create_sale(seller_id, customer_id, payment_type, sale_date_str, items_data, local_id, guide_id, boss_id)
    
    if error:
        return jsonify({"message": error}), 400
    
    return jsonify({"message": "Sale created successfully", "sale": new_sale.to_dict()}), 201

@sale_bp.route("/sales", methods=["GET"])
@jwt_required()
def get_sales():
    current_user = get_jwt_identity()
    
    sales = SaleService.get_sales(current_user["role"], current_user["id"], current_user.get("boss_id"))
    
    return jsonify([sale.to_dict() for sale in sales]), 200

@sale_bp.route("/sales/<int:sale_id>", methods=["GET"])
@jwt_required()
def get_sale(sale_id):
    current_user = get_jwt_identity()
    
    sale = SaleService.get_sale_by_id(sale_id, current_user["role"], current_user["id"], current_user.get("boss_id"))
    
    if not sale:
        return jsonify({"message": "Sale not found"}), 404
    
    return jsonify(sale.to_dict()), 200

@sale_bp.route("/sales/<int:sale_id>", methods=["DELETE"])
@jwt_required()
def delete_sale(sale_id):
    current_user = get_jwt_identity()
    
    sale = SaleService.get_sale_by_id(sale_id, current_user["role"], current_user["id"], current_user.get("boss_id"))
    
    if not sale:
        return jsonify({"message": "Sale not found"}), 404
    
    SaleService.delete_sale(sale)
    
    return jsonify({"message": "Sale deleted successfully"}), 204


