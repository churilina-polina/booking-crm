import logging
from datetime import timedelta

from django.conf import settings
from django.utils import timezone

from celery import shared_task

from apps.bookings.models import Booking

logger = logging.getLogger(__name__)

REMINDER_WINDOW_MINUTES = 60


@shared_task
def send_upcoming_booking_reminders():
    """Find bookings starting within the reminder window and notify clients."""
    from .models import NotificationLog

    now = timezone.now()
    window_end = now + timedelta(minutes=REMINDER_WINDOW_MINUTES)

    upcoming = Booking.objects.filter(
        status=Booking.Status.CONFIRMED,
        reminder_sent=False,
        start_time__gte=now,
        start_time__lte=window_end,
    ).select_related('client', 'service', 'employee__user')

    sent = 0
    for booking in upcoming:
        try:
            send_telegram_reminder(booking)
            NotificationLog.objects.create(
                booking=booking,
                channel=NotificationLog.Channel.TELEGRAM,
                status=NotificationLog.Status.SENT,
            )
            booking.reminder_sent = True
            booking.save(update_fields=['reminder_sent'])
            sent += 1
        except Exception as exc:  # noqa: BLE001 — log and continue with next booking
            logger.exception('Failed to send reminder for booking %s', booking.id)
            NotificationLog.objects.create(
                booking=booking,
                channel=NotificationLog.Channel.TELEGRAM,
                status=NotificationLog.Status.FAILED,
                error_message=str(exc),
            )
    return sent


def send_telegram_reminder(booking):
    """Send a reminder message via the Telegram Bot API to the client, if linked."""
    import requests

    client = booking.client
    if not client.telegram_id or not settings.TELEGRAM_BOT_TOKEN:
        return

    text = (
        f'Напоминаем: запись на «{booking.service.name}» '
        f'{booking.start_time:%d.%m в %H:%M} к {booking.employee.user.get_full_name()}.'
    )
    url = f'https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage'
    response = requests.post(url, json={'chat_id': client.telegram_id, 'text': text}, timeout=10)
    response.raise_for_status()
