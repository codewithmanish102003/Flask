import datetime
from functools import wraps

import jwt
from bson import ObjectId
from flask import Flask, jsonify, request
from pymongo import MongoClient
from werkzeug.security import check_password_hash, generate_password_hash

# ---------------------------------
# CONFIGURATION
# ---------------------------------
app = Flask(__name__)
app.config["SECRET_KEY"] = "supersecretkey"  # use .env in production

# MongoDB Connection
client = MongoClient("mongodb://localhost:27017/")
db = client["flask_jwt_db"]
users_collection = db["users"]
revoked_tokens = db.revoked_tokens

# ---------------------------------
# JWT TOKEN DECORATOR
# ---------------------------------
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # JWT token usually comes from Authorization Header
        if "Authorization" in request.headers:
            auth_header = request.headers["Authorization"]
            parts = auth_header.split()
            if len(parts) == 2:
                token = parts[1]

        if not token:
            return jsonify({"error": "Token missing!"}), 401

        # check if token was revoked
        if revoked_tokens.find_one({"token": token}):
            return jsonify({"error": "Token has been revoked"}), 401

        try:
            data = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
            current_user = users_collection.find_one({"_id": ObjectId(data["user_id"])})
        except Exception as e:
            return jsonify({"error": "Invalid or expired token", "details": str(e)}), 401

        return f(current_user, *args, **kwargs)
    return decorated

# ---------------------------------
# REGISTER ROUTE
# ---------------------------------
@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if users_collection.find_one({"email": email}):
        return jsonify({"error": "User already exists"}), 400

    hashed_password = generate_password_hash(password)
    users_collection.insert_one({"email": email, "password": hashed_password})

    return jsonify({"message": "User registered successfully"}), 201

# ---------------------------------
# LOGIN ROUTE
# ---------------------------------
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    user = users_collection.find_one({"email": email})
    if not user or not check_password_hash(user["password"], password):
        return jsonify({"error": "Invalid credentials"}), 401

    # Generate JWT token
    token = jwt.encode({
        "user_id": str(user["_id"]),
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }, app.config["SECRET_KEY"], algorithm="HS256")

    return jsonify({"token": token}), 200

# ---------------------------------
# PROTECTED ROUTE (Requires Token)
# ---------------------------------
@app.route("/dashboard", methods=["GET"])
@token_required
def dashboard(current_user):
    return jsonify({
        "message": f"Welcome, {current_user['email']}!",
        "user_id": str(current_user['_id'])
    })

# ---------------------------------
# LOGOUT (Frontend handles token removal)
# ---------------------------------
@app.route('/api/logout', methods=['POST'])
def logout():
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return jsonify({'error': 'Missing token'}), 400

    parts = auth_header.split()
    if len(parts) != 2:
        return jsonify({'error': 'Invalid Authorization header'}), 400

    token = parts[1]

    try:
        decoded = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        # fetch user email from DB (token payload contains user_id)
        user = users_collection.find_one({"_id": ObjectId(decoded.get("user_id"))})
        revoked_tokens.insert_one({
            "token": token,
            "email": user["email"] if user else None,
            "revoked_at": datetime.datetime.utcnow()
        })
        return jsonify({'message': 'Logout successful, token revoked'}), 200
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Token already expired'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Invalid token'}), 401
# ---------------------------------
# RUN SERVER
# ---------------------------------
if __name__ == "__main__":
    # disable the reloader on Windows to avoid socket-related OSError during restarts
    app.run(debug=True, use_reloader=False)
