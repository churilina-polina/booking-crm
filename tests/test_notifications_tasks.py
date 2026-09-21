from datetime import timedelta
from unittest.mock import patch

from django.utils import timezone

import pytest

from apps.bookings.models import Booking
from apps.notifications.models import NotificationLog
from apps.notifications.tasks import send_upcoming_booking_reminders

pytestmark = pytest.mark.django_db


@pytest.fixture
def confirmed_booking_soon(client_user, employee, service):
    client_user.telegram_id = 123456
    client_user.save()
    return Booking.objects.create(
        client=client_user,
        employee=employee,
        service=service,
        start_time=timezone.now() + timedelta(minutes=30),
        end_time=timezone.now() + timedelta(minutes=90),
        status=Booking.Status.CONFIRMED,
    )


@patch('apps.notifications.tasks.settings')
@patch('requests.post')
def test_sends_reminder_and_logs_it(mock_post, mock_settings, confirmed_booking_soon):
    mock_settings.TELEGRAM_BOT_TOKEN = 'test-token'
    mock_post.return_value.raise_for_status.return_value = None

    sent = send_upcoming_booking_reminders()

    assert sent == 1
    confirmed_booking_soon.refresh_from_db()
    assert confirmed_booking_soon.reminder_sent is True
    assert NotificationLog.objects.filter(
        booking=confirmed_booking_soon,
        status=NotificationLog.Status.SENT,
    ).exists()


def test_no_reminder_for_bookings_outside_window(client_user, employee, service):
    booking = Booking.objects.create(
        client=client_user,
        employee=employee,
        service=service,
        start_time=timezone.now() + timedelta(hours=5),
        end_time=timezone.now() + timedelta(hours=6),
        status=Booking.Status.CONFIRMED,
    )
    sent = send_upcoming_booking_reminders()
    assert sent == 0
    booking.refresh_from_db()
    assert booking.reminder_sent is False
