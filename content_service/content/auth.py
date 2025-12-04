import requests
import jwt
from django.contrib.auth import get_user_model
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

User = get_user_model()


class ClerkJWTAuthentication(BaseAuthentication):
    """
    Authenticates incoming requests using Clerk-issued JWTs.
    """

    JWKS_URL = "https://fitting-alpaca-51.clerk.accounts.dev/.well-known/jwks.json"
    ISSUER = "https://fitting-alpaca-51.clerk.accounts.dev/"
    AUDIENCE = "authenticated"  # Required by Clerk

    def __init__(self):
        self.jwk_cache = {}

    # ----------------------------------------------------
    # Fetch JSON Web Keys
    # ----------------------------------------------------
    def fetch_jwks(self):
        resp = requests.get(self.JWKS_URL)
        resp.raise_for_status()
        jwks = resp.json().get("keys", [])

        self.jwk_cache = {
            k["kid"]: jwt.algorithms.RSAAlgorithm.from_jwk(k) for k in jwks
        }

    # ----------------------------------------------------
    # Get public RSA key from cache or fetch if missing
    # ----------------------------------------------------
    def get_public_key(self, kid):
        if kid not in self.jwk_cache:
            self.fetch_jwks()
        return self.jwk_cache.get(kid)

    # ----------------------------------------------------
    # Main authentication function
    # ----------------------------------------------------
    def authenticate(self, request):
        auth = request.headers.get("Authorization", "")
        if not auth.startswith("Bearer "):
            return None

        token = auth.split(" ")[1]

        try:
            # Extract unverified header
            unverified_header = jwt.get_unverified_header(token)
            kid = unverified_header.get("kid")
            if not kid:
                raise AuthenticationFailed("Missing 'kid' in token header.")

            # Retrieve proper signing key
            public_key = self.get_public_key(kid)
            if not public_key:
                raise AuthenticationFailed("Unable to verify token: unknown key")

            # Decode and validate token
            payload = jwt.decode(
                token,
                key=public_key,
                algorithms=["RS256"],
                audience=self.AUDIENCE,
                issuer=self.ISSUER,
            )

        except Exception as e:
            raise AuthenticationFailed(f"Invalid Clerk token: {str(e)}")

        # ----------------------------------------------------
        # Extract Clerk user claims
        # ----------------------------------------------------
        id = payload.get("sub")
        if not id:
            raise AuthenticationFailed("Token missing 'sub' user ID.")

        email = payload.get("email", payload.get("email_address", ""))
        first_name = payload.get("first_name", payload.get("given_name", ""))
        last_name = payload.get("last_name", payload.get("family_name", ""))

        # ----------------------------------------------------
        # Create/update local user
        # ----------------------------------------------------
        user, _ = User.objects.update_or_create(
            id=id,
            defaults={
                "email": email,
                "first_name": first_name,
                "last_name": last_name,
                "is_active": True,
            },
        )

        return (user, token)
