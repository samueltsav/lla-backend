import jwt
import os
import requests
import logging
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from types import SimpleNamespace
from dotenv import load_dotenv


logger = logging.getLogger(__name__)
load_dotenv()


class AuthenticatedUser(SimpleNamespace):
    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    @property
    def is_active(self):
        return getattr(self, "is_active", True)

    def __str__(self):
        return f"User({getattr(self, 'uid', 'unknown')})"


class JWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return None

        token = auth_header.split(" ")[1]

        try:
            payload = jwt.decode(
                token,
                os.getenv("JWT_KEY"),
                algorithms=[os.getenv("JWT_ALGORITHM")],
            )
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Expired token")
        except jwt.InvalidTokenError:
            raise AuthenticationFailed("Invalid token")

        # Create user object that works with DRF
        user = AuthenticatedUser(**payload)
        return (user, None)

    def validate_admin_user(self, uid):
        try:
            response = requests.post(
                f"{self.base_url}/auth/service/validate-admin/",
                json={"uid": uid},
                headers=self.headers,
                timeout=20,
            )

            if response.status_code == 200:
                data = response.json()
                return data.get("is_staff", False) and data.get("is_active", False)

            return False

        except requests.RequestException as e:
            logger.error(f"Error validating admin status for user {uid}: {e}")
            return False
