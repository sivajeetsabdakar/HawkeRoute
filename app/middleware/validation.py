from flask import request, jsonify
from functools import wraps
from marshmallow import Schema, fields, ValidationError

class RequestValidator:
    """Middleware for validating request data using Marshmallow schemas."""
    
    def __init__(self, schema_class):
        """
        Initialize the validator with a Marshmallow schema class.
        
        Args:
            schema_class: A Marshmallow Schema class to use for validation
        """
        self.schema_class = schema_class
    
    def __call__(self, f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                # Create schema instance
                schema = self.schema_class()
                
                # Get request data based on method
                if request.method == 'GET':
                    data = request.args.to_dict()
                else:
                    data = request.get_json() or {}
                
                # Validate the data
                validated_data = schema.load(data)
                
                # Add validated data to request context
                request.validated_data = validated_data
                
                return f(*args, **kwargs)
                
            except ValidationError as e:
                return jsonify({
                    'status': 'error',
                    'message': 'Validation error',
                    'errors': e.messages
                }), 400
                
        return decorated_function

# Example schemas for different request types
class UserCreateSchema(Schema):
    """Schema for user creation requests."""
    email = fields.Email(required=True)
    password = fields.Str(required=True, min_length=8)
    name = fields.Str(required=True)
    phone = fields.Str(required=False)

class UserUpdateSchema(Schema):
    """Schema for user update requests."""
    email = fields.Email(required=False)
    name = fields.Str(required=False)
    phone = fields.Str(required=False)
    current_password = fields.Str(required=False)
    new_password = fields.Str(required=False, min_length=8)

class OrderCreateSchema(Schema):
    """Schema for order creation requests."""
    pickup_address = fields.Str(required=True)
    delivery_address = fields.Str(required=True)
    items = fields.List(fields.Dict(), required=True)
    notes = fields.Str(required=False)

class LocationUpdateSchema(Schema):
    """Schema for location update requests."""
    latitude = fields.Float(required=True)
    longitude = fields.Float(required=True)
    accuracy = fields.Float(required=False)
    timestamp = fields.DateTime(required=False)

# Decorator for validating request data
def validate_request(schema_class):
    """
    Decorator for validating request data using a Marshmallow schema.
    
    Args:
        schema_class: A Marshmallow Schema class to use for validation
        
    Returns:
        Decorated function with validation
    """
    return RequestValidator(schema_class) 