import os
from flask import Flask
from .config import config
from .routes.auth_routes import auth_bp
from .routes.main_routes import main_bp
from .routes.user_routes import user_bp
from .utils.db_connect import get_db
from .utils.exception_handler import register_error_handlers
from .utils.logger import log_request_info, setup_logging
from .utils.rate_limiter import init_rate_limiter


def create_app(config_name=None):
    app = Flask(__name__)
    config_name = config_name or os.getenv('FLASK_CONFIG', 'default')
    app.config.from_object(config[config_name])
    app.secret_key = app.config['SECRET_KEY']
    db = get_db(app.config['MONGO_URI'])
    setattr(app, 'db', db)
    setup_logging(app)
    log_request_info(app)
    register_error_handlers(app)
    limiter = init_rate_limiter(app)
    setattr(app, 'limiter', limiter)
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(main_bp)
    app.register_blueprint(user_bp, url_prefix='/api/users')

    app.logger.info('Flask application initialized')
    return app