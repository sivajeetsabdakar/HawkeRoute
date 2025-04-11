from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from app.services.order_service import OrderService
from app.schemas.order_rating_schema import OrderRatingSchema
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.middleware.validation import validate_request
from app.schemas.order_schema import OrderCreateSchema, OrderUpdateSchema, OrderCancellationSchema, OrderRefundSchema
from datetime import datetime

# Create blueprint
bp = Blueprint('order', __name__, url_prefix='/api/orders')

@bp.route('/orders/<int:order_id>/rate', methods=['POST'])
@login_required
@validate_request(OrderRatingSchema)
def rate_order(order_id):
    """
    Rate an order with detailed feedback
    """
    try:
        data = request.get_json()
        
        rating = OrderService.rate_order(
            order_id=order_id,
            user_id=current_user.id,
            rating=data['rating'],
            comment=data.get('comment'),
            food_quality=data.get('food_quality'),
            delivery_time=data.get('delivery_time'),
            communication=data.get('communication'),
            packaging=data.get('packaging'),
            value_for_money=data.get('value_for_money'),
            tags=data.get('tags'),
            photos=data.get('photos')
        )
        
        return jsonify({
            'success': True,
            'message': 'Rating submitted successfully',
            'data': rating
        }), 200
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400
    except Exception as e:
        current_app.logger.error(f"Error rating order: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'An error occurred while submitting the rating'
        }), 500

@bp.route('/<int:order_id>/cancel', methods=['POST'])
@jwt_required()
@validate_request(OrderCancellationSchema)
def cancel_order(order_id):
    """Cancel an order"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        result = order_service.cancel_order(
            order_id=order_id,
            user_id=user_id,
            reason_code=data['reason_code'],
            details=data.get('details')
        )
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@bp.route('/<int:order_id>/refund', methods=['POST'])
@jwt_required()
@validate_request(OrderRefundSchema)
def request_refund(order_id):
    """Request a refund for an order"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        result = order_service.request_refund(
            order_id=order_id,
            user_id=user_id,
            amount=data.get('amount'),
            reason=data.get('reason'),
            details=data.get('details')
        )
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@bp.route('/cancellation-reasons', methods=['GET'])
@jwt_required()
def get_cancellation_reasons():
    """Get all active cancellation reasons"""
    try:
        from app.models.order import CancellationReason
        
        category = request.args.get('category')
        query = CancellationReason.query.filter_by(is_active=True)
        
        if category:
            query = query.filter_by(category=category)
            
        reasons = query.all()
        
        return jsonify({
            'success': True,
            'data': [reason.to_dict() for reason in reasons]
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500 