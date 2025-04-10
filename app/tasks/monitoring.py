from app.tasks import celery
from celery.signals import task_success, task_failure, task_revoked
from datetime import datetime
import logging
import json

logger = logging.getLogger(__name__)

class TaskMonitor:
    def __init__(self):
        self.task_stats = {}
        self.failed_tasks = {}
        self.revoked_tasks = {}
    
    def record_task_success(self, task_id, task_name, runtime):
        """Record successful task execution."""
        if task_name not in self.task_stats:
            self.task_stats[task_name] = {
                'success_count': 0,
                'failure_count': 0,
                'total_runtime': 0,
                'last_success': None
            }
        
        stats = self.task_stats[task_name]
        stats['success_count'] += 1
        stats['total_runtime'] += runtime
        stats['last_success'] = datetime.utcnow().isoformat()
        
        logger.info(f"Task {task_name} completed successfully in {runtime:.2f}s")
    
    def record_task_failure(self, task_id, task_name, exception):
        """Record failed task execution."""
        if task_name not in self.task_stats:
            self.task_stats[task_name] = {
                'success_count': 0,
                'failure_count': 0,
                'total_runtime': 0,
                'last_success': None
            }
        
        stats = self.task_stats[task_name]
        stats['failure_count'] += 1
        
        if task_id not in self.failed_tasks:
            self.failed_tasks[task_id] = []
        
        self.failed_tasks[task_id].append({
            'timestamp': datetime.utcnow().isoformat(),
            'exception': str(exception)
        })
        
        logger.error(f"Task {task_name} failed: {str(exception)}")
    
    def record_task_revoked(self, task_id, task_name, reason):
        """Record revoked task."""
        if task_id not in self.revoked_tasks:
            self.revoked_tasks[task_id] = []
        
        self.revoked_tasks[task_id].append({
            'timestamp': datetime.utcnow().isoformat(),
            'reason': reason
        })
        
        logger.warning(f"Task {task_name} was revoked: {reason}")
    
    def get_task_stats(self):
        """Get current task statistics."""
        return {
            'task_stats': self.task_stats,
            'failed_tasks': self.failed_tasks,
            'revoked_tasks': self.revoked_tasks
        }
    
    def export_stats(self, filepath):
        """Export task statistics to a JSON file."""
        stats = self.get_task_stats()
        with open(filepath, 'w') as f:
            json.dump(stats, f, indent=2)

# Initialize task monitor
task_monitor = TaskMonitor()

# Register signal handlers
@task_success.connect
def handle_task_success(sender=None, **kwargs):
    task_monitor.record_task_success(
        kwargs.get('task_id'),
        kwargs.get('name'),
        kwargs.get('runtime', 0)
    )

@task_failure.connect
def handle_task_failure(sender=None, **kwargs):
    task_monitor.record_task_failure(
        kwargs.get('task_id'),
        kwargs.get('name'),
        kwargs.get('exception')
    )

@task_revoked.connect
def handle_task_revoked(sender=None, **kwargs):
    task_monitor.record_task_revoked(
        kwargs.get('task_id'),
        kwargs.get('name'),
        kwargs.get('reason')
    ) 