from flask import jsonify
from werkzeug.exceptions import HTTPException
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from marshmallow import ValidationError
import logging

logger = logging.getLogger(__name__)

def register_error_handlers(app):
    """Register error handlers for the application."""
    
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'status': 'error',
            'message': 'Bad request',
            'details': str(error)
        }), 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({
            'status': 'error',
            'message': 'Unauthorized',
            'details': str(error)
        }), 401
    
    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({
            'status': 'error',
            'message': 'Forbidden',
            'details': str(error)
        }), 403
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'status': 'error',
            'message': 'Resource not found',
            'details': str(error)
        }), 404
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            'status': 'error',
            'message': 'Method not allowed',
            'details': str(error)
        }), 405
    
    @app.errorhandler(409)
    def conflict(error):
        return jsonify({
            'status': 'error',
            'message': 'Resource conflict',
            'details': str(error)
        }), 409
    
    @app.errorhandler(422)
    def unprocessable_entity(error):
        return jsonify({
            'status': 'error',
            'message': 'Unprocessable entity',
            'details': str(error)
        }), 422
    
    @app.errorhandler(429)
    def too_many_requests(error):
        return jsonify({
            'status': 'error',
            'message': 'Too many requests',
            'details': str(error)
        }), 429
    
    @app.errorhandler(500)
    def internal_server_error(error):
        logger.error(f"Internal server error: {error}")
        return jsonify({
            'status': 'error',
            'message': 'Internal server error',
            'details': str(error) if app.debug else 'An unexpected error occurred'
        }), 500
    
    @app.errorhandler(HTTPException)
    def handle_http_exception(error):
        return jsonify({
            'status': 'error',
            'message': error.description,
            'details': str(error)
        }), error.code
    
    @app.errorhandler(ValidationError)
    def handle_validation_error(error):
        return jsonify({
            'status': 'error',
            'message': 'Validation error',
            'details': error.messages
        }), 422
    
    @app.errorhandler(SQLAlchemyError)
    def handle_db_error(error):
        logger.error(f"Database error: {error}")
        return jsonify({
            'status': 'error',
            'message': 'Database error',
            'details': str(error) if app.debug else 'A database error occurred'
        }), 500
    
    @app.errorhandler(IntegrityError)
    def handle_integrity_error(error):
        logger.error(f"Integrity error: {error}")
        return jsonify({
            'status': 'error',
            'message': 'Data integrity error',
            'details': str(error) if app.debug else 'A data integrity error occurred'
        }), 409
    
    @app.errorhandler(Exception)
    def handle_exception(error):
        logger.error(f"Unhandled exception: {error}")
        return jsonify({
            'status': 'error',
            'message': 'An unexpected error occurred',
            'details': str(error) if app.debug else 'An unexpected error occurred'
        }), 500 