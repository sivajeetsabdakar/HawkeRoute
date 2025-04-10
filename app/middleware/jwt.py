from flask_jwt_extended import verify_jwt_in_request
from app.models.token_blacklist import TokenBlacklist
from functools import wraps
from flask import jsonify

def check_token_blacklist():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            jti = get_jwt()["jti"]
            if TokenBlacklist.is_blacklisted(jti):
                return jsonify({"error": "Token has been revoked"}), 401
            return fn(*args, **kwargs)
        return decorator
    return wrapper 