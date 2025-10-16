import logging
from random import randint
from typing import Any, Optional

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction

from orderflow.users.models import OTP, Roles

logger = logging.getLogger(__name__)
User = get_user_model()


def send_otp(destination: str, extra: dict[str, Any] | None = None) -> OTP:
    code = str(randint(10_000, 99_999))
    otp = OTP.objects.create(password=code, destination=destination, extra=extra or {})
    logger.info("sent OTP to %s , code: %s, ID: %s", destination, code, otp.id)
    return otp


@transaction.atomic(savepoint=False)
def _use_otp(otp_id: str, code: str) -> OTP:
    otp = OTP.objects.filter(id=otp_id, password=code).select_for_update().first()
    if otp is None:
        raise ValidationError("OTP is invalid.", code="invalid_auth/otp")
    if otp.is_expired():
        raise ValidationError("OTP is expired.", code="invalid_auth/otp_expired")
    if otp.is_used:
        raise ValidationError("OTP already used.", code="invalid_auth/otp_used")
    otp.is_used = True
    otp.save()
    return otp


@transaction.atomic(savepoint=False)
def _create_customer(username: str, *, password: Optional[str] = None) -> User:  # type: ignore
    try:
        user = User(
            username=username,
            is_active=True,
            first_name="",
            last_name="",
            role=Roles.CUSTOMER,
        )
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save()
        return user
    except IntegrityError as e:
        if "duplicate key value" in str(e) and "username" in str(e):
            raise ValidationError(
                "This mobile is already registered.", code="invalid_auth/duplicate"
            )
        raise


@transaction.atomic(savepoint=False)
def register_user_by_password(username: str, password: str) -> User:  # type: ignore
    return _create_customer(username, password=password)


@transaction.atomic(savepoint=False)
def register_user_by_otp(otp_id: str, code: str) -> User:  # type: ignore
    otp = _use_otp(otp_id, code)
    user = User.objects.filter(username=otp.destination).first()
    if user:
        return user
    return _create_customer(otp.destination)


@transaction.atomic(savepoint=False)
def get_user_by_otp(otp_id: str, code: str) -> User:  # type: ignore
    otp = _use_otp(otp_id, code)
    user = User.objects.filter(username=otp.destination).first()
    if not user:
        raise ValidationError(
            "No account for this mobile. Please sign up first.",
            code="invalid_auth/no_user",
        )
    if not user.is_active:
        raise ValidationError("User is inactive.", code="invalid_auth/inactive_user")
    return user
