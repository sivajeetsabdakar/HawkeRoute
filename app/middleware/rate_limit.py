from flask import request, jsonify
from functools import wraps
import time
from redis import Redis
from current_app import current_app

class RateLimiter:
    """Rate limiting middleware using Redis for storage."""
    
    def __init__(self, key_prefix='rate_limit:', default_limit=100, default_period=60):
        """
        Initialize the rate limiter.
        
        Args:
            key_prefix: Prefix for Redis keys
            default_limit: Default number of requests allowed per period
            default_period: Default time period in seconds
        """
        self.redis = Redis.from_url(current_app.config['REDIS_URL'])
        self.key_prefix = key_prefix
        self.default_limit = default_limit
        self.default_period = default_period
    
    def _get_key(self, key):
        """Get the Redis key for rate limiting."""
        return f"{self.key_prefix}{key}"
    
    def is_rate_limited(self, key, limit=None, period=None):
        """
        Check if the request should be rate limited.
        
        Args:
            key: Unique identifier for the rate limit (e.g., IP address or user ID)
            limit: Maximum number of requests allowed per period
            period: Time period in seconds
            
        Returns:
            bool: True if rate limited, False otherwise
        """
        limit = limit or self.default_limit
        period = period or self.default_period
        
        redis_key = self._get_key(key)
        current = self.redis.get(redis_key)
        
        if current is None:
            # First request, set the counter and expiry
            self.redis.setex(redis_key, period, 1)
            return False
        
        if int(current) >= limit:
            return True
        
        # Increment the counter
        self.redis.incr(redis_key)
        return False
    
    def get_remaining_requests(self, key, limit=None):
        """
        Get the number of remaining requests allowed.
        
        Args:
            key: Unique identifier for the rate limit
            limit: Maximum number of requests allowed per period
            
        Returns:
            int: Number of remaining requests
        """
        limit = limit or self.default_limit
        redis_key = self._get_key(key)
        current = self.redis.get(redis_key)
        
        if current is None:
            return limit
        
        return max(0, limit - int(current))
    
    def get_reset_time(self, key, period=None):
        """
        Get the time until the rate limit resets.
        
        Args:
            key: Unique identifier for the rate limit
            period: Time period in seconds
            
        Returns:
            int: Seconds until reset
        """
        period = period or self.default_period
        redis_key = self._get_key(key)
        ttl = self.redis.ttl(redis_key)
        
        return max(0, ttl)

def rate_limit(limit=None, period=None, key_func=None):
    """
    Decorator for rate limiting requests.
    
    Args:
        limit: Maximum number of requests allowed per period
        period: Time period in seconds
        key_func: Function to generate the rate limit key
        
    Returns:
        Decorated function with rate limiting
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get the rate limiter instance
            limiter = RateLimiter()
            
            # Get the rate limit key
            if key_func:
                key = key_func()
            else:
                # Default to using IP address
                key = request.remote_addr
            
            # Check if rate limited
            if limiter.is_rate_limited(key, limit, period):
                return jsonify({
                    'status': 'error',
                    'message': 'Rate limit exceeded',
                    'retry_after': limiter.get_reset_time(key, period)
                }), 429
            
            # Add rate limit headers
            response = f(*args, **kwargs)
            if not isinstance(response, tuple):
                response = (response, 200)
            
            response_obj, status_code = response
            headers = {
                'X-RateLimit-Limit': str(limit or limiter.default_limit),
                'X-RateLimit-Remaining': str(limiter.get_remaining_requests(key, limit)),
                'X-RateLimit-Reset': str(int(time.time()) + limiter.get_reset_time(key, period))
            }
            
            if isinstance(response_obj, dict):
                response_obj = jsonify(response_obj)
            
            for key, value in headers.items():
                response_obj.headers[key] = value
            
            return response_obj, status_code
            
        return decorated_function
    return decorator

# Example key functions
def get_user_id():
    """Get the current user's ID for rate limiting."""
    from flask_jwt_extended import get_jwt_identity
    return f"user:{get_jwt_identity()}"

def get_ip_address():
    """Get the client's IP address for rate limiting."""
    return request.remote_addr

# Rate limit by user ID for authenticated routes
def user_rate_limit(limit_string):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            from flask_jwt_extended import get_jwt_identity
            user_id = get_jwt_identity()
            if user_id:
                limiter.limit(limit_string, key_func=lambda: f"user:{user_id}")(f)(*args, **kwargs)
            return f(*args, **kwargs)
        return wrapped
    return decorator

# Rate limit by IP address
def ip_rate_limit(limit_string):
    return rate_limit(limit_string, key_func=get_remote_address)

# Apply rate limiting to specific endpoints
def apply_rate_limits(app):
    # Apply to all routes by default
    limiter.init_app(app)
    
    # Override default error handler
    @app.errorhandler(429)
    def ratelimit_handler(e):
        return jsonify({
            "success": False,
            "error": "Rate limit exceeded",
            "message": "Too many requests. Please try again later.",
            "retry_after": e.description
        }), 429 