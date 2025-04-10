import firebase_admin
from firebase_admin import credentials, messaging
from flask import current_app
import json
import os

class PushNotificationService:
    """Service for sending push notifications using Firebase Cloud Messaging"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PushNotificationService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not PushNotificationService._initialized:
            # Initialize Firebase Admin SDK
            cred_path = current_app.config.get('FIREBASE_CREDENTIALS_PATH')
            if cred_path and os.path.exists(cred_path):
                cred = credentials.Certificate(cred_path)
                firebase_admin.initialize_app(cred)
                PushNotificationService._initialized = True
    
    def send_notification(self, user, title, body, data=None, image=None):
        """
        Send push notification to a user's devices
        
        Args:
            user: User model instance
            title: Notification title
            body: Notification body
            data: Additional data to send with notification
            image: URL of image to display in notification
            
        Returns:
            bool: True if notification was sent successfully, False otherwise
        """
        if not user.device_tokens:
            return False
        
        success = False
        failed_tokens = []
        
        # Prepare notification message
        notification = messaging.Notification(
            title=title,
            body=body,
            image=image
        )
        
        # Send to each device token
        for device in user.device_tokens:
            token = device.get('token')
            platform = device.get('platform', 'unknown')
            
            try:
                # Create message
                message = messaging.Message(
                    notification=notification,
                    data=data or {},
                    token=token,
                    android=messaging.AndroidConfig(
                        priority='high',
                        notification=messaging.AndroidNotification(
                            icon='stock_ticker_update',
                            color='#f45342',
                            sound='default'
                        )
                    ) if platform == 'android' else None,
                    apns=messaging.APNSConfig(
                        payload=messaging.APNSPayload(
                            aps=messaging.Aps(
                                sound='default',
                                badge=1
                            )
                        )
                    ) if platform == 'ios' else None
                )
                
                # Send message
                response = messaging.send(message)
                success = True
                
            except messaging.ApiCallError as e:
                # Handle invalid token
                if e.code == 'invalid-argument':
                    failed_tokens.append(token)
                current_app.logger.error(f"Failed to send push notification: {str(e)}")
            except Exception as e:
                current_app.logger.error(f"Error sending push notification: {str(e)}")
        
        # Remove failed tokens
        if failed_tokens:
            for token in failed_tokens:
                user.remove_device_token(token)
        
        return success
    
    def send_multicast(self, users, title, body, data=None, image=None):
        """
        Send push notification to multiple users
        
        Args:
            users: List of User model instances
            title: Notification title
            body: Notification body
            data: Additional data to send with notification
            image: URL of image to display in notification
            
        Returns:
            tuple: (success_count, failure_count)
        """
        if not users:
            return (0, 0)
        
        # Collect all device tokens
        tokens = []
        token_to_user = {}
        
        for user in users:
            if not user.device_tokens:
                continue
            
            for device in user.device_tokens:
                token = device.get('token')
                tokens.append(token)
                token_to_user[token] = user
        
        if not tokens:
            return (0, 0)
        
        # Prepare notification message
        notification = messaging.Notification(
            title=title,
            body=body,
            image=image
        )
        
        # Create multicast message
        message = messaging.MulticastMessage(
            notification=notification,
            data=data or {},
            tokens=tokens
        )
        
        try:
            # Send multicast message
            response = messaging.send_multicast(message)
            
            # Handle failed tokens
            if response.failure_count > 0:
                for idx, result in enumerate(response.responses):
                    if not result.success:
                        token = tokens[idx]
                        user = token_to_user.get(token)
                        if user:
                            user.remove_device_token(token)
            
            return (response.success_count, response.failure_count)
            
        except Exception as e:
            current_app.logger.error(f"Error sending multicast notification: {str(e)}")
            return (0, len(tokens)) 