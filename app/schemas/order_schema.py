from marshmallow import Schema, fields, validate

class OrderCancellationSchema(Schema):
    reason_code = fields.String(required=True)
    details = fields.String(allow_none=True)

class OrderRefundSchema(Schema):
    amount = fields.Float(allow_none=True, validate=validate.Range(min=0.01))
    reason = fields.String(required=True)
    details = fields.String(allow_none=True) 