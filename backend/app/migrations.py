from flask_migrate import Migrate
from flask import Flask
from app import db

def init_migrations(app: Flask):
    """Initialize Flask-Migrate for database migrations."""
    migrate = Migrate(app, db)
    return migrate 