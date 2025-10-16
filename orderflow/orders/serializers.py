from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from . import services
from .models import Order, OrderItem, Product


# ---------- Read side ----------
class OrderItemReadSerializer(serializers.ModelSerializer):
    product_id = serializers.UUIDField(read_only=True)
    product_name = serializers.CharField(source="product.name", read_only=True)
    line_total = serializers.DecimalField(
        max_digits=14, decimal_places=2, read_only=True
    )

    class Meta:
        model = OrderItem
        fields = (
            "id",
            "product_id",
            "product_name",
            "quantity",
            "unit_price",
            "line_total",
        )
        read_only_fields = fields


class OrderReadSerializer(serializers.ModelSerializer):
    customer_id = serializers.UUIDField(read_only=True)
    items = OrderItemReadSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = (
            "id",
            "customer_id",
            "total_price",
            "created_at",
            "updated_at",
            "items",
        )
        read_only_fields = fields


# ---------- Write side ----------
class OrderItemWriteSerializer(serializers.Serializer):
    """
    Write-contract for a line (upsert semantics):
      - quantity > 0 => set/create
      - quantity == 0 => remove
    """

    product = serializers.UUIDField()
    quantity = serializers.IntegerField(min_value=0)

    def validate(self, attrs):
        pid = attrs["product"]
        try:
            product = Product.objects.only("id", "is_active").get(id=pid)
        except Product.DoesNotExist:
            raise serializers.ValidationError({"product": _("Product not found.")})
        if not product.is_active:
            raise serializers.ValidationError({"product": _("Product is inactive.")})
        attrs["_product_instance"] = product
        return attrs


class OrderCreateSerializer(serializers.Serializer):
    items = OrderItemWriteSerializer(many=True, allow_empty=False)

    def create(self, validated_data):
        user = self.context["request"].user
        return services.create_order(customer=user, items=validated_data["items"])

    def to_representation(self, instance):
        return OrderReadSerializer(instance, context=self.context).data


class OrderUpdateSerializer(serializers.Serializer):
    items = OrderItemWriteSerializer(many=True, allow_empty=False)

    def update(self, instance, validated_data):
        return services.update_order(order=instance, items=validated_data["items"])

    def to_representation(self, instance):
        return OrderReadSerializer(instance, context=self.context).data
