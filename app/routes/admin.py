from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user import User
from app.models.order import Order
from app.models.product import Product
from app.models.payment import Payment
from app import db
from datetime import datetime, timedelta
from sqlalchemy import func

bp = Blueprint('admin', __name__)

def admin_required(f):
    """Decorator to check if the user is an admin"""
    @jwt_required()
    def decorated_function(*args, **kwargs):
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or user.role != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        return f(*args, **kwargs)
    
    decorated_function.__name__ = f.__name__
    return decorated_function

@bp.route('/users', methods=['GET'])
@admin_required
def get_users():
    # Get query parameters
    role = request.args.get('role')
    is_active = request.args.get('is_active', type=bool)
    search = request.args.get('search')
    
    # Base query
    query = User.query
    
    # Apply filters
    if role:
        query = query.filter_by(role=role)
    if is_active is not None:
        query = query.filter_by(is_active=is_active)
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (User.name.ilike(search_term)) |
            (User.email.ilike(search_term)) |
            (User.phone.ilike(search_term))
        )
    
    # Get users
    users = query.order_by(User.created_at.desc()).all()
    return jsonify([user.to_dict() for user in users]), 200

@bp.route('/users/<int:user_id>', methods=['GET'])
@admin_required
def get_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify(user.to_dict()), 200

