import traceback
from flask import jsonify
from marshmallow import ValidationError


class CustomAPIException(Exception):
    """Custom API exception class."""
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv

def register_error_handlers(app):
    """Register global error handlers."""
    
    @app.errorhandler(CustomAPIException)
    def handle_custom_exception(error):
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        app.logger.error(f"CustomAPIException: {error.message}")
        return response

    @app.errorhandler(ValidationError)
    def handle_validation_error(error):
        response = jsonify({
            "message": "Validation error",
            "errors": error.messages
        })
        response.status_code = 400
        app.logger.error(f"ValidationError: {error.messages}")
        return response

    @app.errorhandler(404)
    def not_found(error):
        response = jsonify({
            "message": "Resource not found"
        })
        response.status_code = 404
        app.logger.error(f"404 Error: {error}")
        return response

    @app.errorhandler(500)
    def internal_error(error):
        response = jsonify({
            "message": "Internal server error"
        })
        response.status_code = 500
        app.logger.error(f"500 Error: {error}", exc_info=True)
        return response

    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        response = jsonify({
            "message": "An unexpected error occurred"
        })
        response.status_code = 500
        app.logger.error(f"Unexpected error: {str(error)}", exc_info=True)
        return response