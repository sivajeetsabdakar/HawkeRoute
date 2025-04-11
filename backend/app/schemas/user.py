from marshmallow import Schema, fields, validate

class UserUpdateSchema(Schema):
    """Schema for updating user profile"""
    name = fields.Str(validate=validate.Length(min=2, max=100))
    email = fields.Email()
    phone = fields.Str(validate=validate.Regexp(r'^\+?1?\d{9,15}$'))
    password = fields.Str(validate=validate.Length(min=8))
    email_notifications = fields.Boolean()
    push_notifications = fields.Boolean()
    sms_notifications = fields.Boolean()

class UserPreferencesSchema(Schema):
    """Schema for updating user notification preferences"""
    email_notifications = fields.Boolean(required=True)
    push_notifications = fields.Boolean(required=True)
    sms_notifications = fields.Boolean(required=True) 