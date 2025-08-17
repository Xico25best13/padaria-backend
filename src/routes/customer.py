from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models import db, Customer, Boss, Seller
from src.services.customer_service import CustomerService

customer_bp = Blueprint("customer", __name__)

@customer_bp.route("/customers", methods=["POST"])
@jwt_required()
def create_customer():
    current_user = get_jwt_identity()
    
    if current_user["role"] == "boss":
        boss_id = current_user["id"]
    elif current_user["role"] == "seller":
        boss_id = current_user["boss_id"]
    else:
        return jsonify({"message": "Unauthorized"}), 403
    
    data = request.get_json()
    name = data.get("name")
    address = data.get("address")
    phone = data.get("phone")
    
    if not name:
        return jsonify({"message": "Missing customer name"}), 400
    
    new_customer = CustomerService.create_customer(boss_id, name, address, phone)
    
    return jsonify({"message": "Customer created successfully", "customer": new_customer.to_dict()}), 201

@customer_bp.route("/customers", methods=["GET"])
@jwt_required()
def get_customers():
    current_user = get_jwt_identity()
    
    if current_user["role"] == "boss":
        customers = CustomerService.get_customers_by_boss(current_user["id"])
    elif current_user["role"] == "seller":
        customers = CustomerService.get_customers_by_boss(current_user["boss_id"])
    else:
        return jsonify({"message": "Unauthorized"}), 403
    
    return jsonify([customer.to_dict() for customer in customers]), 200

@customer_bp.route("/customers/<int:customer_id>", methods=["GET"])
@jwt_required()
def get_customer(customer_id):
    current_user = get_jwt_identity()
    
    if current_user["role"] == "boss":
        customer = CustomerService.get_customer_by_id(customer_id, current_user["id"])
    elif current_user["role"] == "seller":
        customer = CustomerService.get_customer_by_id(customer_id, current_user["boss_id"])
    else:
        return jsonify({"message": "Unauthorized"}), 403
    
    if not customer:
        return jsonify({"message": "Customer not found"}), 404
    
    return jsonify(customer.to_dict()), 200

@customer_bp.route("/customers/<int:customer_id>", methods=["PUT"])
@jwt_required()
def update_customer(customer_id):
    current_user = get_jwt_identity()
    
    if current_user["role"] == "boss":
        customer = CustomerService.get_customer_by_id(customer_id, current_user["id"])
    elif current_user["role"] == "seller":
        customer = CustomerService.get_customer_by_id(customer_id, current_user["boss_id"])
    else:
        return jsonify({"message": "Unauthorized"}), 403
    
    if not customer:
        return jsonify({"message": "Customer not found"}), 404
    
    data = request.get_json()
    updated_customer = CustomerService.update_customer(customer, name=data.get("name"), address=data.get("address"), phone=data.get("phone"))
    
    return jsonify({"message": "Customer updated successfully", "customer": updated_customer.to_dict()}), 200

@customer_bp.route("/customers/<int:customer_id>", methods=["DELETE"])
@jwt_required()
def delete_customer(customer_id):
    current_user = get_jwt_identity()
    
    if current_user["role"] == "boss":
        customer = CustomerService.get_customer_by_id(customer_id, current_user["id"])
    elif current_user["role"] == "seller":
        customer = CustomerService.get_customer_by_id(customer_id, current_user["boss_id"])
    else:
        return jsonify({"message": "Unauthorized"}), 403
    
    if not customer:
        return jsonify({"message": "Customer not found"}), 404
    
    CustomerService.delete_customer(customer)
    
    return jsonify({"message": "Customer deleted successfully"}), 204

