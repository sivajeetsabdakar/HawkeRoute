import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'postgresql://user:password@localhost:5432/hawkerroute')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your-jwt-secret-key')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # Razorpay
    RAZORPAY_KEY_ID = os.getenv('RAZORPAY_KEY_ID')
    RAZORPAY_KEY_SECRET = os.getenv('RAZORPAY_KEY_SECRET')
    
    # Google Maps
    GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY')
    
    # Application Settings
    ORDER_CUTOFF_TIME = "14:00"  # 2 PM
    DELIVERY_START_TIME = "16:00"  # 4 PM
    DELIVERY_END_TIME = "20:00"   # 8 PM
    
    # Socket.IO
    SOCKETIO_PING_TIMEOUT = 10
    SOCKETIO_PING_INTERVAL = 25 