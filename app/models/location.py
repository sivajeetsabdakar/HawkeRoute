from app import db
from datetime import datetime

class LocationHistory(db.Model):
    """Model for storing location history"""
    
    __tablename__ = 'location_history'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    accuracy = db.Column(db.Float)  # Accuracy in meters
    speed = db.Column(db.Float)  # Speed in meters per second
    bearing = db.Column(db.Float)  # Bearing in degrees
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    address = db.Column(db.String(500))  # Formatted address
    place_id = db.Column(db.String(100))  # Google Places ID
    
    # Relationships
    user = db.relationship('User', backref=db.backref('location_history', lazy=True))
    
    def __init__(self, user_id, latitude, longitude, accuracy=None, speed=None, bearing=None, timestamp=None, address=None, place_id=None):
        self.user_id = user_id
        self.latitude = latitude
        self.longitude = longitude
        self.accuracy = accuracy
        self.speed = speed
        self.bearing = bearing
        self.timestamp = timestamp or datetime.utcnow()
        self.address = address
        self.place_id = place_id
    
    def to_dict(self):
        """Convert location history to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'accuracy': self.accuracy,
            'speed': self.speed,
            'bearing': self.bearing,
            'timestamp': self.timestamp.isoformat(),
            'address': self.address,
            'place_id': self.place_id
        }
    
    def __repr__(self):
        return f'<LocationHistory {self.id}: {self.latitude}, {self.longitude}>' 