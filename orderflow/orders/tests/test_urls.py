import pytest
from django.urls import resolve, reverse

from .factories import OrderFactory  # <-- bring in a factory for the fixture

pytestmark = pytest.mark.django_db


def test_orders_list_url():
    name = "v1-orders-list"
    url = "/api/v1/orders"
    assert reverse(name) == url
    assert resolve(url).view_name == name


def test_orders_detail_url(order):
    name = "v1-orders-detail"
    url = f"/api/v1/orders/{order.id}"
    assert reverse(name, kwargs={"pk": order.id}) == url
    assert resolve(url).view_name == name


# ---- local fixture for this module ----
@pytest.fixture
def order(db):
    return OrderFactory()
