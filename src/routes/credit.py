from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models import db, Credit, CreditPayment, Customer, Seller
from src.services.credit_service import CreditService
from datetime import date

credit_bp = Blueprint("credit", __name__)

@credit_bp.route("/credits", methods=["GET"])
@jwt_required()
def get_credits():
    current_user = get_jwt_identity()
    
    credits = CreditService.get_credits(current_user["role"], current_user["id"], current_user.get("boss_id"))
    
    return jsonify([credit.to_dict() for credit in credits]), 200

@credit_bp.route("/credits/<int:credit_id>", methods=["GET"])
@jwt_required()
def get_credit(credit_id):
    current_user = get_jwt_identity()
    
    credit = CreditService.get_credit_by_id(credit_id, current_user["role"], current_user["id"], current_user.get("boss_id"))
    
    if not credit:
        return jsonify({"message": "Credit not found"}), 404
    
    return jsonify(credit.to_dict()), 200

@credit_bp.route("/credits/<int:credit_id>/pay", methods=["POST"])
@jwt_required()
def pay_credit(credit_id):
    current_user = get_jwt_identity()
    
    credit = CreditService.get_credit_by_id(credit_id, current_user["role"], current_user["id"], current_user.get("boss_id"))
    
    if not credit:
        return jsonify({"message": "Credit not found"}), 404
    
    if credit.is_paid:
        return jsonify({"message": "Credit already fully paid"}), 400
    
    data = request.get_json()
    amount = data.get("amount")
    payment_date_str = data.get("payment_date")
    local_id = data.get("local_id")
    
    if not amount:
        return jsonify({"message": "Missing payment amount"}), 400
    
    new_payment, error = CreditService.pay_credit(credit, amount, payment_date_str, local_id)
    
    if error:
        return jsonify({"message": error}), 400
    
    return jsonify({"message": "Payment recorded successfully", "credit": credit.to_dict()}), 200

@credit_bp.route("/credits/<int:credit_id>/payments", methods=["GET"])
@jwt_required()
def get_credit_payments(credit_id):
    current_user = get_jwt_identity()
    
    payments = CreditService.get_credit_payments(credit_id, current_user["role"], current_user["id"], current_user.get("boss_id"))
    
    if payments is None:
        return jsonify({"message": "Credit not found"}), 404
    
    return jsonify([payment.to_dict() for payment in payments]), 200


