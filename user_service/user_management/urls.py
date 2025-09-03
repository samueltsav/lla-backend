from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic import TemplateView
from django.urls import include, path, re_path
from users.urls import service_patterns
from users.views import MyTokenCreateView
from rest_framework_simplejwt.views import TokenRefreshView
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
)
from users.views import HealthCheckView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", TemplateView.as_view(template_name="index.html"), name="home"),
    path("auth/jwt/create/", MyTokenCreateView.as_view(), name="jwt-create"),
    path("auth/jwt/refresh/", TokenRefreshView.as_view(), name="jwt-refresh"),
    re_path(r"^auth/", include("djoser.urls")),
    re_path(r"^auth/", include("djoser.urls.jwt")),
    path("auth/account/", include("dashboard.urls")),
    path("auth/service/", include(service_patterns)),
    path("auth/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("auth/schema/docs/", SpectacularSwaggerView.as_view(url_name="schema")),
    path("health", HealthCheckView.as_view()),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
