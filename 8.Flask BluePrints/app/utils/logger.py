import logging
import os
import time
from logging.handlers import RotatingFileHandler

from flask import g, request


def setup_logging(app):
    """Set up logging for the application."""
    log_dir = os.path.dirname(app.config['LOG_FILE'])
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Configure root logger
    logging.basicConfig(
        level=app.config['LOG_LEVEL'],
        format='%(asctime)s %(levelname)s %(name)s %(message)s'
    )
    
    # Create file handler for general logs
    file_handler = RotatingFileHandler(
        app.config['LOG_FILE'], 
        maxBytes=10240000,  # 10MB
        backupCount=10
    )
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(app.config['LOG_LEVEL'])
    
    # Add handler to app logger
    app.logger.addHandler(file_handler)
    app.logger.setLevel(app.config['LOG_LEVEL'])
    app.logger.info('Application startup')

def log_request_info(app):
    """Log information about each request."""
    @app.before_request
    def before_request():
        g.start_time = time.time()
        app.logger.info(f"Request: {request.method} {request.url} from {request.remote_addr}")

    @app.after_request
    def after_request(response):
        duration = time.time() - g.start_time
        app.logger.info(f"Response: {response.status_code} for {request.method} {request.url} "
                       f"[Duration: {duration:.4f}s]")
        return response

def log_error(app, error):
    """Log error information."""
    app.logger.error(f"Error occurred: {str(error)}", exc_info=True)