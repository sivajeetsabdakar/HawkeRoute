from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.location import LocationService
from app.middleware.validation import validate_request
from app.schemas.location_schema import LocationUpdateSchema, LocationSearchSchema
from datetime import datetime

bp = Blueprint('location', __name__)
location_service = LocationService()

@bp.route('/update', methods=['POST'])
@jwt_required()
@validate_request(LocationUpdateSchema)
def update_location():
    """Update user's current location"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        location = location_service.update_location(
            user_id=user_id,
            latitude=data['latitude'],
            longitude=data['longitude'],
            accuracy=data.get('accuracy'),
            speed=data.get('speed'),
            heading=data.get('heading'),
            location_type=data.get('location_type', 'idle'),
            order_id=data.get('order_id')
        )
        
        return jsonify({
            'status': 'success',
            'data': location
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@bp.route('/history', methods=['GET'])
@jwt_required()
def get_location_history():
    """Get user's location history"""
    try:
        user_id = get_jwt_identity()
        
        # Parse query parameters
        start_time = request.args.get('start_time')
        end_time = request.args.get('end_time')
        location_type = request.args.get('location_type')
        order_id = request.args.get('order_id')
        limit = request.args.get('limit', 100, type=int)
        
        # Convert time strings to datetime objects
        if start_time:
            start_time = datetime.fromisoformat(start_time)
        if end_time:
            end_time = datetime.fromisoformat(end_time)
        
        history = location_service.get_location_history(
            user_id=user_id,
            start_time=start_time,
            end_time=end_time,
            location_type=location_type,
            order_id=order_id,
            limit=limit
        )
        
        return jsonify({
            'status': 'success',
            'data': history
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@bp.route('/search', methods=['POST'])
@jwt_required()
@validate_request(LocationSearchSchema)
def search_nearby_locations():
    """Search for locations within a radius"""
    try:
        data = request.get_json()
        
        locations = location_service.search_nearby_locations(
            latitude=data['latitude'],
            longitude=data['longitude'],
            radius_km=data.get('radius_km', 5),
            location_type=data.get('location_type'),
            order_id=data.get('order_id')
        )
        
        return jsonify({
            'status': 'success',
            'data': locations
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@bp.route('/current', methods=['GET'])
@jwt_required()
def get_current_location():
    """Get user's current location"""
    try:
        user_id = get_jwt_identity()
        
        location = location_service.get_user_location(user_id)
        
        if not location:
            return jsonify({
                'status': 'error',
                'message': 'No active location found'
            }), 404
        
        return jsonify({
            'status': 'success',
            'data': location
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@bp.route('/active-users', methods=['GET'])
@jwt_required()
def get_active_users_in_area():
    """Get all active users in a specific area"""
    try:
        # Parse query parameters
        latitude = request.args.get('latitude', type=float)
        longitude = request.args.get('longitude', type=float)
        radius_km = request.args.get('radius_km', 5, type=float)
        
        if not latitude or not longitude:
            return jsonify({
                'status': 'error',
                'message': 'Latitude and longitude are required'
            }), 400
        
        users = location_service.get_active_users_in_area(
            latitude=latitude,
            longitude=longitude,
            radius_km=radius_km
        )
        
        return jsonify({
            'status': 'success',
            'data': users
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500 