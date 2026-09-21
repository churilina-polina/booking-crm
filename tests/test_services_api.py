from django.urls import reverse

import pytest

pytestmark = pytest.mark.django_db


def test_authenticated_client_can_list_services(auth_client, service):
    response = auth_client.get(reverse('service-list'))
    assert response.status_code == 200
    assert response.data['count'] == 1


def test_client_cannot_create_service(auth_client):
    response = auth_client.post(
        reverse('service-list'),
        {
            'name': 'Хочу без прав',
            'duration_minutes': 30,
            'price': '500',
        },
    )
    assert response.status_code == 403


def test_staff_can_create_service(api_client, employee):
    api_client.force_authenticate(user=employee.user)
    response = api_client.post(
        reverse('service-list'),
        {
            'name': 'Новая услуга',
            'duration_minutes': 45,
            'price': '800',
        },
    )
    assert response.status_code == 201, response.data
