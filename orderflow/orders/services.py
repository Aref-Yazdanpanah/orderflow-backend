from __future__ import annotations

from decimal import Decimal
from typing import Dict, Iterable

from django.db import transaction

from .models import Order, OrderItem, Product


# ---------- helpers ----------
def _normalize(items: Iterable[Dict]) -> Dict:
    """
    Serializer injects _product_instance; convert to {pid: (Product, qty)}.
    """
    out = {}
    for row in items:
        p = row["_product_instance"]
        q = int(row["quantity"])
        out[p.id] = (p, q)
    return out


def _lock_products(product_ids):
    return (
        Product.objects.select_for_update()
        .only("id", "unit_price", "is_active", "name")
        .filter(id__in=product_ids, is_active=True)
    )


def _snapshot_line(order: Order, product: Product, qty: int) -> OrderItem:
    return OrderItem(
        order=order, product=product, quantity=qty, unit_price=product.unit_price
    )


def _bulk_create_items(order: Order, pairs):
    if not pairs:
        return
    OrderItem.objects.bulk_create([_snapshot_line(order, p, q) for (p, q) in pairs])


def _bulk_update_quantities(lines: Iterable[OrderItem]):
    if not lines:
        return
    OrderItem.objects.bulk_update(lines, fields=["quantity"])


def _bulk_delete_ids(order: Order, ids: list):
    if not ids:
        return
    OrderItem.objects.filter(order=order, id__in=ids).delete()


# ---------- public API ----------
@transaction.atomic
def create_order(*, customer, items: Iterable[Dict]) -> Order:
    data = _normalize(items)
    product_ids = list(data.keys())

    locked = _lock_products(product_ids)
    locked_by_id = {p.id: p for p in locked}

    order = Order.objects.create(customer=customer, total_price=Decimal("0.00"))

    create_pairs = [
        (locked_by_id[pid], qty)
        for pid, (_, qty) in data.items()
        if qty > 0 and pid in locked_by_id
    ]
    _bulk_create_items(order, create_pairs)

    order.recalculate_totals(save=True)
    return order


@transaction.atomic
def update_order(*, order: Order, items: Iterable[Dict]) -> Order:
    # Lock order row
    order = Order.objects.select_for_update().get(pk=order.pk)

    data = _normalize(items)
    product_ids = list(data.keys())

    # Lock products for consistent snapshots on newly added lines
    locked = _lock_products(product_ids)
    locked_by_id = {p.id: p for p in locked}

    # Load existing lines once
    existing = {li.product_id: li for li in order.items.select_related("product").all()}

    to_delete_ids, to_update, to_create = [], [], []

    for pid, (product, qty) in data.items():
        line = existing.get(pid)

        if qty <= 0:
            if line:
                to_delete_ids.append(line.id)
            continue

        if line:
            if line.quantity != qty:
                line.quantity = qty
                to_update.append(line)
        else:
            p_locked = locked_by_id.get(pid)
            if p_locked:
                to_create.append((p_locked, qty))

    _bulk_delete_ids(order, to_delete_ids)
    _bulk_update_quantities(to_update)
    _bulk_create_items(order, to_create)

    order.recalculate_totals(save=True)
    return order


@transaction.atomic
def delete_order(*, order: Order) -> None:
    order = Order.objects.select_for_update().get(pk=order.pk)
    order.delete()
