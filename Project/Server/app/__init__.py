import os

from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from pymongo import MongoClient

# Load environment variables
load_dotenv()

# Import config
from config import Config


def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config.from_object(Config)
    
    # Initialize extensions
    jwt = JWTManager(app)
    CORS(app)
    
    # Database connection
    client = MongoClient(app.config["MONGO_URI"])
    db = client.get_default_database()
    setattr(app, 'db', db)
    
    # Register blueprints
    from .routes.auth_routes import auth_bp
    from .routes.note_routes import note_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(note_bp, url_prefix='/api/notes')
    
    return app