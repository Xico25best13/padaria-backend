from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models import db, SalesGuide, GuideItem, Product, Seller
from src.services.guide_service import GuideService
from datetime import date

guide_bp = Blueprint("guide", __name__)

@guide_bp.route("/guides", methods=["POST"])
@jwt_required()
def create_guide():
    current_user = get_jwt_identity()
    if current_user["role"] != "seller":
        return jsonify({"message": "Unauthorized"}), 403
    
    seller_id = current_user["id"]
    boss_id = current_user["boss_id"]
    data = request.get_json()
    
    guide_date_str = data.get("guide_date")
    notes = data.get("notes")
    items_data = data.get("items")
    local_id = data.get("local_id")
    
    if not items_data:
        return jsonify({"message": "Missing items data for guide"}), 400
    
    new_guide, error = GuideService.create_guide(seller_id, guide_date_str, notes, items_data, local_id, boss_id)
    
    if error:
        return jsonify({"message": error}), 400
    
    return jsonify({"message": "Sales Guide created successfully", "guide": new_guide.to_dict()}), 201

@guide_bp.route("/guides", methods=["GET"])
@jwt_required()
def get_guides():
    current_user = get_jwt_identity()
    
    guides = GuideService.get_guides(current_user["role"], current_user["id"], current_user.get("boss_id"))
    
    return jsonify([guide.to_dict() for guide in guides]), 200

@guide_bp.route("/guides/<int:guide_id>", methods=["GET"])
@jwt_required()
def get_guide(guide_id):
    current_user = get_jwt_identity()
    
    guide = GuideService.get_guide_by_id(guide_id, current_user["role"], current_user["id"], current_user.get("boss_id"))
    
    if not guide:
        return jsonify({"message": "Sales Guide not found"}), 404
    
    return jsonify(guide.to_dict()), 200

@guide_bp.route("/guides/<int:guide_id>/close", methods=["PUT"])
@jwt_required()
def close_guide():
    current_user = get_jwt_identity()
    if current_user["role"] != "seller":
        return jsonify({"message": "Unauthorized"}), 403
    
    guide_id = request.view_args["guide_id"]
    guide = GuideService.get_guide_by_id(guide_id, current_user["role"], current_user["id"], current_user.get("boss_id"))
    
    if not guide:
        return jsonify({"message": "Sales Guide not found"}), 404
    
    data = request.get_json()
    items_data = data.get("items")
    
    if not items_data:
        return jsonify({"message": "Missing items data for closing guide"}), 400
    
    closed_guide, error = GuideService.close_guide(guide, items_data)
    
    if error:
        return jsonify({"message": error}), 400
    
    return jsonify({"message": "Sales Guide closed successfully", "guide": closed_guide.to_dict()}), 200

@guide_bp.route("/guides/<int:guide_id>/items/<int:item_id>", methods=["PUT"])
@jwt_required()
def update_guide_item(guide_id, item_id):
    current_user = get_jwt_identity()
    if current_user["role"] != "seller":
        return jsonify({"message": "Unauthorized"}), 403
    
    guide = GuideService.get_guide_by_id(guide_id, current_user["role"], current_user["id"], current_user.get("boss_id"))
    if not guide:
        return jsonify({"message": "Sales Guide not found"}), 404
    
    data = request.get_json()
    quantity_remaining = data.get("quantity_remaining")
    
    if quantity_remaining is None:
        return jsonify({"message": "Missing quantity_remaining"}), 400
    
    updated_item, error = GuideService.update_guide_item(guide, item_id, quantity_remaining)
    
    if error:
        return jsonify({"message": error}), 400
    
    return jsonify({"message": "Guide Item updated successfully", "item": updated_item.to_dict()}), 200

@guide_bp.route("/guides/<int:guide_id>", methods=["DELETE"])
@jwt_required()
def delete_guide(guide_id):
    current_user = get_jwt_identity()
    if current_user["role"] != "boss":
        return jsonify({"message": "Unauthorized"}), 403
    
    guide = GuideService.get_guide_by_id(guide_id, current_user["role"], current_user["id"], current_user.get("boss_id"))
    if not guide:
        return jsonify({"message": "Sales Guide not found"}), 404
    
    GuideService.delete_guide(guide)
    
    return jsonify({"message": "Sales Guide deleted successfully"}), 204


