from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
from app.models.order import Order
from app.models.route import HawkerRoute
from app.models.user import User
from app import db
from datetime import datetime, date, timedelta
import math
import json
import numpy as np
from typing import List, Dict, Tuple
import requests

class RouteOptimizer:
    def __init__(self, hawker_id, delivery_date):
        self.hawker_id = hawker_id
        self.delivery_date = delivery_date
        self.hawker = User.query.get(hawker_id)
        self.orders = self._get_orders()
        self.locations = self._prepare_locations()
        self.distance_matrix = self._create_distance_matrix()
        self.api_key = None  # Google Maps API key should be set in config
        
    def _get_orders(self):
        """Get all pending orders for the hawker on the specified date"""
        return Order.query.filter_by(
            hawker_id=self.hawker_id,
            status='pending'
        ).filter(
            db.func.date(Order.created_at) == self.delivery_date
        ).all()
    
    def _prepare_locations(self):
        """Prepare locations array with hawker's starting point and all delivery points"""
        locations = []
        
        # Add hawker's starting location
        locations.append({
            'id': 'hawker',
            'lat': self.hawker.latitude,
            'lng': self.hawker.longitude,
            'order_id': None
        })
        
        # Add delivery locations
        for order in self.orders:
            locations.append({
                'id': f'order_{order.id}',
                'lat': order.delivery_latitude,
                'lng': order.delivery_longitude,
                'order_id': order.id
            })
        
        return locations
    
    def _create_distance_matrix(self):
        """Create distance matrix for OR-tools"""
        size = len(self.locations)
        matrix = [[0 for _ in range(size)] for _ in range(size)]
        
        for i in range(size):
            for j in range(size):
                if i != j:
                    # Calculate distance between two points using Haversine formula
                    matrix[i][j] = self._calculate_distance(
                        self.locations[i]['lat'], self.locations[i]['lng'],
                        self.locations[j]['lat'], self.locations[j]['lng']
                    )
        
        return matrix
    
    def _calculate_distance(self, lat1, lng1, lat2, lng2):
        """Calculate distance between two points using Haversine formula"""
        R = 6371000  # Earth radius in meters
        
        lat1_rad = math.radians(lat1)
        lng1_rad = math.radians(lng1)
        lat2_rad = math.radians(lat2)
        lng2_rad = math.radians(lng2)
        
        dlat = lat2_rad - lat1_rad
        dlng = lng2_rad - lng1_rad
        
        a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlng/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        return int(R * c)  # Distance in meters
    
    def optimize(self):
        """Optimize delivery route using OR-tools"""
        if not self.orders:
            return None
        
        # Create routing model
        manager = pywrapcp.RoutingIndexManager(
            len(self.distance_matrix), 1, 0  # 1 vehicle, depot at index 0
        )
        routing = pywrapcp.RoutingModel(manager)
        
        # Register distance callback
        def distance_callback(from_index, to_index):
            from_node = manager.IndexToNode(from_index)
            to_node = manager.IndexToNode(to_index)
            return self.distance_matrix[from_node][to_node]
        
        transit_callback_index = routing.RegisterTransitCallback(distance_callback)
        routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)
        
        # Add distance constraint
        routing.AddDimension(
            transit_callback_index,
            0,  # no slack
            100000,  # maximum distance per vehicle (100km)
            True,  # start cumul to zero
            'Distance'
        )
        distance_dimension = routing.GetDimensionOrDie('Distance')
        
        # Set first solution heuristic
        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        search_parameters.first_solution_strategy = (
            routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
        )
        
        # Solve the problem
        solution = routing.SolveWithParameters(search_parameters)
        
        if not solution:
            return None
        
        # Extract the route
        index = routing.Start(0)
        route = []
        total_distance = 0
        
        while not routing.IsEnd(index):
            node_index = manager.IndexToNode(index)
            location = self.locations[node_index]
            
            if location['order_id'] is not None:
                route.append(location['order_id'])
            
            previous_index = index
            index = solution.Value(routing.NextVar(index))
            total_distance += routing.GetArcCostForVehicle(
                previous_index, index, 0
            )
        
        # Add the return to depot
        total_distance += routing.GetArcCostForVehicle(
            manager.NodeToIndex(route[-1] if route else 0),
            manager.NodeToIndex(0),
            0
        )
        
        # Create route plan
        route_plan = HawkerRoute(
            hawker_id=self.hawker_id,
            date=self.delivery_date,
            order_ids=route,
            total_distance=total_distance,
            estimated_duration=int(total_distance / 0.5),  # Assuming 0.5 m/s average speed
            status='pending'
        )
        
        try:
            db.session.add(route_plan)
            db.session.commit()
            return route_plan
        except Exception as e:
            db.session.rollback()
            print(f"Error saving route plan: {str(e)}")
            return None

    def optimize_route(self, hawker_id: int, date: datetime = None) -> Dict:
        """
        Optimize delivery route for a hawker on a specific date
        Returns optimized route with estimated times and distances
        """
        if date is None:
            date = datetime.now().date()
            
        # Get all pending orders for the hawker on the specified date
        orders = Order.query.filter(
            Order.hawker_id == hawker_id,
            Order.status.in_(['confirmed', 'preparing']),
            Order.created_at >= date,
            Order.created_at < date + timedelta(days=1)
        ).all()
        
        if not orders:
            return {
                'success': True,
                'message': 'No orders to optimize',
                'route': []
            }
            
        # Get hawker's location
        hawker = User.query.get(hawker_id)
        if not hawker or not hawker.latitude or not hawker.longitude:
            return {
                'success': False,
                'message': 'Hawker location not found'
            }
            
        # Prepare locations for optimization
        locations = []
        for order in orders:
            if order.delivery_latitude and order.delivery_longitude:
                locations.append({
                    'order_id': order.id,
                    'lat': order.delivery_latitude,
                    'lng': order.delivery_longitude,
                    'address': order.delivery_address
                })
                
        if not locations:
            return {
                'success': False,
                'message': 'No valid delivery locations found'
            }
            
        # Add hawker's location as start and end point
        start_point = {
            'lat': hawker.latitude,
            'lng': hawker.longitude,
            'address': hawker.address
        }
        
        # Optimize route using Google Maps Distance Matrix API
        try:
            optimized_route = self._optimize_with_google_maps(start_point, locations)
            
            # Update orders with optimized sequence
            for idx, stop in enumerate(optimized_route['route']):
                order = Order.query.get(stop['order_id'])
                if order:
                    order.delivery_sequence = idx + 1
                    
            db.session.commit()
            
            return {
                'success': True,
                'route': optimized_route['route'],
                'total_distance': optimized_route['total_distance'],
                'total_duration': optimized_route['total_duration'],
                'estimated_completion': optimized_route['estimated_completion']
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Route optimization failed: {str(e)}'
            }
            
    def _optimize_with_google_maps(self, start_point: Dict, locations: List[Dict]) -> Dict:
        """
        Optimize route using Google Maps Distance Matrix API
        Implements nearest neighbor algorithm with time windows
        """
        if not self.api_key:
            raise ValueError("Google Maps API key not configured")
            
        # Prepare distance matrix
        origins = [f"{start_point['lat']},{start_point['lng']}"]
        destinations = [f"{loc['lat']},{loc['lng']}" for loc in locations]
        
        # Get distance matrix from Google Maps API
        url = f"https://maps.googleapis.com/maps/api/distancematrix/json"
        params = {
            'origins': '|'.join(origins),
            'destinations': '|'.join(destinations),
            'mode': 'driving',
            'key': self.api_key
        }
        
        response = requests.get(url, params=params)
        data = response.json()
        
        if data['status'] != 'OK':
            raise Exception(f"Google Maps API error: {data['status']}")
            
        # Extract distances and durations
        distances = []
        durations = []
        for element in data['rows'][0]['elements']:
            if element['status'] == 'OK':
                distances.append(element['distance']['value'])
                durations.append(element['duration']['value'])
            else:
                raise Exception(f"Could not calculate distance: {element['status']}")
                
        # Implement nearest neighbor algorithm
        n = len(locations)
        visited = [False] * n
        route = []
        current = 0  # Start from first location
        total_distance = 0
        total_duration = 0
        
        while len(route) < n:
            visited[current] = True
            route.append({
                'order_id': locations[current]['order_id'],
                'address': locations[current]['address'],
                'distance': distances[current],
                'duration': durations[current]
            })
            
            total_distance += distances[current]
            total_duration += durations[current]
            
            # Find nearest unvisited location
            min_dist = float('inf')
            next_loc = -1
            
            for i in range(n):
                if not visited[i]:
                    if distances[i] < min_dist:
                        min_dist = distances[i]
                        next_loc = i
                        
            if next_loc == -1:
                break
                
            current = next_loc
            
        # Add return to start point
        total_distance += distances[0]
        total_duration += durations[0]
        
        # Calculate estimated completion time
        base_time = datetime.now()
        estimated_completion = base_time + timedelta(seconds=total_duration)
        
        return {
            'route': route,
            'total_distance': total_distance,
            'total_duration': total_duration,
            'estimated_completion': estimated_completion.isoformat()
        }
        
    def get_eta(self, order_id: int) -> Dict:
        """
        Get estimated time of arrival for a specific order
        """
        order = Order.query.get(order_id)
        if not order:
            return {
                'success': False,
                'message': 'Order not found'
            }
            
        # Get hawker's current location
        hawker = User.query.get(order.hawker_id)
        if not hawker or not hawker.latitude or not hawker.longitude:
            return {
                'success': False,
                'message': 'Hawker location not found'
            }
            
        # Get ETA from Google Maps API
        url = "https://maps.googleapis.com/maps/api/distancematrix/json"
        params = {
            'origins': f"{hawker.latitude},{hawker.longitude}",
            'destinations': f"{order.delivery_latitude},{order.delivery_longitude}",
            'mode': 'driving',
            'key': self.api_key
        }
        
        try:
            response = requests.get(url, params=params)
            data = response.json()
            
            if data['status'] != 'OK':
                return {
                    'success': False,
                    'message': f"Google Maps API error: {data['status']}"
                }
                
            element = data['rows'][0]['elements'][0]
            if element['status'] != 'OK':
                return {
                    'success': False,
                    'message': f"Could not calculate ETA: {element['status']}"
                }
                
            duration = element['duration']['value']
            distance = element['distance']['value']
            
            eta = datetime.now() + timedelta(seconds=duration)
            
            return {
                'success': True,
                'eta': eta.isoformat(),
                'duration_seconds': duration,
                'distance_meters': distance
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f"Failed to calculate ETA: {str(e)}"
            } 