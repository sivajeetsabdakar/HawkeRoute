from flask import request, g
from functools import wraps
import time
import secrets

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