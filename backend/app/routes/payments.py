from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.order import Order
from app.models.payment import Payment
from app.models.user import User
from app import db
import razorpay
from datetime import datetime

bp = Blueprint('payments', __name__)

def get_razorpay_client():
    """Get Razorpay client instance"""
    return razorpay.Client(
        auth=(current_app.config['RAZORPAY_KEY_ID'], current_app.config['RAZORPAY_KEY_SECRET'])
    )

@bp.route('/initiate', methods=['POST'])
@jwt_required()
def initiate_payment():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.get_json()
    
    # Validate required fields
    if 'order_id' not in data:
        return jsonify({'error': 'Order ID is required'}), 400
    
    order = Order.query.get(data['order_id'])
    if not order:
        return jsonify({'error': 'Order not found'}), 404
    
    # Check if order belongs to the user
    if order.customer_id != current_user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Check if order is already paid
    existing_payment = Payment.query.filter_by(
        order_id=order.id,
        status='success'
    ).first()
    
    if existing_payment:
        return jsonify({'error': 'Order is already paid'}), 400
    
    try:
        # Create Razorpay order
        razorpay_client = get_razorpay_client()
        razorpay_order = razorpay_client.order.create({
            'amount': int(order.total_amount * 100),  # Convert to paise
            'currency': 'INR',
            'receipt': f'order_{order.id}',
            'notes': {
                'order_id': order.id,
                'customer_id': current_user_id
            }
        })
        
        # Create payment record
        payment = Payment(
            order_id=order.id,
            amount=order.total_amount,
            payment_method='razorpay',
            status='pending',
            transaction_id=razorpay_order['id'],
            payment_data=razorpay_order
        )
        
        db.session.add(payment)
        db.session.commit()
        
        return jsonify({
            'order_id': razorpay_order['id'],
            'amount': razorpay_order['amount'],
            'currency': razorpay_order['currency'],
            'key': current_app.config['RAZORPAY_KEY_ID']
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/verify', methods=['POST'])
@jwt_required()
def verify_payment():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['razorpay_payment_id', 'razorpay_order_id', 'razorpay_signature']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    try:
        # Verify payment signature
        razorpay_client = get_razorpay_client()
        razorpay_client.utility.verify_payment_signature({
            'razorpay_payment_id': data['razorpay_payment_id'],
            'razorpay_order_id': data['razorpay_order_id'],
            'razorpay_signature': data['razorpay_signature']
        })
        
        # Get payment record
        payment = Payment.query.filter_by(
            transaction_id=data['razorpay_order_id']
        ).first()
        
        if not payment:
            return jsonify({'error': 'Payment record not found'}), 404
        
        # Update payment status
        payment.status = 'success'
        payment.payment_data = {
            **payment.payment_data,
            'razorpay_payment_id': data['razorpay_payment_id'],
            'razorpay_signature': data['razorpay_signature']
        }
        
        # Update order status
        order = payment.order
        order.status = 'confirmed'
        
        db.session.commit()
        
        return jsonify({
            'message': 'Payment verified successfully',
            'payment': payment.to_dict(),
            'order': order.to_dict()
        }), 200
        
    except razorpay.errors.SignatureVerificationError:
        return jsonify({'error': 'Invalid payment signature'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/cod', methods=['POST'])
@jwt_required()
def record_cod_payment():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user or user.role != 'hawker':
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    
    # Validate required fields
    if 'order_id' not in data:
        return jsonify({'error': 'Order ID is required'}), 400
    
    order = Order.query.get(data['order_id'])
    if not order:
        return jsonify({'error': 'Order not found'}), 404
    
    # Check if order belongs to the hawker
    if order.hawker_id != current_user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Check if order is already paid
    existing_payment = Payment.query.filter_by(
        order_id=order.id,
        status='success'
    ).first()
    
    if existing_payment:
        return jsonify({'error': 'Order is already paid'}), 400
    
    try:
        # Create payment record for COD
        payment = Payment(
            order_id=order.id,
            amount=order.total_amount,
            payment_method='cod',
            status='success',
            transaction_id=f'cod_{order.id}_{datetime.utcnow().timestamp()}'
        )
        
        db.session.add(payment)
        db.session.commit()
        
        return jsonify({
            'message': 'COD payment recorded successfully',
            'payment': payment.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500 