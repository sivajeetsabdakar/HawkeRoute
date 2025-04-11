from datetime import datetime
from typing import List, Optional
from app.models.order import Order
from app.models.user import User
from app.database import db
from app.services.notification import NotificationService
from app.services.route_optimizer import RouteOptimizer

class OrderService:
    @staticmethod
    def create_order(customer_id: int, hawker_id: int, items: List[dict], 
                    pickup_address: str, delivery_address: str, notes: Optional[str] = None) -> Order:
        """Create a new order."""
        order = Order(
            customer_id=customer_id,
            hawker_id=hawker_id,
            items=items,
            pickup_address=pickup_address,
            delivery_address=delivery_address,
            notes=notes,
            status='pending',
            created_at=datetime.utcnow()
        )
        
        try:
            db.session.add(order)
            db.session.commit()
            
            # Send notifications
            NotificationService.send_order_notification(order.id, 'order_created')
            
            return order
        except Exception as e:
            db.session.rollback()
            raise e

    @staticmethod
    def get_order(order_id: int) -> Optional[Order]:
        """Get an order by ID."""
        return Order.query.get(order_id)

    @staticmethod
    def get_customer_orders(customer_id: int) -> List[Order]:
        """Get all orders for a customer."""
        return Order.query.filter_by(customer_id=customer_id).all()

    @staticmethod
    def get_hawker_orders(hawker_id: int) -> List[Order]:
        """Get all orders for a hawker."""
        return Order.query.filter_by(hawker_id=hawker_id).all()

    @staticmethod
    def update_order_status(order_id: int, status: str, hawker_id: Optional[int] = None) -> Order:
        """Update the status of an order."""
        order = Order.query.get(order_id)
        if not order:
            raise ValueError(f"Order {order_id} not found")
        
        if hawker_id and order.hawker_id != hawker_id:
            raise ValueError("Unauthorized to update this order")
        
        valid_statuses = ['pending', 'confirmed', 'preparing', 'ready', 'delivering', 'delivered', 'cancelled']
        if status not in valid_statuses:
            raise ValueError(f"Invalid status. Must be one of: {', '.join(valid_statuses)}")
        
        order.status = status
        order.updated_at = datetime.utcnow()
        
        try:
            db.session.commit()
            
            # Send notifications
            NotificationService.send_order_notification(order.id, f'order_{status}')
            
            # If order is confirmed, optimize routes
            if status == 'confirmed':
                hawker = User.query.get(order.hawker_id)
                if hawker:
                    RouteOptimizer.optimize_routes(hawker)
            
            return order
        except Exception as e:
            db.session.rollback()
            raise e

    @staticmethod
    def cancel_order(order_id: int, user_id: int, reason: str) -> Order:
        """Cancel an order."""
        order = Order.query.get(order_id)
        if not order:
            raise ValueError(f"Order {order_id} not found")
        
        # Check if user is authorized to cancel
        if user_id != order.customer_id and user_id != order.hawker_id:
            raise ValueError("Unauthorized to cancel this order")
        
        # Check if order can be cancelled
        if order.status in ['delivered', 'cancelled']:
            raise ValueError(f"Cannot cancel order in {order.status} status")
        
        order.status = 'cancelled'
        order.cancellation_reason = reason
        order.cancelled_at = datetime.utcnow()
        order.cancelled_by_id = user_id
        order.updated_at = datetime.utcnow()
        
        try:
            db.session.commit()
            
            # Send notifications
            NotificationService.send_order_notification(order.id, 'order_cancelled', {'reason': reason})
            
            return order
        except Exception as e:
            db.session.rollback()
            raise e 