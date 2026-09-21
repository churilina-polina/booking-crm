from datetime import timedelta

from django.urls import reverse
from django.utils import timezone

import pytest

from apps.bookings.models import Booking, Payment

pytestmark = pytest.mark.django_db


@pytest.fixture
def paid_booking(client_user, employee, service):
    booking = Booking.objects.create(
        client=client_user,
        employee=employee,
        service=service,
        start_time=timezone.now() + timedelta(hours=1),
        end_time=timezone.now() + timedelta(hours=2),
        status=Booking.Status.CONFIRMED,
    )
    Payment.objects.create(booking=booking, amount=service.price, status=Payment.Status.PAID)
    return booking


def test_client_cannot_view_revenue_report(auth_client, paid_booking):
    response = auth_client.get(reverse('report-revenue'))
    assert response.status_code == 403


def _period_covering(booking):
    local_date = timezone.localtime(booking.start_time).date()
    return {
        'date_from': (local_date - timedelta(days=1)).isoformat(),
        'date_to': (local_date + timedelta(days=1)).isoformat(),
    }


def test_staff_can_view_revenue_report(api_client, employee, paid_booking):
    api_client.force_authenticate(user=employee.user)
    response = api_client.get(reverse('report-revenue'), _period_covering(paid_booking))
    assert response.status_code == 200
    assert float(response.data['total_revenue']) == float(paid_booking.payment.amount)


def test_employee_load_report(api_client, employee, paid_booking):
    api_client.force_authenticate(user=employee.user)
    response = api_client.get(reverse('report-employee-load'), _period_covering(paid_booking))
    assert response.status_code == 200
    assert response.data['employees'][0]['bookings_count'] == 1
