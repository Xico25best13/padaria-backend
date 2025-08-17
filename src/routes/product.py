from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models import db, Product, Boss
from src.services.product_service import ProductService

product_bp = Blueprint("product", __name__)

@product_bp.route("/products", methods=["POST"])
@jwt_required()
def create_product():
    current_user = get_jwt_identity()
    if current_user["role"] != "boss":
        return jsonify({"message": "Unauthorized"}), 403
    
    data = request.get_json()
    name = data.get("name")
    price = data.get("price")
    
    if not all([name, price]):
        return jsonify({"message": "Missing product name or price"}), 400
    
    try:
        price = float(price)
        if price <= 0:
            raise ValueError("Price must be positive")
    except ValueError:
        return jsonify({"message": "Invalid price format"}), 400
    
    new_product = ProductService.create_product(current_user["id"], name, price)
    
    return jsonify({"message": "Product created successfully", "product": new_product.to_dict()}), 201

@product_bp.route("/products", methods=["GET"])
@jwt_required()
def get_products():
    current_user = get_jwt_identity()
    
    if current_user["role"] == "boss":
        products = ProductService.get_products_by_boss(current_user["id"])
    elif current_user["role"] == "seller":
        products = ProductService.get_products_by_boss(current_user["boss_id"], is_active=True)
    else:
        return jsonify({"message": "Unauthorized"}), 403
    
    return jsonify([product.to_dict() for product in products]), 200

@product_bp.route("/products/<int:product_id>", methods=["GET"])
@jwt_required()
def get_product(product_id):
    current_user = get_jwt_identity()
    
    if current_user["role"] == "boss":
        product = ProductService.get_product_by_id(product_id, current_user["id"])
    elif current_user["role"] == "seller":
        product = ProductService.get_product_by_id(product_id, current_user["boss_id"], is_active=True)
    else:
        return jsonify({"message": "Unauthorized"}), 403
    
    if not product:
        return jsonify({"message": "Product not found"}), 404
    
    return jsonify(product.to_dict()), 200

@product_bp.route("/products/<int:product_id>", methods=["PUT"])
@jwt_required()
def update_product(product_id):
    current_user = get_jwt_identity()
    if current_user["role"] != "boss":
        return jsonify({"message": "Unauthorized"}), 403
    
    product = ProductService.get_product_by_id(product_id, current_user["id"])
    if not product:
        return jsonify({"message": "Product not found"}), 404
    
    data = request.get_json()
    name = data.get("name")
    is_active = data.get("is_active")
    price = data.get("price")
    
    if price is not None:
        try:
            price = float(price)
            if price <= 0:
                raise ValueError("Price must be positive")
        except ValueError:
            return jsonify({"message": "Invalid price format"}), 400
    
    updated_product = ProductService.update_product(product, name=name, price=price, is_active=is_active)
    
    return jsonify({"message": "Product updated successfully", "product": updated_product.to_dict()}), 200

@product_bp.route("/products/<int:product_id>", methods=["DELETE"])
@jwt_required()
def delete_product(product_id):
    current_user = get_jwt_identity()
    if current_user["role"] != "boss":
        return jsonify({"message": "Unauthorized"}), 403
    
    product = ProductService.get_product_by_id(product_id, current_user["id"])
    if not product:
        return jsonify({"message": "Product not found"}), 404
    
    ProductService.delete_product(product)
    
    return jsonify({"message": "Product deleted successfully"}), 204

