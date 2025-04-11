from marshmallow import Schema, fields, validate

class OrderItemSchema(Schema):
    """Schema for order items."""
    item_id = fields.Int(required=True)
    quantity = fields.Int(required=True, validate=validate.Range(min=1))
    notes = fields.Str(allow_none=True)

class OrderCreateSchema(Schema):
    """Schema for creating a new order."""
    hawker_id = fields.Int(required=True)
    items = fields.List(fields.Nested(OrderItemSchema), required=True, validate=validate.Length(min=1))
    pickup_address = fields.Str(required=True)
    delivery_address = fields.Str(required=True)
    notes = fields.Str(allow_none=True)
    scheduled_delivery_time = fields.DateTime(allow_none=True)

class OrderUpdateSchema(Schema):
    """Schema for updating an order."""
    status = fields.Str(validate=validate.OneOf([
        'pending', 'confirmed', 'preparing', 'ready', 
        'delivering', 'delivered', 'cancelled'
    ]))
    estimated_delivery_time = fields.DateTime(allow_none=True)
    delivery_sequence = fields.Int(allow_none=True)
    notes = fields.Str(allow_none=True)

class OrderCancellationSchema(Schema):
    """Schema for cancelling an order."""
    reason = fields.Str(required=True)

class OrderRefundSchema(Schema):
    """Schema for refunding an order."""
    amount = fields.Float(required=True, validate=validate.Range(min=0))
    reason = fields.Str(required=True)

class OrderRatingSchema(Schema):
    """Schema for rating an order."""
    rating = fields.Float(required=True, validate=validate.Range(min=1, max=5))
    food_quality = fields.Float(required=True, validate=validate.Range(min=1, max=5))
    delivery_time = fields.Float(required=True, validate=validate.Range(min=1, max=5))
    communication = fields.Float(required=True, validate=validate.Range(min=1, max=5))
    packaging = fields.Float(required=True, validate=validate.Range(min=1, max=5))
    value_for_money = fields.Float(required=True, validate=validate.Range(min=1, max=5))
    comment = fields.Str(allow_none=True)
    tags = fields.List(fields.Str(), allow_none=True)
    photos = fields.List(fields.Str(), allow_none=True)