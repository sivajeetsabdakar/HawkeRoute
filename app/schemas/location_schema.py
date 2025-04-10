from marshmallow import Schema, fields, validate

class LocationUpdateSchema(Schema):
    latitude = fields.Float(required=True, validate=validate.Range(min=-90, max=90))
    longitude = fields.Float(required=True, validate=validate.Range(min=-180, max=180))
    accuracy = fields.Float(allow_none=True, validate=validate.Range(min=0))
    speed = fields.Float(allow_none=True, validate=validate.Range(min=0))
    heading = fields.Float(allow_none=True, validate=validate.Range(min=0, max=360))
    location_type = fields.String(allow_none=True, validate=validate.OneOf(
        ['idle', 'pickup', 'delivery', 'return']
    ))
    order_id = fields.Integer(allow_none=True)

class LocationSearchSchema(Schema):
    latitude = fields.Float(required=True, validate=validate.Range(min=-90, max=90))
    longitude = fields.Float(required=True, validate=validate.Range(min=-180, max=180))
    radius_km = fields.Float(allow_none=True, validate=validate.Range(min=0.1, max=100))
    location_type = fields.String(allow_none=True, validate=validate.OneOf(
        ['idle', 'pickup', 'delivery', 'return']
    ))
    order_id = fields.Integer(allow_none=True)