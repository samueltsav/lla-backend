from rest_framework import permissions
from .authentication import JWTAuthentication


class IsAdminUser(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user or not hasattr(request.user, "user_id"):
            return False

        # Service-user bypass
        if getattr(request.user, "user_id", None) == 0:
            return True

        return JWTAuthentication.validate_admin_user(request.user.user_id)


class IsOwnerOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return request.user and hasattr(request.user, "user_id")

        # Check for ownership
        is_owner = hasattr(obj, "user_id") and obj.user_id == request.user.user_id

        # Check for admin
        is_admin = JWTAuthentication.validate_admin_user(request.user.user_id)

        # Service-user bypass
        is_service_user = getattr(request.user, "user_id", None) == 0

        return is_owner or is_admin or is_service_user
