from flask import Blueprint, jsonify, request, current_app
from flask_login import login_required, current_user
from app.models.user import User
from app.models.order import Order
from app import db, socketio
from datetime import datetime
import json

bp = Blueprint('location', __name__, url_prefix='/api/location')

@bp.route('/update', methods=['POST'])
@login_required
def update_location():
    """
    Update user's current location
    """
    data = request.get_json()
    
    # Validate input
    if not data:
        return jsonify({
            'success': False,
            'message': 'No data provided'
        }), 400
    
    # Get location data
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    address = data.get('address')
    
    if latitude is None or longitude is None:
        return jsonify({
            'success': False,
            'message': 'Latitude and longitude are required'
        }), 400
    
    try:
        latitude = float(latitude)
        longitude = float(longitude)
    except ValueError:
        return jsonify({
            'success': False,
            'message': 'Invalid latitude or longitude'
        }), 400
    
    # Update user location
    current_user.latitude = latitude
    current_user.longitude = longitude
    if address:
        current_user.address = address
    
    try:
        db.session.commit()
        
        # If user is a hawker, emit location update to relevant orders
        if current_user.is_hawker:
            # Get active orders for this hawker
            active_orders = Order.query.filter(
                Order.hawker_id == current_user.id,
                Order.status.in_(['confirmed', 'preparing', 'ready', 'delivering'])
            ).all()
            
            # Emit location update to each order's room
            for order in active_orders:
                socketio.emit('location_update', {
                    'user_id': current_user.id,
                    'username': current_user.username,
                    'latitude': latitude,
                    'longitude': longitude,
                    'address': address,
                    'updated_at': datetime.now().isoformat()
                }, room=f'order_{order.id}')
        
        return jsonify({
            'success': True,
            'message': 'Location updated successfully'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Failed to update location: {str(e)}'
        }), 500

@bp.route('/batch-update', methods=['POST'])
@login_required
def batch_update_location():
    """
    Update location for multiple users (admin only)
    """
    # Check if user is admin
    if not current_user.is_admin:
        return jsonify({
            'success': False,
            'message': 'Only admins can update multiple locations'
        }), 403
    
    data = request.get_json()
    
    # Validate input
    if not data or 'users' not in data:
        return jsonify({
            'success': False,
            'message': 'No users provided'
        }), 400
    
    # Process each user
    results = []
    for user_data in data['users']:
        user_id = user_data.get('user_id')
        if not user_id:
            continue
        
        user = User.query.get(user_id)
        if not user:
            continue
        
        # Get location data
        latitude = user_data.get('latitude')
        longitude = user_data.get('longitude')
        address = user_data.get('address')
        
        if latitude is None or longitude is None:
            continue
        
        try:
            latitude = float(latitude)
            longitude = float(longitude)
        except ValueError:
            continue
        
        # Update user location
        user.latitude = latitude
        user.longitude = longitude
        if address:
            user.address = address
        
        results.append({
            'user_id': user_id,
            'success': True
        })
    
    try:
        db.session.commit()
        
        # Emit location updates via Socket.IO
        for result in results:
            user = User.query.get(result['user_id'])
            if user and user.is_hawker:
                # Get active orders for this hawker
                active_orders = Order.query.filter(
                    Order.hawker_id == user.id,
                    Order.status.in_(['confirmed', 'preparing', 'ready', 'delivering'])
                ).all()
                
                # Emit location update to each order's room
                for order in active_orders:
                    socketio.emit('location_update', {
                        'user_id': user.id,
                        'username': user.username,
                        'latitude': user.latitude,
                        'longitude': user.longitude,
                        'address': user.address,
                        'updated_at': datetime.now().isoformat()
                    }, room=f'order_{order.id}')
        
        return jsonify({
            'success': True,
            'message': 'Locations updated successfully',
            'results': results
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Failed to update locations: {str(e)}'
        }), 500

@bp.route('/<int:user_id>', methods=['GET'])
@login_required
def get_location(user_id):
    """
    Get user's current location
    """
    # Check if user is authorized to view this location
    if not (current_user.is_admin or current_user.id == user_id):
        return jsonify({
            'success': False,
            'message': 'Unauthorized to view this location'
        }), 403
    
    user = User.query.get_or_404(user_id)
    
    return jsonify({
        'success': True,
        'user_id': user.id,
        'username': user.username,
        'latitude': user.latitude,
        'longitude': user.longitude,
        'address': user.address
    }) 