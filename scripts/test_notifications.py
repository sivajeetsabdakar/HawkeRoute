import os
import sys
import logging
from flask import Flask
from flask_mail import Mail

# Add the project root directory to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_test_app():
    """Create a minimal Flask app for testing notifications."""
    app = Flask(__name__)
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
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
    
    # Initialize Flask-Mail
    mail = Mail(app)
    app.extensions['mail'] = mail
    
    return app

def test_notifications():
    """Test both email and SMS notifications."""
    app = create_test_app()
    
    with app.app_context():
        try:
            # Test email
            from flask_mail import Message
            email_result = False
            try:
                msg = Message(
                    subject="Test Email from HawkeRoute",
                    recipients=["sagarsabdakar98@gmail.com"],  # Replace with your email
                    html="""
                    <html>
                    <body>
                        <h1>Test Email</h1>
                        <p>This is a test email from HawkeRoute notification system.</p>
                        <p>If you receive this, email notifications are working correctly!</p>
                    </body>
                    </html>
                    """
                )
                app.extensions['mail'].send(msg)
                email_result = True
                logger.info("Email test successful")
            except Exception as e:
                logger.error(f"Email test failed: {str(e)}")
            
            # Test SMS
            sms_result = False
            try:
                from app.services.sms_notification import SMSNotificationService
                sms_service = SMSNotificationService()
                sms_result = sms_service.send_sms(
                    "+917217556581",  # Replace with your phone number
                    "Test SMS from HawkeRoute. If you receive this, SMS notifications are working!"
                )
                if sms_result:
                    logger.info("SMS test successful")
                else:
                    logger.error("SMS test failed: Service returned False")
            except Exception as e:
                logger.error(f"SMS test failed: {str(e)}")
            
            logger.info(f"Test results - Email: {'Success' if email_result else 'Failed'}, SMS: {'Success' if sms_result else 'Failed'}")
            
        except Exception as e:
            logger.error(f"Error testing notifications: {str(e)}")

if __name__ == '__main__':
    test_notifications() 