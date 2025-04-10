x`from functools import wraps
from flask import request, jsonify
from datetime import datetime
import pytz
from app.config import Config

def check_order_time():
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get current time in configured timezone
            tz = pytz.timezone(Config.TIMEZONE)
            current_time = datetime.now(tz).time()
            cutoff_time = datetime.strptime(Config.ORDER_CUTOFF_TIME, "%H:%M").time()
            
            # Check if current time is after cutoff
            if current_time >= cutoff_time:
                return jsonify({
                    'error': 'Orders can only be placed before 2 PM',
                    'cutoff_time': Config.ORDER_CUTOFF_TIME
                }), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator 