from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.order import Order, OrderItem
from app.models.product import Product
from app.models.user import User
from app import db
from app.middleware.check_time import check_order_time
from datetime import datetime

orders_bp = Blueprint('orders', __name__)

@orders_bp.route('', methods=['POST'])
@jwt_required()
@check_order_time()
def create_order():
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['hawker_id', 'items', 'delivery_address', 'delivery_latitude', 'delivery_longitude']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Validate hawker exists and is active
    hawker = User.query.filter_by(id=data['hawker_id'], role='hawker', is_active=True).first()
    if not hawker:
        return jsonify({'error': 'Invalid hawker or hawker is inactive'}), 400
    
    # Calculate total amount and validate products
    total_amount = 0
    order_items = []
    
    for item in data['items']:
        if not all(field in item for field in ['product_id', 'quantity']):
            return jsonify({'error': 'Invalid item format'}), 400
        
        product = Product.query.filter_by(
            id=item['product_id'],
            hawker_id=data['hawker_id'],
            is_available=True
        ).first()
        
        if not product:
            return jsonify({'error': f'Product {item["product_id"]} not found or unavailable'}), 400
        
        total_amount += product.price * item['quantity']
        order_items.append({
            'product': product,
            'quantity': item['quantity'],
            'price': product.price
        })
    
    try:
        # Create order
        order = Order(
            customer_id=current_user_id,
            hawker_id=data['hawker_id'],
            total_amount=total_amount,
            delivery_address=data['delivery_address'],
            delivery_latitude=data['delivery_latitude'],
            delivery_longitude=data['delivery_longitude'],
            delivery_instructions=data.get('delivery_instructions'),
            status='pending'
        )
        
        db.session.add(order)
        db.session.flush()  # Get order ID without committing
        
        # Create order items
        for item in order_items:
            order_item = OrderItem(
                order_id=order.id,
                product_id=item['product'].id,
                quantity=item['quantity'],
                price=item['price']
            )
            db.session.add(order_item)
        
        db.session.commit()
        return jsonify(order.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@orders_bp.route('', methods=['GET'])
@jwt_required()
def get_orders():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Get query parameters
    status = request.args.get('status')
    date = request.args.get('date')
    
    # Base query
    if user.role == 'customer':
        query = Order.query.filter_by(customer_id=current_user_id)
    elif user.role == 'hawker':
        query = Order.query.filter_by(hawker_id=current_user_id)
    else:
        query = Order.query
    
    # Apply filters
    if status:
        query = query.filter_by(status=status)
    if date:
        try:
            date_obj = datetime.strptime(date, '%Y-%m-%d').date()
            query = query.filter(db.func.date(Order.created_at) == date_obj)
        except ValueError:
            return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
    
    # Get orders
    orders = query.order_by(Order.created_at.desc()).all()
    return jsonify([order.to_dict() for order in orders]), 200

@orders_bp.route('/<int:order_id>', methods=['GET'])
@jwt_required()
def get_order(order_id):
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    order = Order.query.get(order_id)
    if not order:
        return jsonify({'error': 'Order not found'}), 404
    
    # Check if user has access to this order
    if user.role == 'customer' and order.customer_id != current_user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    elif user.role == 'hawker' and order.hawker_id != current_user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    return jsonify(order.to_dict()), 200

@orders_bp.route('/<int:order_id>/status', methods=['PATCH'])
@jwt_required()
def update_order_status(order_id):
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user or user.role != 'hawker':
        return jsonify({'error': 'Unauthorized'}), 403
    
    order = Order.query.get(order_id)
    if not order:
        return jsonify({'error': 'Order not found'}), 404
    
    if order.hawker_id != current_user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    if 'status' not in data:
        return jsonify({'error': 'Status is required'}), 400
    
    valid_statuses = ['confirmed', 'preparing', 'delivering', 'delivered', 'cancelled']
    if data['status'] not in valid_statuses:
        return jsonify({'error': 'Invalid status'}), 400
    
    try:
        order.status = data['status']
        if data['status'] == 'delivered':
            order.delivery_time = datetime.utcnow()
        
        db.session.commit()
        return jsonify(order.to_dict()), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500 