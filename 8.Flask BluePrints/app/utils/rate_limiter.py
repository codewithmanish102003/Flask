import logging

from flask import jsonify, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address


def init_rate_limiter(app):
    """Initialize rate limiter for the application."""
    limiter = Limiter(
        get_remote_address,
        app=app,
        storage_uri=app.config['RATELIMIT_STORAGE_URL'],
        default_limits=[app.config['DEFAULT_RATE_LIMIT']]
    )
    
    # Register a custom error handler for rate limit exceeded
    @app.errorhandler(429)
    def ratelimit_handler(e):
        app.logger.warning(f"Rate limit exceeded for IP: {get_remote_address()}")
        return jsonify({
            "message": "Rate limit exceeded",
            "retry_after": str(e.description)
        }), 429
    
    return limiter

def get_client_ip():
    """Get the real IP address of the client."""
    x_forwarded_for = request.headers.get('X-Forwarded-For')
    if x_forwarded_for:
        # Get the first IP if there are multiple (comma-separated)
        return x_forwarded_for.split(',')[0].strip()
    elif request.headers.get('X-Real-IP'):
        return request.headers.get('X-Real-IP')
    else:
        return request.remote_addr