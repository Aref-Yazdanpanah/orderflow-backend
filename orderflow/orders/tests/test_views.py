from decimal import Decimal

import pytest
from django.contrib.auth.models import Permission
from django.urls import reverse
from rest_framework.test import APIClient

from orderflow.orders.models import Order, OrderItem

from .factories import OrderFactory, ProductFactory

pytestmark = pytest.mark.django_db


def D(x) -> Decimal:
    return x if isinstance(x, Decimal) else Decimal(str(x))


def grant_perm(user, codename: str):
    perm = Permission.objects.get(codename=codename)
    user.user_permissions.add(perm)
    user.refresh_from_db()
    return user


class TestListAndRetrieve:
    list_url = reverse("v1-orders-list")

    def test_list_scoped_to_owner(self, user, other_user, client: APIClient):
        o1 = OrderFactory(customer=user)
        o2 = OrderFactory(customer=other_user)

        client.force_authenticate(user=user)
        resp = client.get(self.list_url)
        assert resp.status_code == 200
        body = resp.json()
        rows = body.get("results", body)
        ids = {r["id"] for r in rows}
        assert str(o1.id) in ids
        assert str(o2.id) not in ids

    def test_list_admin_with_perm_sees_all(self, user, other_user, client: APIClient):
        o1 = OrderFactory(customer=user)
        o2 = OrderFactory(customer=other_user)

        grant_perm(user, "view_all_orders")
        client.force_authenticate(user=user)
        resp = client.get(self.list_url)
        assert resp.status_code == 200
        body = resp.json()
        rows = body.get("results", body)
        ids = {r["id"] for r in rows}
        assert {str(o1.id), str(o2.id)}.issubset(ids)

    def test_retrieve_own_ok(self, user, client: APIClient):
        order = OrderFactory(customer=user)
        client.force_authenticate(user=user)
        resp = client.get(f"/api/v1/orders/{order.id}/")
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == str(order.id)
        assert data["customer_id"] == str(user.id)

    def test_retrieve_other_404_due_to_scope(self, user, other_user, client: APIClient):
        order = OrderFactory(customer=other_user)
        client.force_authenticate(user=user)
        resp = client.get(f"/api/v1/orders/{order.id}/")
        assert resp.status_code == 404


class TestCreate:
    url = reverse("v1-orders-list")

    def test_create_success_201(self, user, client: APIClient):
        p1 = ProductFactory(unit_price="4.50")
        p2 = ProductFactory(unit_price="1.00")

        client.force_authenticate(user=user)
        payload = {
            "items": [
                {"product": str(p1.id), "quantity": 2},
                {"product": str(p2.id), "quantity": 3},
            ]
        }
        resp = client.post(self.url, payload, format="json")
        assert resp.status_code == 201
        data = resp.json()

        expected = D(2) * D(p1.unit_price) + D(3) * D(p2.unit_price)
        assert data["total_price"] == str(expected)
        assert len(data["items"]) == 2

        order = Order.objects.get(pk=data["id"])
        assert order.total_price == expected

    def test_create_rejects_inactive_product(self, user, client: APIClient):
        inactive = ProductFactory(is_active=False)
        client.force_authenticate(user=user)
        payload = {"items": [{"product": str(inactive.id), "quantity": 1}]}
        resp = client.post(self.url, payload, format="json")
        assert resp.status_code == 400
        body = resp.json()
        assert "product" in body["items"][0]


class TestUpdateAndDelete:
    def test_owner_can_update(self, user, client: APIClient):
        p1 = ProductFactory(unit_price="2.00")
        p2 = ProductFactory(unit_price="5.00")
        order = OrderFactory(customer=user)
        OrderItem.objects.create(
            order=order, product=p1, quantity=1, unit_price=p1.unit_price
        )

        client.force_authenticate(user=user)
        payload = {
            "items": [
                {"product": str(p1.id), "quantity": 3},
                {"product": str(p2.id), "quantity": 2},
            ]
        }
        resp = client.put(f"/api/v1/orders/{order.id}/", payload, format="json")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["items"]) == 2
        expected = D(3) * D(p1.unit_price) + D(2) * D(p2.unit_price)
        assert data["total_price"] == str(expected)

    def test_non_owner_without_perms_cannot_update_404_by_scope(
        self, user, other_user, client: APIClient
    ):
        p = ProductFactory(unit_price="2.00")
        order = OrderFactory(customer=other_user)
        client.force_authenticate(user=user)
        resp = client.put(
            f"/api/v1/orders/{order.id}/",
            {"items": [{"product": str(p.id), "quantity": 1}]},
            format="json",
        )
        assert resp.status_code == 404

    def test_non_owner_with_view_and_edit_perms_can_update(
        self, user, other_user, client: APIClient
    ):
        p = ProductFactory(unit_price="3.00")
        order = OrderFactory(customer=other_user)

        grant_perm(user, "view_all_orders")
        grant_perm(user, "edit_any_order")

        client.force_authenticate(user=user)
        resp = client.put(
            f"/api/v1/orders/{order.id}/",
            {"items": [{"product": str(p.id), "quantity": 4}]},
            format="json",
        )
        assert resp.status_code == 200
        assert resp.json()["total_price"] == str(D(4) * D(p.unit_price))

    def test_owner_can_delete(self, user, client: APIClient):
        order = OrderFactory(customer=user)
        client.force_authenticate(user=user)
        resp = client.delete(f"/api/v1/orders/{order.id}/")
        assert resp.status_code == 204
        assert not Order.objects.filter(pk=order.id).exists()

    def test_non_owner_with_view_and_delete_perms_can_delete(
        self, user, other_user, client: APIClient
    ):
        order = OrderFactory(customer=other_user)
        grant_perm(user, "view_all_orders")
        grant_perm(user, "delete_any_order")

        client.force_authenticate(user=user)
        resp = client.delete(f"/api/v1/orders/{order.id}/")
        assert resp.status_code == 204
        assert not Order.objects.filter(pk=order.id).exists()


class TestFilteringAndOrdering:
    list_url = reverse("v1-orders-list")

    def test_filter_by_min_total_and_ordering(self, user, client: APIClient):
        p = ProductFactory(unit_price="10.00")
        client.force_authenticate(user=user)

        # o1: total 10
        r1 = client.post(
            self.list_url,
            {"items": [{"product": str(p.id), "quantity": 1}]},
            format="json",
        )
        o1 = r1.json()

        # o2: total 20
        r2 = client.post(
            self.list_url,
            {"items": [{"product": str(p.id), "quantity": 2}]},
            format="json",
        )
        o2 = r2.json()

        # o3: total 30
        r3 = client.post(
            self.list_url,
            {"items": [{"product": str(p.id), "quantity": 3}]},
            format="json",
        )
        o3 = r3.json()

        resp = client.get(self.list_url + "?min_total=15&ordering=total_price")
        assert resp.status_code == 200
        body = resp.json()
        rows = body.get("results", body)
        ids = [r["id"] for r in rows]
        assert o1["id"] not in ids
        assert o2["id"] in ids and o3["id"] in ids

        totals = [D(r["total_price"]) for r in rows]
        assert totals == sorted(totals)
