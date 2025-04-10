from marshmallow import Schema, fields, validate, ValidationError, post_load
from app.models.user import User
from app.models.order import Order
from app.models.product import Product

class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=2, max=100))
    email = fields.Email(required=True)
    phone = fields.Str(required=True, validate=validate.Regexp(r'^\+?1?\d{9,15}$'))
    role = fields.Str(required=True, validate=validate.OneOf(['customer', 'hawker']))
    is_active = fields.Bool(dump_only=True)
    email_verified = fields.Bool(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    
    # Hawker-specific fields
    business_name = fields.Str(allow_none=True)
    business_address = fields.Str(allow_none=True)
    latitude = fields.Float(allow_none=True)
    longitude = fields.Float(allow_none=True)
    
    @post_load
    def make_user(self, data, **kwargs):
        return User(**data)

class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True, load_only=True)

class PasswordResetRequestSchema(Schema):
    email = fields.Email(required=True)

class PasswordResetSchema(Schema):
    new_password = fields.Str(required=True, validate=validate.Length(min=8))

class OrderSchema(Schema):
    id = fields.Int(dump_only=True)
    customer_id = fields.Int(required=True)
    hawker_id = fields.Int(required=True)
    status = fields.Str(dump_only=True)
    total_amount = fields.Float(required=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    
    @post_load
    def make_order(self, data, **kwargs):
        return Order(**data)

class OrderItemSchema(Schema):
    product_id = fields.Int(required=True)
    quantity = fields.Int(required=True, validate=validate.Range(min=1))
    price = fields.Float(required=True, validate=validate.Range(min=0))

class ProductSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=2, max=100))
    description = fields.Str(allow_none=True)
    price = fields.Float(required=True, validate=validate.Range(min=0))
    hawker_id = fields.Int(required=True)
    is_available = fields.Bool(default=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    
    @post_load
    def make_product(self, data, **kwargs):
        return Product(**data)

class LocationUpdateSchema(Schema):
    latitude = fields.Float(required=True, validate=validate.Range(min=-90, max=90))
    longitude = fields.Float(required=True, validate=validate.Range(min=-180, max=180))
    address = fields.Str(allow_none=True)

class RouteOptimizationSchema(Schema):
    date = fields.Date(required=True)
    strategy = fields.Str(validate=validate.OneOf(['distance', 'time', 'efficiency']))
    time_window = fields.Int(validate=validate.Range(min=1, max=24))
    return_to_start = fields.Bool(default=True)

class NotificationPreferencesSchema(Schema):
    order_created = fields.Bool(default=True)
    order_confirmed = fields.Bool(default=True)
    order_preparing = fields.Bool(default=True)
    order_ready = fields.Bool(default=True)
    order_delivered = fields.Bool(default=True)
    order_cancelled = fields.Bool(default=True)
    account_updates = fields.Bool(default=True)
    promotions = fields.Bool(default=True)
    email_notifications = fields.Bool(default=True)
    push_notifications = fields.Bool(default=True)
    sms_notifications = fields.Bool(default=False)

# Validation decorator
def validate_request(schema_class):
    def decorator(f):
        def wrapped(*args, **kwargs):
            schema = schema_class()
            try:
                data = schema.load(request.get_json())
                return f(data, *args, **kwargs)
            except ValidationError as e:
                return jsonify({
                    "success": False,
                    "error": "Validation error",
                    "message": str(e.messages)
                }), 400
        wrapped.__name__ = f.__name__
        return wrapped
    return decorator 