@bp.route('/users/<int:user_id>', methods=['PUT'])
@admin_required
def update_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.get_json()
    
    try:
        if 'name' in data:
            user.name = data['name']
        if 'email' in data:
            user.email = data['email']
        if 'phone' in data:
            user.phone = data['phone']
        if 'role' in data and data['role'] in ['customer', 'hawker', 'admin']:
            user.role = data['role']
        if 'is_active' in data:
            user.is_active = data['is_active']
        if 'business_name' in data and user.role == 'hawker':
            user.business_name = data['business_name']
        if 'business_address' in data and user.role == 'hawker':
            user.business_address = data['business_address']
        
        db.session.commit()
        return jsonify(user.to_dict()), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/users/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    try:
        # Instead of deleting, deactivate the user
        user.is_active = False
        db.session.commit()
        return jsonify({'message': 'User deactivated successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/orders', methods=['GET'])
@admin_required
def get_orders():
    # Get query parameters
    status = request.args.get('status')
    hawker_id = request.args.get('hawker_id', type=int)
    customer_id = request.args.get('customer_id', type=int)
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    
    # Base query
    query = Order.query
    
    # Apply filters
    if status:
        query = query.filter_by(status=status)
    if hawker_id:
        query = query.filter_by(hawker_id=hawker_id)
    if customer_id:
        query = query.filter_by(customer_id=customer_id)
    if date_from:
        try:
            date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
            query = query.filter(db.func.date(Order.created_at) >= date_from_obj)
        except ValueError:
            return jsonify({'error': 'Invalid date_from format. Use YYYY-MM-DD'}), 400
    if date_to:
        try:
            date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
            query = query.filter(db.func.date(Order.created_at) <= date_to_obj)
        except ValueError:
            return jsonify({'error': 'Invalid date_to format. Use YYYY-MM-DD'}), 400
    
    # Get orders
    orders = query.order_by(Order.created_at.desc()).all()
    return jsonify([order.to_dict() for order in orders]), 200

@bp.route('/orders/<int:order_id>', methods=['GET'])
@admin_required
def get_order(order_id):
    order = Order.query.get(order_id)
    if not order:
        return jsonify({'error': 'Order not found'}), 404
    
    return jsonify(order.to_dict()), 200

@bp.route('/orders/<int:order_id>/resolve', methods=['POST'])
@admin_required
def resolve_order_dispute(order_id):
    order = Order.query.get(order_id)
    if not order:
        return jsonify({'error': 'Order not found'}), 404
    
    data = request.get_json()
    
    # Validate required fields
    if 'resolution' not in data or 'status' not in data:
        return jsonify({'error': 'Missing resolution or status'}), 400
    
    if data['status'] not in ['cancelled', 'delivered', 'refunded']:
        return jsonify({'error': 'Invalid status'}), 400
    
    try:
        # Update order status
        order.status = data['status']
        
        # If refunded, create a refund record
        if data['status'] == 'refunded':
            # Check if payment exists
            payment = Payment.query.filter_by(order_id=order.id).first()
            if payment and payment.status == 'success':
                # Create refund record
                refund = Payment(
                    order_id=order.id,
                    amount=-order.total_amount,  # Negative amount for refund
                    payment_method=payment.payment_method,
                    status='success',
                    transaction_id=f"refund_{payment.transaction_id}",
                    payment_data={
                        'original_payment_id': payment.transaction_id,
                        'reason': data.get('reason', 'Admin refund')
                    }
                )
                db.session.add(refund)
        
        db.session.commit()
        return jsonify(order.to_dict()), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/products', methods=['GET'])
@admin_required
def get_products():
    # Get query parameters
    hawker_id = request.args.get('hawker_id', type=int)
    is_available = request.args.get('is_available', type=bool)
    
    # Base query
    query = Product.query
    
    # Apply filters
    if hawker_id:
        query = query.filter_by(hawker_id=hawker_id)
    if is_available is not None:
        query = query.filter_by(is_available=is_available)
    
    # Get products
    products = query.order_by(Product.created_at.desc()).all()
    return jsonify([product.to_dict() for product in products]), 200

@bp.route('/products/<int:product_id>', methods=['PUT'])
@admin_required
def update_product(product_id):
    product = Product.query.get(product_id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    
    data = request.get_json()
    
    try:
        if 'name' in data:
            product.name = data['name']
        if 'description' in data:
            product.description = data['description']
        if 'price' in data:
            product.price = data['price']
        if 'is_available' in data:
            product.is_available = data['is_available']
        
        db.session.commit()
        return jsonify(product.to_dict()), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/dashboard', methods=['GET'])
@admin_required
def get_dashboard_stats():
    # Get date range
    today = datetime.now().date()
    last_week = today - timedelta(days=7)
    last_month = today - timedelta(days=30)
    
    # Get stats
    total_users = User.query.count()
    total_customers = User.query.filter_by(role='customer').count()
    total_hawkers = User.query.filter_by(role='hawker').count()
    
    total_orders = Order.query.count()
    orders_today = Order.query.filter(db.func.date(Order.created_at) == today).count()
    orders_this_week = Order.query.filter(db.func.date(Order.created_at) >= last_week).count()
    orders_this_month = Order.query.filter(db.func.date(Order.created_at) >= last_month).count()
    
    total_revenue = db.session.query(func.sum(Order.total_amount)).filter_by(status='delivered').scalar() or 0
    revenue_today = db.session.query(func.sum(Order.total_amount)).filter(
        Order.status == 'delivered',
        db.func.date(Order.created_at) == today
    ).scalar() or 0
    revenue_this_week = db.session.query(func.sum(Order.total_amount)).filter(
        Order.status == 'delivered',
        db.func.date(Order.created_at) >= last_week
    ).scalar() or 0
    revenue_this_month = db.session.query(func.sum(Order.total_amount)).filter(
        Order.status == 'delivered',
        db.func.date(Order.created_at) >= last_month
    ).scalar() or 0
    
    # Get order status distribution
    order_status = db.session.query(
        Order.status, func.count(Order.id)
    ).group_by(Order.status).all()
    
    status_distribution = {status: count for status, count in order_status}
    
    return jsonify({
        'users': {
            'total': total_users,
            'customers': total_customers,
            'hawkers': total_hawkers
        },
        'orders': {
            'total': total_orders,
            'today': orders_today,
            'this_week': orders_this_week,
            'this_month': orders_this_month,
            'status_distribution': status_distribution
        },
        'revenue': {
            'total': total_revenue,
            'today': revenue_today,
            'this_week': revenue_this_week,
            'this_month': revenue_this_month
        }
    }), 200 