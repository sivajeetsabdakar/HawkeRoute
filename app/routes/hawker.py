from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user import User
from app.services.user import UserService
from app.services.order_service import OrderService
from app.services.route_optimizer import RouteOptimizer

bp = Blueprint('hawker', __name__, url_prefix='/api/hawker')

@bp.route('/orders', methods=['GET'])
@jwt_required()
def get_hawker_orders():
    """Get orders assigned to the hawker"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user or user.role != 'hawker':
            return jsonify({'error': 'Unauthorized access'}), 403
            
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        status = request.args.get('status')
        
        orders = OrderService.get_hawker_orders(user_id, page, per_page, status)
        return jsonify(orders), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/route', methods=['GET'])
@jwt_required()
def get_optimized_route():
    """Get optimized delivery route for the hawker"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user or user.role != 'hawker':
            return jsonify({'error': 'Unauthorized access'}), 403
            
        route = RouteOptimizer.optimize_routes(user)
        return jsonify(route), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/location', methods=['PUT'])
@jwt_required()
def update_location():
    """Update hawker's current location"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user or user.role != 'hawker':
            return jsonify({'error': 'Unauthorized access'}), 403
            
        data = request.get_json()
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        
        if not latitude or not longitude:
            return jsonify({'error': 'Latitude and longitude are required'}), 400
            
        UserService.update_location(user_id, latitude, longitude)
        return jsonify({'message': 'Location updated successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500 