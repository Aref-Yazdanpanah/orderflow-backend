import django_filters as df

from .models import Order


class OrderFilter(df.FilterSet):
    created_from = df.DateTimeFilter(field_name="created_at", lookup_expr="gte")
    created_to = df.DateTimeFilter(field_name="created_at", lookup_expr="lte")
    edited_from = df.DateTimeFilter(field_name="updated_at", lookup_expr="gte")
    edited_to = df.DateTimeFilter(field_name="updated_at", lookup_expr="lte")
    min_total = df.NumberFilter(field_name="total_price", lookup_expr="gte")
    max_total = df.NumberFilter(field_name="total_price", lookup_expr="lte")

    class Meta:
        model = Order
        fields = (
            "created_from",
            "created_to",
            "edited_from",
            "edited_to",
            "min_total",
            "max_total",
        )
