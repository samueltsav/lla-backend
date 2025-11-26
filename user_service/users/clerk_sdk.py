import logging
import requests
from django.core.cache import cache
from user_service_config.django import base
# from django.conf import settings

logger = logging.getLogger(__name__)

JWKS_CACHE_KEY = "clerk_jwks"
JWKS_CACHE_TIMEOUT = 60 * 60  # 1 hour


class ClerkSDK:
    """Thin wrapper around Clerk REST API and JWKS fetching."""

    def __init__(self):
        self.api_key = getattr(base, "CLERK_API_KEY", None)
        self.frontend_api = getattr(
            base, "CLERK_FRONTEND_API_URL", "https://api.clerk.com"
        )
        self.api_url = getattr(base, "CLERK_API_URL", "https://api.clerk.com")

    def get_jwks(self):
        jwks = cache.get(JWKS_CACHE_KEY)
        if jwks:
            return jwks
        url = f"{self.frontend_api}/.well-known/jwks.json"
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        jwks = resp.json()
        cache.set(JWKS_CACHE_KEY, jwks, JWKS_CACHE_TIMEOUT)
        return jwks

    def fetch_user(self, user_id: str):
        url = f"{self.api_url}/v1/users/{user_id}"
        headers = {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}
        resp = requests.get(url, headers=headers, timeout=5)
        if resp.status_code == 200:
            return resp.json()
        if resp.status_code == 404:
            return None
        resp.raise_for_status()

    def verify_webhook_signature(self, body: bytes, signature_header: str) -> bool:
        """
        Basic HMAC verification used earlier in examples. If Clerk uses a different scheme in your
        workspace (e.g., Ed25519), replace this with the correct verification logic."
        secret = getattr(base, "CLERK_WEBHOOK_SECRET", None)
        if not secret or not signature_header:
            return False
        computed = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
        return hmac.compare_digest(computed, signature_header)

        """
