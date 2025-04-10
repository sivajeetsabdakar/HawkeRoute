from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_socketio import SocketIO
from flask_migrate import Migrate
from datetime import timedelta
from .config import Config

db = SQLAlchemy()
jwt = JWTManager()
socketio = SocketIO()
migrate = Migrate()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    socketio.init_app(app)
    migrate.init_app(app, db)

    # Register blueprints
    from .routes.auth import auth_bp
    from .routes.orders import orders_bp
    from .routes.products import products_bp
    from .routes.delivery import delivery_bp
    from .routes.admin import admin_bp
    from .routes.payments import payments_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(orders_bp, url_prefix='/api/orders')
    app.register_blueprint(products_bp, url_prefix='/api/products')
    app.register_blueprint(delivery_bp, url_prefix='/api/delivery')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(payments_bp, url_prefix='/api/payments')

    # Create database tables
    with app.app_context():
        db.create_all()

    return app 