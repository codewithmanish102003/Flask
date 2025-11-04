from flask import Flask, request, jsonify

app = Flask(__name__)

users = {
    "manish@example.com": {"password": "12345", "role": "admin"},
    "student@example.com": {"password": "abcde", "role": "user"},
}

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    user = users.get(email)

    if user and user["password"] == password:
        return jsonify({"message": "Authenticated successfully", "role": user["role"]})
    return jsonify({"error": "Invalid credentials"}), 401

@app.route("/admin")
def admin_panel():
    return jsonify({"message": "Welcome to admin panel! Only admins should access this."})

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)