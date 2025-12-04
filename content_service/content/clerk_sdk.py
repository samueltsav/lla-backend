import logging
from user_service_config.django import base
from svix.webhooks import Webhook

logger = logging.getLogger(__name__)

JWKS_CACHE_KEY = "clerk_jwks"
JWKS_CACHE_TIMEOUT = 60 * 60  # 1 hour


class ClerkSDK:
    def __init__(self):
        self.api_key = getattr(base, "CLERK_SECRET_KEY", None)
        self.api_url = getattr(base, "CLERK_API_URL", "https://api.clerk.com")
        self.frontend_api = getattr(
            base,
            "CLERK_FRONTEND_API_URL",
            "https://fitting-alpaca-51.clerk.accounts.dev",
        )

    def verify_webhook_signature(self, body: bytes, signature_header: str) -> bool:
        secret = getattr(base, "CLERK_WEBHOOK_SECRET", None)

        if not secret or not signature_header:
            return False

        try:
            wh = Webhook(secret)
            wh.verify(body, signature_header)  # raises exception if invalid
            return True
        except Exception as e:
            logger.error(f"Webhook signature verification failed: {e}")
            return False
