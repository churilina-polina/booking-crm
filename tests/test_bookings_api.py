from datetime import timedelta

from django.urls import reverse
from django.utils import timezone

import pytest

from apps.bookings.models import Booking
from tests.factories import UserFactory

pytestmark = pytest.mark.django_db


def test_anonymous_cannot_list_bookings(api_client):
    url = reverse('booking-list')
    response = api_client.get(url)
    assert response.status_code == 401


def test_client_can_create_booking(auth_client, employee, service):
    url = reverse('booking-list')
    start = timezone.now() + timedelta(days=1)
    payload = {
        'employee': employee.id,
        'service': service.id,
        'start_time': start.isoformat(),
    }
    response = auth_client.post(url, payload)
    assert response.status_code == 201, response.data
    assert response.data['status'] == Booking.Status.PENDING


def test_client_sees_only_own_bookings(auth_client, client_user, employee, service):
    other_client = UserFactory()
    Booking.objects.create(
        client=other_client,
        employee=employee,
        service=service,
        start_time=timezone.now() + timedelta(days=1),
        end_time=timezone.now() + timedelta(days=1, hours=1),
    )
    url = reverse('booking-list')
    response = auth_client.get(url)
    assert response.status_code == 200
    assert response.data['count'] == 0


def test_client_can_cancel_own_booking(auth_client, client_user, employee, service):
    booking = Booking.objects.create(
        client=client_user,
        employee=employee,
        service=service,
        start_time=timezone.now() + timedelta(days=1),
        end_time=timezone.now() + timedelta(days=1, hours=1),
    )
    url = reverse('booking-cancel', args=[booking.id])
    response = auth_client.post(url)
    assert response.status_code == 200
    booking.refresh_from_db()
    assert booking.status == Booking.Status.CANCELLED
