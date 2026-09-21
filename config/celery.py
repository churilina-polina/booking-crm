import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('booking_crm')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'send-booking-reminders-every-5-minutes': {
        'task': 'apps.notifications.tasks.send_upcoming_booking_reminders',
        'schedule': 300.0,
    },
}
