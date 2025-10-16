from django.db.models import Prefetch

from .models import Order, OrderItem


def order_base_qs():
    """
    Minimal columns + eager loading to avoid N+1.
    """
    return (
        Order.objects.select_related("customer")
        .only("id", "customer_id", "total_price", "created_at", "updated_at")
        .prefetch_related(
            Prefetch(
                "items",
                queryset=OrderItem.objects.select_related("product").only(
                    "id",
                    "order_id",
                    "product_id",
                    "quantity",
                    "unit_price",
                    "created_at",
                    "updated_at",
                    "product__name",
                ),
            )
        )
    )


def scope_for_user(qs, user):
    """
    Admins (or holders of 'orders.view_all_orders') see all; others see their own.
    """
    if user.has_perm("orders.view_all_orders"):
        return qs
    return qs.filter(customer_id=user.id)
