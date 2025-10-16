from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from orderflow.contrib.models import TimeStampedUUIDModel


class Product(TimeStampedUUIDModel):
    """
    `unit_price` is the *current* catalog price; each OrderItem stores a snapshot.
    """

    name = models.CharField(max_length=255, unique=True, db_index=True)
    unit_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
        help_text=_("Current unit price in the default currency."),
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = _("product")
        verbose_name_plural = _("products")
        ordering = ["name"]
        indexes = [
            models.Index(fields=["is_active", "name"]),
            models.Index(fields=["unit_price"]),
        ]

    def __str__(self) -> str:
        return self.name


class Order(TimeStampedUUIDModel):
    """
    An order placed by a customer (User). Totals are denormalized for fast filtering.
    Use the service layer to mutate items and call `recalculate_totals()` in a tx.
    """

    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="orders",
        db_index=True,
    )

    # Denormalized total (kept in sync by services)
    total_price = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
        help_text=_("Sum of line items (quantity × unit_price snapshot)."),
    )

    class Meta:
        verbose_name = _("order")
        verbose_name_plural = _("orders")
        ordering = ["-created_at"]
        permissions = [
            ("view_all_orders", "Can view all orders"),
            ("edit_any_order", "Can edit any order"),
            ("delete_any_order", "Can delete any order"),
        ]
        indexes = [
            models.Index(fields=["customer", "created_at"]),
            models.Index(fields=["total_price"]),
        ]

    def __str__(self) -> str:
        return f"Order {self.pk} by {self.customer}"

    def recalculate_totals(self, save: bool = True) -> Decimal:
        """
        Recompute and (optionally) persist the denormalized total_price from items.
        Intended to be called by the service layer within a transaction.
        """
        total = self.items.aggregate(
            s=models.Sum(
                models.F("quantity") * models.F("unit_price"),
                output_field=models.DecimalField(max_digits=14, decimal_places=2),
            )
        )["s"] or Decimal("0.00")
        self.total_price = total
        if save:
            self.save(update_fields=["total_price", "updated_at"])
        return total

    def is_owner(self, user) -> bool:
        return bool(
            user
            and getattr(user, "is_authenticated", False)
            and user.pk == self.customer_id
        )


class OrderItem(TimeStampedUUIDModel):
    """
    Line item for an Order. Stores a *price snapshot* at the time of addition.
    Enforces one row per (order, product) to avoid duplicate lines; adjust via services.
    """

    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="items", db_index=True
    )
    product = models.ForeignKey(
        Product, on_delete=models.PROTECT, related_name="order_items", db_index=True
    )

    quantity = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        help_text=_("Number of units purchased."),
    )

    # Snapshot of product price at the time this line was added/updated
    unit_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
        help_text=_("Unit price snapshot captured when item was added."),
    )

    class Meta:
        verbose_name = _("order item")
        verbose_name_plural = _("order items")
        constraints = [
            models.CheckConstraint(
                check=models.Q(quantity__gte=1), name="orderitem_quantity_gte_1"
            ),
            models.CheckConstraint(
                check=models.Q(unit_price__gte=0), name="orderitem_unit_price_gte_0"
            ),
            models.UniqueConstraint(
                fields=["order", "product"], name="uniq_order_product_per_order"
            ),
        ]
        indexes = [
            models.Index(fields=["order", "product"]),
        ]

    def __str__(self) -> str:
        return f"{self.product} × {self.quantity}"

    @property
    def line_total(self) -> Decimal:
        return (self.unit_price or Decimal("0.00")) * Decimal(self.quantity)
