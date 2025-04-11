from flask import Blueprint, jsonify, request, current_app
from flask_login import login_required, current_user
from app.services.route_optimizer import RouteOptimizer
from app.models.order import Order
from app import db, socketio
from datetime import datetime
import json

bp = Blueprint('eta', __name__, url_prefix='/api/eta')
route_optimizer = RouteOptimizer()

@bp.route('/update/<int:order_id>', methods=['POST'])
@login_required
def update_eta(order_id):
    """
    Update ETA for a specific order
    """
    # Check if user is authorized to update this order
    order = Order.query.get_or_404(order_id)
    if not (current_user.is_admin or current_user.id == order.hawker_id):
        return jsonify({
            'success': False,
            'message': 'Unauthorized to update this order'
        }), 403
    
    data = request.get_json()
    
    # Validate input
    if not data:
        return jsonify({
            'success': False,
            'message': 'No data provided'
        }), 400
    
    # Get ETA data
    eta = data.get('eta')
    if not eta:
        return jsonify({
            'success': False,
            'message': 'ETA is required'
        }), 400
    
    try:
        eta_datetime = datetime.fromisoformat(eta.replace('Z', '+00:00'))
    except ValueError:
        return jsonify({
            'success': False,
            'message': 'Invalid ETA format'
        }), 400
    
    # Update order ETA
    order.eta = eta_datetime
    
    try:
        db.session.commit()
        
        # Emit ETA update via Socket.IO
        socketio.emit('eta_update', {
            'order_id': order_id,
            'eta': eta,
            'updated_by': current_user.username,
            'updated_at': datetime.now().isoformat()
        }, room=f'order_{order_id}')
        
        return jsonify({
            'success': True,
            'message': 'ETA updated successfully'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Failed to update ETA: {str(e)}'
        }), 500

@bp.route('/batch-update', methods=['POST'])
@login_required
def batch_update_eta():
    """
    Update ETA for multiple orders
    """
    # Check if user is a hawker
    if not current_user.is_hawker:
        return jsonify({
            'success': False,
            'message': 'Only hawkers can update ETAs'
        }), 403
    
    data = request.get_json()
    
    # Validate input
    if not data or 'orders' not in data:
        return jsonify({
            'success': False,
            'message': 'No orders provided'
        }), 400
    
    # Set API key from config
    route_optimizer.api_key = current_app.config['GOOGLE_MAPS_API_KEY']
    
    # Process each order
    results = []
    for order_data in data['orders']:
        order_id = order_data.get('order_id')
        if not order_id:
            continue
        
        order = Order.query.get(order_id)
        if not order or order.hawker_id != current_user.id:
            continue
        
        # Get ETA from route optimizer
        eta_result = route_optimizer.get_eta(order_id)
        if not eta_result['success']:
            continue
        
        # Update order ETA
        order.eta = datetime.fromisoformat(eta_result['eta'].replace('Z', '+00:00'))
        
        results.append({
            'order_id': order_id,
            'eta': eta_result['eta'],
            'success': True
        })
    
    try:
        db.session.commit()
        
        # Emit ETA updates via Socket.IO
        for result in results:
            socketio.emit('eta_update', {
                'order_id': result['order_id'],
                'eta': result['eta'],
                'updated_by': current_user.username,
                'updated_at': datetime.now().isoformat()
            }, room=f'order_{result["order_id"]}')
        
        return jsonify({
            'success': True,
            'message': 'ETAs updated successfully',
            'results': results
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Failed to update ETAs: {str(e)}'
        }), 500

@bp.route('/<int:order_id>', methods=['GET'])
@login_required
def get_eta(order_id):
    """
    Get ETA for a specific order
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