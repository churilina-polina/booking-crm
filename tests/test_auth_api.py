import pytest
from django.urls import reverse

from apps.users.models import User

pytestmark = pytest.mark.django_db


def test_user_can_register(api_client):
    url = reverse('register')
    payload = {'username': 'newclient', 'email': 'new@example.com', 'password': 'strongpass123'}
    response = api_client.post(url, payload)
    assert response.status_code == 201
    user = User.objects.get(username='newclient')
    assert user.role == User.Role.CLIENT
    assert user.check_password('strongpass123')


def test_user_can_obtain_token(api_client):
    User.objects.create_user(username='loginuser', password='strongpass123')
    url = reverse('token_obtain_pair')
    response = api_client.post(url, {'username': 'loginuser', 'password': 'strongpass123'})
    assert response.status_code == 200
    assert 'access' in response.data
    assert 'refresh' in response.data
