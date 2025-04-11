import os
import sys
import logging
from flask import Flask
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta

# Add the project root directory to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask extensions
db = SQLAlchemy()

def create_test_app():
    """Create a minimal Flask app for sending notifications."""
    app = Flask(__name__)
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Configure database
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///app.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Configure email
    app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
    app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
    app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')
    
    # Configure Twilio
    app.config['TWILIO_ACCOUNT_SID'] = os.getenv('TWILIO_ACCOUNT_SID')
    app.config['TWILIO_AUTH_TOKEN'] = os.getenv('TWILIO_AUTH_TOKEN')
    app.config['TWILIO_PHONE_NUMBER'] = os.getenv('TWILIO_FROM_NUMBER')
    
    # Initialize extensions
    db.init_app(app)
    mail = Mail(app)
    app.extensions['mail'] = mail
    
    return app

# Import models after db is initialized
from app.models.user import User
from app.models.order import Order
from app.models.notification import Notification
from app.services.sms_notification import SMSNotificationService

def send_hawker_daily_notification(hawker_id, app):
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
            try:
                from flask_mail import Message
                msg = Message(
                    subject=title,
                    recipients=[hawker.email],
                    html=email_html
                )
                app.extensions['mail'].send(msg)
                logger.info(f"Email sent to {hawker.email}")
            except Exception as e:
                logger.error(f"Failed to send email to {hawker.email}: {str(e)}")
        
        # Send SMS if enabled and phone number exists
        if hawker.sms_notifications and hawker.phone:
            try:
                sms_service = SMSNotificationService()
                if sms_service.send_sms(hawker.phone, message):
                    logger.info(f"SMS sent to {hawker.phone}")
                else:
                    logger.error(f"Failed to send SMS to {hawker.phone}")
            except Exception as e:
                logger.error(f"Failed to send SMS to {hawker.phone}: {str(e)}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error sending hawker daily notification: {str(e)}")
        return False

def send_daily_notifications():
    """Send daily notifications to all active hawkers."""
    app = create_test_app()
    with app.app_context():
        try:
            # Get all active hawkers
            hawkers = User.query.filter_by(
                role='hawker',
                is_active=True
            ).all()
            
            success_count = 0
            for hawker in hawkers:
                if send_hawker_daily_notification(hawker.id, app):
                    success_count += 1
            
            logger.info(f"Successfully sent notifications to {success_count} out of {len(hawkers)} hawkers")
            
        except Exception as e:
            logger.error(f"Error sending daily notifications: {str(e)}")

if __name__ == '__main__':
    send_daily_notifications() 