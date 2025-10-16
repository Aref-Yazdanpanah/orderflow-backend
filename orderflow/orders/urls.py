from rest_framework.routers import DefaultRouter

from .views import OrderViewSetV1

app_name = "orders"

router = DefaultRouter()
router.register("v1/orders", OrderViewSetV1, basename="v1-orders")

urlpatterns = []
