from flask import request, g, jsonify, current_app
from functools import wraps
import time
import secrets
from datetime import datetime, timedelta
from collections import defaultdict

# Rate limiting storage
rate_limit_storage = defaultdict(lambda: {'count': 0, 'reset_time': datetime.now()})

def add_security_headers(response):
    """Add security headers to the response."""
    # Prevent clickjacking
    response.headers['X-Frame-Options'] = 'DENY'
    
    # Enable XSS protection
    response.headers['X-XSS-Protection'] = '1; mode=block'
    
    # Prevent MIME type sniffing
    response.headers['X-Content-Type-Options'] = 'nosniff'
    
    # Set strict transport security
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    
    # Set content security policy
    response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self' data:; connect-src 'self' wss: ws:;"
    
    # Set referrer policy
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    
    # Set permissions policy
    response.headers['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
    
    return response

def request_id_middleware():
    """Add a unique request ID to each request."""
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            # Generate a unique request ID
            g.request_id = secrets.token_hex(16)
            return f(*args, **kwargs)
        return wrapped
    return decorator

def timing_middleware():
    """Track request timing."""
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            # Start timing
            start_time = time.time()
            
            # Process the request
            response = f(*args, **kwargs)
            
            # Calculate duration
            duration = time.time() - start_time
            
            # Add timing header
            if hasattr(response, 'headers'):
                response.headers['X-Request-Time'] = f"{duration:.3f}s"
            
            return response
        return wrapped
    return decorator

def cors_middleware():
    """Handle CORS preflight requests."""
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            # Handle preflight requests
            if request.method == 'OPTIONS':
                response = app.make_default_options_response()
                response.headers['Access-Control-Allow-Origin'] = '*'
                response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
                response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
                response.headers['Access-Control-Max-Age'] = '3600'
                return response
            
            # Process the request
            response = f(*args, **kwargs)
            
            # Add CORS headers to the response
            if hasattr(response, 'headers'):
                response.headers['Access-Control-Allow-Origin'] = '*'
                response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
                response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
            
            return response
        return wrapped
    return decorator

def rate_limit(limit=100, per=60):
    """
    Rate limiting decorator.
    :param limit: Maximum number of requests allowed
    :param per: Time window in seconds
    """
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            # Get client identifier (IP or API key)
            client_id = request.headers.get('X-API-Key') or request.remote_addr
            
            # Get current time
            now = datetime.now()
            
            # Get or initialize rate limit data for this client
            rate_data = rate_limit_storage[client_id]
            
            # Reset counter if time window has passed
            if now > rate_data['reset_time']:
                rate_data['count'] = 0
                rate_data['reset_time'] = now + timedelta(seconds=per)
            
            # Check if rate limit exceeded
            if rate_data['count'] >= limit:
                return jsonify({
                    'error': 'Rate limit exceeded',
                    'message': f'Please try again in {int((rate_data["reset_time"] - now).total_seconds())} seconds'
                }), 429
            
            # Increment counter
            rate_data['count'] += 1
            
            return f(*args, **kwargs)
        return wrapped
    return decorator

def validate_api_key():
    """Validate API key for protected endpoints."""
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            api_key = request.headers.get('X-API-Key')
            if not api_key:
                return jsonify({
                    'status': 'error',
                    'message': 'API key is required'
                }), 401
            
            # Validate against configured API keys
            valid_keys = current_app.config.get('API_KEYS', [])
            if api_key not in valid_keys:
                return jsonify({
                    'status': 'error',
                    'message': 'Invalid API key'
                }), 401
            
            return f(*args, **kwargs)
        return wrapped
    return decorator

def sanitize_request_data():
    """Sanitize request data to prevent XSS and injection attacks."""
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if request.is_json:
                data = request.get_json()
                if data:
                    # Sanitize string values
                    sanitized_data = {}
                    for key, value in data.items():
                        if isinstance(value, str):
                            # Remove potential XSS and injection patterns
                            sanitized_value = value.replace('<script', '').replace('javascript:', '')
                            sanitized_data[key] = sanitized_value
                        else:
                            sanitized_data[key] = value
                    request._cached_json = sanitized_data
            
            return f(*args, **kwargs)
        return wrapped
    return decorator

def validate_password_strength(password):
    """
    Validate password strength according to policy.
    Returns (is_valid, message) tuple.
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter"
    
    if not any(c.islower() for c in password):
        return False, "Password must contain at least one lowercase letter"
    
    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one number"
    
    if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
        return False, "Password must contain at least one special character"
    
    return True, "Password meets requirements"

def enforce_password_policy():
    """Middleware to enforce password policy on password-related endpoints."""
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if request.is_json:
                data = request.get_json()
                if 'password' in data:
                    is_valid, message = validate_password_strength(data['password'])
                    if not is_valid:
                        return jsonify({
                            'error': 'Invalid password',
                            'message': message
                        }), 400
            return f(*args, **kwargs)
        return wrapped
    return decorator

def apply_security_middleware(app):
    """Apply all security middleware to the app."""
    # Add security headers to all responses
    app.after_request(add_security_headers)
    
    # Add request ID to all requests
    app.before_request(request_id_middleware())
    
    # Add timing to all requests
    app.before_request(timing_middleware())
    
    # Add CORS handling
    app.before_request(cors_middleware())
    
    # Add rate limiting to all routes by default
    app.before_request(rate_limit(limit=100, per=60)) 