from flask import Flask, request, jsonify
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from bson import ObjectId
from functools import wraps

# ---------------------------------
# APP CONFIG
# ---------------------------------
app = Flask(__name__)
app.config["SECRET_KEY"] = "supersecretkey"  # use env var in production

# ---------------------------------
# MONGO CONNECTION
# ---------------------------------
client = MongoClient("mongodb://localhost:27017/")
db = client["flask_full_auth_db"]
users_collection = db["users"]

# ---------------------------------
# TOKEN VALIDATOR DECORATOR
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

                # Role check (optional)
                if role and current_user["role"] != role:
                    return jsonify({"error": "Access denied: Insufficient permissions"}), 403

            except Exception as e:
                return jsonify({"error": "Invalid or expired token", "details": str(e)}), 401

            return f(current_user, *args, **kwargs)
        return decorated
    return decorator

# ---------------------------------
# REGISTER
# ---------------------------------
@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    role = data.get("role", "user")

    if not email or not password:
        return jsonify({"error": "Missing email or password"}), 400

    if users_collection.find_one({"email": email}):
        return jsonify({"error": "User already exists"}), 400

    hashed_password = generate_password_hash(password)
    users_collection.insert_one({
        "email": email,
        "password": hashed_password,
        "role": role,
        "created_at": datetime.datetime.utcnow()
    })

    return jsonify({"message": f"User registered successfully as {role}"}), 201

# ---------------------------------
# LOGIN
# ---------------------------------
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    user = users_collection.find_one({"email": email})
    if not user or not check_password_hash(user["password"], password):
        return jsonify({"error": "Invalid credentials"}), 401

    token = jwt.encode({
        "user_id": str(user["_id"]),
        "role": user["role"],
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=2)
    }, app.config["SECRET_KEY"], algorithm="HS256")

    return jsonify({
        "message": "Login successful",
        "token": token,
        "role": user["role"]
    })

# ---------------------------------
# GET PROFILE
# ---------------------------------
@app.route("/profile", methods=["GET"])
@token_required()
def profile(current_user):
    user_data = {
        "id": str(current_user["_id"]),
        "email": current_user["email"],
        "role": current_user["role"]
    }
    return jsonify(user_data)

# ---------------------------------
# UPDATE USER (SELF or ADMIN)
# ---------------------------------
@app.route("/update", methods=["PUT"])
@token_required()
def update_user(current_user):
    data = request.get_json()
    new_email = data.get("email")
    new_password = data.get("password")

    update_data = {}
    if new_email:
        update_data["email"] = new_email
    if new_password:
        update_data["password"] = generate_password_hash(new_password)

    if update_data:
        users_collection.update_one({"_id": current_user["_id"]}, {"$set": update_data})
        return jsonify({"message": "Profile updated successfully"})

    return jsonify({"message": "No changes made"})

# ---------------------------------
# DELETE USER (Only Admin)
# ---------------------------------
@app.route("/delete/<user_id>", methods=["DELETE"])
@token_required(role="admin")
def delete_user(current_user, user_id):
    result = users_collection.delete_one({"_id": ObjectId(user_id)})
    if result.deleted_count == 0:
        return jsonify({"error": "User not found"}), 404
    return jsonify({"message": "User deleted successfully"})

# ---------------------------------
# GET ALL USERS (Admin Only)
# ---------------------------------
@app.route("/users", methods=["GET"])
@token_required(role="admin")
def get_all_users(current_user):
    users = list(users_collection.find({}, {"password": 0}))
    for user in users:
        user["_id"] = str(user["_id"])
    return jsonify(users)

# ---------------------------------
# RUN SERVER
# ---------------------------------
if __name__ == "__main__":
    app.run(debug=True)
