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
app.config["SECRET_KEY"] = "supersecretkey"  # use .env in production

# MongoDB Connection
client = MongoClient("mongodb://localhost:27017/")
db = client["flask_jwt_db"]
users_collection = db["users"]

# ---------------------------------
# JWT TOKEN DECORATOR
# ---------------------------------
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # JWT token usually comes from Authorization Header
        if "Authorization" in request.headers:
            token = request.headers["Authorization"].split(" ")[1]

        if not token:
            return jsonify({"error": "Token missing!"}), 401

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
@app.route("/logout", methods=["POST"])
def logout():
    return jsonify({"message": "Logout successful. Just remove token from frontend."}), 200

# ---------------------------------
# RUN SERVER
# ---------------------------------
if __name__ == "__main__":
    app.run(debug=True)
