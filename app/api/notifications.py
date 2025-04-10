from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user import User
from app.models.notification import Notification
from app import db
from datetime import datetime, timedelta

notifications_bp = Blueprint('notifications', __name__)

@notifications_bp.route('/preferences', methods=['GET'])
@jwt_required()
def get_preferences():
    """Get user's notification preferences"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    preferences = {
        'notify_order_created': user.notify_order_created,
        'notify_order_confirmed': user.notify_order_confirmed,
        'notify_order_preparing': user.notify_order_preparing,
        'notify_order_ready': user.notify_order_ready,
        'notify_order_delivered': user.notify_order_delivered,
        'notify_order_cancelled': user.notify_order_cancelled,
        'notify_account_updates': user.notify_account_updates,
        'notify_promotions': user.notify_promotions,
        'notify_email': user.notify_email,
        'notify_push': user.notify_push,
        'notify_sms': user.notify_sms
    }
    
    return jsonify(preferences)

@notifications_bp.route('/preferences', methods=['POST'])
@jwt_required()
def update_preferences():
    """Update user's notification preferences"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.get_json()
    
    # Update preferences
    if 'notify_order_created' in data:
        user.notify_order_created = bool(data['notify_order_created'])
    if 'notify_order_confirmed' in data:
        user.notify_order_confirmed = bool(data['notify_order_confirmed'])
    if 'notify_order_preparing' in data:
        user.notify_order_preparing = bool(data['notify_order_preparing'])
    if 'notify_order_ready' in data:
        user.notify_order_ready = bool(data['notify_order_ready'])
    if 'notify_order_delivered' in data:
        user.notify_order_delivered = bool(data['notify_order_delivered'])
    if 'notify_order_cancelled' in data:
        user.notify_order_cancelled = bool(data['notify_order_cancelled'])
    if 'notify_account_updates' in data:
        user.notify_account_updates = bool(data['notify_account_updates'])
    if 'notify_promotions' in data:
        user.notify_promotions = bool(data['notify_promotions'])
    if 'notify_email' in data:
        user.notify_email = bool(data['notify_email'])
    if 'notify_push' in data:
        user.notify_push = bool(data['notify_push'])
    if 'notify_sms' in data:
        user.notify_sms = bool(data['notify_sms'])
    
    try:
        db.session.commit()
        return jsonify({'message': 'Preferences updated successfully'})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Failed to update preferences: {str(e)}")
        return jsonify({'error': 'Failed to update preferences'}), 500

@notifications_bp.route('/history', methods=['GET'])
@jwt_required()
def get_history():
    """Get user's notification history"""
    user_id = get_jwt_identity()
    
    # Get query parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    notification_type = request.args.get('type')
    read_status = request.args.get('read')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    # Build query
    query = Notification.query.filter_by(user_id=user_id)
    
    # Apply filters
    if notification_type:
        query = query.filter_by(type=notification_type)
    if read_status is not None:
        query = query.filter_by(read=(read_status.lower() == 'true'))
    if start_date:
        try:
            start_date = datetime.fromisoformat(start_date)
            query = query.filter(Notification.created_at >= start_date)
        except ValueError:
            return jsonify({'error': 'Invalid start_date format'}), 400
    if end_date:
        try:
            end_date = datetime.fromisoformat(end_date)
            query = query.filter(Notification.created_at <= end_date)
        except ValueError:
            return jsonify({'error': 'Invalid end_date format'}), 400
    
    # Order by created_at descending
    query = query.order_by(Notification.created_at.desc())
    
    # Paginate results
    pagination = query.paginate(page=page, per_page=per_page)
    
    # Prepare response
    notifications = [notification.to_dict() for notification in pagination.items]
    
    return jsonify({
        'notifications': notifications,
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    })

@notifications_bp.route('/mark-read', methods=['POST'])
@jwt_required()
def mark_read():
    """Mark notifications as read"""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data or 'notification_ids' not in data:
        return jsonify({'error': 'notification_ids is required'}), 400
    
    notification_ids = data['notification_ids']
    
    try:
        # Mark notifications as read
        Notification.query.filter(
            Notification.id.in_(notification_ids),
            Notification.user_id == user_id
        ).update(
            {
                'read': True,
                'read_at': datetime.utcnow()
            },
            synchronize_session=False
        )
        
        db.session.commit()
        return jsonify({'message': 'Notifications marked as read'})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Failed to mark notifications as read: {str(e)}")
        return jsonify({'error': 'Failed to mark notifications as read'}), 500

@notifications_bp.route('/mark-all-read', methods=['POST'])
@jwt_required()
def mark_all_read():
    """Mark all notifications as read"""
    user_id = get_jwt_identity()
    
    try:
        # Mark all notifications as read
        Notification.query.filter_by(
            user_id=user_id,
            read=False
        ).update(
            {
                'read': True,
                'read_at': datetime.utcnow()
            },
            synchronize_session=False
        )
        
        db.session.commit()
        return jsonify({'message': 'All notifications marked as read'})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Failed to mark all notifications as read: {str(e)}")
        return jsonify({'error': 'Failed to mark all notifications as read'}), 500

@notifications_bp.route('/unread-count', methods=['GET'])
@jwt_required()
def get_unread_count():
    """Get count of unread notifications"""
    user_id = get_jwt_identity()
    
    try:
        count = Notification.query.filter_by(
            user_id=user_id,
            read=False
        ).count()
        
        return jsonify({'unread_count': count})
    except Exception as e:
        current_app.logger.error(f"Failed to get unread count: {str(e)}")
        return jsonify({'error': 'Failed to get unread count'}), 500 