from datetime import datetime, timedelta
from sqlalchemy import and_, or_, func
from app import db
from app.models.location import Location, LocationHistory
from app.services.geocoding import GeocodingService
from app.services.notification import NotificationService

class LocationService:
    def __init__(self):
        self.geocoding_service = GeocodingService()
        self.notification_service = NotificationService()
    
    def update_location(self, user_id, latitude, longitude, accuracy=None, 
                       speed=None, heading=None, location_type='idle', 
                       order_id=None):
        """
        Update user's current location and store in history
        """
        try:
            # Get address from coordinates
            address = self.geocoding_service.reverse_geocode(latitude, longitude)
            
            # Update current location
            current_location = Location.query.filter_by(user_id=user_id).first()
            if current_location:
                current_location.latitude = latitude
                current_location.longitude = longitude
                current_location.accuracy = accuracy
                current_location.speed = speed
                current_location.heading = heading
                current_location.timestamp = datetime.utcnow()
            else:
                current_location = Location(
                    user_id=user_id,
                    latitude=latitude,
                    longitude=longitude,
                    accuracy=accuracy,
                    speed=speed,
                    heading=heading
                )
                db.session.add(current_location)
            
            # Store in history
            history_entry = LocationHistory(
                user_id=user_id,
                latitude=latitude,
                longitude=longitude,
                accuracy=accuracy,
                speed=speed,
                heading=heading,
                address=address,
                location_type=location_type,
                order_id=order_id
            )
            db.session.add(history_entry)
            
            db.session.commit()
            
            # If this is a delivery location update, notify relevant parties
            if order_id and location_type in ['pickup', 'delivery']:
                self.notification_service.send_order_notification(
                    order_id=order_id,
                    notification_type=f'location_{location_type}',
                    data={
                        'latitude': latitude,
                        'longitude': longitude,
                        'address': address
                    }
                )
            
            return current_location.to_dict()
            
        except Exception as e:
            db.session.rollback()
            raise
    
    def get_location_history(self, user_id, start_time=None, end_time=None, 
                           location_type=None, order_id=None, limit=100):
        """
        Get location history for a user with optional filters
        """
        query = LocationHistory.query.filter_by(user_id=user_id)
        
        if start_time:
            query = query.filter(LocationHistory.timestamp >= start_time)
        if end_time:
            query = query.filter(LocationHistory.timestamp <= end_time)
        if location_type:
            query = query.filter_by(location_type=location_type)
        if order_id:
            query = query.filter_by(order_id=order_id)
            
        query = query.order_by(LocationHistory.timestamp.desc())
        
        if limit:
            query = query.limit(limit)
            
        return [entry.to_dict() for entry in query.all()]
    
    def search_nearby_locations(self, latitude, longitude, radius_km=5, 
                              location_type=None, order_id=None):
        """
        Search for locations within a radius
        """
        # Convert radius to degrees (approximate)
        radius_deg = radius_km / 111.32  # 1 degree = 111.32 km
        
        query = Location.query.filter(
            and_(
                Location.latitude.between(latitude - radius_deg, latitude + radius_deg),
                Location.longitude.between(longitude - radius_deg, longitude + radius_deg),
                Location.is_active == True
            )
        )
        
        if location_type:
            query = query.join(LocationHistory).filter(
                LocationHistory.location_type == location_type
            )
        if order_id:
            query = query.join(LocationHistory).filter(
                LocationHistory.order_id == order_id
            )
            
        # Calculate actual distance using Haversine formula
        locations = query.all()
        nearby_locations = []
        
        for loc in locations:
            distance = self._calculate_distance(
                latitude, longitude,
                loc.latitude, loc.longitude
            )
            if distance <= radius_km:
                loc_dict = loc.to_dict()
                loc_dict['distance_km'] = distance
                nearby_locations.append(loc_dict)
        
        return sorted(nearby_locations, key=lambda x: x['distance_km'])
    
    def get_user_location(self, user_id):
        """
        Get user's current location
        """
        location = Location.query.filter_by(
            user_id=user_id,
            is_active=True
        ).first()
        
        return location.to_dict() if location else None
    
    def get_active_users_in_area(self, latitude, longitude, radius_km=5):
        """
        Get all active users in a specific area
        """
        return self.search_nearby_locations(
            latitude, longitude, radius_km,
            location_type='idle'
        )
    
    def _calculate_distance(self, lat1, lon1, lat2, lon2):
        """
        Calculate distance between two points using Haversine formula
        """
        from math import radians, sin, cos, sqrt, atan2
        
        R = 6371  # Earth's radius in kilometers
        
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        distance = R * c
        
        return distance 