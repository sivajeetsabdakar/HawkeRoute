import click
from flask.cli import with_appcontext
from app import db

@click.command('init-db')
@with_appcontext
def init_db_command():
    """Initialize the database."""
    # Import all models to ensure they are registered with SQLAlchemy
    from app.models.user import User
    from app.models.token_blacklist import TokenBlacklist
    from app.models.order import Order
    from app.models.notification import Notification
    from app.models.product import Product
    from app.models.payment import Payment
    
    # Create all tables
    db.create_all()
    click.echo('Initialized the database.') 