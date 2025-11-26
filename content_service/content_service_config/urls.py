from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
)
from content.views import HealthCheckView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("content.urls")),
    path("health", HealthCheckView.as_view()),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/schema/docs/", SpectacularSwaggerView.as_view(url_name="schema")),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
