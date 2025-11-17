from functools import wraps

import jwt
from flask import (Blueprint, current_app, jsonify, redirect, render_template,
                   request, session, url_for)

main_bp = Blueprint('main_bp', __name__)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = session.get('token')
        
        if not token:
            return redirect(url_for('main_bp.login_page'))
        
        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            db = getattr(current_app, 'db')
            user_data = db.users.find_one({"email": data['email']})
            
            if not user_data:
                return redirect(url_for('main_bp.login_page'))
            
            # Store user data in session for use in the route
            session['user'] = {
                'email': user_data['email'],
                'role': user_data.get('role', 'user')
            }
        except:
            # If token is invalid, redirect to login
            return redirect(url_for('main_bp.login_page'))
        
        return f(*args, **kwargs)
    
    return decorated

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/login')
def login_page():
    if 'token' in session:
        return redirect(url_for('main_bp.dashboard'))
    return render_template('login.html')

@main_bp.route('/register')
def register_page():
    return render_template('register.html')

@main_bp.route('/dashboard')
def dashboard_redirect():
    token = session.get('token')
    if not token:
        return render_template('dashboard_redirect.html')

    return redirect(url_for('main_bp.dashboard_protected'))

@main_bp.route('/dashboard/protected')
@token_required
def dashboard_protected():
    user = session.get('user')
    return render_template('dashboard.html', user=user)

@main_bp.route('/set-session-token', methods=['POST'])
def set_session_token():
    data = request.get_json()
    token = data.get('token')
    
    if token:
        session['token'] = token
        try:
            user_data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            db = getattr(current_app, 'db')
            db_user = db.users.find_one({"email": user_data['email']})
            
            if not db_user:
                return jsonify({"message": "User not found"}), 404
                
            session['user'] = {
                'email': db_user['email'],
                'role': db_user.get('role', 'user')
            }
            return jsonify({"message": "Session token set successfully"}), 200
        except Exception as e:
            return jsonify({"message": f"Invalid token: {str(e)}"}), 400
    
    return jsonify({"message": "No token provided"}), 400

@main_bp.route('/logout')
def logout():
    session.pop('token', None)
    session.pop('user', None)
    return redirect(url_for('main_bp.login_page'))