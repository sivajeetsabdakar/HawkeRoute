from flask import current_app
from app import socketio, mail
from flask_mail import Message
from app.models.user import User
from app.models.order import Order
from app.models.notification import Notification
from app import db
from datetime import datetime
from app.services.sms_notification import SMSNotificationService
import logging

logger = logging.getLogger(__name__)

# Initialize notification services
sms_service = SMSNotificationService()

class NotificationService:
    """Service for sending notifications via email and SMS."""
    
    @staticmethod
    def send_hawker_daily_notification(hawker_id):
        """
        Send daily notification to hawker about their deliveries.
        This should be called before 4 PM to inform hawkers about their deliveries.
        """
        try:
            hawker = User.query.get(hawker_id)
            if not hawker:
                logger.error(f"Hawker {hawker_id} not found")
                return False
            
            # Get today's pending deliveries
            from datetime import datetime, timedelta
            today = datetime.utcnow().date()
            tomorrow = today + timedelta(days=1)
            
            pending_deliveries = Order.query.filter(
                Order.hawker_id == hawker_id,
                Order.status.in_(['accepted', 'picked_up']),
                Order.created_at >= today,
                Order.created_at < tomorrow
            ).all()
            
            # Prepare notification content
            if pending_deliveries:
                title = "You Have Deliveries Today"
                message = f"You have {len(pending_deliveries)} delivery{'s' if len(pending_deliveries) > 1 else ''} today."
                email_html = f"""
                <html>
                <body>
                    <h1>{title}</h1>
                    <p>{message}</p>
                    <h2>Your Deliveries:</h2>
                    <ul>
                    {''.join(f'<li>Order #{order.id} - {order.status}</li>' for order in pending_deliveries)}
                    </ul>
                    <p>Please check your app for more details.</p>
                </body>
                </html>
                """
            else:
                title = "No Deliveries Today"
                message = "You have no deliveries scheduled for today."
                email_html = f"""
                <html>
                <body>
                    <h1>{title}</h1>
                    <p>{message}</p>
                </body>
                </html>
                """
            
            # Create notification record
            notification = Notification(
                user_id=hawker_id,
                type='daily_delivery_summary',
                title=title,
                message=message,
                data={'delivery_count': len(pending_deliveries)}
            )
            
            db.session.add(notification)
            db.session.commit()
            
            # Send email notification
            if hawker.email_notifications:
                NotificationService.send_email_notification(
                    hawker.email,
                    title,
                    email_html
                )
            
            # Send SMS if enabled and phone number exists
            if hawker.sms_notifications and hawker.phone:
                try:
                    sms_service.send_sms(
                        hawker.phone,
                        message
                    )
                except Exception as e:
                    logger.error(f"Failed to send SMS: {str(e)}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error sending hawker daily notification: {str(e)}")
            return False
    
    @staticmethod
    def send_email_notification(to_email, subject, html_content):
        """
        Send an email notification.
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            html_content: HTML content of the email
        """
        try:
            msg = Message(
                subject=subject,
                recipients=[to_email],
                html=html_content
            )
            mail.send(msg)
            return True
        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
            return False
    
    @staticmethod
    def send_order_notification(order_id, notification_type, data=None):
        """
        Send notifications related to orders to both customers and hawkers.
        
        Args:
            order_id: ID of the order
            notification_type: Type of notification (e.g., 'order_created', 'order_accepted')
            data: Additional data for the notification
        """
        try:
            order = Order.query.get(order_id)
            if not order:
                logger.error(f"Order {order_id} not found")
                return False
            
            # Get notification content
            title = NotificationService._get_notification_title(notification_type, order)
            message = NotificationService._get_notification_message(notification_type, order, data)
            
            # Create notification record
            notification = Notification(
                user_id=order.customer_id,
                type=notification_type,
                title=title,
                message=message,
                data=data or {},
                related_id=order_id,
                related_type='order'
            )
            
            # Also notify hawker if applicable
            if order.hawker_id and notification_type in ['order_accepted', 'order_picked_up', 'order_delivered']:
                hawker_notification = Notification(
                    user_id=order.hawker_id,
                    type=notification_type,
                    title=title,
                    message=message,
                    data=data or {},
                    related_id=order_id,
                    related_type='order'
                )
                db.session.add(hawker_notification)
            
            db.session.add(notification)
            db.session.commit()
            
            # Send real-time notification via SocketIO
            socketio.emit('notification', {
                'id': notification.id,
                'type': notification_type,
                'title': title,
                'message': message,
                'data': data or {},
                'created_at': notification.created_at.isoformat()
            }, room=f"user_{order.customer_id}")
            
            if order.hawker_id and notification_type in ['order_accepted', 'order_picked_up', 'order_delivered']:
                socketio.emit('notification', {
                    'id': hawker_notification.id,
                    'type': notification_type,
                    'title': title,
                    'message': message,
                    'data': data or {},
                    'created_at': hawker_notification.created_at.isoformat()
                }, room=f"user_{order.hawker_id}")
            
            # Send email if enabled
            customer = User.query.get(order.customer_id)
            if customer and customer.notify_email:
                email_html = NotificationService._get_email_template(notification_type, order, data)
                NotificationService.send_email_notification(
                    customer.email,
                    title,
                    email_html
                )
            
            # Send SMS if enabled
            if customer and customer.notify_sms and customer.phone:
                try:
                    sms_service.send_sms(
                        customer.phone,
                        message
                    )
                except Exception as e:
                    logger.error(f"Failed to send SMS: {str(e)}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error sending order notification: {str(e)}")
            return False
    
    @staticmethod
    def send_system_notification(user_id, notification_type, data=None):
        """
        Send system notifications to a specific user.
        
        Args:
            user_id: ID of the user
            notification_type: Type of notification (e.g., 'account_activated', 'password_reset')
            data: Additional data for the notification
        """
        try:
            user = User.query.get(user_id)
            if not user:
                logger.error(f"User {user_id} not found")
                return False
            
            # Get notification content
            title = NotificationService._get_system_notification_title(notification_type)
            message = NotificationService._get_system_notification_message(notification_type, data)
            
            # Create notification record
            notification = Notification(
                user_id=user_id,
                type=notification_type,
                title=title,
                message=message,
                data=data or {}
            )
            
            db.session.add(notification)
            db.session.commit()
            
            # Send real-time notification via SocketIO
            socketio.emit('notification', {
                'id': notification.id,
                'type': notification_type,
                'title': title,
                'message': message,
                'data': data or {},
                'created_at': notification.created_at.isoformat()
            }, room=f"user_{user_id}")
            
            # Send email if enabled
            if user.notify_email:
                email_html = NotificationService._get_system_email_template(notification_type, data)
                NotificationService.send_email_notification(
                    user.email,
                    title,
                    email_html
                )
            
            # Send SMS if enabled
            if user.notify_sms and user.phone:
                try:
                    sms_service.send_sms(
                        user.phone,
                        message
                    )
                except Exception as e:
                    logger.error(f"Failed to send SMS: {str(e)}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error sending system notification: {str(e)}")
            return False
    
    @staticmethod
    def _get_notification_title(notification_type, order):
        """Get the title for an order notification."""
        titles = {
            'order_created': 'New Order Created',
            'order_accepted': 'Order Accepted',
            'order_picked_up': 'Order Picked Up',
            'order_delivered': 'Order Delivered',
            'order_cancelled': 'Order Cancelled',
            'order_expired': 'Order Expired',
            'payment_successful': 'Payment Successful',
            'payment_failed': 'Payment Failed',
            'eta_updated': 'ETA Updated'
        }
        return titles.get(notification_type, 'Order Update')
    
    @staticmethod
    def _get_notification_message(notification_type, order, data=None):
        """Get the message for an order notification."""
        messages = {
            'order_created': f'Your order #{order.id} has been created and is waiting for a hawker to accept it.',
            'order_accepted': f'Your order #{order.id} has been accepted by a hawker and is being prepared.',
            'order_picked_up': f'Your order #{order.id} has been picked up and is on its way to you.',
            'order_delivered': f'Your order #{order.id} has been delivered. Enjoy your meal!',
            'order_cancelled': f'Your order #{order.id} has been cancelled.',
            'order_expired': f'Your order #{order.id} has expired because no hawker accepted it within the time limit.',
            'payment_successful': f'Payment for order #{order.id} was successful.',
            'payment_failed': f'Payment for order #{order.id} failed. Please try again.',
            'eta_updated': f'The estimated delivery time for your order #{order.id} has been updated.'
        }
        
        message = messages.get(notification_type, f'Update for your order #{order.id}')
        
        # Add ETA if available
        if order.eta and notification_type in ['order_accepted', 'order_picked_up', 'eta_updated']:
            message += f' Estimated delivery time: {order.eta.strftime("%I:%M %p")}'
        
        return message
    
    @staticmethod
    def _get_system_notification_title(notification_type):
        """Get the title for a system notification."""
        titles = {
            'account_activated': 'Account Activated',
            'password_reset': 'Password Reset',
            'profile_updated': 'Profile Updated',
            'new_message': 'New Message',
            'system_maintenance': 'System Maintenance',
            'promotion': 'Special Promotion'
        }
        return titles.get(notification_type, 'System Notification')
    
    @staticmethod
    def _get_system_notification_message(notification_type, data=None):
        """Get the message for a system notification."""
        messages = {
            'account_activated': 'Your account has been successfully activated. Welcome to HawkeRoute!',
            'password_reset': 'Your password has been reset successfully.',
            'profile_updated': 'Your profile has been updated successfully.',
            'new_message': f'You have a new message from {data.get("sender", "a user")}.',
            'system_maintenance': 'The system will be undergoing maintenance. Service may be interrupted.',
            'promotion': data.get('message', 'Check out our latest promotion!')
        }
        return messages.get(notification_type, 'You have a new notification.')
    
    @staticmethod
    def _get_email_template(notification_type, order, data=None):
        """Get the HTML email template for an order notification."""
        # This would typically load from a template file
        # For now, we'll return a simple HTML template
        return f"""
        <html>
        <body>
            <h1>{NotificationService._get_notification_title(notification_type, order)}</h1>
            <p>{NotificationService._get_notification_message(notification_type, order, data)}</p>
            <p>Order ID: {order.id}</p>
            <p>Thank you for using HawkeRoute!</p>
        </body>
        </html>
        """
    
    @staticmethod
    def _get_system_email_template(notification_type, data=None):
        """Get the HTML email template for a system notification."""
        # This would typically load from a template file
        # For now, we'll return a simple HTML template
        return f"""
        <html>
        <body>
            <h1>{NotificationService._get_system_notification_title(notification_type)}</h1>
            <p>{NotificationService._get_system_notification_message(notification_type, data)}</p>
            <p>Thank you for using HawkeRoute!</p>
        </body>
        </html>
        """
    
    @staticmethod
    def _should_send_email(user, notification_type):
        """Check if email notification should be sent based on user preferences"""
        if notification_type.startswith('order_'):
            if notification_type == 'order_created' and not user.notify_order_created:
                return False
            if notification_type == 'order_accepted' and not user.notify_order_accepted:
                return False
            if notification_type == 'order_picked_up' and not user.notify_order_picked_up:
                return False
            if notification_type == 'order_delivered' and not user.notify_order_delivered:
                return False
            if notification_type == 'order_cancelled' and not user.notify_order_cancelled:
                return False
        elif notification_type == 'account_updates' and not user.notify_account_updates:
            return False
        elif notification_type == 'promotions' and not user.notify_promotions:
            return False
        
        return True
    
    @staticmethod
    def _should_send_push(user, notification_type):
        """Check if push notification should be sent based on user preferences"""
        return NotificationService._should_send_email(user, notification_type)
    
    @staticmethod
    def _should_send_sms(user, notification_type):
        """Check if SMS notification should be sent based on user preferences"""
        # SMS notifications are more limited to critical updates
        critical_types = ['order_delivered', 'order_cancelled', 'account_deactivated']
        return notification_type in critical_types and NotificationService._should_send_email(user, notification_type) 