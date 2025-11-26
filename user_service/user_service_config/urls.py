from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
)
from users.views import HealthCheckView


urlpatterns = [
    path("admin/", admin.site.urls),
    path("auth/", include("dashboard.urls")),
    path("auth/", include("users.urls")),
    path("auth/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("auth/schema/docs/", SpectacularSwaggerView.as_view(url_name="schema")),
    path("health", HealthCheckView.as_view()),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
