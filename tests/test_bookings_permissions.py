from datetime import timedelta

from django.urls import reverse
from django.utils import timezone

import pytest

from apps.bookings.models import Booking

pytestmark = pytest.mark.django_db


@pytest.fixture
def booking(client_user, employee, service):
    return Booking.objects.create(
        client=client_user,
        employee=employee,
        service=service,
        start_time=timezone.now() + timedelta(days=1),
        end_time=timezone.now() + timedelta(days=1, hours=1),
    )


def test_client_cannot_confirm_booking(auth_client, booking):
    response = auth_client.post(reverse('booking-confirm', args=[booking.id]))
    assert response.status_code == 403
    booking.refresh_from_db()
    assert booking.status == Booking.Status.PENDING


def test_staff_can_confirm_booking(api_client, employee, booking):
    api_client.force_authenticate(user=employee.user)
    response = api_client.post(reverse('booking-confirm', args=[booking.id]))
    assert response.status_code == 200
    booking.refresh_from_db()
    assert booking.status == Booking.Status.CONFIRMED


def test_client_cannot_access_other_clients_booking_detail(api_client, booking):
    from tests.factories import UserFactory

    other_client = UserFactory()
    api_client.force_authenticate(user=other_client)
    response = api_client.get(reverse('booking-detail', args=[booking.id]))
    assert response.status_code == 404
