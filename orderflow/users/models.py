from datetime import timedelta

from django.apps import apps
from django.contrib import auth
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import PermissionsMixin
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from orderflow.contrib.models import CreatedAtMixin, UUIDPKMixin


# ---- Roles ----
class Roles(models.TextChoices):
    ADMIN = "ADMIN", "Admin"
    CUSTOMER = "CUSTOMER", "Customer"


# ---- User Manager ----
class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, username, password, **extra_fields):
        if not username:
            raise ValueError("Username (mobile) must be set")

        GlobalUserModel = apps.get_model(
            self.model._meta.app_label, self.model._meta.object_name
        )
        username = GlobalUserModel.normalize_username(username)

        user = self.model(username=username, **extra_fields)
        user.password = (
            make_password(password) if password else user.set_unusable_password()
        )
        user.save(using=self._db)
        return user

    def create_user(self, username, password=None, **extra_fields):
        extra_fields.setdefault("role", Roles.CUSTOMER)
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(username, password, **extra_fields)

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault("role", Roles.ADMIN)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        return self._create_user(username, password, **extra_fields)

    def with_perm(
        self, perm, is_active=True, include_superusers=True, backend=None, obj=None
    ):
        if backend is None:
            backends = auth._get_backends(return_tuples=True)
            if len(backends) == 1:
                backend, _ = backends[0]
            else:
                raise ValueError(
                    "Multiple authentication backends configured; provide `backend`."
                )
        elif not isinstance(backend, str):
            raise TypeError("backend must be a dotted import path string.")
        else:
            backend = auth.load_backend(backend)

        if hasattr(backend, "with_perm"):
            return backend.with_perm(
                perm,
                is_active=is_active,
                include_superusers=include_superusers,
                obj=obj,
            )
        return self.none()


# ---- User ----
class User(UUIDPKMixin, AbstractBaseUser, PermissionsMixin):
    """
    Username is local mobile like 09121234567. Supports password and OTP flows.
    """

    phone_regex = RegexValidator(
        regex=r"^09\d{9}$",
        message=_("Enter a valid mobile like 09121234567."),
    )

    username = models.CharField(
        _("mobile"),
        max_length=11,
        unique=True,
        validators=[phone_regex],
        help_text=_("Local mobile number (e.g., 09121234567)."),
        error_messages={"unique": _("A user with that mobile already exists.")},
        db_index=True,
    )

    first_name = models.CharField(_("first name"), max_length=150, blank=False)
    last_name = models.CharField(_("last name"), max_length=150, blank=False)

    role = models.CharField(
        max_length=20, choices=Roles.choices, default=Roles.CUSTOMER, db_index=True
    )

    is_staff = models.BooleanField(_("staff status"), default=False)
    is_active = models.BooleanField(_("active"), default=True)
    date_joined = models.DateTimeField(_("date joined"), default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")
        swappable = "AUTH_USER_MODEL"
        indexes = [
            models.Index(fields=["username"]),
            models.Index(fields=["role"]),
            models.Index(fields=["is_active", "role"]),
        ]

    def __str__(self):
        return str(self.username)

    @classmethod
    def normalize_username(cls, username: str) -> str:
        if username is None:
            return username
        return str(username).strip()


# ---- OTP ----
class OTP(UUIDPKMixin, CreatedAtMixin, models.Model):
    """
    One-Time Password model (LOGIN/REGISTER flows implemented elsewhere).
    """

    expiration_time = timedelta(minutes=10)

    password = models.CharField(max_length=8, editable=False)
    destination = models.CharField(max_length=128, editable=False)  # target mobile
    is_used = models.BooleanField(default=False)
    extra = models.JSONField(default=dict)

    def is_expired(self):
        return self.created_at + self.expiration_time < timezone.now()

    def __str__(self):
        return str(self.id)

    class Meta:
        indexes = [
            models.Index(fields=["destination", "is_used", "created_at"]),
            models.Index(fields=["created_at"]),
        ]
