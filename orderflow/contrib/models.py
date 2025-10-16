from uuid import uuid4

from django.db import models


class UUIDPKMixin(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)

    class Meta:
        abstract = True


class CreatedAtMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, editable=False, db_index=True)

    class Meta:
        abstract = True


class UpdatedAtMixin(models.Model):
    updated_at = models.DateTimeField(auto_now=True, db_index=True)

    class Meta:
        abstract = True


class TimeStampedUUIDModel(UUIDPKMixin, CreatedAtMixin, UpdatedAtMixin):
    """
    Convenient base model: UUID + created_at + updated_at.
    """

    class Meta:
        abstract = True
