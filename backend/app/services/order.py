from flask import current_app
from app.models.order import Order, OrderRating, OrderDispute
from app.models.user import User
from app import db
from datetime import datetime
import logging
from app.services.notification import NotificationService
from app.services.payment import PaymentService
from app.models.cancellation_reason import CancellationReason
from app.models.payment import Payment

class OrderService:
    """Service for handling order operations"""
    
    def __init__(self):
        self.notification_service = NotificationService()
        self.payment_service = PaymentService()
    
    def cancel_order(self, order_id, user_id, reason_code, details=None):
        """
        Cancel an order and process refund if necessary
        
        Args:
            order_id: ID of the order to cancel
            user_id: ID of the user requesting cancellation
            reason_code: Code of the cancellation reason
            details: Additional details about the cancellation
            
        Returns:
            dict: Result of the cancellation operation
        """
        try:
            order = Order.query.get(order_id)
            if not order:
                return {
                    'success': False,
                    'message': "Order not found"
                }
            
            # Check if user is authorized to cancel
            if order.customer_id != user_id and order.hawker_id != user_id:
                return {
                    'success': False,
                    'message': "Unauthorized to cancel this order"
                }
            
            # Check if order can be cancelled
            if order.status in ['delivered', 'cancelled']:
                return {
                    'success': False,
                    'message': f"Order cannot be cancelled in {order.status} status"
                }
            
            # Get cancellation reason
            cancellation_reason = CancellationReason.query.filter_by(
                code=reason_code,
                is_active=True
            ).first()
            
            if not cancellation_reason:
                return {
                    'success': False,
                    'message': "Invalid cancellation reason"
                }
            
            # Update order status
            order.status = 'cancelled'
            order.cancelled_at = datetime.utcnow()
            order.cancelled_by = user_id
            order.cancellation_reason = reason_code
            order.cancellation_details = details
            
            # Process refund if payment was made and refund is required
            if order.payment_status == 'paid' and cancellation_reason.requires_refund:
                # Calculate refund amount based on percentage
                refund_amount = order.total_amount * (cancellation_reason.refund_percentage / 100.0)
                
                # Update refund status
                order.refund_status = 'pending'
                order.refund_amount = refund_amount
                
                # Process refund
                refund_result = self.payment_service.process_refund(
                    order.payment_id,
                    refund_amount,
                    f"Order cancellation: {cancellation_reason.name}"
                )
                
                if refund_result['success']:
                    order.refund_status = 'completed'
                    order.refunded_at = datetime.utcnow()
                    order.payment_status = 'refunded' if refund_amount == order.total_amount else 'partially_refunded'
                else:
                    order.refund_status = 'failed'
                    # Log the refund failure but don't prevent cancellation
                    logging.error(f"Refund failed for order {order_id}: {refund_result['message']}")
            
            # Save changes
            db.session.commit()
            
            # Send notifications
            self.notification_service.send_order_notification(
                order_id=order_id,
                notification_type='order_cancelled',
                data={
                    'cancelled_by': user_id,
                    'reason': cancellation_reason.name,
                    'details': details,
                    'refund_status': order.refund_status,
                    'refund_amount': order.refund_amount
                }
            )
            
            return {
                'success': True,
                'message': "Order cancelled successfully",
                'data': {
                    'order_id': order_id,
                    'status': order.status,
                    'cancelled_at': order.cancelled_at.isoformat(),
                    'cancellation_reason': cancellation_reason.name,
                    'refund_status': order.refund_status,
                    'refund_amount': order.refund_amount
                }
            }
            
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error cancelling order {order_id}: {str(e)}")
            return {
                'success': False,
                'message': f"Error cancelling order: {str(e)}"
            }
    
    def rate_order(self, order_id, user_id, rating, comment=None, 
                  product_quality=None, delivery_time=None, communication=None,
                  packaging=None, value_for_money=None, product_condition=None,
                  tags=None, photos=None):
        """
        Rate an order with detailed feedback for any type of product
        """
        order = Order.query.get_or_404(order_id)
        
        # Verify user is authorized to rate this order
        if user_id not in [order.customer_id, order.hawker_id]:
            raise ValueError("User is not authorized to rate this order")
        
        # Check if order is completed
        if order.status != 'completed':
            raise ValueError("Order must be completed before rating")
        
        # Check if already rated
        existing_rating = OrderRating.query.filter_by(
            order_id=order_id,
            user_id=user_id
        ).first()
        
        if existing_rating:
            raise ValueError("Order has already been rated")
            
        # Create rating
        rating = OrderRating(
            order_id=order_id,
            user_id=user_id,
            rating=rating,
            comment=comment,
            product_quality=product_quality,
            delivery_time=delivery_time,
            communication=communication,
            packaging=packaging,
            value_for_money=value_for_money,
            product_condition=product_condition,
            tags=tags,
            photos=photos
        )
        
        try:
            db.session.add(rating)
            
            # Update hawker's average rating
            if user_id == order.customer_id:  # Only customer ratings affect hawker rating
                hawker = User.query.get(order.hawker_id)
                if hawker:
                    # Calculate new average rating
                    all_ratings = OrderRating.query.join(Order).filter(
                        Order.hawker_id == order.hawker_id,
                        Order.status == 'completed'
                    ).all()
                    
                    if all_ratings:
                        total_rating = sum(r.rating for r in all_ratings)
                        hawker.rating = total_rating / len(all_ratings)
            
            db.session.commit()
            
            # Send notification to hawker
            self.notification_service.send_order_notification(
                order_id=order_id,
                notification_type='order_rated',
                data={'rating': rating.to_dict()}
            )
            
            return rating.to_dict()
            
        except Exception as e:
            db.session.rollback()
            logging.error(f"Failed to submit rating: {str(e)}")
            raise
    
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
    
    def resolve_dispute(self, dispute_id, admin_id, resolution_type, action=None, refund_amount=None):
        """
        Resolve a dispute with different resolution types and actions
        
        Args:
            dispute_id: ID of the dispute to resolve
            admin_id: ID of the admin resolving dispute
            resolution_type: Type of resolution (refund, partial_refund, reject, accept)
            action: Additional action to take (e.g., 'block_hawker', 'warn_customer')
            refund_amount: Amount to refund for partial refunds
            
        Returns:
            tuple: (success, message)
        """
        try:
            dispute = OrderDispute.query.get(dispute_id)
            if not dispute:
                return False, "Dispute not found"
            
            order = Order.query.get(dispute.order_id)
            
            # Process refund if needed
            if resolution_type in ['refund', 'partial_refund']:
                amount = order.total_amount if resolution_type == 'refund' else refund_amount
                if not amount:
                    return False, "Refund amount is required for partial refund"
                    
                refund_result = self.payment_service.process_refund(
                    order.payment_id,
                    amount,
                    f"Dispute resolution: {resolution_type}"
                )
                if not refund_result['success']:
                    return False, f"Failed to process refund: {refund_result['message']}"
            
            # Take additional actions
            if action:
                if action == 'block_hawker':
                    hawker = User.query.get(order.hawker_id)
                    hawker.status = 'blocked'
                    hawker.blocked_reason = f"Multiple disputes: {dispute.reason}"
                elif action == 'warn_customer':
                    customer = User.query.get(order.customer_id)
                    customer.warning_count = (customer.warning_count or 0) + 1
            
            # Update dispute status
            dispute.status = 'resolved'
            dispute.resolution = {
                'type': resolution_type,
                'action': action,
                'refund_amount': float(amount) if resolution_type in ['refund', 'partial_refund'] else None,
                'resolved_by': admin_id,
                'resolved_at': datetime.utcnow().isoformat()
            }
            dispute.resolved_by = admin_id
            dispute.resolved_at = datetime.utcnow()
            
            # Update order status
            order.status = 'cancelled' if resolution_type == 'refund' else 'completed'
            
            db.session.commit()
            
            # Send notifications
            self.notification_service.send_order_notification(
                order_id=order.id,
                notification_type='dispute_resolved',
                data={
                    'resolution_type': resolution_type,
                    'action': action,
                    'refund_amount': float(amount) if resolution_type in ['refund', 'partial_refund'] else None
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
    
    def request_refund(self, order_id, user_id, amount=None, reason=None, details=None):
        """
        Request a refund for an order
        
        Args:
            order_id: ID of the order to refund
            user_id: ID of the user requesting the refund
            amount: Amount to refund (optional, defaults to full amount)
            reason: Reason for the refund
            details: Additional details about the refund request
            
        Returns:
            dict: Result of the refund request
        """
        try:
            order = Order.query.get(order_id)
            if not order:
                return {
                    'success': False,
                    'message': "Order not found"
                }
            
            # Check if user is authorized to request refund
            if order.customer_id != user_id and order.hawker_id != user_id:
                return {
                    'success': False,
                    'message': "Unauthorized to request refund for this order"
                }
            
            # Check if order is eligible for refund
            if order.payment_status not in ['paid', 'partially_refunded']:
                return {
                    'success': False,
                    'message': f"Order with payment status '{order.payment_status}' is not eligible for refund"
                }
            
            # Check if order is already fully refunded
            if order.payment_status == 'refunded':
                return {
                    'success': False,
                    'message': "Order has already been fully refunded"
                }
            
            # Get payment
            payment = Payment.query.get(order.payment_id)
            if not payment:
                return {
                    'success': False,
                    'message': "Payment not found for this order"
                }
            
            # Calculate refund amount
            refund_amount = amount
            if refund_amount is None:
                # Full refund
                refund_amount = order.total_amount - (order.refund_amount or 0)
            else:
                # Partial refund
                remaining_amount = order.total_amount - (order.refund_amount or 0)
                if refund_amount > remaining_amount:
                    return {
                        'success': False,
                        'message': f"Refund amount exceeds remaining amount ({remaining_amount})"
                    }
            
            # Process refund
            refund_result = self.payment_service.process_refund(
                payment.id,
                refund_amount,
                reason
            )
            
            if not refund_result['success']:
                return {
                    'success': False,
                    'message': f"Failed to process refund: {refund_result['message']}"
                }
            
            # Update order refund status
            order.refund_status = 'completed' if refund_result['success'] else 'failed'
            order.refund_amount = (order.refund_amount or 0) + refund_amount
            order.refunded_at = datetime.utcnow()
            
            # Update payment status
            if order.refund_amount >= order.total_amount:
                order.payment_status = 'refunded'
            else:
                order.payment_status = 'partially_refunded'
            
            # Save changes
            db.session.commit()
            
            # Send notifications
            self.notification_service.send_order_notification(
                order_id=order_id,
                notification_type='order_refunded',
                data={
                    'refunded_by': user_id,
                    'reason': reason,
                    'details': details,
                    'refund_amount': refund_amount,
                    'total_refunded': order.refund_amount,
                    'remaining_amount': order.total_amount - order.refund_amount
                }
            )
            
            return {
                'success': True,
                'message': "Refund processed successfully",
                'data': {
                    'order_id': order_id,
                    'refund_amount': refund_amount,
                    'total_refunded': float(order.refund_amount),
                    'remaining_amount': float(order.total_amount - order.refund_amount),
                    'payment_status': order.payment_status
                }
            }
            
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error processing refund for order {order_id}: {str(e)}")
            return {
                'success': False,
                'message': f"Error processing refund: {str(e)}"
            } 