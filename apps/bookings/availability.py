"""Shared slot-availability calculation, used by both the REST API and the Telegram bot."""

from datetime import datetime, timedelta

from django.utils import timezone

SLOT_STEP_MINUTES = 30
MAX_DAYS_AHEAD = 7


def get_available_dates(employee, days_ahead=MAX_DAYS_AHEAD):
    today = timezone.localdate()
    working_weekdays = set(employee.working_hours.values_list('weekday', flat=True))
    return [
        today + timedelta(days=offset)
        for offset in range(days_ahead)
        if (today + timedelta(days=offset)).weekday() in working_weekdays
    ]


def get_available_slots(employee, service, date):
    from .models import Booking

    working_hours = employee.working_hours.filter(weekday=date.weekday()).first()
    if not working_hours:
        return []

    tz = timezone.get_current_timezone()
    current = timezone.make_aware(datetime.combine(date, working_hours.start_time), tz)
    end_of_day = timezone.make_aware(datetime.combine(date, working_hours.end_time), tz)
    duration = service.duration

    existing = list(
        Booking.objects.filter(
            employee=employee,
            start_time__date=date,
            status__in=(Booking.Status.PENDING, Booking.Status.CONFIRMED),
        )
    )

    now = timezone.now()
    slots = []
    while current + duration <= end_of_day:
        overlaps = any(b.start_time < current + duration and b.end_time > current for b in existing)
        if not overlaps and current > now:
            slots.append(current)
        current += timedelta(minutes=SLOT_STEP_MINUTES)
    return slots
