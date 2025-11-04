from flask import (Flask, current_app, jsonify, redirect, render_template,
                   request, url_for)
from flask_login import (LoginManager, UserMixin, current_user, login_required,
                         login_user, logout_user)

app = Flask(__name__)
app.secret_key = "supersecretkey" # Required for session cookies 

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"  # Redirects to /login if unauthorized

# Mock database
users = {
    "manish@example.com": {"password": "12345", "role": "admin"},
    "student@example.com": {"password": "abcde", "role": "user"},
}

# User model
class User(UserMixin):
    def __init__(self, email):
        self.id = email
        self.role = users[email]["role"]

@login_manager.user_loader
def load_user(user_id):
    if user_id in users:
        return User(user_id)
    return None

@app.context_processor
def inject_auth_urls():
    def build_url(candidates):
        for ep in candidates:
            if ep in current_app.view_functions:
                try:
                    return url_for(ep)
                except Exception:
                    pass
        return None

    return {
        "login_url": build_url(["auth.login", "login"]),
        "register_url": build_url(["auth.register", "register"]),
        "logout_url": build_url(["auth.logout", "logout"]),
        "dashboard_url": build_url(["auth.dashboard", "dashboard"]),
        "has_auth": "auth" in current_app.blueprints,
    }

# Routes


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        data = request.get_json()
        email = data.get("email")
        password = data.get("password")

        if email in users and users[email]["password"] == password:
            user = User(email)
            login_user(user)
            return jsonify({"message": "Login successful", "user": email})
        return jsonify({"error": "Invalid credentials"}), 401
    return render_template("login.html")

@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", user=current_user)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)