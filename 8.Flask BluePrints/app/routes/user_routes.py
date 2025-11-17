from flask import Blueprint, current_app, jsonify, request

user_bp = Blueprint('user_bp', __name__)

@user_bp.route('/profile', methods=['GET'])
def get_profile():
    return jsonify({"message": "User profile endpoint"})

@user_bp.route('/health', methods=['GET'])
def health_check():
    # Simple health check endpoint
    return jsonify({
        "status": "healthy",
        "message": "Flask application is running"
    }), 200
