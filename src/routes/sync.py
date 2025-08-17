from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models import db, SyncQueue, SyncLog, Sale, SaleItem, Credit, CreditPayment, SalesGuide, GuideItem, Product, Customer
from src.services.sync_service import SyncService
from datetime import datetime

sync_bp = Blueprint("sync", __name__)

@sync_bp.route("/sync/upload", methods=["POST"])
@jwt_required()
def upload_sync_data():
    current_user = get_jwt_identity()
    if current_user["role"] != "seller":
        return jsonify({"message": "Unauthorized"}), 403
    
    seller_id = current_user["id"]
    boss_id = current_user["boss_id"]
    data = request.get_json()
    sync_operations = data.get("operations", [])
    
    if not sync_operations:
        return jsonify({"message": "No operations to sync"}), 200
    
    results, error = SyncService.process_upload_operations(seller_id, sync_operations, boss_id)
    
    if error:
        return jsonify({"message": error}), 500
    
    return jsonify({"message": "Sync upload completed", "results": results}), 200

@sync_bp.route("/sync/download", methods=["GET"])
@jwt_required()
def download_sync_data():
    current_user = get_jwt_identity()
    if current_user["role"] != "seller":
        return jsonify({"message": "Unauthorized"}), 403
    
    seller_id = current_user["id"]
    boss_id = current_user["boss_id"]
    
    data, error = SyncService.get_download_data(seller_id, boss_id)
    
    if error:
        return jsonify({"message": error}), 500
    
    return jsonify(data), 200


