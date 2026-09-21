import pytest
from rest_framework.test import APIClient

from .factories import EmployeeFactory, ServiceFactory, UserFactory, WorkingHoursFactory


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def client_user():
    return UserFactory()


@pytest.fixture
def service():
    return ServiceFactory()


@pytest.fixture
def employee(service):
    employee = EmployeeFactory(services=[service])
    WorkingHoursFactory(employee=employee, weekday=0, start_time='09:00', end_time='18:00')
    return employee


@pytest.fixture
def auth_client(api_client, client_user):
    api_client.force_authenticate(user=client_user)
    return api_client
