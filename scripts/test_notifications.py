from app import create_app
from app.services.notification import NotificationService
import logging

logger = logging.getLogger(__name__)

def test_notifications():
    """Test both email and SMS notifications."""
    app = create_app()
    with app.app_context():
        try:
            # Test email
            email_result = NotificationService.send_email_notification(
                to_email="your-test-email@gmail.com",  # Replace with your email
                subject="Test Email from HawkeRoute",
                html_content="""
                <html>
                <body>
                    <h1>Test Email</h1>
                    <p>This is a test email from HawkeRoute notification system.</p>
                    <p>If you receive this, email notifications are working correctly!</p>
                </body>
                </html>
                """
            )
            logger.info(f"Email test {'successful' if email_result else 'failed'}")
            
            # Test SMS
            from app.services.sms_notification import SMSNotificationService
            sms_service = SMSNotificationService()
            sms_result = sms_service.send_sms(
                to_number="your-phone-number",  # Replace with your phone number
                message="Test SMS from HawkeRoute. If you receive this, SMS notifications are working!"
            )
            logger.info(f"SMS test {'successful' if sms_result else 'failed'}")
            
        except Exception as e:
            logger.error(f"Error testing notifications: {str(e)}")

if __name__ == '__main__':
    test_notifications() 