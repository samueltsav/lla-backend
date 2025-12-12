from clerk_backend_api import Clerk
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from user_service_config.django import base
from django.contrib.auth import get_user_model


User = get_user_model()

clerk_client = Clerk(bearer_auth=base.CLERK_SECRET_KEY)

class ClerkAuthentication(BaseAuthentication):
    """
    DRF authentication backend using Clerk SDK.
    """

    def authenticate(self, request):
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return None

        if not auth_header.startswith("Bearer "):
            raise AuthenticationFailed("Invalid Authorization header")

        token = auth_header.split("Bearer ")[1]

        try:
            session = clerk_client.verify_token(token)  
            # -> returns session claims if valid
        except Exception as e:
            raise AuthenticationFailed(f"Token verification failed: {e}")

        clerk_user_id = session.get("sub")
        email = session.get("email")

        if not clerk_user_id:
            raise AuthenticationFailed("No Clerk user ID found in token")

        # Mirror local user
        user, _ = User.objects.get_or_create(
            user_id=clerk_user_id,
            defaults={"email": email or ""},
        )

        # Attach claims for downstream use
        request.clerk_claims = session

        return (user, None)
