from datetime import timedelta

from django.urls import reverse
from django.utils import timezone
from django.utils.dateparse import parse_datetime

import pytest

from apps.bookings.models import Booking

pytestmark = pytest.mark.django_db


def _next_working_date(employee):
    working_weekdays = set(employee.working_hours.values_list('weekday', flat=True))
    today = timezone.localdate()
    for offset in range(8):
        candidate = today + timedelta(days=offset)
        if candidate.weekday() in working_weekdays:
            return candidate
    raise AssertionError('Employee fixture has no working hours configured')


def test_available_slots_excludes_existing_booking(auth_client, client_user, employee, service):
    date = _next_working_date(employee)
    url = reverse('employee-available-slots', args=[employee.id])

    response = auth_client.get(url, {'service': service.id, 'date': date.isoformat()})
    assert response.status_code == 200
    slots_before = response.data
    assert len(slots_before) > 0

    first_slot = parse_datetime(slots_before[0])
    Booking.objects.create(
        client=client_user,
        employee=employee,
        service=service,
        start_time=first_slot,
        end_time=first_slot + service.duration,
    )

    response = auth_client.get(url, {'service': service.id, 'date': date.isoformat()})
    assert response.status_code == 200
    assert slots_before[0] not in response.data


def test_available_slots_requires_service_and_date(auth_client, employee):
    url = reverse('employee-available-slots', args=[employee.id])
    response = auth_client.get(url)
    assert response.status_code == 400


def test_available_slots_rejects_unrelated_service(auth_client, employee):
    from tests.factories import ServiceFactory

    other_service = ServiceFactory()
    url = reverse('employee-available-slots', args=[employee.id])
    response = auth_client.get(url, {'service': other_service.id, 'date': timezone.localdate().isoformat()})
    assert response.status_code == 400
