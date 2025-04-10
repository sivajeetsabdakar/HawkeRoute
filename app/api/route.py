from flask import Blueprint, jsonify, request, current_app
from flask_login import login_required, current_user
from app.services.route_optimizer import RouteOptimizer
from app.models.order import Order
from app.models.user import User
from app import db
from datetime import datetime
import json

bp = Blueprint('route', __name__, url_prefix='/api/route')
route_optimizer = RouteOptimizer()

@bp.route('/optimize', methods=['POST'])
@login_required
def optimize_route():
    """
    Optimize delivery route for a hawker
    """
    # Check if user is a hawker
    if not current_user.is_hawker:
        return jsonify({
            'success': False,
            'message': 'Only hawkers can optimize routes'
        }), 403
    
    data = request.get_json()
    
    # Validate input
    if not data:
        return jsonify({
            'success': False,
            'message': 'No data provided'
        }), 400
    
    # Parse date
    try:
        date = datetime.strptime(data.get('date', datetime.now().strftime('%Y-%m-%d')), '%Y-%m-%d')
    except ValueError:
        return jsonify({
            'success': False,
            'message': 'Invalid date format'
        }), 400
    
    # Get optimization parameters
    strategy = data.get('strategy', 'distance')
    time_window = data.get('time_window', 8)
    return_to_start = data.get('return_to_start', True)
    
    # Set API key from config
    route_optimizer.api_key = current_app.config['GOOGLE_MAPS_API_KEY']
    
    # Optimize route
    result = route_optimizer.optimize_route(current_user.id, date)
    
    if not result['success']:
        return jsonify(result), 400
    
    # Add hawker location to result
    result['hawker_location'] = {
        'lat': current_user.latitude,
        'lng': current_user.longitude,
        'address': current_user.address
    }
    
    return jsonify(result)

@bp.route('/current', methods=['GET'])
@login_required
def get_current_route():
    """
    Get current optimized route for a hawker
    """
    # Check if user is a hawker
    if not current_user.is_hawker:
        return jsonify({
            'success': False,
            'message': 'Only hawkers can view routes'
        }), 403
    
    # Set API key from config
    route_optimizer.api_key = current_app.config['GOOGLE_MAPS_API_KEY']
    
    # Get current route
    result = route_optimizer.optimize_route(current_user.id)
    
    if not result['success']:
        return jsonify(result), 400
    
    # Add hawker location to result
    result['hawker_location'] = {
        'lat': current_user.latitude,
        'lng': current_user.longitude,
        'address': current_user.address
    }
    
    return jsonify(result)

@bp.route('/save', methods=['POST'])
@login_required
def save_route():
    """
    Save the current optimized route
    """
    # Check if user is a hawker
    if not current_user.is_hawker:
        return jsonify({
            'success': False,
            'message': 'Only hawkers can save routes'
        }), 403
    
    # Get current route
    result = route_optimizer.optimize_route(current_user.id)
    
    if not result['success']:
        return jsonify(result), 400
    
    # Update order delivery sequences
    for idx, stop in enumerate(result['route']):
        order = Order.query.get(stop['order_id'])
        if order:
            order.delivery_sequence = idx + 1
    
    try:
        db.session.commit()
        return jsonify({
            'success': True,
            'message': 'Route saved successfully'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Failed to save route: {str(e)}'
        }), 500

@bp.route('/eta/<int:order_id>', methods=['GET'])
@login_required
def get_eta(order_id):
    """
    Get estimated time of arrival for a specific order
    """
    # Check if user is authorized to view this order
    order = Order.query.get_or_404(order_id)
    if not (current_user.is_admin or current_user.id == order.customer_id or current_user.id == order.hawker_id):
        return jsonify({
            'success': False,
            'message': 'Unauthorized to view this order'
        }), 403
    
    # Set API key from config
    route_optimizer.api_key = current_app.config['GOOGLE_MAPS_API_KEY']
    
    # Get ETA
    result = route_optimizer.get_eta(order_id)
    
    if not result['success']:
        return jsonify(result), 400
    
    return jsonify(result) 