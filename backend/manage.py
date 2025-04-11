import os
import click
from flask.cli import with_appcontext
from app import create_app, db
from flask_migrate import Migrate, upgrade, init, migrate, stamp

app = create_app()

@app.cli.command('init-db')
@with_appcontext
def init_db_command():
    """Initialize the database."""
    db.create_all()
    click.echo('Initialized the database.')

@app.cli.command('create-migrations')
@with_appcontext
def create_migrations_command():
    """Create initial migrations."""
    init()
    migrate()
    click.echo('Created initial migrations.')

@app.cli.command('upgrade-db')
@with_appcontext
def upgrade_db_command():
    """Upgrade the database to the latest migration."""
    upgrade()
    click.echo('Upgraded the database.')

@app.cli.command('stamp-db')
@with_appcontext
def stamp_db_command():
    """Stamp the database with the current migration version."""
    stamp()
    click.echo('Stamped the database.')

if __name__ == '__main__':
    app.run(debug=True) 