from flask import current_app
from app.models.order import Order, OrderRating, OrderDispute
from app.models.user import User
from app import db
from datetime import datetime
import logging
from app.services.notification import NotificationService
from app.services.payment import PaymentService

class OrderService:
    """Service for handling order operations"""
    
    def __init__(self):
        self.notification_service = NotificationService()
        self.payment_service = PaymentService()
    
    def cancel_order(self, order_id, user_id, reason):
        """
        Cancel an order and process refund if necessary
        
        Args:
            order_id: ID of the order to cancel
            user_id: ID of the user requesting cancellation
            reason: Cancellation reason
            
        Returns:
            tuple: (success, message)
        """
        try:
            order = Order.query.get(order_id)
            if not order:
                return False, "Order not found"
            
            # Check if user is authorized to cancel
            if order.customer_id != user_id and order.hawker_id != user_id:
                return False, "Unauthorized to cancel this order"
            
            # Check if order can be cancelled
            if order.status not in ['pending', 'confirmed', 'preparing']:
                return False, f"Order cannot be cancelled in {order.status} status"
            
            # Process refund if payment was made
            if order.payment_status == 'paid':
                refund_result = self.payment_service.process_refund(
                    order.payment_id,
                    order.total_amount,
                    reason
                )
                if not refund_result['success']:
                    return False, f"Failed to process refund: {refund_result['message']}"
            
            # Update order status
            order.status = 'cancelled'
            order.cancelled_at = datetime.utcnow()
            order.cancellation_reason = reason
            order.cancelled_by = user_id
            
            db.session.commit()
            
            # Send notifications
            self.notification_service.send_order_notification(
                order_id=order.id,
                notification_type='order_cancelled',
                data={'reason': reason}
            )
            
            return True, "Order cancelled successfully"
            
        except Exception as e:
            db.session.rollback()
            logging.error(f"Failed to cancel order: {str(e)}")
            return False, "Failed to cancel order"
    
    def rate_order(self, order_id, user_id, rating, comment=None):
        """
        Rate an order
        
        Args:
            order_id: ID of the order to rate
            user_id: ID of the user submitting rating
            rating: Rating value (1-5)
            comment: Optional rating comment
            
        Returns:
            tuple: (success, message)
        """
        try:
            order = Order.query.get(order_id)
            if not order:
                return False, "Order not found"
            
            # Check if user is authorized to rate
            if order.customer_id != user_id:
                return False, "Unauthorized to rate this order"
            
            # Check if order is completed
            if order.status != 'completed':
                return False, "Can only rate completed orders"
            
            # Check if already rated
            existing_rating = OrderRating.query.filter_by(
                order_id=order_id,
                user_id=user_id
            ).first()
            
            if existing_rating:
                return False, "Order already rated"
            
            # Create rating
            rating = OrderRating(
                order_id=order_id,
                user_id=user_id,
                rating=rating,
                comment=comment
            )
            
            db.session.add(rating)
            db.session.commit()
            
            # Update hawker's average rating
            self._update_hawker_rating(order.hawker_id)
            
            # Send notification to hawker
            self.notification_service.send_order_notification(
                order_id=order_id,
                notification_type='order_rated',
                data={'rating': rating, 'comment': comment}
            )
            
            return True, "Rating submitted successfully"
            
        except Exception as e:
            db.session.rollback()
            logging.error(f"Failed to submit rating: {str(e)}")
            return False, "Failed to submit rating"
    
    def create_dispute(self, order_id, user_id, reason, description, evidence=None):
        """
        Create a dispute for an order
        
        Args:
            order_id: ID of the order to dispute
            user_id: ID of the user creating dispute
            reason: Dispute reason
            description: Detailed description
            evidence: Optional evidence files/links
            
        Returns:
            tuple: (success, message)
        """
        try:
            order = Order.query.get(order_id)
            if not order:
                return False, "Order not found"
            
            # Check if user is authorized to create dispute
            if order.customer_id != user_id and order.hawker_id != user_id:
                return False, "Unauthorized to create dispute for this order"
            
            # Check if dispute already exists
            existing_dispute = OrderDispute.query.filter_by(order_id=order_id).first()
            if existing_dispute:
                return False, "Dispute already exists for this order"
            
            # Create dispute
            dispute = OrderDispute(
                order_id=order_id,
                user_id=user_id,
                reason=reason,
                description=description,
                evidence=evidence,
                status='pending'
            )
            
            db.session.add(dispute)
            
            # Update order status
            order.status = 'disputed'
            order.dispute_id = dispute.id
            
            db.session.commit()
            
            # Send notifications
            self.notification_service.send_order_notification(
                order_id=order_id,
                notification_type='order_disputed',
                data={
                    'reason': reason,
                    'description': description
                }
            )
            
            return True, "Dispute created successfully"
            
        except Exception as e:
            db.session.rollback()
            logging.error(f"Failed to create dispute: {str(e)}")
            return False, "Failed to create dispute"
    
    def resolve_dispute(self, dispute_id, admin_id, resolution, action=None):
        """
        Resolve a dispute
        
        Args:
            dispute_id: ID of the dispute to resolve
            admin_id: ID of the admin resolving dispute
            resolution: Resolution details
            action: Action to take (refund, partial_refund, none)
            
        Returns:
            tuple: (success, message)
        """
        try:
            dispute = OrderDispute.query.get(dispute_id)
            if not dispute:
                return False, "Dispute not found"
            
            order = Order.query.get(dispute.order_id)
            
            # Process refund if needed
            if action in ['refund', 'partial_refund']:
                refund_amount = order.total_amount if action == 'refund' else resolution.get('refund_amount')
                refund_result = self.payment_service.process_refund(
                    order.payment_id,
                    refund_amount,
                    f"Dispute resolution: {resolution['reason']}"
                )
                if not refund_result['success']:
                    return False, f"Failed to process refund: {refund_result['message']}"
            
            # Update dispute status
            dispute.status = 'resolved'
            dispute.resolution = resolution
            dispute.resolved_by = admin_id
            dispute.resolved_at = datetime.utcnow()
            
            # Update order status
            order.status = 'cancelled' if action == 'refund' else 'completed'
            
            db.session.commit()
            
            # Send notifications
            self.notification_service.send_order_notification(
                order_id=order.id,
                notification_type='dispute_resolved',
                data={
                    'resolution': resolution,
                    'action': action
                }
            )
            
            return True, "Dispute resolved successfully"
            
        except Exception as e:
            db.session.rollback()
            logging.error(f"Failed to resolve dispute: {str(e)}")
            return False, "Failed to resolve dispute"
    
    def _update_hawker_rating(self, hawker_id):
        """Update hawker's average rating"""
        try:
            # Calculate new average rating
            ratings = OrderRating.query.join(Order).filter(
                Order.hawker_id == hawker_id
            ).all()
            
            if ratings:
                avg_rating = sum(r.rating for r in ratings) / len(ratings)
                
                # Update hawker's rating
                hawker = User.query.get(hawker_id)
                hawker.rating = avg_rating
                
                db.session.commit()
        except Exception as e:
            db.session.rollback()
            logging.error(f"Failed to update hawker rating: {str(e)}") 