from flask import current_app
from flask_socketio import SocketIO
from flask_mail import Mail, Message
from app.models.user import User
from app.models.order import Order
from app.models.notification import Notification
from app import db
from datetime import datetime
import json
from app.services.push_notification import PushNotificationService
from app.services.sms_notification import SMSNotificationService

socketio = SocketIO()
mail = Mail()
push_service = PushNotificationService()
sms_service = SMSNotificationService()

class NotificationService:
    @staticmethod
    def send_order_notification(order_id, notification_type, data=None):
        """Send order-related notifications"""
        order = Order.query.get(order_id)
        if not order:
            return False
        
        # Get users to notify
        users_to_notify = []
        
        # Add customer
        customer = User.query.get(order.customer_id)
        if customer:
            users_to_notify.append(customer)
        
        # Add hawker
        hawker = User.query.get(order.hawker_id)
        if hawker:
            users_to_notify.append(hawker)
        
        # Prepare notification data
        notification_data = {
            'order_id': order_id,
            'type': notification_type,
            'timestamp': datetime.utcnow().isoformat(),
            'data': data or {}
        }
        
        # Send notifications to each user
        for user in users_to_notify:
            # Create notification record
            notification = Notification(
                user_id=user.id,
                type='order',
                title=NotificationService._get_notification_title(notification_type, order),
                message=NotificationService._get_notification_message(notification_type, order, data),
                data=notification_data
            )
            
            try:
                db.session.add(notification)
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                current_app.logger.error(f"Failed to save notification: {str(e)}")
                continue
            
            # Send real-time notification
            socketio.emit('notification', notification.to_dict(), room=f"user_{user.id}")
            
            # Send email if enabled
            if user.notify_email and NotificationService._should_send_email(user, notification_type):
                NotificationService.send_email_notification(
                    user.email,
                    f"Order Update - {notification_type}",
                    NotificationService._get_email_template(notification_type, order, data)
                )
            
            # Send push notification if enabled
            if user.notify_push and NotificationService._should_send_push(user, notification_type):
                push_service.send_notification(
                    user,
                    notification.title,
                    notification.message,
                    notification_data
                )
            
            # Send SMS if enabled
            if user.notify_sms and NotificationService._should_send_sms(user, notification_type):
                sms_service.send_sms(
                    user.phone,
                    f"{notification.title}: {notification.message}"
                )
        
        return True
    
    @staticmethod
    def send_system_notification(user_id, notification_type, data=None):
        """Send system notifications to a specific user"""
        user = User.query.get(user_id)
        if not user:
            return False
        
        # Prepare notification data
        notification_data = {
            'type': notification_type,
            'timestamp': datetime.utcnow().isoformat(),
            'data': data or {}
        }
        
        # Create notification record
        notification = Notification(
            user_id=user.id,
            type='system',
            title=NotificationService._get_system_notification_title(notification_type),
            message=NotificationService._get_system_notification_message(notification_type, data),
            data=notification_data
        )
        
        try:
            db.session.add(notification)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Failed to save notification: {str(e)}")
            return False
        
        # Send real-time notification
        socketio.emit('notification', notification.to_dict(), room=f"user_{user.id}")
        
        # Send email if enabled
        if user.notify_email and NotificationService._should_send_email(user, notification_type):
            NotificationService.send_email_notification(
                user.email,
                f"System Notification - {notification_type}",
                NotificationService._get_system_email_template(notification_type, data)
            )
        
        # Send push notification if enabled
        if user.notify_push and NotificationService._should_send_push(user, notification_type):
            push_service.send_notification(
                user,
                notification.title,
                notification.message,
                notification_data
            )
        
        # Send SMS if enabled
        if user.notify_sms and NotificationService._should_send_sms(user, notification_type):
            sms_service.send_sms(
                user.phone,
                f"{notification.title}: {notification.message}"
            )
        
        return True
    
    @staticmethod
    def send_email_notification(to_email, subject, html_content):
        """Send email notification"""
        try:
            msg = Message(
                subject=subject,
                recipients=[to_email],
                html=html_content,
                sender=current_app.config['MAIL_DEFAULT_SENDER']
            )
            mail.send(msg)
            return True
        except Exception as e:
            current_app.logger.error(f"Failed to send email notification: {str(e)}")
            return False
    
    @staticmethod
    def _get_notification_title(notification_type, order):
        """Get notification title for order notifications"""
        titles = {
            'order_created': 'New Order Received',
            'order_confirmed': 'Order Confirmed',
            'order_preparing': 'Order Being Prepared',
            'order_ready': 'Order Ready for Delivery',
            'order_delivering': 'Order Out for Delivery',
            'order_delivered': 'Order Delivered',
            'order_cancelled': 'Order Cancelled',
            'payment_received': 'Payment Received',
            'payment_failed': 'Payment Failed'
        }
        return titles.get(notification_type, 'Order Update')
    
    @staticmethod
    def _get_notification_message(notification_type, order, data=None):
        """Get notification message for order notifications"""
        messages = {
            'order_created': f'Order #{order.id} has been received',
            'order_confirmed': f'Order #{order.id} has been confirmed',
            'order_preparing': f'Order #{order.id} is being prepared',
            'order_ready': f'Order #{order.id} is ready for delivery',
            'order_delivering': f'Order #{order.id} is out for delivery',
            'order_delivered': f'Order #{order.id} has been delivered',
            'order_cancelled': f'Order #{order.id} has been cancelled',
            'payment_received': f'Payment received for Order #{order.id}',
            'payment_failed': f'Payment failed for Order #{order.id}'
        }
        return messages.get(notification_type, f'Update for Order #{order.id}')
    
    @staticmethod
    def _get_system_notification_title(notification_type):
        """Get notification title for system notifications"""
        titles = {
            'account_activated': 'Account Activated',
            'account_deactivated': 'Account Deactivated',
            'password_reset': 'Password Reset Request',
            'email_verification': 'Email Verification',
            'route_optimized': 'Delivery Route Optimized'
        }
        return titles.get(notification_type, 'System Notification')
    
    @staticmethod
    def _get_system_notification_message(notification_type, data=None):
        """Get notification message for system notifications"""
        messages = {
            'account_activated': 'Your account has been activated successfully',
            'account_deactivated': 'Your account has been deactivated',
            'password_reset': 'A password reset has been requested for your account',
            'email_verification': 'Please verify your email address',
            'route_optimized': 'Your delivery route has been optimized'
        }
        return messages.get(notification_type, 'System notification received')
    
    @staticmethod
    def _get_email_template(notification_type, order, data=None):
        """Get email template for order notifications"""
        templates = {
            'order_created': f"""
                <h2>New Order Received</h2>
                <p>Order ID: {order.id}</p>
                <p>Total Amount: ₹{order.total_amount}</p>
                <p>Status: {order.status}</p>
                <p>View your order details in the app.</p>
            """,
            'order_confirmed': f"""
                <h2>Order Confirmed</h2>
                <p>Order ID: {order.id}</p>
                <p>Your order has been confirmed and is being prepared.</p>
                <p>View your order details in the app.</p>
            """,
            'order_delivering': f"""
                <h2>Order Out for Delivery</h2>
                <p>Order ID: {order.id}</p>
                <p>Your order is out for delivery.</p>
                <p>Track your order in real-time in the app.</p>
            """,
            'order_delivered': f"""
                <h2>Order Delivered</h2>
                <p>Order ID: {order.id}</p>
                <p>Your order has been delivered successfully.</p>
                <p>Thank you for using our service!</p>
            """,
            'order_cancelled': f"""
                <h2>Order Cancelled</h2>
                <p>Order ID: {order.id}</p>
                <p>Your order has been cancelled.</p>
                <p>Reason: {data.get('reason', 'Not specified')}</p>
            """,
            'payment_received': f"""
                <h2>Payment Received</h2>
                <p>Order ID: {order.id}</p>
                <p>Amount: ₹{order.total_amount}</p>
                <p>Payment Method: {data.get('payment_method', 'Not specified')}</p>
            """,
            'payment_failed': f"""
                <h2>Payment Failed</h2>
                <p>Order ID: {order.id}</p>
                <p>Amount: ₹{order.total_amount}</p>
                <p>Reason: {data.get('reason', 'Not specified')}</p>
                <p>Please try again or contact support.</p>
            """
        }
        
        return templates.get(notification_type, "Notification received")
    
    @staticmethod
    def _get_system_email_template(notification_type, data=None):
        """Get email template for system notifications"""
        templates = {
            'account_activated': """
                <h2>Account Activated</h2>
                <p>Your account has been activated successfully.</p>
                <p>You can now log in and use all features of the app.</p>
            """,
            'account_deactivated': """
                <h2>Account Deactivated</h2>
                <p>Your account has been deactivated.</p>
                <p>Reason: {reason}</p>
                <p>Please contact support for more information.</p>
            """,
            'password_reset': """
                <h2>Password Reset Request</h2>
                <p>A password reset has been requested for your account.</p>
                <p>If you did not request this, please ignore this email.</p>
                <p>Reset Code: {code}</p>
            """,
            'email_verification': """
                <h2>Email Verification</h2>
                <p>Please verify your email address by clicking the link below:</p>
                <p><a href="{verification_link}">Verify Email</a></p>
                <p>If you did not request this, please ignore this email.</p>
            """,
            'route_optimized': """
                <h2>Delivery Route Optimized</h2>
                <p>Your delivery route for today has been optimized.</p>
                <p>Total Orders: {total_orders}</p>
                <p>Estimated Duration: {duration} minutes</p>
                <p>View your route in the app.</p>
            """
        }
        
        template = templates.get(notification_type, "Notification received")
        if data:
            template = template.format(**data)
        
        return template
    
    @staticmethod
    def _should_send_email(user, notification_type):
        """Check if email notification should be sent based on user preferences"""
        if notification_type.startswith('order_'):
            if notification_type == 'order_created' and not user.notify_order_created:
                return False
            if notification_type == 'order_confirmed' and not user.notify_order_confirmed:
                return False
            if notification_type == 'order_preparing' and not user.notify_order_preparing:
                return False
            if notification_type == 'order_ready' and not user.notify_order_ready:
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