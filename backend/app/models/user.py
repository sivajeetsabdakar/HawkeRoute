from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # customer, hawker, admin
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Email verification fields
    email_verified = db.Column(db.Boolean, default=False)
    email_verified_at = db.Column(db.DateTime)
    email_verification_sent_at = db.Column(db.DateTime)
    
    # Role-specific fields for hawkers
    business_name = db.Column(db.String(100))
    business_address = db.Column(db.String(200))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    
    # Notification preferences
    notify_order_created = db.Column(db.Boolean, default=True)
    notify_order_confirmed = db.Column(db.Boolean, default=True)
    notify_order_preparing = db.Column(db.Boolean, default=True)
    notify_order_ready = db.Column(db.Boolean, default=True)
    notify_order_delivered = db.Column(db.Boolean, default=True)
    notify_order_cancelled = db.Column(db.Boolean, default=True)
    notify_account_updates = db.Column(db.Boolean, default=True)
    notify_promotions = db.Column(db.Boolean, default=True)
    
    # Notification methods
    notify_email = db.Column(db.Boolean, default=True)
    notify_push = db.Column(db.Boolean, default=True)
    notify_sms = db.Column(db.Boolean, default=False)
    
    # Device tokens for push notifications
    device_tokens = db.Column(db.JSON, default=list)  # List of device tokens for push notifications
    
    def __init__(self, name, email, phone, password, role):
        self.name = name
        self.email = email
        self.phone = phone
        self.set_password(password)
        self.role = role
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def add_device_token(self, token, platform=None):
        """Add a device token for push notifications"""
        if not self.device_tokens:
            self.device_tokens = []
        
        # Check if token already exists
        for device in self.device_tokens:
            if device.get('token') == token:
                # Update platform if provided
                if platform:
                    device['platform'] = platform
                return
        
        # Add new token
        self.device_tokens.append({
            'token': token,
            'platform': platform,
            'added_at': datetime.utcnow().isoformat()
        })
    
    def remove_device_token(self, token):
        """Remove a device token"""
        if not self.device_tokens:
            return
        
        self.device_tokens = [device for device in self.device_tokens if device.get('token') != token]
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'role': self.role,
            'is_active': self.is_active,
            'email_verified': self.email_verified,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'business_name': self.business_name if self.role == 'hawker' else None,
            'business_address': self.business_address if self.role == 'hawker' else None,
            'latitude': self.latitude if self.role == 'hawker' else None,
            'longitude': self.longitude if self.role == 'hawker' else None,
            'notification_preferences': {
                'order_created': self.notify_order_created,
                'order_confirmed': self.notify_order_confirmed,
                'order_preparing': self.notify_order_preparing,
                'order_ready': self.notify_order_ready,
                'order_delivered': self.notify_order_delivered,
                'order_cancelled': self.notify_order_cancelled,
                'account_updates': self.notify_account_updates,
                'promotions': self.notify_promotions,
                'email_notifications': self.notify_email,
                'push_notifications': self.notify_push,
                'sms_notifications': self.notify_sms
            }
        } 