from datetime import timedelta

import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone

from apps.bookings.models import Booking
from tests.factories import UserFactory

pytestmark = pytest.mark.django_db


def make_booking(client_user, employee, service, start_offset_minutes=60):
    start = timezone.now() + timedelta(minutes=start_offset_minutes)
    return Booking(
        client=client_user,
        employee=employee,
        service=service,
        start_time=start,
        end_time=start + service.duration,
    )


def test_booking_saves_successfully(client_user, employee, service):
    booking = make_booking(client_user, employee, service)
    booking.save()
    assert booking.pk is not None
    assert booking.status == Booking.Status.PENDING


def test_overlapping_booking_is_rejected(client_user, employee, service):
    first = make_booking(client_user, employee, service, start_offset_minutes=60)
    first.save()

    second_client = UserFactory()
    overlapping = make_booking(second_client, employee, service, start_offset_minutes=90)

    with pytest.raises(ValidationError):
        overlapping.save()


def test_non_overlapping_booking_is_allowed(client_user, employee, service):
    first = make_booking(client_user, employee, service, start_offset_minutes=60)
    first.save()

    second_client = UserFactory()
    later = make_booking(second_client, employee, service, start_offset_minutes=60 + service.duration_minutes)
    later.save()

    assert later.pk is not None


def test_end_before_start_is_rejected(client_user, employee, service):
    start = timezone.now() + timedelta(hours=1)
    booking = Booking(
        client=client_user, employee=employee, service=service,
        start_time=start, end_time=start - timedelta(minutes=10),
    )
    with pytest.raises(ValidationError):
        booking.save()
