from celery import Celery
from celery.schedules import crontab
from celery.signals import after_setup_logger
import logging
from app.celery_app import celery_app

# Initialize Celery
celery = celery_app

# Configure Celery
celery.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour
    worker_max_tasks_per_child=1000,
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    task_default_retry_delay=300,  # 5 minutes
    task_max_retries=3,
)

# Configure scheduled tasks
celery.conf.beat_schedule = {
    'cleanup-expired-orders': {
        'task': 'app.tasks.order.cleanup_expired_orders',
        'schedule': crontab(minute='*/15'),  # Every 15 minutes
    },
    'update-hawker-locations': {
        'task': 'app.tasks.location.update_hawker_locations',
        'schedule': crontab(minute='*/5'),  # Every 5 minutes
    },
    'generate-daily-reports': {
        'task': 'app.tasks.reports.generate_daily_reports',
        'schedule': crontab(hour=0, minute=0),  # Daily at midnight
    },
}

# Setup logging
@after_setup_logger.connect
def setup_loggers(logger, *args, **kwargs):
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # File handler for all tasks
    fh = logging.FileHandler('logs/celery.log')
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    
    # File handler for errors only
    error_fh = logging.FileHandler('logs/celery_error.log')
    error_fh.setLevel(logging.ERROR)
    error_fh.setFormatter(formatter)
    logger.addHandler(error_fh)

# Import task modules
from app.tasks import order, location, reports 