from flask import Flask, request, jsonify
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from bson import ObjectId
from functools import wraps

# ---------------------------------
# CONFIGURATION
# ---------------------------------
app = Flask(__name__)
app.config["SECRET_KEY"] = "supersecretkey"

# MongoDB Connection
client = MongoClient("mongodb://localhost:27017/")
db = client["flask_rbac_db"]
users_collection = db["users"]

# ---------------------------------
# TOKEN VALIDATION DECORATOR
# ---------------------------------
def token_required(role=None):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            token = None
            if "Authorization" in request.headers:
                token = request.headers["Authorization"].split(" ")[1]

            if not token:
                return jsonify({"error": "Token missing!"}), 401

            try:
                data = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
                current_user = users_collection.find_one({"_id": ObjectId(data["user_id"])})
                if not current_user:
                    return jsonify({"error": "User not found"}), 404

                # Check if route has role restriction
                if role and current_user["role"] != role:
                    return jsonify({"error": "Access denied: Insufficient permissions"}), 403

            except Exception as e:
                return jsonify({"error": "Invalid or expired token", "details": str(e)}), 401

            return f(current_user, *args, **kwargs)
        return decorated
    return decorator

# ---------------------------------
# REGISTER ROUTE
# ---------------------------------
@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    role = data.get("role", "user")  # default role: user

    if users_collection.find_one({"email": email}):
        return jsonify({"error": "User already exists"}), 400

    hashed_password = generate_password_hash(password)
    users_collection.insert_one({
        "email": email,
        "password": hashed_password,
        "role": role
    })

    return jsonify({"message": f"User registered successfully as {role}"}), 201

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

    # Generate JWT with role embedded
    token = jwt.encode({
        "user_id": str(user["_id"]),
        "role": user["role"],
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }, app.config["SECRET_KEY"], algorithm="HS256")

    return jsonify({
        "message": "Login successful",
        "role": user["role"],
        "token": token
    }), 200

# ---------------------------------
# PROTECTED ROUTES
# ---------------------------------

@app.route("/dashboard", methods=["GET"])
@token_required()
def dashboard(current_user):
    return jsonify({
        "message": f"Welcome, {current_user['email']}!",
        "role": current_user["role"]
    })

# ✅ Admin-only route
@app.route("/admin/users", methods=["GET"])
@token_required(role="admin")
def admin_users(current_user):
    users = list(users_collection.find({}, {"password": 0}))
    for u in users:
        u["_id"] = str(u["_id"])
    return jsonify({
        "admin": current_user["email"],
        "users": users
    })

# ✅ User-only route
@app.route("/profile", methods=["GET"])
@token_required(role="user")
def user_profile(current_user):
    return jsonify({
        "email": current_user["email"],
        "role": current_user["role"]
    })

# ---------------------------------
# RUN SERVER
# ---------------------------------
if __name__ == "__main__":
    app.run(debug=True)
