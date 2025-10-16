from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .filters import OrderFilter
from .permissions import IsOwnerOrHasOrderPerms
from .selectors import order_base_qs, scope_for_user
from .serializers import OrderCreateSerializer, OrderReadSerializer, OrderUpdateSerializer


class OrderViewSetV1(viewsets.ModelViewSet):
    """
    CRUD with RBAC and filtering:
      - list/retrieve: customer → own orders; admin → all
      - create: customer or admin
      - update/destroy: owner OR holders of custom perms
    """

    permission_classes = (IsAuthenticated, IsOwnerOrHasOrderPerms)
    throttle_scope = "orders"

    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filterset_class = OrderFilter
    ordering_fields = ("created_at", "updated_at", "total_price")
    ordering = ("-created_at",)

    def get_queryset(self):
        # Tiny and clear: base → scope
        return scope_for_user(order_base_qs(), self.request.user)

    def get_serializer_class(self):
        return {
            "create": OrderCreateSerializer,
            "update": OrderUpdateSerializer,
            "partial_update": OrderUpdateSerializer,
            "list": OrderReadSerializer,
            "retrieve": OrderReadSerializer,
            "destroy": OrderReadSerializer,
        }[self.action]

    def create(self, request, *args, **kwargs):
        ser = self.get_serializer(data=request.data, context={"request": request})
        ser.is_valid(raise_exception=True)
        order = ser.save()
        return Response(
            OrderReadSerializer(order, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        ser = self.get_serializer(
            instance, data=request.data, context={"request": request}
        )
        ser.is_valid(raise_exception=True)
        order = ser.save()
        return Response(
            OrderReadSerializer(order, context={"request": request}).data,
            status=status.HTTP_200_OK,
        )

    def partial_update(self, request, *args, **kwargs):
        # Same contract as update (client sends new desired items state)
        return self.update(request, *args, **kwargs)
