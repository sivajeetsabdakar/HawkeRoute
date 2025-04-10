from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from app.models.user import User
from app.models.order import Order
from app.services.route_optimizer import RouteOptimizer
from app import db
from datetime import datetime, date
import pytz
from app.config import Config

def optimize_routes():
    """Optimize routes for all hawkers with pending orders"""
    # Get current date in the configured timezone
    tz = pytz.timezone(Config.TIMEZONE)
    current_date = datetime.now(tz).date()
    
    # Get all active hawkers
    hawkers = User.query.filter_by(role='hawker', is_active=True).all()
    
    for hawker in hawkers:
        # Check if hawker has pending orders for today
        pending_orders = Order.query.filter_by(
            hawker_id=hawker.id,
            status='pending'
        ).filter(
            db.func.date(Order.created_at) == current_date
        ).count()
        
        if pending_orders > 0:
            # Create route optimizer and optimize
            optimizer = RouteOptimizer(hawker.id, current_date)
            route_plan = optimizer.optimize()
            
            if route_plan:
                print(f"Route optimized for hawker {hawker.id} with {pending_orders} orders")
            else:
                print(f"Failed to optimize route for hawker {hawker.id}")

def init_scheduler(app):
    """Initialize the scheduler with the Flask app context"""
    scheduler = BackgroundScheduler()
    
    # Schedule route optimization to run at 2 PM daily
    scheduler.add_job(
        func=optimize_routes,
        trigger=CronTrigger(hour=14, minute=0),  # 2 PM
        id='route_optimization',
        name='Optimize delivery routes',
        replace_existing=True
    )
    
    # Start the scheduler
    scheduler.start()
    
    # Shut down the scheduler when the app is shutting down
    app.teardown_appcontext(lambda _: scheduler.shutdown())
    
    return scheduler 