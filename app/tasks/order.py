from app.tasks import celery
from app.models.order import Order
from app.models.user import User
from app.services.notification import NotificationService
from datetime import datetime, timedelta
from sqlalchemy import and_
import logging

logger = logging.getLogger(__name__)

@celery.task(bind=True, max_retries=3)
def cleanup_expired_orders(self):
    """Clean up expired orders that haven't been accepted."""
    try:
        # Find orders that are older than 30 minutes and still pending
        expiry_time = datetime.utcnow() - timedelta(minutes=30)
        expired_orders = Order.query.filter(
            and_(
                Order.status == 'pending',
                Order.created_at < expiry_time
            )
        ).all()
        
        for order in expired_orders:
            # Update order status
            order.status = 'expired'
            order.updated_at = datetime.utcnow()
            
            # Notify customer
            NotificationService.send_order_notification(
                order.id,
                'order_expired',
                {'reason': 'No hawker accepted the order within 30 minutes'}
            )
        
        # Commit changes
        from app import db
        db.session.commit()
        
        logger.info(f"Cleaned up {len(expired_orders)} expired orders")
        
    except Exception as exc:
        logger.error(f"Error cleaning up expired orders: {str(exc)}")
        self.retry(exc=exc)

@celery.task(bind=True, max_retries=3)
def process_order_payment(self, order_id):
    """Process payment for an order."""
    try:
        order = Order.query.get(order_id)
        if not order:
            logger.error(f"Order {order_id} not found")
            return
        
        # Process payment logic here
        # ...
        
        # Update order status
        order.status = 'paid'
        order.updated_at = datetime.utcnow()
        
        # Notify customer
        NotificationService.send_order_notification(
            order.id,
            'payment_successful'
        )
        
        # Commit changes
        from app import db
        db.session.commit()
        
        logger.info(f"Processed payment for order {order_id}")
        
    except Exception as exc:
        logger.error(f"Error processing payment for order {order_id}: {str(exc)}")
        self.retry(exc=exc)

@celery.task(bind=True, max_retries=3)
def update_order_eta(self, order_id):
    """Update estimated time of arrival for an order."""
    try:
        order = Order.query.get(order_id)
        if not order:
            logger.error(f"Order {order_id} not found")
            return
        
        # Calculate new ETA based on current location and traffic
        # ...
        
        # Update order ETA
        order.eta = new_eta
        order.updated_at = datetime.utcnow()
        
        # Notify customer
        NotificationService.send_order_notification(
            order.id,
            'eta_updated',
            {'eta': new_eta.isoformat()}
        )
        
        # Commit changes
        from app import db
        db.session.commit()
        
        logger.info(f"Updated ETA for order {order_id}")
        
    except Exception as exc:
        logger.error(f"Error updating ETA for order {order_id}: {str(exc)}")
        self.retry(exc=exc) 