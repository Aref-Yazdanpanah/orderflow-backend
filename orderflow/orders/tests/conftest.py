import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from .factories import ProductFactory, UserFactory

User = get_user_model()


@pytest.fixture
def user(db) -> User:  # type: ignore
    return UserFactory()


@pytest.fixture
def other_user(db) -> User:  # type: ignore
    return UserFactory()


@pytest.fixture
def client() -> APIClient:
    return APIClient()


@pytest.fixture
def auth_client(client: APIClient, user: User) -> APIClient:  # type: ignore
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def product(db):
    return ProductFactory(unit_price="10.00", is_active=True)


@pytest.fixture
def inactive_product(db):
    return ProductFactory(is_active=False)
