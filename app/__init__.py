from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_socketio import SocketIO
from flask_mail import Mail
import os
from dotenv import load_dotenv

from app.database import init_db, db
from app.migrations import init_migrations
from app.celery_app import create_celery_app

# Load environment variables
load_dotenv()

# Initialize extensions
socketio = SocketIO()
jwt = JWTManager()
mail = Mail()

def create_app(config=None):
    """Application factory function."""
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object('app.config.default')
    if config:
        app.config.update(config)
    
    # Initialize extensions
    CORS(app)
    jwt.init_app(app)
    mail.init_app(app)
    socketio.init_app(app, message_queue=os.getenv('SOCKETIO_MESSAGE_QUEUE', 'redis://localhost:6379/0'))
    
    # Initialize database
    init_db(app)
    
    # Initialize migrations
    init_migrations(app)
    
    # Initialize Celery
    celery = create_celery_app(app)
    
    # Register blueprints
    from app.routes import auth, user, order, hawker, admin, payment
    app.register_blueprint(auth.bp)
    app.register_blueprint(user.bp)
    app.register_blueprint(order.bp)
    app.register_blueprint(hawker.bp)
    app.register_blueprint(admin.bp)
    app.register_blueprint(payment.bp)
    
    # Register error handlers
    from app.errors import register_error_handlers
    register_error_handlers(app)
    
    return app 