from app import create_app, db
from app.models.user import User
from app.services.notification import NotificationService
import logging

logger = logging.getLogger(__name__)

def send_daily_notifications():
    """Send daily notifications to all active hawkers."""
    app = create_app()
    with app.app_context():
        try:
            # Get all active hawkers
            hawkers = User.query.filter_by(
                role='hawker',
                is_active=True
            ).all()
            
            success_count = 0
            for hawker in hawkers:
                if NotificationService.send_hawker_daily_notification(hawker.id):
                    success_count += 1
            
            logger.info(f"Successfully sent notifications to {success_count} out of {len(hawkers)} hawkers")
            
        except Exception as e:
            logger.error(f"Error sending daily notifications: {str(e)}")

if __name__ == '__main__':
    send_daily_notifications() 