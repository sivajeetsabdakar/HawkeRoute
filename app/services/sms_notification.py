from twilio.rest import Client
from flask import current_app
import logging

logger = logging.getLogger(__name__)

class SMSNotificationService:
    """Service for sending SMS notifications using Twilio"""
    
    _instance = None
    _initialized = False
    _client = None
    _from_number = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SMSNotificationService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not SMSNotificationService._initialized:
            SMSNotificationService._initialized = True
    
    def _initialize_client(self):
        """Initialize Twilio client if not already initialized."""
        if SMSNotificationService._client is None:
            try:
                account_sid = current_app.config.get('TWILIO_ACCOUNT_SID')
                auth_token = current_app.config.get('TWILIO_AUTH_TOKEN')
                SMSNotificationService._from_number = current_app.config.get('TWILIO_PHONE_NUMBER')
                
                if not all([account_sid, auth_token, SMSNotificationService._from_number]):
                    logger.error("Missing Twilio configuration")
                    return False
                
                SMSNotificationService._client = Client(account_sid, auth_token)
                return True
            except Exception as e:
                logger.error(f"Failed to initialize Twilio client: {str(e)}")
                return False
        return True
    
    def send_sms(self, to_number, message):
        """
        Send an SMS message.
        
        Args:
            to_number: Recipient phone number
            message: Message content
            
        Returns:
            bool: True if message was sent successfully, False otherwise
        """
        if not self._initialize_client():
            return False
        
        try:
            self._client.messages.create(
                body=message,
                from_=self._from_number,
                to=to_number
            )
            return True
        except Exception as e:
            logger.error(f"Failed to send SMS: {str(e)}")
            return False
    
    def send_bulk_sms(self, phone_numbers, message):
        """
        Send SMS to multiple phone numbers
        
        Args:
            phone_numbers: List of recipient phone numbers
            message: SMS message content
            
        Returns:
            tuple: (success_count, failure_count)
        """
        if not SMSNotificationService._client:
            logging.warning("Twilio client not initialized. Cannot send SMS.")
            return (0, len(phone_numbers))
        
        success_count = 0
        failure_count = 0
        
        for phone_number in phone_numbers:
            if self.send_sms(phone_number, message):
                success_count += 1
            else:
                failure_count += 1
        
        return (success_count, failure_count) 