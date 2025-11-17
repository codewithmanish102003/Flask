import datetime
import jwt
from flask import Blueprint, current_app, jsonify, request
from werkzeug.security import check_password_hash
from ..models.user_model import User
from ..utils.exception_handler import CustomAPIException

auth_bp = Blueprint('auth_bp', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        if not data or not data.get("email") or not data.get("password"):
            raise CustomAPIException("Email and password are required", status_code=400)

        db = getattr(current_app, 'db')
        
        if db.users.find_one({"email": data["email"]}):
            raise CustomAPIException("Email already exists", status_code=400)

        # Create new user using the User model
        user = User(
            email=data["email"],
            password=data["password"],
            role=data.get("role", "user")
        )
        
        # Save user to database
        db.users.insert_one(user.to_dict())
        
        return jsonify({"message": "User registered successfully"}), 201
    except CustomAPIException:
        # Re-raise our custom exceptions
        raise
    except Exception as e:
        # Log the error and raise a custom exception
        current_app.logger.error(f"Registration error: {str(e)}")
        raise CustomAPIException("Registration failed due to internal error", status_code=500)

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        if not data or not data.get("email") or not data.get("password"):
            raise CustomAPIException("Email and password are required", status_code=400)

        db = getattr(current_app, 'db')
        
        # Find user
        user_data = db.users.find_one({"email": data["email"]})
        if not user_data or not check_password_hash(user_data["password"], data["password"]):
            raise CustomAPIException("Invalid credentials", status_code=401)

        # Create User object from database data
        user = User.from_dict(user_data)
        
        # Generate JWT token
        token = jwt.encode({
            'email': user.email,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }, current_app.config['SECRET_KEY'], algorithm='HS256')
        
        return jsonify({
            "message": "Login successful",
            "token": token,
            "user": {
                "email": user.email,
                "role": user.role
            }
        }), 200
    except CustomAPIException:
        raise
    except Exception as e:
        current_app.logger.error(f"Login error: {str(e)}")
        raise CustomAPIException("Login failed due to internal error", status_code=500)