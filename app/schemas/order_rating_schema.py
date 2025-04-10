from marshmallow import Schema, fields, validate

class OrderRatingSchema(Schema):
    rating = fields.Integer(required=True, validate=validate.Range(min=1, max=5))
    comment = fields.String(allow_none=True)
    product_quality = fields.Integer(allow_none=True, validate=validate.Range(min=1, max=5))
    delivery_time = fields.Integer(allow_none=True, validate=validate.Range(min=1, max=5))
    communication = fields.Integer(allow_none=True, validate=validate.Range(min=1, max=5))
    packaging = fields.Integer(allow_none=True, validate=validate.Range(min=1, max=5))
    value_for_money = fields.Integer(allow_none=True, validate=validate.Range(min=1, max=5))
    product_condition = fields.Integer(allow_none=True, validate=validate.Range(min=1, max=5))
    tags = fields.List(fields.String(), allow_none=True)
    photos = fields.List(fields.Url(), allow_none=True) 