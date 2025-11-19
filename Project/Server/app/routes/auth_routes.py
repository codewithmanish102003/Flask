import datetime

from bson.objectid import ObjectId
from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import (create_access_token, get_jwt_identity,
                                jwt_required)
from werkzeug.security import check_password_hash, generate_password_hash

from ..models.user_model import User

auth_bp = Blueprint('auth_bp', __name__)

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.json
    username = data.get("username")
    password = data.get("password")
    if not username or not password:
        return jsonify({"msg":"username and password required"}), 400
    
    db = current_app.db
    if db.users.find_one({"username": username}):
        return jsonify({"msg":"username taken"}), 400
    
    user = User(username=username, password=password)
    res = db.users.insert_one(user.to_dict())
    return jsonify({"msg":"registered"}), 201

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")
    
    db = current_app.db
    user_data = db.users.find_one({"username": username})
    if not user_data or not check_password_hash(user_data["password"], password):
        return jsonify({"msg":"bad credentials"}), 401
    
    token = create_access_token(
        identity=str(user_data["_id"]), 
        expires_delta=datetime.timedelta(days=7)
    )
    return jsonify({
        "access_token": token, 
        "username": user_data["username"], 
        "id": str(user_data["_id"])
    }), 200