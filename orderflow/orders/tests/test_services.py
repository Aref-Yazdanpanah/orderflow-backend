from decimal import Decimal

import pytest

from orderflow.orders import services as s
from orderflow.orders.models import Order, OrderItem

from .factories import OrderFactory, OrderItemFactory, ProductFactory

pytestmark = pytest.mark.django_db


# Helper: coerce model field or primitive to Decimal robustly
def D(x) -> Decimal:
    return x if isinstance(x, Decimal) else Decimal(str(x))


class TestCreateOrder:
    def test_creates_lines_and_total_from_snapshots(self, user):
        p1 = ProductFactory(unit_price="10.50")
        p2 = ProductFactory(unit_price="3.40")

        order = s.create_order(
            customer=user,
            items=[
                {"product": p1.id, "quantity": 2, "_product_instance": p1},
                {"product": p2.id, "quantity": 5, "_product_instance": p2},
            ],
        )

        order.refresh_from_db()
        lines = list(order.items.order_by("product__name"))
        assert len(lines) == 2

        expected = D(2) * D(p1.unit_price) + D(5) * D(p2.unit_price)
        assert order.total_price == expected

        unit_prices = {D(li.unit_price) for li in lines}
        assert D(p1.unit_price) in unit_prices and D(p2.unit_price) in unit_prices


class TestUpdateOrder:
    def test_upsert_quantities_add_remove_and_recalculate(self, user):
        p1 = ProductFactory(unit_price="10.00")
        p2 = ProductFactory(unit_price="20.00")
        p3 = ProductFactory(unit_price="30.00")

        order = OrderFactory(customer=user)
        OrderItemFactory(order=order, product=p1, quantity=2, unit_price=p1.unit_price)

        order = s.update_order(
            order=order,
            items=[
                {"product": p1.id, "quantity": 3, "_product_instance": p1},
                {"product": p2.id, "quantity": 1, "_product_instance": p2},
                {"product": p3.id, "quantity": 0, "_product_instance": p3},
            ],
        )

        order.refresh_from_db()
        lines = {li.product_id: li for li in order.items.all()}

        assert set(lines.keys()) == {p1.id, p2.id}
        assert lines[p1.id].quantity == 3
        assert D(lines[p1.id].unit_price) == D(p1.unit_price)  # snapshot unchanged
        assert lines[p2.id].quantity == 1
        assert D(lines[p2.id].unit_price) == D(p2.unit_price)  # snapshot on creation

        expected = D(3) * D(p1.unit_price) + D(1) * D(p2.unit_price)
        assert order.total_price == expected

    def test_setting_quantity_zero_deletes_line(self, user):
        p = ProductFactory(unit_price="7.00")
        order = OrderFactory(customer=user)
        OrderItemFactory(order=order, product=p, quantity=4, unit_price=p.unit_price)

        order = s.update_order(
            order=order,
            items=[{"product": p.id, "quantity": 0, "_product_instance": p}],
        )

        assert not OrderItem.objects.filter(order=order, product=p).exists()
        assert order.total_price == D("0.00")


class TestDeleteOrder:
    def test_deletes_order_and_items(self, user):
        order = OrderFactory(customer=user)
        OrderItemFactory(order=order)
        OrderItemFactory(order=order)

        s.delete_order(order=order)
        assert not Order.objects.filter(pk=order.pk).exists()
        assert not OrderItem.objects.filter(order_id=order.pk).exists()
