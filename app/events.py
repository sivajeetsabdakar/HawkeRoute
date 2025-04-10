from flask_socketio import emit, join_room, leave_room
from flask_login import current_user
from app import socketio
from app.models.order import Order
from app.models.user import User
from app.services.route_optimizer import RouteOptimizer
from app.services.notification import NotificationService
from datetime import datetime
import json

# Initialize route optimizer
route_optimizer = RouteOptimizer()

@socketio.on('connect')
def handle_connect():
    """
    Handle client connection
    """
    if not current_user.is_authenticated:
        return False
    
    # Join user's personal room
    join_room(f'user_{current_user.id}')
    
    # If user is a hawker, join hawker room
    if current_user.is_hawker:
        join_room(f'hawker_{current_user.id}')
    
    # If user is an admin, join admin room
    if current_user.is_admin:
        join_room('admin')
    
    emit('connected', {'user_id': current_user.id, 'username': current_user.username})

@socketio.on('disconnect')
def handle_disconnect():
    """
    Handle client disconnection
    """
    if current_user.is_authenticated:
        # Leave user's personal room
        leave_room(f'user_{current_user.id}')
        
        # If user is a hawker, leave hawker room
        if current_user.is_hawker:
            leave_room(f'hawker_{current_user.id}')
        
        # If user is an admin, leave admin room
        if current_user.is_admin:
            leave_room('admin')

@socketio.on('join_order_tracking')
def handle_join_order_tracking(data):
    """
    Join order tracking room
    """
    if not current_user.is_authenticated:
        return
    
    order_id = data.get('order_id')
    if not order_id:
        return
    
    # Check if user is authorized to track this order
    order = Order.query.get(order_id)
    if not order:
        return
    
    if not (current_user.is_admin or current_user.id == order.customer_id or current_user.id == order.hawker_id):
        return
    
    # Join order room
    join_room(f'order_{order_id}')
    
    # Send initial tracking data
    emit('tracking_joined', {'order_id': order_id})

@socketio.on('leave_order_tracking')
def handle_leave_order_tracking(data):
    """
    Leave order tracking room
    """
    if not current_user.is_authenticated:
        return
    
    order_id = data.get('order_id')
    if not order_id:
        return
    
    # Leave order room
    leave_room(f'order_{order_id}')
    
    emit('tracking_left', {'order_id': order_id})

@socketio.on('location_update')
def handle_location_update(data):
    """
    Handle location update from client
    """
    if not current_user.is_authenticated:
        return
    
    # Validate data
    if not data or 'latitude' not in data or 'longitude' not in data:
        return
    
    try:
        latitude = float(data['latitude'])
        longitude = float(data['longitude'])
    except ValueError:
        return
    
    # Update user location
    current_user.latitude = latitude
    current_user.longitude = longitude
    if 'address' in data:
        current_user.address = data['address']
    
    # If user is a hawker, emit location update to relevant orders
    if current_user.is_hawker:
        # Get active orders for this hawker
        active_orders = Order.query.filter(
            Order.hawker_id == current_user.id,
            Order.status.in_(['confirmed', 'preparing', 'ready', 'delivering'])
        ).all()
        
        # Emit location update to each order's room
        for order in active_orders:
            emit('location_update', {
                'user_id': current_user.id,
                'username': current_user.username,
                'latitude': latitude,
                'longitude': longitude,
                'address': current_user.address,
                'updated_at': datetime.now().isoformat()
            }, room=f'order_{order.id}')

@socketio.on('order_status_update')
def handle_order_status_update(data):
    """
    Handle order status update
    """
    if not current_user.is_authenticated:
        return
    
    order_id = data.get('order_id')
    new_status = data.get('status')
    
    if not order_id or not new_status:
        return
    
    # Get order
    order = Order.query.get(order_id)
    if not order:
        return
    
    # Check if user is authorized to update this order
    if not (current_user.is_admin or current_user.id == order.hawker_id):
        return
    
    # Update order status
    order.status = new_status
    
    # Send notification
    NotificationService.send_order_notification(order_id, new_status)
    
    # Emit status update to order room
    emit('order_status_update', {
        'order_id': order_id,
        'status': new_status,
        'updated_by': current_user.username,
        'updated_at': datetime.now().isoformat()
    }, room=f'order_{order_id}')
    
    # If order is being delivered, start ETA updates
    if new_status == 'delivering':
        # Set API key from config
        route_optimizer.api_key = current_app.config['GOOGLE_MAPS_API_KEY']
        
        # Get ETA
        eta_result = route_optimizer.get_eta(order_id)
        if eta_result['success']:
            emit('eta_update', {
                'order_id': order_id,
                'eta': eta_result['eta'],
                'updated_at': datetime.now().isoformat()
            }, room=f'order_{order_id}')

@socketio.on('route_update')
def handle_route_update(data):
    """
    Handle route update
    """
    if not current_user.is_authenticated:
        return
    
    # Check if user is a hawker
    if not current_user.is_hawker:
        return
    
    # Set API key from config
    route_optimizer.api_key = current_app.config['GOOGLE_MAPS_API_KEY']
    
    # Get current route
    result = route_optimizer.optimize_route(current_user.id)
    
    if result['success']:
        # Add hawker location to result
        result['hawker_location'] = {
            'lat': current_user.latitude,
            'lng': current_user.longitude,
            'address': current_user.address
        }
        
        # Emit route update to hawker room
        emit('route_update', result, room=f'hawker_{current_user.id}')
        
        # Update order delivery sequences
        for idx, stop in enumerate(result['route']):
            order = Order.query.get(stop['order_id'])
            if order:
                order.delivery_sequence = idx + 1
                
                # Emit ETA update to order room
                eta_result = route_optimizer.get_eta(order.id)
                if eta_result['success']:
                    emit('eta_update', {
                        'order_id': order.id,
                        'eta': eta_result['eta'],
                        'updated_at': datetime.now().isoformat()
                    }, room=f'order_{order.id}') 