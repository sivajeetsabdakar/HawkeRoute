import firebase_admin
from firebase_admin import credentials, messaging
from flask import current_app
import logging

logger = logging.getLogger(__name__)

class PushNotificationService:
    """Service for sending push notifications via Firebase Cloud Messaging."""
    
    _initialized = False
    _firebase_app = None
    
    def __init__(self):
        """Initialize the push notification service."""
        # Don't initialize Firebase here, do it lazily when needed
        pass
    
    def _initialize_firebase(self):
        """Initialize Firebase if not already initialized."""
        if not self._initialized:
            try:
                cred_path = current_app.config.get('FIREBASE_CREDENTIALS_PATH')
                if cred_path:
                    cred = credentials.Certificate(cred_path)
                    self._firebase_app = firebase_admin.initialize_app(cred)
                    self._initialized = True
                    logger.info("Firebase initialized successfully")
                else:
                    logger.warning("Firebase credentials path not configured")
            except Exception as e:
                logger.error(f"Failed to initialize Firebase: {str(e)}")
    
    def send_notification(self, token, title, body, data=None):
        """
        Send a push notification to a specific device.
        
        Args:
            token (str): The FCM token of the device
            title (str): The notification title
            body (str): The notification body
            data (dict, optional): Additional data to send with the notification
        
        Returns:
            bool: True if the notification was sent successfully, False otherwise
        """
        try:
            # Initialize Firebase if not already initialized
            self._initialize_firebase()
            
            if not self._initialized:
                logger.error("Firebase not initialized, cannot send notification")
                return False
            
            # Create the message
            message = messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=body
                ),
                data=data or {},
                token=token
            )
            
            # Send the message
            response = messaging.send(message)
            logger.info(f"Successfully sent notification: {response}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send push notification: {str(e)}")
            return False
    
    def send_multicast_notification(self, tokens, title, body, data=None):
        """
        Send a push notification to multiple devices.
        
        Args:
            tokens (list): List of FCM tokens
            title (str): The notification title
            body (str): The notification body
            data (dict, optional): Additional data to send with the notification
        
        Returns:
            tuple: (success_count, failure_count)
        """
        try:
            # Initialize Firebase if not already initialized
            self._initialize_firebase()
            
            if not self._initialized:
                logger.error("Firebase not initialized, cannot send notification")
                return 0, len(tokens)
            
            # Create the message
            message = messaging.MulticastMessage(
                notification=messaging.Notification(
                    title=title,
                    body=body
                ),
                data=data or {},
                tokens=tokens
            )
            
            # Send the message
            response = messaging.send_multicast(message)
            logger.info(f"Successfully sent multicast notification: {response.success_count} successful, {response.failure_count} failed")
            return response.success_count, response.failure_count
            
        except Exception as e:
            logger.error(f"Failed to send multicast push notification: {str(e)}")
            return 0, len(tokens) 