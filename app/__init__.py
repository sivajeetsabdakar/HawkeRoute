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
from app.config import Config
from app.cli import init_db_command

# Load environment variables
load_dotenv()

# Initialize extensions
# socketio = SocketIO()  # Temporarily disabled
jwt = JWTManager()
mail = Mail()

def create_app(config=None):
    """Application factory function."""
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(Config)
    if config:
        app.config.update(config)
    
    # Initialize extensions
    CORS(app)
    jwt.init_app(app)
    mail.init_app(app)
    # socketio.init_app(app, message_queue=os.getenv('SOCKETIO_MESSAGE_QUEUE', 'redis://localhost:6379/0'))  # Temporarily disabled
    
    # Initialize database
    init_db(app)
    
    # Initialize migrations
    init_migrations(app)
    
    # Initialize Celery
    celery = create_celery_app(app)
    
    # Register CLI commands
    app.cli.add_command(init_db_command)
    
    # Register blueprints
    from app.routes import auth, user, order, hawker, admin, payments, products, orders, location, delivery
    app.register_blueprint(auth.bp, url_prefix='/api/auth')
    app.register_blueprint(user.bp, url_prefix='/api/user')
    app.register_blueprint(order.bp, url_prefix='/api/order')
    app.register_blueprint(hawker.bp, url_prefix='/api/hawker')
    app.register_blueprint(admin.bp, url_prefix='/api/admin')
    app.register_blueprint(payments.bp, url_prefix='/api/payments')
    app.register_blueprint(products.bp, url_prefix='/api/products')
    app.register_blueprint(orders.bp, url_prefix='/api/orders')
    app.register_blueprint(location.bp, url_prefix='/api/location')
    app.register_blueprint(delivery.bp, url_prefix='/api/delivery')
    
    # Register error handlers
    from app.errors import register_error_handlers
    register_error_handlers(app)
    
    return app 