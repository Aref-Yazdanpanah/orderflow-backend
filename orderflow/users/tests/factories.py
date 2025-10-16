from typing import Any, Sequence

import factory
from django.contrib.auth import get_user_model
from factory import fuzzy as fz
from factory.django import DjangoModelFactory

from orderflow.users.models import OTP


class UserFactory(DjangoModelFactory):
    """
    Local mobile usernames like 0912xxxxxxx
    """

    username = factory.Sequence(lambda n: f"0912000{n:04d}")
    first_name = fz.FuzzyText(length=8)
    last_name = fz.FuzzyText(length=12)

    @factory.post_generation
    def password(self, create: bool, extracted: Sequence[Any], **kwargs):
        if extracted:
            self.set_password(extracted)

    class Meta:
        model = get_user_model()
        django_get_or_create = ["username"]
        skip_postgeneration_save = True


class OTPFactory(DjangoModelFactory):
    destination = factory.Sequence(lambda n: f"0912000{n:04d}")
    password = factory.Sequence(lambda n: f"{n:06d}")

    class Meta:
        model = OTP
