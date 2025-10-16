import pytest
from django.urls import resolve, reverse

from .factories import UserFactory

pytestmark = pytest.mark.django_db


def test_user_detail():
    user = UserFactory()
    name = "v1-user-detail"
    url = f"/api/v1/users/{user.id}"
    # lookup_field is "id" on the viewset
    assert reverse(name, kwargs={"id": user.id}) == url
    assert resolve(url).view_name == name


def test_user_me():
    name = "v1-user-me"
    url = "/api/v1/users/i"
    assert reverse(name) == url
    assert resolve(url).view_name == name


def test_authentication_refresh_token():
    name = "v1-authentication-refresh-token"
    url = "/api/v1/auth/refresh-jwt"
    assert reverse(name) == url
    assert resolve(url).view_name == name


def test_authentication_sign_in_password():
    name = "v1-authentication-sign-in-password"
    url = "/api/v1/auth/sign-in/password"
    assert reverse(name) == url
    assert resolve(url).view_name == name


def test_authentication_sign_up_password():
    name = "v1-authentication-sign-up-password"
    url = "/api/v1/auth/sign-up/password"
    assert reverse(name) == url
    assert resolve(url).view_name == name


def test_authentication_sign_in_mobile_step1():
    name = "v1-authentication-sign-in-mobile-step1"
    url = "/api/v1/auth/sign-in/mobile/step1"
    assert reverse(name) == url
    assert resolve(url).view_name == name


def test_authentication_sign_in_otp_step2():
    name = "v1-authentication-sign-in-otp-step2"
    url = "/api/v1/auth/sign-in/otp/step2"
    assert reverse(name) == url
    assert resolve(url).view_name == name


def test_authentication_sign_up_mobile_step1():
    name = "v1-authentication-sign-up-mobile-step1"
    url = "/api/v1/auth/sign-up/mobile/step1"
    assert reverse(name) == url
    assert resolve(url).view_name == name


def test_authentication_sign_up_otp_step2():
    name = "v1-authentication-sign-up-otp-step2"
    url = "/api/v1/auth/sign-up/otp/step2"
    assert reverse(name) == url
    assert resolve(url).view_name == name
