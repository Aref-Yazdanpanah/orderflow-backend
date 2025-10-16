from rest_framework.routers import DefaultRouter

from . import views as v

app_name = "users"

router = DefaultRouter()
router.register("v1/auth", v.AuthenticationViewSetV1, basename="v1-authentication")
router.register("v1/users", v.UserViewSetV1, basename="v1-user")

urlpatterns = []
