from twilio.rest import Client
from flask import current_app
import logging

class SMSNotificationService:
    """Service for sending SMS notifications using Twilio"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SMSNotificationService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not SMSNotificationService._initialized:
            # Initialize Twilio client
            account_sid = current_app.config.get('TWILIO_ACCOUNT_SID')
            auth_token = current_app.config.get('TWILIO_AUTH_TOKEN')
            self.from_number = current_app.config.get('TWILIO_PHONE_NUMBER')
            
            if account_sid and auth_token and self.from_number:
                self.client = Client(account_sid, auth_token)
                SMSNotificationService._initialized = True
            else:
                self.client = None
                logging.warning("Twilio credentials not configured. SMS notifications will be disabled.")
    
    def send_sms(self, to_number, message):
        """
        Send SMS to a phone number
        
        Args:
            to_number: Recipient's phone number
            message: SMS message content
            
        Returns:
            bool: True if SMS was sent successfully, False otherwise
        """
        if not self.client:
            logging.warning("Twilio client not initialized. Cannot send SMS.")
            return False
        
        try:
            # Format phone number (remove spaces, ensure it starts with +)
            to_number = to_number.replace(' ', '')
            if not to_number.startswith('+'):
                to_number = '+' + to_number
            
            # Send message
            self.client.messages.create(
                body=message,
                from_=self.from_number,
                to=to_number
            )
            return True
            
        except Exception as e:
            logging.error(f"Failed to send SMS: {str(e)}")
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
        if not self.client:
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