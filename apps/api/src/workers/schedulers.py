"""
Celery Beat scheduled tasks (stub for future use).
"""

from celery.schedules import crontab
from .celery_app import celery_app

# Example scheduled tasks configuration
celery_app.conf.beat_schedule = {
    # Clean up old jobs daily at 2 AM
    'cleanup-old-jobs': {
        'task': 'src.workers.tasks.cleanup_old_jobs',
        'schedule': crontab(hour=2, minute=0),
        'args': (30,)  # Days to keep
    },
    
    # Generate daily reports at 6 AM
    # 'daily-reports': {
    #     'task': 'src.workers.tasks.generate_daily_reports',
    #     'schedule': crontab(hour=6, minute=0),
    # },
}