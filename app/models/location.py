from app import db
from datetime import datetime

class Location(db.Model):
    """Model for storing current location data"""
    
    __tablename__ = 'locations'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    accuracy = db.Column(db.Float)  # in meters
    speed = db.Column(db.Float)  # in meters per second
    heading = db.Column(db.Float)  # in degrees
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('location', uselist=False))
    
    def __init__(self, user_id, latitude, longitude, accuracy=None, 
                 speed=None, heading=None):
        self.user_id = user_id
        self.latitude = latitude
        self.longitude = longitude
        self.accuracy = accuracy
        self.speed = speed
        self.heading = heading
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'accuracy': self.accuracy,
            'speed': self.speed,
            'heading': self.heading,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'is_active': self.is_active
        }
    
    def __repr__(self):
        return f'<Location {self.id}: ({self.latitude}, {self.longitude})>'

class LocationHistory(db.Model):
    """Model for storing location history"""
    
    __tablename__ = 'location_history'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    accuracy = db.Column(db.Float)  # in meters
    speed = db.Column(db.Float)  # in meters per second
    heading = db.Column(db.Float)  # in degrees
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    address = db.Column(db.String(255))  # Cached address from geocoding
    location_type = db.Column(db.String(50))  # e.g., 'pickup', 'delivery', 'idle'
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=True)
    
    # Relationships
    user = db.relationship('User', backref='location_history')
    order = db.relationship('Order', backref='location_history')
    
    def __init__(self, user_id, latitude, longitude, accuracy=None, 
                 speed=None, heading=None, address=None, 
                 location_type='idle', order_id=None):
        self.user_id = user_id
        self.latitude = latitude
        self.longitude = longitude
        self.accuracy = accuracy
        self.speed = speed
        self.heading = heading
        self.address = address
        self.location_type = location_type
        self.order_id = order_id
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'accuracy': self.accuracy,
            'speed': self.speed,
            'heading': self.heading,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'address': self.address,
            'location_type': self.location_type,
            'order_id': self.order_id
        }
    
    def __repr__(self):
        return f'<LocationHistory {self.id}: ({self.latitude}, {self.longitude})>' 