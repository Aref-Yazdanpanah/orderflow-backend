import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient

User = get_user_model()
pytestmark = pytest.mark.django_db


class TestUsersMe:
    url = reverse("v1-user-me")

    def test_me_ok(self, user: User, client: APIClient):  # type: ignore
        client.force_authenticate(user=user)
        resp = client.get(self.url)
        assert resp.status_code == 200
        data = resp.json()
        # drop dynamic fields for stable asserts
        data.pop("date_joined", None)
        data.pop("last_login", None)
        assert data == {
            "id": str(user.id),
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "is_superuser": user.is_superuser,
        }

    def test_me_anonymous_unauthorized(self, client: APIClient):
        resp = client.get(self.url)
        assert resp.status_code == 401


class TestUserRetrieve:
    def test_retrieve_self(self, user: User, client: APIClient):  # type: ignore
        client.force_authenticate(user=user)
        resp = client.get(f"/api/v1/users/{user.id}/")
        assert resp.status_code == 200

    def test_retrieve_other_allowed_readonly(self, user: User, client: APIClient):  # type: ignore
        other = User.objects.create(username="09120000001", first_name="", last_name="")
        client.force_authenticate(user=user)
        resp = client.get(f"/api/v1/users/{other.id}/")
        assert resp.status_code == 200

    def test_retrieve_not_found(self, user: User, client: APIClient):  # type: ignore
        client.force_authenticate(user=user)
        resp = client.get("/api/v1/users/99999999/")
        assert resp.status_code == 404
