from flask import current_app
from app.models.location import LocationHistory
from app import db
from datetime import datetime, timedelta
import logging
from sqlalchemy import func
from app.services.geocoding import GeocodingService

class LocationTrackingService:
    """Service for handling location tracking and history"""
    
    def __init__(self):
        self.geocoding_service = GeocodingService()
    
    def track_location(self, user_id, latitude, longitude, accuracy=None, speed=None, bearing=None, timestamp=None):
        """
        Track a new location for a user
        
        Args:
            user_id: ID of the user
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            accuracy: Location accuracy in meters
            speed: Speed in meters per second
            bearing: Bearing in degrees
            timestamp: Timestamp of the location (defaults to current time)
            
        Returns:
            LocationHistory: Created location history record
        """
        try:
            # Get address information
            address_info = self.geocoding_service.reverse_geocode(latitude, longitude)
            
            location = LocationHistory(
                user_id=user_id,
                latitude=latitude,
                longitude=longitude,
                accuracy=accuracy,
                speed=speed,
                bearing=bearing,
                timestamp=timestamp or datetime.utcnow(),
                address=address_info['formatted_address'] if address_info else None,
                place_id=address_info['place_id'] if address_info else None
            )
            
            db.session.add(location)
            db.session.commit()
            
            return location
        except Exception as e:
            db.session.rollback()
            logging.error(f"Failed to track location: {str(e)}")
            return None
    
    def get_location_history(self, user_id, start_time=None, end_time=None, limit=100):
        """
        Get location history for a user
        
        Args:
            user_id: ID of the user
            start_time: Start time for filtering
            end_time: End time for filtering
            limit: Maximum number of records to return
            
        Returns:
            list: List of LocationHistory records
        """
        query = LocationHistory.query.filter_by(user_id=user_id)
        
        if start_time:
            query = query.filter(LocationHistory.timestamp >= start_time)
        if end_time:
            query = query.filter(LocationHistory.timestamp <= end_time)
        
        return query.order_by(LocationHistory.timestamp.desc()).limit(limit).all()
    
    def get_last_location(self, user_id):
        """
        Get the last known location for a user
        
        Args:
            user_id: ID of the user
            
        Returns:
            LocationHistory: Last location record
        """
        return LocationHistory.query.filter_by(user_id=user_id)\
            .order_by(LocationHistory.timestamp.desc())\
            .first()
    
    def get_location_stats(self, user_id, start_time=None, end_time=None):
        """
        Get location statistics for a user
        
        Args:
            user_id: ID of the user
            start_time: Start time for filtering
            end_time: End time for filtering
            
        Returns:
            dict: Location statistics
        """
        query = LocationHistory.query.filter_by(user_id=user_id)
        
        if start_time:
            query = query.filter(LocationHistory.timestamp >= start_time)
        if end_time:
            query = query.filter(LocationHistory.timestamp <= end_time)
        
        stats = {
            'total_locations': query.count(),
            'avg_accuracy': query.with_entities(func.avg(LocationHistory.accuracy)).scalar(),
            'avg_speed': query.with_entities(func.avg(LocationHistory.speed)).scalar(),
            'first_location': query.order_by(LocationHistory.timestamp.asc()).first(),
            'last_location': query.order_by(LocationHistory.timestamp.desc()).first()
        }
        
        return stats
    
    def cleanup_old_locations(self, days=30):
        """
        Clean up old location history records
        
        Args:
            days: Number of days to keep
            
        Returns:
            int: Number of records deleted
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        try:
            deleted = LocationHistory.query.filter(LocationHistory.timestamp < cutoff_date).delete()
            db.session.commit()
            return deleted
        except Exception as e:
            db.session.rollback()
            logging.error(f"Failed to cleanup old locations: {str(e)}")
            return 0
    
    def get_nearby_locations(self, latitude, longitude, radius_meters=1000, limit=100):
        """
        Get locations within a radius of a point
        
        Args:
            latitude: Center latitude
            longitude: Center longitude
            radius_meters: Search radius in meters
            limit: Maximum number of records to return
            
        Returns:
            list: List of nearby LocationHistory records
        """
        # Using Haversine formula in SQL
        query = LocationHistory.query.filter(
            func.acos(
                func.sin(func.radians(latitude)) * func.sin(func.radians(LocationHistory.latitude)) +
                func.cos(func.radians(latitude)) * func.cos(func.radians(LocationHistory.latitude)) *
                func.cos(func.radians(longitude - LocationHistory.longitude))
            ) * 6371000 <= radius_meters
        ).order_by(LocationHistory.timestamp.desc()).limit(limit)
        
        return query.all()
    
    def get_location_density(self, latitude, longitude, radius_meters=1000):
        """
        Get location density within a radius
        
        Args:
            latitude: Center latitude
            longitude: Center longitude
            radius_meters: Search radius in meters
            
        Returns:
            dict: Location density statistics
        """
        # Using Haversine formula in SQL
        query = LocationHistory.query.filter(
            func.acos(
                func.sin(func.radians(latitude)) * func.sin(func.radians(LocationHistory.latitude)) +
                func.cos(func.radians(latitude)) * func.cos(func.radians(LocationHistory.latitude)) *
                func.cos(func.radians(longitude - LocationHistory.longitude))
            ) * 6371000 <= radius_meters
        )
        
        stats = {
            'total_locations': query.count(),
            'unique_users': query.with_entities(LocationHistory.user_id).distinct().count(),
            'avg_accuracy': query.with_entities(func.avg(LocationHistory.accuracy)).scalar(),
            'time_distribution': query.with_entities(
                func.extract('hour', LocationHistory.timestamp).label('hour'),
                func.count().label('count')
            ).group_by('hour').all()
        }
        
        return stats 