import googlemaps
from flask import current_app
from datetime import datetime
import logging

class GeocodingService:
    """Service for handling geocoding operations using Google Maps API"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GeocodingService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not GeocodingService._initialized:
            api_key = current_app.config.get('GOOGLE_MAPS_API_KEY')
            if api_key:
                self.client = googlemaps.Client(key=api_key)
                GeocodingService._initialized = True
            else:
                self.client = None
                logging.warning("Google Maps API key not configured. Geocoding service will be disabled.")
    
    def geocode_address(self, address):
        """
        Convert address to coordinates
        
        Args:
            address: Address string to geocode
            
        Returns:
            dict: {
                'latitude': float,
                'longitude': float,
                'formatted_address': str,
                'place_id': str,
                'components': dict
            }
        """
        if not self.client:
            return None
        
        try:
            result = self.client.geocode(address)
            if not result:
                return None
            
            location = result[0]['geometry']['location']
            components = self._extract_address_components(result[0]['address_components'])
            
            return {
                'latitude': location['lat'],
                'longitude': location['lng'],
                'formatted_address': result[0]['formatted_address'],
                'place_id': result[0]['place_id'],
                'components': components
            }
        except Exception as e:
            logging.error(f"Geocoding error: {str(e)}")
            return None
    
    def reverse_geocode(self, latitude, longitude):
        """
        Convert coordinates to address
        
        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            
        Returns:
            dict: {
                'formatted_address': str,
                'place_id': str,
                'components': dict
            }
        """
        if not self.client:
            return None
        
        try:
            result = self.client.reverse_geocode((latitude, longitude))
            if not result:
                return None
            
            components = self._extract_address_components(result[0]['address_components'])
            
            return {
                'formatted_address': result[0]['formatted_address'],
                'place_id': result[0]['place_id'],
                'components': components
            }
        except Exception as e:
            logging.error(f"Reverse geocoding error: {str(e)}")
            return None
    
    def validate_address(self, address):
        """
        Validate if an address exists and is valid
        
        Args:
            address: Address string to validate
            
        Returns:
            tuple: (is_valid, formatted_address, components)
        """
        result = self.geocode_address(address)
        if not result:
            return False, None, None
        
        return True, result['formatted_address'], result['components']
    
    def get_distance_matrix(self, origins, destinations, mode='driving'):
        """
        Get distance matrix between multiple origins and destinations
        
        Args:
            origins: List of origin addresses or coordinates
            destinations: List of destination addresses or coordinates
            mode: Travel mode (driving, walking, bicycling, transit)
            
        Returns:
            dict: Distance matrix with durations and distances
        """
        if not self.client:
            return None
        
        try:
            result = self.client.distance_matrix(
                origins,
                destinations,
                mode=mode,
                departure_time=datetime.now()
            )
            
            return self._parse_distance_matrix(result)
        except Exception as e:
            logging.error(f"Distance matrix error: {str(e)}")
            return None
    
    def _extract_address_components(self, components):
        """Extract and organize address components"""
        result = {}
        for component in components:
            for type_ in component['types']:
                result[type_] = component['long_name']
        return result
    
    def _parse_distance_matrix(self, matrix):
        """Parse distance matrix response"""
        result = {
            'rows': [],
            'status': matrix['status']
        }
        
        for row in matrix['rows']:
            row_data = {
                'elements': []
            }
            for element in row['elements']:
                element_data = {
                    'status': element['status'],
                    'distance': element.get('distance', {}).get('text'),
                    'duration': element.get('duration', {}).get('text'),
                    'duration_in_traffic': element.get('duration_in_traffic', {}).get('text')
                }
                row_data['elements'].append(element_data)
            result['rows'].append(row_data)
        
        return result 