from django.urls import path

from .views import DashboardApiView

app_name = "dashboard"

urlpatterns = [
    path("", DashboardApiView.as_view(), name="account"),
]
