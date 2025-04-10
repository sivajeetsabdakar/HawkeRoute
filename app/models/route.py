from app import db
from datetime import datetime
import json

class HawkerRoute(db.Model):
    __tablename__ = 'hawker_routes'
    
    id = db.Column(db.Integer, primary_key=True)
    hawker_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    order_sequence = db.Column(db.Text, nullable=False)  # JSON array of order IDs
    total_distance = db.Column(db.Float, nullable=False)  # in meters
    estimated_duration = db.Column(db.Integer, nullable=False)  # in seconds
    status = db.Column(db.String(20), default='pending')  # pending, in_progress, completed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    hawker = db.relationship('User', backref=db.backref('routes', lazy=True))
    
    @property
    def order_ids(self):
        """Returns the order sequence as a list of integers"""
        return json.loads(self.order_sequence)
    
    @order_ids.setter
    def order_ids(self, value):
        """Sets the order sequence from a list of integers"""
        self.order_sequence = json.dumps(value)
    
    def to_dict(self):
        return {
            'id': self.id,
            'hawker_id': self.hawker_id,
            'date': self.date.isoformat(),
            'order_sequence': self.order_ids,
            'total_distance': self.total_distance,
            'estimated_duration': self.estimated_duration,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'hawker_name': self.hawker.business_name or self.hawker.name
        }

class Route(db.Model):
    """Model for storing optimized routes"""
    
    __tablename__ = 'routes'
    
    id = db.Column(db.Integer, primary_key=True)
    orders = db.Column(db.JSON)  # List of order IDs
    waypoints = db.Column(db.JSON)  # List of waypoint addresses
    polyline = db.Column(db.Text)  # Encoded polyline
    distance = db.Column(db.Integer)  # Total distance in meters
    duration = db.Column(db.Integer)  # Total duration in seconds
    duration_in_traffic = db.Column(db.Integer)  # Duration with traffic in seconds
    start_location = db.Column(db.JSON)  # {lat: float, lng: float}
    end_location = db.Column(db.JSON)  # {lat: float, lng: float}
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    shared_with = db.Column(db.JSON, default=list)  # List of user IDs
    
    # Relationships
    history = db.relationship('RouteHistory', backref='route', lazy=True)
    analytics = db.relationship('RouteAnalytics', backref='route', lazy=True, uselist=False)
    
    def __init__(self, orders, waypoints, polyline, distance, duration, duration_in_traffic=None, start_location=None, end_location=None):
        self.orders = orders
        self.waypoints = waypoints
        self.polyline = polyline
        self.distance = distance
        self.duration = duration
        self.duration_in_traffic = duration_in_traffic
        self.start_location = start_location
        self.end_location = end_location
    
    def to_dict(self):
        """Convert route to dictionary"""
        return {
            'id': self.id,
            'orders': self.orders,
            'waypoints': self.waypoints,
            'polyline': self.polyline,
            'distance': self.distance,
            'duration': self.duration,
            'duration_in_traffic': self.duration_in_traffic,
            'start_location': self.start_location,
            'end_location': self.end_location,
            'created_at': self.created_at.isoformat(),
            'shared_with': self.shared_with
        }
    
    def __repr__(self):
        return f'<Route {self.id}: {len(self.orders)} orders>'

class RouteHistory(db.Model):
    """Model for storing route history"""
    
    __tablename__ = 'route_history'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    route_id = db.Column(db.Integer, db.ForeignKey('routes.id'), nullable=False)
    status = db.Column(db.String(20), nullable=False)  # completed, cancelled, etc.
    distance = db.Column(db.Integer)  # Actual distance in meters
    duration = db.Column(db.Integer)  # Actual duration in seconds
    duration_in_traffic = db.Column(db.Integer)  # Actual duration with traffic
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('route_history', lazy=True))
    
    def __init__(self, user_id, route_id, status, distance, duration, duration_in_traffic=None):
        self.user_id = user_id
        self.route_id = route_id
        self.status = status
        self.distance = distance
        self.duration = duration
        self.duration_in_traffic = duration_in_traffic
    
    def to_dict(self):
        """Convert route history to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'route_id': self.route_id,
            'status': self.status,
            'distance': self.distance,
            'duration': self.duration,
            'duration_in_traffic': self.duration_in_traffic,
            'created_at': self.created_at.isoformat()
        }
    
    def __repr__(self):
        return f'<RouteHistory {self.id}: {self.status}>'

class RouteAnalytics(db.Model):
    """Model for storing route analytics"""
    
    __tablename__ = 'route_analytics'
    
    id = db.Column(db.Integer, primary_key=True)
    route_id = db.Column(db.Integer, db.ForeignKey('routes.id'), nullable=False)
    total_distance = db.Column(db.Integer)  # Total distance in meters
    total_duration = db.Column(db.Integer)  # Total duration in seconds
    avg_speed = db.Column(db.Float)  # Average speed in meters per second
    traffic_data = db.Column(db.JSON)  # Traffic data for route segments
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    def __init__(self, route_id, total_distance, total_duration, avg_speed, traffic_data):
        self.route_id = route_id
        self.total_distance = total_distance
        self.total_duration = total_duration
        self.avg_speed = avg_speed
        self.traffic_data = traffic_data
    
    def to_dict(self):
        """Convert route analytics to dictionary"""
        return {
            'id': self.id,
            'route_id': self.route_id,
            'total_distance': self.total_distance,
            'total_duration': self.total_duration,
            'avg_speed': self.avg_speed,
            'traffic_data': self.traffic_data,
            'updated_at': self.updated_at.isoformat()
        }
    
    def __repr__(self):
        return f'<RouteAnalytics {self.id}: {self.route_id}>' 