import os

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

from orderflow.contrib.routers import ExtendableRouter
from orderflow.users.urls import router as users_router

root_router = ExtendableRouter()
for r in [
    users_router,
]:
    root_router.extend(r)


# Admin URLs
admin_urlpatterns = [
    path("admin/", admin.site.urls),
]


# Apps URLs
apps_urlpatterns = [
    re_path(r"^api/", include(root_router.urls)),
]


# Schema URLs
schema_urlpatterns = [
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "schema/swagger-ui/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "schema/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"
    ),
]


# Combine all URL patterns
urlpatterns = admin_urlpatterns + apps_urlpatterns + schema_urlpatterns


if os.environ.get("DJANGO_SETTINGS_MODULE") == "orderflow.settings.local":
    import debug_toolbar

    urlpatterns = [
        path("__debug__/", include(debug_toolbar.urls)),
    ] + urlpatterns
    #
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
