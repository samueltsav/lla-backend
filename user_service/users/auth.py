import jwt
import logging
from jwt.algorithms import RSAAlgorithm
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth import get_user_model
from django.utils import timezone
from user_service_config.django import base
#from django.conf import base

User = get_user_model()
logger = logging.getLogger(__name__)


class ClerkJWTAuthentication(BaseAuthentication):
    """
    DRF Authentication class that validates Clerk JWTs and syncs user on-demand.
    """

    def authenticate(self, request):
        auth = request.headers.get("Authorization") or request.headers.get(
            "authorization"
        )
        if not auth:
            return None
        parts = auth.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            raise AuthenticationFailed("Invalid Authorization header")

        token = parts[1]
        payload = self._validate_token(token)
        sub = payload.get("sub")
        if not sub:
            raise AuthenticationFailed("Invalid token payload: missing sub")

        # get or create local user
        user, created = User.objects.get_or_create(id=sub)

        # Fetch latest profile data from Clerk (best-effort). Errors should not block auth.
        try:
            from .clerk_sdk import ClerkSDK

            sdk = ClerkSDK()
            data = sdk.fetch_user(sub)
            if data:
                # Map fields carefully (api shape may differ)
                emails = data.get("email_addresses") or []
                email = emails[0].get("email_address") if emails else ""
                user.email = email
                user.first_name = data.get("first_name", "")
                user.last_name = data.get("last_name", "")
                # Clerk uses epoch millis for some timestamps; be defensive
                last_sign_in = data.get("last_sign_in_at") or data.get("last_sign_in")
                if last_sign_in:
                    try:
                        ts = int(last_sign_in)
                        user.last_login = timezone.datetime.fromtimestamp(
                            ts / 1000, tz=timezone.utc
                        )
                    except Exception:
                        pass
                user.save()
        except Exception as e:
            logger.exception("Clerk profile fetch failed: %s", e)

        if not user.is_active:
            raise AuthenticationFailed("User is inactive")

        return (user, None)

    def _validate_token(self, token: str):
        try:
            # fetch jwks and find key
            from .clerk_sdk import ClerkSDK

            sdk = ClerkSDK()
            jwks = sdk.get_jwks()
            header = jwt.get_unverified_header(token)
            kid = header.get("kid")
            key = None
            for jwk in jwks.get("keys", []):
                if jwk.get("kid") == kid:
                    key = RSAAlgorithm.from_jwk(jwk)
                    break
            if not key:
                raise AuthenticationFailed("Signing key not found")

            payload = jwt.decode(
                token,
                key,
                algorithms=["RS256"],
                audience=getattr(base, "CLERK_AUDIENCE", None),
                issuer=getattr(base, "CLERK_ISSUER", None),
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Token expired")
        except jwt.InvalidTokenError as e:
            raise AuthenticationFailed(f"Invalid token: {e}")
