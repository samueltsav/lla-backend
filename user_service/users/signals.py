from axes.signals import user_locked_out
from rest_framework.exceptions import PermissionDenied
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in
from .login_handler import LoginNotificationHandler


@receiver(user_locked_out)
def raise_permission_denied(*args, **kwargs):
    raise PermissionDenied("Too many failed login attempts. Your account is locked.")

# Signal to listen to login event
@receiver(user_logged_in)
def send_login_notification(sender, request, user, **kwargs):
    handler = LoginNotificationHandler(user=user, request=request)
    handler.handle_login()