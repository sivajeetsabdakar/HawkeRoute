from flask import current_app
from app.models.route import Route, RouteHistory, RouteAnalytics
from app.models.order import Order
from app import db
from datetime import datetime, timedelta
import logging
from sqlalchemy import func
from app.services.geocoding import GeocodingService
import googlemaps
import polyline
import json

class RouteService:
    """Service for handling route optimization and analytics"""
    
    def __init__(self):
        self.geocoding_service = GeocodingService()
        api_key = current_app.config.get('GOOGLE_MAPS_API_KEY')
        if api_key:
            self.client = googlemaps.Client(key=api_key)
        else:
            self.client = None
            logging.warning("Google Maps API key not configured. Route service will be disabled.")
    
    def optimize_route(self, orders, start_location=None, end_location=None):
        """
        Optimize delivery route for a list of orders
        
        Args:
            orders: List of Order objects
            start_location: Starting location (lat, lng)
            end_location: Ending location (lat, lng)
            
        Returns:
            dict: Optimized route information
        """
        if not self.client or not orders:
            return None
        
        try:
            # Prepare waypoints
            waypoints = []
            for order in orders:
                if order.pickup_address:
                    waypoints.append(order.pickup_address)
                if order.delivery_address:
                    waypoints.append(order.delivery_address)
            
            # Get route from Google Maps API
            result = self.client.directions(
                origin=start_location or waypoints[0],
                destination=end_location or waypoints[-1],
                waypoints=waypoints[1:-1] if len(waypoints) > 2 else None,
                optimize_waypoints=True,
                departure_time=datetime.now(),
                traffic_model='best_guess'
            )
            
            if not result:
                return None
            
            route = result[0]
            
            # Create route record
            route_record = Route(
                orders=[order.id for order in orders],
                waypoints=waypoints,
                polyline=route['overview_polyline']['points'],
                distance=route['legs'][-1]['distance']['value'],
                duration=route['legs'][-1]['duration']['value'],
                duration_in_traffic=route['legs'][-1].get('duration_in_traffic', {}).get('value'),
                start_location=start_location,
                end_location=end_location,
                created_at=datetime.utcnow()
            )
            
            db.session.add(route_record)
            db.session.commit()
            
            return self._format_route_response(route, route_record)
            
        except Exception as e:
            db.session.rollback()
            logging.error(f"Failed to optimize route: {str(e)}")
            return None
    
    def get_route_history(self, user_id, start_time=None, end_time=None, limit=100):
        """
        Get route history for a user
        
        Args:
            user_id: ID of the user
            start_time: Start time for filtering
            end_time: End time for filtering
            limit: Maximum number of records to return
            
        Returns:
            list: List of RouteHistory records
        """
        query = RouteHistory.query.filter_by(user_id=user_id)
        
        if start_time:
            query = query.filter(RouteHistory.created_at >= start_time)
        if end_time:
            query = query.filter(RouteHistory.created_at <= end_time)
        
        return query.order_by(RouteHistory.created_at.desc()).limit(limit).all()
    
    def save_route_history(self, user_id, route_id, status='completed'):
        """
        Save route history
        
        Args:
            user_id: ID of the user
            route_id: ID of the route
            status: Route status (completed, cancelled, etc.)
            
        Returns:
            RouteHistory: Created route history record
        """
        try:
            route = Route.query.get(route_id)
            if not route:
                return None
            
            history = RouteHistory(
                user_id=user_id,
                route_id=route_id,
                status=status,
                distance=route.distance,
                duration=route.duration,
                duration_in_traffic=route.duration_in_traffic,
                created_at=datetime.utcnow()
            )
            
            db.session.add(history)
            db.session.commit()
            
            return history
        except Exception as e:
            db.session.rollback()
            logging.error(f"Failed to save route history: {str(e)}")
            return None
    
    def update_route_analytics(self, route_id):
        """
        Update analytics for a route
        
        Args:
            route_id: ID of the route
            
        Returns:
            RouteAnalytics: Updated analytics record
        """
        try:
            route = Route.query.get(route_id)
            if not route:
                return None
            
            # Get historical data
            history = RouteHistory.query.filter_by(route_id=route_id).all()
            
            # Calculate analytics
            total_distance = sum(h.distance for h in history)
            total_duration = sum(h.duration for h in history)
            avg_speed = total_distance / total_duration if total_duration > 0 else 0
            
            # Get traffic data
            traffic_data = self._get_traffic_data(route)
            
            analytics = RouteAnalytics(
                route_id=route_id,
                total_distance=total_distance,
                total_duration=total_duration,
                avg_speed=avg_speed,
                traffic_data=json.dumps(traffic_data),
                updated_at=datetime.utcnow()
            )
            
            db.session.add(analytics)
            db.session.commit()
            
            return analytics
        except Exception as e:
            db.session.rollback()
            logging.error(f"Failed to update route analytics: {str(e)}")
            return None
    
    def share_route(self, route_id, shared_with_user_id):
        """
        Share a route with another user
        
        Args:
            route_id: ID of the route
            shared_with_user_id: ID of the user to share with
            
        Returns:
            bool: True if successful
        """
        try:
            route = Route.query.get(route_id)
            if not route:
                return False
            
            # Add user to shared_with list
            if shared_with_user_id not in route.shared_with:
                route.shared_with.append(shared_with_user_id)
                db.session.commit()
            
            return True
        except Exception as e:
            db.session.rollback()
            logging.error(f"Failed to share route: {str(e)}")
            return False
    
    def _format_route_response(self, google_route, route_record):
        """Format route response from Google Maps API"""
        return {
            'id': route_record.id,
            'distance': google_route['legs'][-1]['distance']['text'],
            'duration': google_route['legs'][-1]['duration']['text'],
            'duration_in_traffic': google_route['legs'][-1].get('duration_in_traffic', {}).get('text'),
            'polyline': google_route['overview_polyline']['points'],
            'waypoints': route_record.waypoints,
            'created_at': route_record.created_at.isoformat()
        }
    
    def _get_traffic_data(self, route):
        """Get traffic data for a route"""
        if not self.client:
            return {}
        
        try:
            # Decode polyline to get route points
            points = polyline.decode(route.polyline)
            
            # Get traffic data for each segment
            traffic_data = []
            for i in range(len(points) - 1):
                result = self.client.distance_matrix(
                    origins=[f"{points[i][0]},{points[i][1]}"],
                    destinations=[f"{points[i+1][0]},{points[i+1][1]}"],
                    departure_time=datetime.now(),
                    traffic_model='best_guess'
                )
                
                if result['rows'][0]['elements'][0]['status'] == 'OK':
                    element = result['rows'][0]['elements'][0]
                    traffic_data.append({
                        'segment': i,
                        'distance': element['distance']['value'],
                        'duration': element['duration']['value'],
                        'duration_in_traffic': element.get('duration_in_traffic', {}).get('value')
                    })
            
            return traffic_data
        except Exception as e:
            logging.error(f"Failed to get traffic data: {str(e)}")
            return {}