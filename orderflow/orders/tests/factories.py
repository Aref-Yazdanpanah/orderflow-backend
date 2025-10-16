from decimal import Decimal
from typing import Any, Sequence

import factory
from django.contrib.auth import get_user_model
from factory import fuzzy as fz
from factory.django import DjangoModelFactory

from orderflow.orders.models import Order, OrderItem, Product

User = get_user_model()


class UserFactory(DjangoModelFactory):
    username = factory.Sequence(lambda n: f"0912000{n:04d}")
    first_name = fz.FuzzyText(length=6)
    last_name = fz.FuzzyText(length=8)

    @factory.post_generation
    def password(self, create: bool, extracted: Sequence[Any], **kwargs):
        if extracted:
            self.set_password(extracted)

    class Meta:
        model = User
        django_get_or_create = ["username"]
        skip_postgeneration_save = True


class ProductFactory(DjangoModelFactory):
    name = factory.Sequence(lambda n: f"Product-{n}")
    unit_price = Decimal("5.00")
    is_active = True

    class Meta:
        model = Product


class OrderFactory(DjangoModelFactory):
    customer = factory.SubFactory(UserFactory)
    total_price = Decimal("0.00")

    class Meta:
        model = Order


class OrderItemFactory(DjangoModelFactory):
    order = factory.SubFactory(OrderFactory)
    product = factory.SubFactory(ProductFactory)
    quantity = 1
    unit_price = factory.LazyAttribute(lambda o: o.product.unit_price)

    class Meta:
        model = OrderItem
