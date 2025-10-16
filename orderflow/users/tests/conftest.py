import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from .factories import UserFactory


@pytest.fixture
def user(db):
    return UserFactory()


@pytest.fixture
def inactive_user(db):
    u = UserFactory()
    u.is_active = False
    u.save(update_fields=["is_active"])
    return u


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def auth_client(client: APIClient, user: get_user_model()):  # type: ignore
    client.force_authenticate(user=user)
    return client
