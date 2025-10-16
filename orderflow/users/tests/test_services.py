from datetime import timedelta
from uuid import uuid4

import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from orderflow.users import services as s
from orderflow.users.models import OTP

from .factories import OTPFactory, UserFactory

User = get_user_model()
pytestmark = pytest.mark.django_db


class Test_use_otp:
    def test_absent_otp(self):
        with pytest.raises(ValidationError) as exc:
            s._use_otp(str(uuid4()), "000000")
        assert "OTP is invalid." in exc.value.messages

    def test_wrong_code(self):
        otp = OTPFactory()
        with pytest.raises(ValidationError) as exc:
            s._use_otp(str(otp.id), otp.password + "1")
        assert "OTP is invalid." in exc.value.messages

    def test_expired(self):
        otp = OTPFactory()
        otp.created_at -= timedelta(days=2)
        otp.save(update_fields=["created_at"])
        with pytest.raises(ValidationError) as exc:
            s._use_otp(str(otp.id), otp.password)
        assert "OTP is expired." in exc.value.messages

    def test_used(self):
        otp = OTPFactory(is_used=True)
        with pytest.raises(ValidationError) as exc:
            s._use_otp(str(otp.id), otp.password)
        assert "OTP already used." in exc.value.messages

    def test_valid_marks_used(self):
        otp = OTPFactory()
        s._use_otp(str(otp.id), otp.password)
        otp.refresh_from_db()
        assert otp.is_used is True


class Test_register_user_by_password:
    def test_creates_customer_with_password(self):
        mobile = "09121234567"
        assert not User.objects.filter(username=mobile).exists()
        user = s.register_user_by_password(mobile, "s3cret!")
        assert user.username == mobile
        assert user.is_active is True
        assert user.check_password("s3cret!")


class Test_register_user_by_otp:
    def test_creates_new_user_if_missing(self):
        otp = OTPFactory()
        assert not User.objects.filter(username=otp.destination).exists()
        user = s.register_user_by_otp(str(otp.id), otp.password)
        assert user.username == otp.destination
        assert user.is_active is True

    def test_returns_existing_user_if_present(self):
        user = UserFactory()
        otp = OTP.objects.create(destination=user.username, password="12345")
        got = s.register_user_by_otp(str(otp.id), "12345")
        assert got.id == user.id


class Test_get_user_by_otp:
    def test_existing_active_user(self, user):
        otp = OTP.objects.create(destination=user.username, password="123456")
        got = s.get_user_by_otp(str(otp.id), "123456")
        assert got.id == user.id

    def test_inactive_user(self, inactive_user):
        otp = OTP.objects.create(destination=inactive_user.username, password="123456")
        with pytest.raises(ValidationError) as exc:
            s.get_user_by_otp(str(otp.id), "123456")
        assert "User is inactive." in exc.value.messages

    def test_no_user_requires_signup(self):
        otp = OTPFactory()
        assert not User.objects.filter(username=otp.destination).exists()
        with pytest.raises(ValidationError) as exc:
            s.get_user_by_otp(str(otp.id), otp.password)
        assert "No account for this mobile. Please sign up first." in exc.value.messages
