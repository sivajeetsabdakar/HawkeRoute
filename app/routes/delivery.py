from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user import User
from app.models.order import Order
from app.models.route import HawkerRoute
from app import db
from datetime import datetime, date
import pytz
from app.config import Config

# Import socketio conditionally
try:
    from app import socketio
    SOCKETIO_AVAILABLE = True
except ImportError:
    SOCKETIO_AVAILABLE = False
    # Create a dummy socketio object for when it's not available
    class DummySocketIO:
        def on(self, *args, **kwargs):
            def decorator(f):
                return f
            return decorator
    socketio = DummySocketIO()

bp = Blueprint('delivery', __name__)

@bp.route('/route', methods=['GET'])
@jwt_required()
def get_route():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Get current date in the configured timezone
    tz = pytz.timezone(Config.TIMEZONE)
    current_date = datetime.now(tz).date()
    
    # Get route for today
    route = HawkerRoute.query.filter_by(
        hawker_id=current_user_id,
        date=current_date
    ).first()
    
    if not route:
        return jsonify({'error': 'No route found for today'}), 404
    
    return jsonify(route.to_dict()), 200

@bp.route('/location', methods=['POST'])
@jwt_required()
def update_location():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user or user.role != 'hawker':
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    
    # Validate required fields
    if not all(field in data for field in ['latitude', 'longitude']):
        return jsonify({'error': 'Missing latitude or longitude'}), 400
    
    try:
        # Update hawker's location
        user.latitude = data['latitude']
        user.longitude = data['longitude']
        db.session.commit()
        
        # Emit location update to connected clients
        socketio.emit('location_update', {
            'hawker_id': current_user_id,
            'latitude': data['latitude'],
            'longitude': data['longitude'],
            'timestamp': datetime.utcnow().isoformat()
        }, namespace='/delivery')
        
        return jsonify({'message': 'Location updated successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/track/<int:hawker_id>', methods=['GET'])
@jwt_required()
def track_hawker(hawker_id):
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    hawker = User.query.get(hawker_id)
    if not hawker or hawker.role != 'hawker':
        return jsonify({'error': 'Hawker not found'}), 404
    
    # Check if user has an active order with this hawker
    active_order = Order.query.filter_by(
        customer_id=current_user_id,
        hawker_id=hawker_id,
        status='delivering'
    ).first()
    
    if not active_order:
        return jsonify({'error': 'No active delivery with this hawker'}), 403
    
    # Get current date in the configured timezone
    tz = pytz.timezone(Config.TIMEZONE)
    current_date = datetime.now(tz).date()
    
    # Get route for today
    route = HawkerRoute.query.filter_by(
        hawker_id=hawker_id,
        date=current_date
    ).first()
    
    if not route:
        return jsonify({'error': 'No route found for today'}), 404
    
    return jsonify({
        'hawker': {
            'id': hawker.id,
            'name': hawker.business_name or hawker.name,
            'latitude': hawker.latitude,
            'longitude': hawker.longitude
        },
        'route': route.to_dict(),
        'order': active_order.to_dict()
    }), 200

# Socket.IO event handlers
if SOCKETIO_AVAILABLE:
    @socketio.on('connect', namespace='/delivery')
    def handle_connect():
        print('Client connected to delivery namespace')

    @socketio.on('disconnect', namespace='/delivery')
    def handle_disconnect():
        print('Client disconnected from delivery namespace')

    @socketio.on('join_tracking', namespace='/delivery')
    def handle_join_tracking(data):
        """Join a room to track a specific hawker"""
        if 'hawker_id' in data:
            room = f"hawker_{data['hawker_id']}"
            socketio.join_room(room, namespace='/delivery')
            print(f'Client joined room: {room}')

    @socketio.on('leave_tracking', namespace='/delivery')
    def handle_leave_tracking(data):
        """Leave a room to stop tracking a specific hawker"""
        if 'hawker_id' in data:
            room = f"hawker_{data['hawker_id']}"
            socketio.leave_room(room, namespace='/delivery')
            print(f'Client left room: {room}') 