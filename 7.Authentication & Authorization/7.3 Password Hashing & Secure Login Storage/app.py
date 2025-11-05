from flask import Flask, request, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient
from bson import ObjectId

app = Flask(__name__)
app.secret_key = "supersecretkey"

# -------------------------------
# MongoDB Connection
# -------------------------------
client = MongoClient("mongodb://localhost:27017/") 
db = client["flask_auth_db"]
users_collection = db["users"]

# -------------------------------
# Flask-Login Setup
# -------------------------------
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# -------------------------------
# User Model
# -------------------------------
class User(UserMixin):
    def __init__(self, user_data):
        self.id = str(user_data["_id"])
        self.email = user_data["email"]

@login_manager.user_loader
def load_user(user_id):
    user_data = users_collection.find_one({"_id": ObjectId(user_id)})
    return User(user_data) if user_data else None

# -------------------------------
# Routes
# -------------------------------

# ✅ Register User
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


# ✅ Login User
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    user_data = users_collection.find_one({"email": email})
    if not user_data or not check_password_hash(user_data["password"], password):
        return jsonify({"error": "Email or password is incorrect"}), 401

    user_obj = User(user_data)
    login_user(user_obj)

    return jsonify({"message": "Login successful", "user_id": user_obj.id})


# Protected Route (Dashboard)
@app.route("/dashboard")
@login_required
def dashboard():
    return jsonify({"message": f"Welcome, {current_user.email}!", "user_id": current_user.id})


# Logout
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Logged out successfully"})


# List All Users (Admin Testing)
@app.route("/users", methods=["GET"])
def get_all_users():
    users = list(users_collection.find({}, {"password": 0}))
    for user in users:
        user["_id"] = str(user["_id"])
    return jsonify(users)


if __name__ == "__main__":
    app.run(debug=True)
