from celery import Celery
from flask import Flask
import os
from dotenv import load_dotenv

load_dotenv()

def create_celery_app(app: Flask = None) -> Celery:
    """Create and configure Celery instance."""
    celery = Celery(
        'hawkeroute',
        broker=os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0'),
        backend=os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0'),
        include=[
            'app.tasks.order',
            'app.tasks.notification',
            'app.tasks.location'
        ]
    )

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
            'schedule': 900.0,  # Every 15 minutes
        },
        'update-hawker-locations': {
            'task': 'app.tasks.location.update_hawker_locations',
            'schedule': 300.0,  # Every 5 minutes
        },
    }

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            if app is not None:
                with app.app_context():
                    return self.run(*args, **kwargs)
            return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery

# Create the Celery instance
celery_app = create_celery_app() 